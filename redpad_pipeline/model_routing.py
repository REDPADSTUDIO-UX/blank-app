"""Owner-controlled, digest-pinned local model routes in the existing sidecar.

Research permission is separate from artistic acceptance. No downloads, hosted
providers, automatic model selection or approval actions exist in this module.
"""
import hashlib
import json
import re
import time
import urllib.request
from .agents import AGENTS, AgentError, encode
from .screenwriter import LocalWriter, WritingError, LocalUnavailable


def local_id(name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*:[A-Za-z0-9_.-]+',name) or 'cloud' in name.lower():
        raise AgentError('An explicit local model tag is required; cloud/URL identifiers are forbidden.')


def inventory():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    with opener.open('http://127.0.0.1:11434/api/tags',timeout=5) as response:
        raw=response.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:raise WritingError('Local inventory exceeds bound.')
    models=json.loads(raw)['models']
    return {m['name']:m['digest'] for m in models}


class ModelRoutes:
    def __init__(self,store):
        self.store=store
        with store.tx() as db:db.executescript('''
            CREATE TABLE IF NOT EXISTS approved_local_models
            (name TEXT PRIMARY KEY,digest TEXT,license_note TEXT,owner TEXT,approved INTEGER);
            CREATE TABLE IF NOT EXISTS specialist_model_routes
            (role TEXT PRIMARY KEY,policy TEXT);
            CREATE TABLE IF NOT EXISTS model_route_snapshots
            (run TEXT PRIMARY KEY,policy TEXT);
            CREATE TABLE IF NOT EXISTS routed_model_attempts
            (id INTEGER PRIMARY KEY,run TEXT,role TEXT,model TEXT,digest TEXT,raw TEXT,evidence TEXT,error TEXT,created REAL);
            CREATE TABLE IF NOT EXISTS model_acceptances
            (role TEXT,name TEXT,digest TEXT,benchmark TEXT,human TEXT,PRIMARY KEY(role,name,digest));
        ''')

    def approve_installed(self,name,digest,license_note,owner,confirmed=False):
        local_id(name)
        if confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Explicit owner and license confirmation required.')
        if not re.fullmatch(r'sha256:[a-f0-9]{64}',digest):raise AgentError('Full installed model digest required.')
        if inventory().get(name)!=digest:raise AgentError('Exact approved model is not installed at this runtime.')
        with self.store.tx() as db:
            db.execute('INSERT OR REPLACE INTO approved_local_models VALUES (?,?,?,?,1)',(name,digest,license_note,owner))
            self.store.event(db,'','owner','approve_local_model',{'name':name,'digest':digest,'owner':owner})

    def revoke(self,name):
        with self.store.tx() as db:
            db.execute('UPDATE approved_local_models SET approved=0 WHERE name=?',(name,))
            db.execute('DELETE FROM model_acceptances WHERE name=?',(name,))
            self.store.event(db,'','owner','revoke_local_model',{'name':name})

    def models(self):
        with self.store.tx() as db:return [dict(r) for r in db.execute('SELECT * FROM approved_local_models ORDER BY name')]

    def policy(self,role):
        with self.store.tx() as db:r=db.execute('SELECT policy FROM specialist_model_routes WHERE role=?',(role,)).fetchone()
        return json.loads(r[0]) if r else None

    def accept(self,role,name,benchmark,human,confirmed=False):
        """Trusted owner entry; the benchmark must contain real matching evidence.
        Human identity/independence is attested, never inferred by a model.
        """
        from .model_benchmark import check_selection
        row=next((m for m in self.models() if m['name']==name and m['approved']),None)
        if not row:raise AgentError('Model has no current owner approval.')
        check_selection(role,name,row['digest'],benchmark,human,confirmed)
        with self.store.tx() as db:
            db.execute('INSERT OR REPLACE INTO model_acceptances VALUES (?,?,?,?,?)',
                       (role,name,row['digest'],encode(benchmark),encode(human)))
            self.store.event(db,'','owner','accept_role_model',{'role':role,'name':name,'digest':row['digest'],'reviewer':human['reviewer']})

    def configure(self,role,names,mode='research'):
        if role not in AGENTS or mode not in ('research','production'):raise AgentError('Invalid role or routing mode.')
        if not isinstance(names,list) or not 1<=len(names)<=3 or len(set(names))!=len(names):raise AgentError('Choose 1–3 distinct approved models in order.')
        installed=inventory();available={m['name']:m for m in self.models() if m['approved']}
        pinned=[]
        with self.store.tx() as db:
            for name in names:
                local_id(name);m=available.get(name)
                if not m or installed.get(name)!=m['digest']:raise AgentError('Route requires exact installed, approved local model digests.')
                if mode=='production' and not db.execute('SELECT 1 FROM model_acceptances WHERE role=? AND name=? AND digest=?',(role,name,m['digest'])).fetchone():
                    raise AgentError('Production route requires role-specific technical evidence and independent human acceptance for EVERY fallback.')
                pinned.append({'name':name,'digest':m['digest']})
            policy={'role':role,'mode':mode,'models':pinned,'fallback':'runtime_unavailable_only','production_approval':False}
            db.execute('INSERT OR REPLACE INTO specialist_model_routes VALUES (?,?)',(role,encode(policy)))
            self.store.event(db,'','owner','configure_model_route',policy)
        return policy

    def snapshot(self,run,role):
        with self.store.tx() as db:
            row=db.execute('SELECT policy FROM model_route_snapshots WHERE run=?',(run,)).fetchone()
            if row:return json.loads(row[0])
            policy=self.policy(role)
            if policy:db.execute('INSERT INTO model_route_snapshots VALUES (?,?)',(run,encode(policy)))
        return policy


class RoutedWriter:
    def __init__(self,routes,run,role,settings=None):
        self.routes=routes;self.run=run;self.role=role;self.settings=dict(settings or {})
        self.policy=routes.snapshot(run,role)
        if not self.policy:raise AgentError('No specialist model route configured.')
        self.model=self.policy['models'][0]['name'];self.last_raw_output='';self.last_evidence={}

    def __call__(self,system,prompt):
        for candidate in self.policy['models']:
            self.model=candidate['name'];self.last_raw_output='';self.last_evidence={};writer=None;error=''
            try:
                current=next((m for m in self.routes.models() if m['name']==self.model),None)
                if not current or not current['approved'] or current['digest']!=candidate['digest']:raise WritingError('Pinned model approval was revoked or changed.')
                if self.policy['mode']=='production':
                    with self.routes.store.tx() as db:
                        if not db.execute('SELECT 1 FROM model_acceptances WHERE role=? AND name=? AND digest=?',(self.role,self.model,candidate['digest'])).fetchone():raise WritingError('Role acceptance no longer valid.')
                try:installed=inventory()
                except (OSError,TimeoutError):raise LocalUnavailable('Local runtime unavailable.') from None
                if self.model not in installed:raise LocalUnavailable('Approved model unavailable in local runtime.')
                if installed[self.model]!=candidate['digest']:raise WritingError('Installed model digest changed; no fallback allowed.')
                writer=LocalWriter(self.model,**self.settings)
                result=writer(system,prompt)
                return result
            except LocalUnavailable as exc:
                error=str(exc)
                # Only transport/unavailable-model errors may try the next pinned model.
            except Exception as exc:
                error=str(exc) if isinstance(exc,(WritingError,AgentError)) else type(exc).__name__
                raise
            finally:
                if writer:self.last_raw_output=writer.last_raw_output;self.last_evidence=dict(writer.last_evidence)
                self.last_evidence.update(route_mode=self.policy['mode'],route_policy_sha256=hashlib.sha256(encode(self.policy).encode()).hexdigest(),model_digest=candidate['digest'])
                with self.routes.store.tx() as db:
                    db.execute('INSERT INTO routed_model_attempts(run,role,model,digest,raw,evidence,error,created) VALUES (?,?,?,?,?,?,?,?)',
                        (self.run,self.role,self.model,candidate['digest'],self.last_raw_output,encode(self.last_evidence),error,time.time()))
        raise LocalUnavailable('All explicitly approved local route models unavailable; no hosted fallback called.')
