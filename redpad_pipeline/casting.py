"""Evidence-limited casting, Director inspection, explicit Producer identity locks."""
import json,re
from uuid import uuid4
from .agents import AgentError,encode
from .producer_references import References

CONSUMERS={'costume','storyboard','performance','cinematographer','motion','video','voice','continuity','qc'}
FIELDS=['id','character','actor_id','appearance','apparent_age','psychology','performance_requirements','voice_requirements','chemistry_requirements','image_refs','voice_refs','recommendation']
EXAMPLE=dict(id='candidate-rafi-1',character='rafi',actor_id='fictional-rafi-01',appearance='Original fictional Bangladeshi man; identity pending Producer lock',apparent_age=33,psychology='Guarded, wanting reassurance',performance_requirements='Restrained reaction, listening, playable objective',voice_requirements='Natural Bangladeshi Bengali; listening review pending',chemistry_requirements='Partner scene must be reviewed',image_refs=[],voice_refs=[],recommendation='Proposal only; media and independent review pending')

def validate(rows,sources):
    from .specialists import records,need,number,text
    records(rows,FIELDS)
    chars={r['id'] for r in sources.get('character',{}).get('records',[])}
    for r in rows:
        need(not chars or r['character'] in chars,'Casting character absent from approved Character Bible.')
        need(bool(re.fullmatch(r'[A-Za-z0-9_-]{1,80}',r['actor_id'])),'Stable safe actor ID required.')
        need(number(r['apparent_age'],0,120),'Invalid apparent age.')
        for f in ('appearance','psychology','performance_requirements','voice_requirements','chemistry_requirements','recommendation'):need(text(r[f]),'Casting brief text required: '+f)
        for f in ('image_refs','voice_refs'):
            need(isinstance(r[f],list) and all(isinstance(x,dict) and set(x)=={'id','version'} and type(x['version']) is int for x in r[f]),'Exact reference ID/version list required.')
        need(not set(r)&{'performance_passed','voice_passed','chemistry_passed','acting_verified'},'Model prose cannot certify tested acting, voice or chemistry.')
    return {'actor_candidates':{r['id']:r['actor_id'] for r in rows},'evaluation_status':'proposal_only','acting_verified':False,'voice_verified':False,'chemistry_verified':False,'human_review_required':True}

