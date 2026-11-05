"""Offline agent registration and contracts. No inference, production DB or network access."""
from contextlib import contextmanager
from pathlib import Path
import json
import re
import sqlite3
from uuid import uuid4

CATALOG = json.loads(Path(__file__).with_name('agent_catalog.json').read_text())
AGENTS = {a['key']: a for a in CATALOG}

class AgentError(ValueError):
    pass

def agent(key):
    if key not in AGENTS:
        raise AgentError('Unknown agent.')
    return AGENTS[key]

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def encode(value):
    try:
        result = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        raise AgentError('Invalid JSON.') from None
    if len(result) > 100000:
        raise AgentError('Record too large.')
    return result

class AgentStore:
    """Separate SQLite sidecar. Trusted owner UI supplies human approval, never model outputs."""
    def __init__(self, path):
        self.path = Path(path)
        if self.path.name != 'agent_control.sqlite3':
            raise AgentError('Use the dedicated agent_control.sqlite3 sidecar.')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.tx() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS config(agent TEXT PRIMARY KEY, model TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, agent TEXT, brief TEXT, refs TEXT, revision INTEGER DEFAULT 0, state TEXT DEFAULT 'Assigned');
            CREATE TABLE IF NOT EXISTS outputs(task TEXT, revision INTEGER, payload TEXT, PRIMARY KEY(task,revision));
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, task TEXT, actor TEXT, action TEXT, detail TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
            ''')
    @contextmanager
    def tx(self):
        with sqlite3.connect(self.path, timeout=15) as db:
            db.row_factory = sqlite3.Row
            yield db
    def event(self, db, task, actor, action, detail):
        db.execute('INSERT INTO events(task,actor,action,detail) VALUES (?,?,?,?)',(task,actor,action,encode(detail)))
    def configure(self, key, model):
        agent(key)
        if not isinstance(model,str) or (model and (not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,120}',model) or 'cloud' in model.lower())):
            raise AgentError('Use a local model identifier only; no credentials or cloud models.')
        with self.tx() as db:
            db.execute('INSERT OR REPLACE INTO config VALUES (?,?)',(key,model))
            self.event(db,'', 'owner','configure',{'agent':key,'model':model})
    def status(self, key):
        agent(key)
        with self.tx() as db:
            row=db.execute('SELECT model FROM config WHERE agent=?',(key,)).fetchone()
        return {'registration':'Registered','configuration':'Configured' if row and row[0] else 'Not configured',
                'model':row[0] if row else '', 'connection':'Model Not Connected','readiness':'Blocked',
                'blocker':'No agent inference adapter verified in this registration phase.',
                'tests':'Registry/contract tests only; see AGENT_CONTROL_VERIFICATION.md',
                'progress':'Foundation registered; individual development pending'}
    def tasks(self):
        with self.tx() as db:
            return [dict(r) for r in db.execute('SELECT * FROM tasks ORDER BY rowid DESC')]
    def outputs(self):
        with self.tx() as db:
            return [dict(r) for r in db.execute("SELECT * FROM outputs ORDER BY task, revision")]
    def history(self):
        with self.tx() as db:
            return [dict(r) for r in db.execute('SELECT * FROM events ORDER BY id DESC')]
    def _task(self, db, tid):
        row=db.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
        if not row: raise AgentError('Unknown task.')
        return dict(row)
    def _current(self,db,t):
        for ref in json.loads(t['refs']):
            source=self._task(db,ref['id'])
            if source['state']!='Approved' or source['revision']!=ref['revision']:
                raise AgentError('Dependency approval is stale.')
            self._current(db,source)
    def assign(self,key,brief,references=None,actor='owner'):
        agent(key)
        if actor not in ('owner','director') or (key=='qc' and actor!='owner'):
            raise AgentError('QC is independent; owner assigns QC tasks.')
        if not nonempty(brief): raise AgentError('Brief is required.')
        references=[] if references is None else references
        if not isinstance(references,list) or any(not isinstance(x,str) for x in references): raise AgentError('Invalid references.')
        encode(brief)
        with self.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            refs=[]
            for tid in dict.fromkeys(references):
                t=self._task(db,tid)
                if t['state']!='Approved': raise AgentError('Handoff requires owner-approved output.')
                self._current(db,t)
                refs.append({'id':tid,'revision':t['revision']})
            tid=uuid4().hex
            db.execute('INSERT INTO tasks(id,agent,brief,refs) VALUES (?,?,?,?)',(tid,key,brief,encode(refs)))
            self.event(db,tid,actor,'assign',{'agent':key,'references':refs})
            for ref in refs: self.event(db,tid,actor,'handoff',ref)
            return tid
    def submit(self,tid,payload,expected_revision):
        with self.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            t=self._task(db,tid)
            self._current(db,t)
            if type(expected_revision)!=int or t['revision']!=expected_revision: raise AgentError('Stale revision; refresh.')
            if t['state'] not in ('Assigned','Revision requested'): raise AgentError('Request a targeted revision first; accepted output is preserved.')
            if not isinstance(payload,dict) or set(payload)!={'schema_version','kind','summary','artifacts','provenance'}: raise AgentError('Output fields do not match contract.')
            if type(payload['schema_version'])!=int or payload['schema_version']!=1 or payload['kind']!=agent(t['agent'])['output_contract']['kind'] or not nonempty(payload['summary']): raise AgentError('Invalid output contract.')
            if payload['provenance'] not in ('manual','simulation') or not isinstance(payload['artifacts'],list) or any(not nonempty(x) for x in payload['artifacts']): raise AgentError('Unverified inference is not accepted.')
            revision=t['revision']+1
            db.execute('INSERT INTO outputs VALUES (?,?,?)',(tid,revision,encode(payload)))
            db.execute("UPDATE tasks SET revision=?,state='Awaiting QC' WHERE id=?",(revision,tid))
            self.event(db,tid,t['agent'],'output',{'revision':revision,'provenance':payload['provenance']})
    def review(self,tid,revision,decision,evidence,actor):
        if decision not in ('Recommend','Reject','Approve','Request revision') or not nonempty(evidence): raise AgentError('Decision and evidence required.')
        if (decision in ('Recommend','Reject') and actor!='qc') or (decision in ('Approve','Request revision') and actor!='owner'): raise AgentError('Only independent QC recommends; only owner approves.')
        with self.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            t=self._task(db,tid)
            if not t['revision'] or type(revision)!=int or revision!=t['revision']: raise AgentError('Stale or missing output.')
            self._current(db,t)
            if actor=='qc' and t['agent']=='qc': raise AgentError('QC cannot review its own output; owner must review QC records separately.')
            if decision in ('Recommend','Reject') and t['state']!='Awaiting QC': raise AgentError('Not awaiting QC.')
            if decision=='Approve' and t['state']!='QC recommended': raise AgentError('Independent QC recommendation required.')
            state={'Recommend':'QC recommended','Reject':'Revision requested','Approve':'Approved','Request revision':'Revision requested'}[decision]
            db.execute('UPDATE tasks SET state=? WHERE id=?',(state,tid))
            self.event(db,tid,actor,decision,{'revision':revision,'evidence':evidence})
