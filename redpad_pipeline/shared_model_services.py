"""Explicit development-only model services shared across all 21 agents.
No downloads, public endpoints, implicit substitutions, or production promotion.
"""
import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from .agents import AGENTS,AgentError,encode
from .offline_media import checkpoint_manifest,sha,digest
from .resource_guard import serialized
from .screenwriter import WritingError,LocalUnavailable

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'assets/professional/phase3_candidates.json'
EXECUTABLE={'hf_text_nf4','flux2_klein','z_image'}

def catalog():
    d=json.loads(CATALOG.read_text())
    if set(d['agents'])!=set(AGENTS):raise AgentError('Candidate architecture must cover exactly registered agents.')
    return d

def profile(id):
    p=catalog()['profiles'].get(id)
    if not p or not re.fullmatch('[a-f0-9]{40}',p.get('revision','')):raise AgentError('Unknown or unpinned candidate; no substitution allowed.')
    return p

def resource_preflight(p,runtime,*,download=False):
    reasons=[];gpu=p['planning_gpu_gib'];cards=runtime.get('gpus',[])
    if not any(c.get('total_bytes',0)>=gpu*2**30 and c.get('free_bytes',0)>=gpu*.9*2**30 for c in cards):reasons.append('No single GPU meets the unmeasured '+str(gpu)+' GiB planning gate/free headroom; separate GPUs are not pooled by this adapter.')
    memory=runtime.get('host_memory',{});available=memory.get('MemAvailable_bytes',0)
    cgroup=runtime.get('cgroup_available_bytes')
    if cgroup is not None:available=min(available,cgroup)
    if available<p['planning_ram_gib']*2**30:reasons.append('Available host/container RAM below conservative planning gate.')
    if download and runtime.get('disk_free_bytes',0)<p['selected_weight_bytes']*1.2+2*2**30:reasons.append('Insufficient measured disk space for source weights, configs and transfer headroom.')
    return {'eligible_for_canary_only':not reasons,'blockers':reasons,'runtime_compatible_verified':False,'memory_scope':'Planning preflight is not actual inference, minimum hardware proof or a fit guarantee.'}