class Casting:
    def __init__(self,program):
        self.p=program;self.store=program.store;self.refs=References(self.store)
        with self.store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS casting_inspections(task TEXT PRIMARY KEY,source TEXT,revision INTEGER);
          CREATE TABLE IF NOT EXISTS casting_locks(id TEXT PRIMARY KEY,task TEXT,revision INTEGER,director TEXT,payload TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS casting_current(character TEXT PRIMARY KEY,lock_id TEXT);
          CREATE TABLE IF NOT EXISTS casting_consumers(task TEXT,character TEXT,lock_id TEXT,PRIMARY KEY(task,character));
          CREATE TABLE IF NOT EXISTS casting_evaluations(id TEXT PRIMARY KEY,task TEXT,revision INTEGER,payload TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
    def proposal(self,task,db=None):
        if db is None:
            with self.store.tx() as tx:return self.proposal(task,tx)
        t=self.store._task(db,task)
        if t['agent']!='casting' or not t['revision'] or t['state'] not in ('Awaiting QC','QC recommended','Approved'):raise AgentError('Current casting proposal required.')
        self.store._current(db,t)
        row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,t['revision'])).fetchone()
        body=json.loads(json.loads(row[0])['summary'])
        if body.get('artifact',{}).get('department')!='casting':raise AgentError('Casting specialist proposal required.')
        return t,body
    def queue_review(self,task):
        t,body=self.proposal(task)
        # Inspection is read-only, pinned independently; never promotes pending material to approved dependencies.
        rid=self.p.engine.enqueue('director',{'producer_director_v1':True,'message':'Review casting fit against the approved brief. Cite candidate IDs; visual appearance does not prove acting, voice or chemistry. No approvals.',
           'context':{'casting_proposal':body},'reply':None},[],mode='local',idempotency_key='casting-review:'+task+':'+str(t['revision']))
        review=next(r['task'] for r in self.p.engine.runs() if r['id']==rid)
        with self.store.tx() as db:
            db.execute('INSERT OR IGNORE INTO casting_inspections VALUES (?,?,?)',(review,task,t['revision']))
        return rid
    def evaluate(self,task,criterion,refs,observation,reviewer):
        t,_=self.proposal(task)
        if criterion not in ('appearance','performance','voice','chemistry') or not all(isinstance(s,str) and s.strip() for s in (observation,reviewer)):raise AgentError('Named human reviewer and observation required.')
        if not refs:raise AgentError('Actual media reference evidence required.')
        actual=[self.refs.get(x['id'],x['version']) for x in refs]
        for r in actual:self.refs.path(r)
        if criterion=='appearance':allowed={'.png','.jpg','.jpeg','.webp','.mp4','.mov','.webm'}
        elif criterion=='voice':allowed={'.wav','.mp3','.m4a','.mp4','.mov','.webm'}
        else:allowed={'.mp4','.mov','.webm'}
        if any(r['extension'] not in allowed for r in actual):raise AgentError('Criterion requires actual suitable media; a still image cannot prove acting or chemistry.')
        payload={'criterion':criterion,'refs':refs,'observation':observation,'reviewer':reviewer,'kind':'human_observation_not_automatic_acceptance'}
        id=uuid4().hex
        with self.store.tx() as db:db.execute('INSERT INTO casting_evaluations(id,task,revision,payload) VALUES (?,?,?,?)',(id,task,t['revision'],encode(payload)))
        return id
    def lock(self,task,director_task,selected,reason,confirm_recast=False):
        if not isinstance(selected,list) or not selected or len(set(selected))!=len(selected) or not isinstance(reason,str) or not reason.strip():raise AgentError('Exact candidate IDs and Producer reason required.')
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');t,body=self.proposal(task,db)
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='producer_decisions'").fetchone():
                decision=db.execute('SELECT action FROM producer_decisions WHERE task=? AND revision=? ORDER BY id DESC LIMIT 1',(task,t['revision'])).fetchone()
                if decision and decision[0] in ('Reject','Request Changes'):raise AgentError('Producer requested a new casting version before approval.')
            if t['state']!='QC recommended':raise AgentError('Independent QC recommendation for casting required.')
            d=self.store._task(db,director_task)
            pin=db.execute('SELECT * FROM casting_inspections WHERE task=?',(director_task,)).fetchone()
            if d['agent']!='director' or d['state'] not in ('QC recommended','Approved') or not pin or pin['source']!=task or pin['revision']!=t['revision']:raise AgentError('Exact Director casting inspection and independent QC recommendation required.')
            self.store._current(db,d)
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='producer_decisions'").fetchone():
                feedback=db.execute('SELECT action FROM producer_decisions WHERE task=? AND revision=? ORDER BY id DESC LIMIT 1',(director_task,d['revision'])).fetchone()
                if feedback and feedback[0] in ('Reject','Request Changes'):raise AgentError('Director inspection requires a revised accepted report.')
            candidates={r['id']:r for r in body['artifact']['records']}
            if not set(selected)<=candidates.keys():raise AgentError('Unknown candidate.')
            rows=[candidates[k] for k in selected];characters=[r['character'] for r in rows]
            if len(set(characters))!=len(rows):raise AgentError('One actor candidate per character.')
            # Every supplied character needs an explicit casting decision, not a hidden missing identity.
            sourcechars=set()
            for ref in json.loads(t['refs']):
                st=self.store._task(db,ref['id'])
                if st['agent']=='character':
                    raw=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(st['id'],st['revision'])).fetchone()
                    sourcechars.update(r['id'] for r in json.loads(json.loads(raw[0])['summary'])['artifact']['records'])
            if not sourcechars or set(characters)!=sourcechars:raise AgentError('Casting must explicitly cover every approved character.')
            assets=[]
            for r in rows:
                if not r['image_refs']:raise AgentError('Actual authorized image references required to lock an actor identity.')
                for ref in r['image_refs']+r['voice_refs']:
                    a=self.refs.get(ref['id'])
                    if a['version']!=ref['version'] or a['archived'] or a['rights'] not in ('fictional_ai','authorized_person') or not a['source'].strip():raise AgentError('Current fictional AI or explicitly authorized human identity rights/source required.')
                    self.refs.path(a)
                    allowed={'.png','.jpg','.jpeg','.webp'} if ref in r['image_refs'] else {'.wav','.mp3','.m4a'}
                    if a['extension'] not in allowed:raise AgentError('Identity image/voice reference type mismatch.')
                    assets.append(ref)
            old=[dict(r) for r in db.execute('SELECT * FROM casting_current') if r['character'] in characters]
            if old and confirm_recast is not True:raise AgentError('Locked identities exist. Explicit recast confirmation required; dependent work will become stale.')
            lock_id=uuid4().hex;payload={'actors':rows,'assets':assets,'producer_reason':reason,'actor':'owner','previous':old,'performance_acceptance':'Not inferred from identity lock; independent media evaluation required.'}
            db.execute('INSERT INTO casting_locks(id,task,revision,director,payload) VALUES (?,?,?,?,?)',(lock_id,task,t['revision'],director_task,encode(payload)))
            for c in characters:db.execute('INSERT OR REPLACE INTO casting_current VALUES (?,?)',(c,lock_id))
            for tid in (task,director_task):
                db.execute("UPDATE tasks SET state='Approved' WHERE id=?",(tid,));self.store.event(db,tid,'owner','Approve',{'revision':t['revision'] if tid==task else d['revision'],'evidence':reason,'casting_lock':lock_id})
            for ref in { (r['id'],r['version']) for r in assets }:
                db.execute('INSERT OR IGNORE INTO producer_ref_pins VALUES (?,?,?)',(task,*ref))
            return lock_id
    def current(self):
        with self.store.tx() as db:return [dict(r) for r in db.execute('SELECT c.character,c.lock_id,l.task,l.revision,l.payload FROM casting_current c JOIN casting_locks l ON l.id=c.lock_id')]

