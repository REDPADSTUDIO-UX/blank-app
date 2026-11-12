"""Provider-neutral experiment identity and append-only access/output evidence.
Reuse existing Kaggle job IDs; this ledger never provisions compute or downloads.
"""
import json,time,math,re,hashlib
from pathlib import Path
from uuid import uuid4
from .agents import AgentError,encode
from .offline_media import digest,sha
from .kaggle_benchmark import KaggleLab

PROVIDERS=('lightning','hugging_face','colab','runpod')
STATES=('Pending','Running','Completed and Verified','Failed With Evidence','Resource Blocked','Authorization Blocked','Human Review Pending')
TERMINAL=('Completed and Verified','Human Review Pending')

class CloudExperiments:
    def __init__(self,store):
        self.store=store
        with store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS cloud_experiments(id TEXT PRIMARY KEY,spec TEXT,state TEXT,output TEXT);
          CREATE TABLE IF NOT EXISTS cloud_attempts(id TEXT PRIMARY KEY,experiment TEXT,provider TEXT,status TEXT,evidence TEXT,created REAL);
        ''')
    def register(self,spec,*,existing_kaggle_job=None):
        if not isinstance(spec,dict) or set(spec)!={'case','model','settings','source_sha256'}:raise AgentError('Stable case/model/settings/source identity required.')
        if not isinstance(spec['source_sha256'],str) or not re.fullmatch(r'[0-9a-f]{64}',spec['source_sha256']):raise AgentError('Exact source SHA256 required.')
        encoded=encode(spec);id=digest(spec)
        if existing_kaggle_job:
            KaggleLab(self.store)
            with self.store.tx() as db:r=db.execute('SELECT payload,state,output FROM kaggle_trial_jobs WHERE id=?',(existing_kaggle_job,)).fetchone()
            if not r:raise AgentError('Unknown existing canonical benchmark job.')
            p=json.loads(r['payload'])
            if spec['case']!=p['case'] or spec['model']!={'profile':p['profile'],'repo':p['repo'],'revision':p['revision']} or spec['settings']!=p['settings'] or spec['source_sha256']!=p['suite_sha256']:raise AgentError('Existing benchmark identity differs; no relabeling or rerun.')
            id=existing_kaggle_job
            output=r['output']
            if r['state']=='Completed':
                o=json.loads(output or '{}');e=o.get('evidence',{})
                if o.get('provenance')!='local_inference' or e.get('actual_inference_verified') is not True or e.get('worker',{}).get('inference_completed') is not True or not isinstance(o.get('raw'),str) or hashlib.sha256(o['raw'].encode()).hexdigest()!=o.get('raw_sha256'):raise AgentError('Completed import requires intact actual inference evidence.')
            state='Human Review Pending' if r['state']=='Completed' else 'Running' if r['state']=='Running' else 'Failed With Evidence' if r['state'].startswith('Failed') else 'Pending'
        else:state='Pending';output=None
        with self.store.tx() as db:
            old=db.execute('SELECT spec FROM cloud_experiments WHERE id=?',(id,)).fetchone()
            if old and old[0]!=encoded:raise AgentError('Stable experiment ID reused with different inputs.')
            db.execute('INSERT OR IGNORE INTO cloud_experiments VALUES (?,?,?,?)',(id,encoded,state,output))
        return id
    def get(self,id):
        with self.store.tx() as db:r=db.execute('SELECT * FROM cloud_experiments WHERE id=?',(id,)).fetchone()
        if not r:raise AgentError('Unknown experiment.')
        return dict(r)
    def blocked(self,id,provider,reason,*,authorization=False,evidence=None):
        if provider not in PROVIDERS or not isinstance(reason,str) or not reason.strip():raise AgentError('Provider and exact observed blocker required.')
        state='Authorization Blocked' if authorization else 'Resource Blocked';payload={'reason':reason,'observations':evidence or {}}
        with self.store.tx() as db:
            row=db.execute('SELECT state FROM cloud_experiments WHERE id=?',(id,)).fetchone()
            if not row:raise AgentError('Unknown experiment.')
            db.execute('INSERT INTO cloud_attempts VALUES (?,?,?,?,?,?)',(uuid4().hex,id,provider,state,encode(payload),time.time()))
            if row[0] not in TERMINAL and row[0]!='Running':db.execute('UPDATE cloud_experiments SET state=? WHERE id=?',(state,id))
        return state
    def begin(self,id,provider,permission):
        if provider not in PROVIDERS or not isinstance(permission,dict):raise AgentError('Authorized provider context required.')
        current=self.get(id)
        if current['state'] in TERMINAL:return {'skip_completed':True,'experiment':id}
        # No SDK calls here. The caller must inspect actual account/hardware,
        # exact model install/license and approved persistent destination first.
        if not all(permission.get(k) is True for k in ('account_authorized','model_install_approved','persistence_approved','actual_runtime_observed','payload_egress_approved')):raise AgentError('Account/model/persistence/runtime/payload approvals are incomplete.')
        if provider=='runpod':
            if permission.get('paid_owner_approved') is not True or not permission.get('approval_reference') or type(permission.get('max_usd')) not in (int,float) or not math.isfinite(permission['max_usd']) or not 0<permission['max_usd']<=1000:raise AgentError('Explicit scoped paid approval and maximum expenditure required. No paid GPU started.')
        elif permission.get('free_only_verified') is not True:raise AgentError('Actual free allocation/credits must be verified; no billing fallback.')
        if type(permission.get('timeout_seconds')) is not int or not 1<=permission['timeout_seconds']<=600 or type(permission.get('remaining_seconds')) not in (int,float) or not math.isfinite(permission['remaining_seconds']) or permission['remaining_seconds']<permission['timeout_seconds']+120:raise AgentError('Insufficient observed quota/session budget and preservation margin.')
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT state FROM cloud_experiments WHERE id=?',(id,)).fetchone()
            if not r:raise AgentError('Unknown experiment.')
            if r[0] in TERMINAL:return {'skip_completed':True,'experiment':id}
            if r[0] in ('Running','Failed With Evidence'):raise AgentError('Do not duplicate an in-flight or failed/uncertain call; investigate preserved evidence first.')
            history=db.execute('SELECT evidence FROM cloud_attempts WHERE experiment=?',(id,)).fetchall()
            if any(json.loads(h[0]).get('observations',{}).get('completion_unknown') is True for h in history):raise AgentError('Prior submission completion unknown; reconcile evidence before any new provider request.')
            attempt=uuid4().hex;db.execute('INSERT INTO cloud_attempts VALUES (?,?,?,?,?,?)',(attempt,id,provider,'Running',encode(permission),time.time()))
            db.execute("UPDATE cloud_experiments SET state='Running' WHERE id=?",(id,))
        return {'skip_completed':False,'attempt':attempt,'experiment':id}
    def retain_hosted_sample(self,id,provider,asset,observations):
        if provider!='hugging_face' or not isinstance(observations,dict) or observations.get('actual_output_received') is not True:raise AgentError('Actual hosted output evidence required; no simulated sample.')
        asset=Path(asset)
        if any(p.is_symlink() for p in (asset,*asset.parents)) or not asset.is_file() or asset.stat().st_size>16*1024*1024:raise AgentError('Bounded real output file required.')
        expected=observations.get('output_sha256') or observations.get('raw_sha256')
        if not expected or sha(asset)!=expected:raise AgentError('Output bytes do not match captured inference receipt.')
        output={'provider':provider,'asset':str(asset),'sha256':expected,'observations':observations,'evidence_class':'hosted_sample_checkpoint_or_settings_unverified','reproducible_benchmark_verified':False,'selection_eligible':False,'human_review_completed':False}
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT state,output FROM cloud_experiments WHERE id=?',(id,)).fetchone()
            if not r:raise AgentError('Unknown experiment.')
            if r[0] in TERMINAL:
                old=json.loads(r[1])
                if old.get('sha256')!=expected:raise AgentError('Completed output is immutable; create an explicit new variation.')
                return old
            db.execute("UPDATE cloud_experiments SET state='Human Review Pending',output=? WHERE id=?",(encode(output),id))
            db.execute('INSERT INTO cloud_attempts VALUES (?,?,?,?,?,?)',(uuid4().hex,id,provider,'Human Review Pending',encode(output),time.time()))
        return output
    def fail(self,attempt,evidence):
        if not isinstance(evidence,dict) or not evidence:raise AgentError('Actual failure evidence required.')
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT experiment,status FROM cloud_attempts WHERE id=?',(attempt,)).fetchone()
            if not r or r['status']!='Running':raise AgentError('Only a current owned attempt may fail.')
            db.execute("UPDATE cloud_attempts SET status='Failed With Evidence',evidence=? WHERE id=?",(encode(evidence),attempt))
            db.execute("UPDATE cloud_experiments SET state='Failed With Evidence' WHERE id=?",(r['experiment'],))
    def export(self):
        with self.store.tx() as db:
            return {'experiments':[dict(r) for r in db.execute('SELECT * FROM cloud_experiments ORDER BY rowid')],'attempts':[dict(r) for r in db.execute('SELECT * FROM cloud_attempts ORDER BY created')],'provisions_compute':False,'automatic_billing':False,'automatic_retries':False}