class SharedServices:
    def __init__(self,store):
        self.store=store
        with store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS shared_model_installs(profile TEXT PRIMARY KEY,payload TEXT);
          CREATE TABLE IF NOT EXISTS shared_dev_routes(role TEXT PRIMARY KEY,payload TEXT);
          CREATE TABLE IF NOT EXISTS shared_backend_bindings(run TEXT PRIMARY KEY,role TEXT,backend TEXT);
          CREATE TABLE IF NOT EXISTS shared_service_snapshots(run TEXT PRIMARY KEY,payload TEXT);
        ''')
    def approve_install(self,id,folder,owner,license_note,confirmed=False):
        p=profile(id)
        if confirmed is not True or not all(isinstance(s,str) and s.strip() for s in (owner,license_note)):raise AgentError('Explicit owner authorization of this exact checkpoint, license and installation required.')
        if p['adapter'] not in EXECUTABLE:raise AgentError('This exact candidate has no new shared-service execution adapter; existing adapters retain separate approval. No substitution.')
        folder=Path(folder).absolute();index='config.json' if p['adapter']=='hf_text_nf4' else 'model_index.json'
        manifest=checkpoint_manifest(folder,index)
        for f in p['selected_weight_files']:
            found=manifest['files'].get(f['path'])
            if not found or found['bytes']!=f['bytes'] or found['sha256']!=f['sha256']:raise AgentError('Installed weights differ from exact official metadata: '+f['path'])
        auxiliary=p.get('auxiliary_files')
        if not isinstance(auxiliary,list) or not auxiliary:raise AgentError('Official tokenizer/config hashes have not been pinned for this candidate.')
        for aux in auxiliary:
            found=manifest['files'].get(aux['path']);file=folder/aux['path']
            if not found or found['bytes']!=aux['bytes']:raise AgentError('Official tokenizer/config component missing or wrong size: '+aux['path'])
            if aux.get('sha256'):
                if found['sha256']!=aux['sha256']:raise AgentError('Tokenizer/config LFS hash mismatch.')
            elif aux.get('git_blob_sha1'):
                raw=file.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                if blob!=aux['git_blob_sha1']:raise AgentError('Tokenizer/config Git blob hash mismatch.')
            else:raise AgentError('Official tokenizer/config hash unavailable; do not assume compatibility.')
        origin=folder/'redpad_model_origin.json'
        if not origin.is_file():raise AgentError('Model origin receipt with exact repository/revision required.')
        identity=json.loads(origin.read_text())
        if identity.get('repo')!=p['repo'] or identity.get('revision')!=p['revision']:raise AgentError('Origin revision mismatch.')
        record={'id':id,'repo':p['repo'],'revision':p['revision'],'folder':str(folder),'manifest':manifest,'owner':owner,'license_note':license_note,'approved_for_research':True,'production_approved':False,'inference_verified':False}
        with self.store.tx() as db:
            db.execute('INSERT OR REPLACE INTO shared_model_installs VALUES (?,?)',(id,encode(record)))
            self.store.event(db,'','owner','approve_shared_research_install',{'profile':id,'revision':p['revision'],'manifest_sha256':manifest['sha256']})
        return record
    def installed(self,id,verify=False):
        with self.store.tx() as db:r=db.execute('SELECT payload FROM shared_model_installs WHERE profile=?',(id,)).fetchone()
        if not r:raise LocalUnavailable('Exact shared model checkpoint/license is not approved and installed; no download attempted.')
        result=json.loads(r[0]);p=profile(id)
        if result['repo']!=p['repo'] or result['revision']!=p['revision']:raise LocalUnavailable('Candidate registry changed after installation approval.')
        if verify:
            index='config.json' if p['adapter']=='hf_text_nf4' else 'model_index.json'
            if checkpoint_manifest(result['folder'],index)!=result['manifest']:raise LocalUnavailable('Shared checkpoint changed after approval.')
        return result
    def configure(self,role,id,*,capability='text',fallback=None):
        if role not in AGENTS or id not in [catalog()['agents'][role]['primary_candidate']]+catalog()['agents'][role]['secondary_candidates']:raise AgentError('Candidate is not explicitly shortlisted for this agent.')
        from .model_routing import ModelRoutes
        existing=ModelRoutes(self.store).policy(role)
        if existing and existing['mode']=='production':raise AgentError('Production route is locked; use a separate development project/store for candidate research.')
        p=profile(id)
        if capability not in p['modalities']:raise AgentError('Candidate does not support this modality; no silent text/vision substitution.')
        self.installed(id,True)
        if fallback is not None:raise AgentError('Shared research runs do not silently fall back. Queue the approved secondary as a separate labeled trial; existing Ollama fallback policy is preserved.')
        policy={'role':role,'profile':id,'capability':capability,'mode':'development_research','production_approved':False,'fallback':None}
        with self.store.tx() as db:
            db.execute('INSERT OR REPLACE INTO shared_dev_routes VALUES (?,?)',(role,encode(policy)))
            self.store.event(db,'','owner','configure_shared_development_route',policy)
        return policy
    def policy(self,role):
        with self.store.tx() as db:r=db.execute('SELECT payload FROM shared_dev_routes WHERE role=?',(role,)).fetchone()
        return json.loads(r[0]) if r else None
    def stage_request(self,run,profile_id,operation,request):
        """CPU-only draft preparation; does not configure or execute a model route."""
        from .no_gpu_staging import StagingLedger
        return StagingLedger(self.store).stage(run,profile_id,operation,request)
    def staged_request(self,id):
        from .no_gpu_staging import StagingLedger
        return StagingLedger(self.store).get(id)
    def stage_tool_request(self,run,operation,request):
        from .no_gpu_staging import StagingLedger
        return StagingLedger(self.store).stage_tool(run,operation,request)
    def prepare_offline_request(self,id,*,spec=None,verify_bundle=False):
        """Map a current staged request to an existing local-worker payload, never run it."""
        from .offline_preparation import PreparedRequests
        return PreparedRequests(self.store).prepare(id,spec=spec,verify_bundle=verify_bundle)
    def prepared_offline_request(self,id):
        from .offline_preparation import PreparedRequests
        return PreparedRequests(self.store).get(id)
    def native_research_workers(self):
        """Offline development lifecycle only; no route promotion or automatic launch."""
        from .native_execution import NativeExecution
        return NativeExecution(self.store)
    def choose_backend(self,run,role):
        """Pin one backend before execution; retries cannot switch provider families."""
        if role not in AGENTS:raise AgentError('Unknown route role.')
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            bound=db.execute('SELECT role,backend FROM shared_backend_bindings WHERE run=?',(run,)).fetchone()
            if bound:
                if bound['role']!=role:raise AgentError('Backend binding role differs from this run.')
                return bound['backend']
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            legacy_snapshot=db.execute('SELECT policy FROM model_route_snapshots WHERE run=?',(run,)).fetchone() if 'model_route_snapshots' in tables else None
            legacy_policy=db.execute('SELECT policy FROM specialist_model_routes WHERE role=?',(role,)).fetchone() if 'specialist_model_routes' in tables else None
            shared_snapshot=db.execute('SELECT payload FROM shared_service_snapshots WHERE run=?',(run,)).fetchone()
            shared_policy=db.execute('SELECT payload FROM shared_dev_routes WHERE role=?',(role,)).fetchone()
            # Existing run snapshots win. Production preference wins only before
            # a run is bound, never by changing an already chosen shared trial.
            if legacy_snapshot:backend='ollama'
            elif shared_snapshot:backend='shared'
            elif legacy_policy and json.loads(legacy_policy[0])['mode']=='production':backend='ollama'
            elif shared_policy:backend='shared'
            else:backend='ollama'
            if backend=='shared' and not shared_snapshot:
                db.execute('INSERT INTO shared_service_snapshots VALUES (?,?)',(run,shared_policy[0]))
            if backend=='ollama' and legacy_policy and not legacy_snapshot:
                db.execute('INSERT INTO model_route_snapshots VALUES (?,?)',(run,legacy_policy[0]))
            db.execute('INSERT INTO shared_backend_bindings VALUES (?,?,?)',(run,role,backend))
            return backend

    def snapshot(self,run,role):
        with self.store.tx() as db:
            row=db.execute('SELECT payload FROM shared_service_snapshots WHERE run=?',(run,)).fetchone()
            if row:return json.loads(row[0])
            p=self.policy(role)
            if p:db.execute('INSERT INTO shared_service_snapshots VALUES (?,?)',(run,encode(p)))
            return p
    @serialized
    def execute(self,id,request,*,timeout=240):
        if type(timeout) is not int or not 30<=timeout<=600:raise AgentError('Bounded 30–600s worker timeout required.')
        p=profile(id);installed=self.installed(id,True)
        from .kaggle_runtime import probe
        preflight=resource_preflight(p,probe())
        if not preflight['eligible_for_canary_only']:raise LocalUnavailable('; '.join(preflight['blockers']))
        validate_request(p,request)
        from .producer_references import References
        references=References(self.store);pins=[];reference_paths=[]
        for ref in request.get('references',[]):
            row=references.get(ref['id'])
            if row['version']!=ref['version'] or row['archived'] or row['rights'] not in ('fictional_ai','authorized_person') or not row['source'].strip() or row['extension'] not in ('.png','.jpg','.jpeg','.webp'):raise AgentError('Current rights-authorized exact image reference version required.')
            reference_paths.append(str(references.path(row)));pins.append(row)
        root=self.store.path.parent/'agent_media'/'shared_model_services'
        if any(x.is_symlink() for x in (root,*root.parents)):raise AgentError('Unsafe shared worker output path.')
        root=root.resolve();folder=root/uuid4().hex;folder.mkdir(parents=True);self.last_folder=folder
        job={'profile':p,'checkpoint':installed['folder'],'request':request,'output_dir':str(folder.resolve()),'timeout_seconds':timeout,'reference_paths':reference_paths}
        (folder/'request.json').write_text(encode(job))
        evidence={'state':'running','profile':id,'model':p['repo'],'revision':p['revision'],'request_sha256':digest(request),'model_manifest_sha256':installed['manifest']['sha256'],'actual_inference_verified':False,'human_review_completed':False,'production_approved':False}
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1')
        start=time.monotonic()
        try:
            with (folder/'worker.log').open('w') as log:subprocess.run([sys.executable,'-m','redpad_pipeline.shared_model_worker',str(folder/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=timeout,check=True)
            result=json.loads((folder/'result.json').read_text())
            for pin in pins:
                if references.get(pin['id'])!=pin:raise WritingError('Image reference changed during generation; output is stale.')
                references.path(pin)
            if result.get('inference_completed') is not True:raise WritingError('No completed model inference evidence.')
            if self.installed(id,True)['manifest']!=installed['manifest']:raise WritingError('Checkpoint changed during inference.')
            evidence.update(state='inference_completed',actual_inference_verified=True,worker=result,runtime_seconds=time.monotonic()-start)
        except (subprocess.SubprocessError,OSError,ValueError,WritingError) as exc:
            evidence.update(state='failed_or_interrupted',error_type=type(exc).__name__,runtime_seconds=time.monotonic()-start)
            raise WritingError('Shared local worker failed/interrupted; raw files retained at '+str(folder)+'. No fallback or automatic retry.') from None
        finally:(folder/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        return folder,evidence

def validate_request(p,r):
    if not isinstance(r,dict):raise AgentError('Inference request must be a bounded object.')
    if p['adapter']=='hf_text_nf4':
        if set(r)!={'system','prompt','max_new_tokens','seed','temperature','context_tokens','thinking'}:raise AgentError('Explicit bounded text inference settings required.')
        if not all(isinstance(r[k],str) and len(r[k])<=50000 for k in ('system','prompt')) or not r['prompt'].strip():raise AgentError('Bounded prompt required.')
        if type(r['max_new_tokens']) is not int or not 32<=r['max_new_tokens']<=1536 or type(r['context_tokens']) is not int or not 512<=r['context_tokens']<=4096 or type(r['seed']) is not int or not 0<=r['seed']<2**31 or type(r['thinking']) is not bool or type(r['temperature']) not in (int,float) or not 0<=r['temperature']<=1:raise AgentError('Text benchmark controls exceed safe research bounds.')
    elif p['adapter'] in ('flux2_klein','z_image'):
        if set(r)!={'prompt','width','height','steps','seed','references'} or not isinstance(r['prompt'],str) or not 1<=len(r['prompt'])<=2000:raise AgentError('Bounded image controls required.')
        if any(type(r[k]) is not int or r[k] not in (512,768,1024) for k in ('width','height')) or type(r['seed']) is not int or not 0<=r['seed']<2**31:raise AgentError('Invalid image dimensions/seed.')
        if type(r['steps']) is not int or r['steps']!=(4 if p['adapter']=='flux2_klein' else 9) or not isinstance(r['references'],list) or len(r['references'])>3:raise AgentError('Fixed native small image step budget and at most 3 references required.')
        if any(not isinstance(x,dict) or set(x)!={'id','version'} or not isinstance(x['id'],str) or type(x['version']) is not int for x in r['references']):raise AgentError('Exact image reference IDs/versions required.')
        if p['adapter']=='z_image' and r['references']:raise AgentError('This Z-Image text-to-image adapter does not implement reference editing.')
    else:raise AgentError('Exact candidate execution adapter is blocked; no legacy substitution.')

class SharedWriter:
    def __init__(self,services,run,role,settings):
        self.services=services;self.policy=services.snapshot(run,role)
        if not self.policy or self.policy['capability']!='text':raise LocalUnavailable('Selected shared route cannot execute text; no substitution.')
        self.id=self.policy['profile'];p=profile(self.id)
        if p['adapter']!='hf_text_nf4':raise LocalUnavailable('Exact text adapter not implemented.')
        self.model=p['repo']+'@'+p['revision']+':nf4';self.settings=settings;self.last_raw_output='';self.last_evidence={}
    def __call__(self,system,prompt):
        options=self.settings
        if options.get('num_predict',1024)>1536 or options.get('num_ctx',4096)>4096:raise LocalUnavailable('Shared research worker requires explicit bounded <=1536 output / <=4096 context settings; use existing staged generation, no silent budget reduction.')
        request=dict(system=system,prompt=prompt,max_new_tokens=min(options.get('num_predict',1024),1536),seed=options.get('seed',117),temperature=options.get('temperature',.7),context_tokens=min(options.get('num_ctx',4096),4096),thinking=False)
        try:folder,evidence=self.services.execute(self.id,request,timeout=min(options.get('timeout_seconds',240),600))
        except WritingError:
            # Worker folders retain raw partial/failure evidence; Engine preserves structured failure.
            raise
        self.last_raw_output=(folder/'raw_response.txt').read_text();self.last_evidence={**evidence,'raw_sha256':sha(folder/'raw_response.txt')}
        if evidence['worker'].get('truncated'):raise WritingError('Model output reached its generation limit; raw response preserved, not repaired.')
        try:return json.loads(self.last_raw_output)
        except ValueError:raise WritingError('Raw model response is not JSON; original output preserved without manual repair.') from None