def check_casting(db,store,t):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='casting_inspections'").fetchone():return
    pin=db.execute('SELECT * FROM casting_inspections WHERE task=?',(t['id'],)).fetchone()
    if pin:
        source=store._task(db,pin['source'])
        if source['revision']!=pin['revision'] or source['state'] not in ('Awaiting QC','QC recommended','Approved'):raise AgentError('Casting inspection source changed.')
        store._current(db,source)
    for c in db.execute('SELECT p.lock_id,c.lock_id FROM casting_consumers p LEFT JOIN casting_current c ON c.character=p.character WHERE p.task=?',(t['id'],)):
        if c[0]!=c[1]:raise AgentError('Recasting invalidated dependent work.')
    for ref in json.loads(t['refs']):
        s=store._task(db,ref['id'])
        if s['agent']=='casting' and t['agent'] in CONSUMERS:
            locks=db.execute('SELECT c.character,l.* FROM casting_current c JOIN casting_locks l ON l.id=c.lock_id WHERE l.task=? AND l.revision=?',(s['id'],s['revision'])).fetchall()
            if not locks:raise AgentError('Producer-locked casting identity required.')
            for row in locks:
                old=db.execute('SELECT lock_id FROM casting_consumers WHERE task=? AND character=?',(t['id'],row['character'])).fetchone()
                if old and old[0]!=row['id']:raise AgentError('Casting lock changed; dependent task stale.')
                db.execute('INSERT OR IGNORE INTO casting_consumers VALUES (?,?,?)',(t['id'],row['character'],row['id']))

def bind_output(db,store,t,result):
    """Derive production identity pins from Producer locks, never from model claims."""
    if t['agent'] not in CONSUMERS:return
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='casting_consumers'").fetchone():return
    pins=[dict(r) for r in db.execute('SELECT p.character,p.lock_id,l.payload FROM casting_consumers p JOIN casting_locks l ON l.id=p.lock_id WHERE p.task=?',(t['id'],))]
    if not pins:return
    actors={p['character']:next(r for r in json.loads(p['payload'])['actors'] if r['character']==p['character']) for p in pins}
    artifact=result['artifact']
    for r in artifact.get('records',[]):
        chars=r.get('characters',[])
        if 'character' in r:chars=[r['character']]
        for c in chars:
            if c not in actors:raise AgentError('Output character has no current locked actor.')
            if 'actor_id' in r and r['actor_id']!=actors[c]['actor_id']:raise AgentError('Output actor differs from Producer-locked identity.')
    artifact.setdefault('derived',{})['casting_identity_locks']=[{'character':p['character'],'lock_id':p['lock_id'],'actor_id':actors[p['character']]['actor_id'],'image_refs':actors[p['character']]['image_refs'],'voice_refs':actors[p['character']]['voice_refs']} for p in pins]
