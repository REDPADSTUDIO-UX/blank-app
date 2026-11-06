"""Bounded real-model experiments over the existing engine. No downloads or cloud jobs.

Preflight/blocked tasks are separate from completed inference. An isolated lab has
its own existing AgentStore; no production DB, approvals or media are imported.
"""
import copy,hashlib,importlib.util,importlib.metadata,json,os,platform,re,shutil,time
from pathlib import Path
from .agents import AgentError,AgentStore,encode
from .agent_engine import Engine
from .creative import evaluate
from .readiness import inspect_resources

ROOT=Path(__file__).resolve().parents[1]
LAB_ROOT=ROOT/'phase3_runs'


def audit(probe=True):
    result=inspect_resources(probe)
    result.update(cpu_arch=platform.machine(),logical_cpus=os.cpu_count(),
        ram_bytes=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'),
        disk_free_bytes=shutil.disk_usage(ROOT).free,
        runtimes={name:bool(shutil.which(name)) for name in ('ollama','llama-cli','nvidia-smi','ffmpeg','ffprobe')},
        modules={name:importlib.util.find_spec(name) is not None for name in ('torch','transformers','diffusers','llama_cpp','streamlit','huggingface_hub')},
        device='GPU not verified' if result['cuda_device'] else 'CPU only',
        model_weights_present=False,remote_inference=False,paid_fallback=False)
    # Inventory reviewed local model/cache locations only. No file contents or secrets.
    roots=[ROOT/'phase3_models',Path.home()/'.cache/huggingface/hub',Path.home()/'.ollama/models']
    weights=[]
    for folder in roots:
        if folder.is_dir() and not folder.is_symlink():
            for pattern in ('*.gguf','*.safetensors'):
                weights += [p.name for p in folder.rglob(pattern) if p.is_file() and not p.is_symlink()][:100]
    result['weight_filenames']=weights[:100];result['model_weights_present']=bool(weights) or bool(result['local_models'])
    binary=ROOT/'phase3_models/ollama-runtime/bin/ollama'
    result['development_ollama_installed']=binary.is_file() and not binary.is_symlink()
    result['local_model_manifests']=[]
    model_root=ROOT/'phase3_models/ollama-weights'
    manifests=model_root/'manifests'
    if manifests.is_dir() and not manifests.is_symlink():
        for path in manifests.rglob('*'):
            if not path.is_file() or path.is_symlink():continue
            try:
                manifest=json.loads(path.read_text())
                layers=[manifest['config'],*manifest['layers']]
                present=all((model_root/'blobs'/layer['digest'].replace(':','-')).is_file() and (model_root/'blobs'/layer['digest'].replace(':','-')).stat().st_size==layer['size'] for layer in layers)
                result['local_model_manifests'].append(dict(name=str(path.relative_to(manifests)),manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_blobs_present=present))
                result['model_weights_present']=result['model_weights_present'] or present
            except (ValueError,KeyError,TypeError,OSError):continue

    result['python_version']=platform.python_version()
    result['package_versions']={}
    for name in ('torch','transformers','diffusers','streamlit','huggingface_hub'):
        try:result['package_versions'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:result['package_versions'][name]=None
    try:
        import psutil
        result['available_ram_bytes']=psutil.virtual_memory().available
    except ImportError:result['available_ram_bytes']=None
    from .local_animation import readiness
    result['svd_preflight']=dict(zip(('ready','reason'),readiness()))
    result['gpu_vram_bytes']=None
    result['limits']='CPU/RAM/disk availability only; CUDA device nodes are not a driver/VRAM validation. Model serving memory and Bangla quality unmeasured.'
    return result


def cases():return json.loads((ROOT/'assets/phase3/benchmark_cases.json').read_text())


def shape(value):
    """Expose schema and enum examples, not previous manually authored stories."""
    if isinstance(value,dict):
        result={}
        for key,item in value.items():
            if key in ('type','ending_type','humor_type','hook_type') and isinstance(item,str):result[key]=item
            else:result[key]=shape(item)
        return result
    if isinstance(value,list):return [shape(x) for x in value]
    if isinstance(value,str):return '<original generated text; preserve approved IDs when referenced>'
    return value


class Lab:
    def __init__(self,lab_id):
        if not isinstance(lab_id,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',lab_id):raise AgentError('Use a safe experiment identifier.')
        root=LAB_ROOT/lab_id
        if any(p.is_symlink() for p in (root,LAB_ROOT)):raise AgentError('Experiment symlinks prohibited.')
        self.root=root;self.store=AgentStore(root/'agent_control.sqlite3');self.engine=Engine(self.store)
        with self.store.tx() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS phase3_cases
            (run TEXT PRIMARY KEY,case_id TEXT,model TEXT,request_sha TEXT,created REAL);
            CREATE TABLE IF NOT EXISTS phase3_reviews
            (task TEXT,revision INTEGER,payload TEXT,created REAL);''')
    def request(self,case_id,source_task=None):
        spec=next((x for x in cases() if x['id']==case_id),None)
        if not spec:raise AgentError('Unknown benchmark case.')
        seed=json.loads((ROOT/'assets/writing/creative/scenarios.json').read_text())
        template=seed[spec['shape_fixture']]
        if spec['kind']=='rewrite':template=[x for x in template['scenes'] if x['id'] in spec['targets']]
        request=dict(creative_v1=True,kind=spec['kind'],brief=copy.deepcopy(spec['brief']),artifact=shape(template))
        if source_task:
            request['source']={'$from':source_task,'path':['artifact']}
            with self.store.tx() as db:
                previous=db.execute('SELECT inputs FROM agent_runs WHERE task=? ORDER BY expected_revision DESC LIMIT 1',(source_task,)).fetchone()
            if previous:
                source_brief=json.loads(previous[0]).get('brief')
                if isinstance(source_brief,dict):request['brief']=copy.deepcopy(source_brief)
        if spec['kind']=='rewrite':request['targets']=spec['targets']
        return spec,request
    def queue(self,case_id,model,dependencies=None,source_task=None):
        dependencies=[] if dependencies is None else list(dependencies)
        if source_task and source_task not in dependencies:dependencies.append(source_task)
        spec,request=self.request(case_id,source_task)
        if spec['requires_source'] and not source_task:raise AgentError('Current owner-approved upstream source required; no fixture substituted.')
        # Validate model identifier through the existing local-only configuration boundary.
        self.store.configure(spec['agent'],model)
        if not model:raise AgentError('Choose an installed local model; no download is performed.')
        token=hashlib.sha256(encode([case_id,model,request,dependencies]).encode()).hexdigest()
        with self.store.tx() as db:
            count=db.execute('SELECT COUNT(*) FROM phase3_cases').fetchone()[0]
            existing=db.execute('SELECT run FROM phase3_cases WHERE request_sha=?',(token,)).fetchone()
            if existing:
                canonical=db.execute('SELECT run FROM agent_run_keys WHERE token=?',('phase3:'+token,)).fetchone()
                rid=canonical[0] if canonical else existing[0]
                if rid!=existing[0]:db.execute('UPDATE phase3_cases SET run=? WHERE run=?',(rid,existing[0]))
                return rid
            if count>=6:raise AgentError('Lab budget exhausted: at most six queued experiments. Create a separately reviewed lab for more.')
        rid=self.engine.enqueue(spec['agent'],request,dependencies,mode='local',idempotency_key='phase3:'+token)
        with self.store.tx() as db:
            db.execute('UPDATE agent_runs SET model=? WHERE id=?',(model,rid))
            db.execute('INSERT OR IGNORE INTO phase3_cases VALUES (?,?,?,?,?)',(rid,case_id,model,token,time.time()))
        return rid
    def run(self,rid):
        # This entry point deliberately has no injected/provider argument.
        with self.store.tx() as db:
            case=db.execute('SELECT 1 FROM phase3_cases WHERE run=?',(rid,)).fetchone()
            if not case:raise AgentError('Not a registered experiment.')
            attempts=db.execute('SELECT attempt FROM agent_runs WHERE id=?',(rid,)).fetchone()[0]
            if attempts>=2:raise AgentError('Two-attempt experiment budget reached. Inspect evidence before further work.')
        return self.engine.execute(rid)
    def recover(self,rid):
        with self.store.tx() as db:
            if not db.execute('SELECT 1 FROM phase3_cases WHERE run=?',(rid,)).fetchone():raise AgentError('Unknown experiment.')
        new_id=self.engine.recover(rid)
        with self.store.tx() as db:db.execute('UPDATE phase3_cases SET run=? WHERE run=?',(new_id,rid))
        return new_id
    def review(self,task,revision,ratings,reviewer,confirmed=False):
        if not confirmed:raise AgentError('Human reviewer confirmation required.')
        with self.store.tx() as db:
            t=self.store._task(db,task);self.store._current(db,t)
            if t['revision']!=revision:raise AgentError('Stale review version.')
            row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,revision)).fetchone()
            if not row:raise AgentError('No generated artifact to review.')
            envelope=json.loads(row[0]);body=json.loads(envelope['summary'])
            if envelope['provenance']!='local_inference':raise AgentError('This Phase 3 rubric requires an actual local-inference artifact.')
            report=evaluate(body['artifact'],ratings,reviewer,'human')
            report['independence']='Reviewer-declared human review; identity/independence not independently verified by software'
            db.execute('INSERT INTO phase3_reviews VALUES (?,?,?,?)',(task,revision,encode(report),time.time()))
            return report
    def summary(self):
        runs=self.engine.runs();raw=[];reviews=[]
        with self.store.tx() as db:
            for row in db.execute('SELECT * FROM local_inference_evidence ORDER BY created'):
                record=dict(row);record['evidence']=json.loads(record['evidence']);raw.append(record)
            reviews=[json.loads(r[0]) for r in db.execute('SELECT payload FROM phase3_reviews')]
        completed=[r for r in raw if r['evidence'].get('inference_completed')]
        verified_runs={r['run'] for r in completed}
        actual={o['task'] for o in self.store.outputs() if json.loads(o['payload']).get('provenance')=='local_inference'}
        validated=[r for r in runs if r['id'] in verified_runs and r['task'] in actual and r['state']=='Awaiting QC' and r['mode']=='local']
        return dict(phase=3,runs=runs,runtime_records=raw,real_inference_completed=len(completed),
                    structurally_validated_outputs=len(validated),blocked_preflight_or_dependency=sum(r['state']=='Blocked' for r in runs),
                    failed_software_or_contract=sum(r['state']=='Failed' for r in runs),
                    review_count=len(reviews),independent_editorial_review_verified=False,creative_media_quality_verified=False,
                    playable_cinematic_export=None,production_ready=False,owner_approved=False,
                    note='Completed runtime replies can still fail JSON/creative contracts. No score or test grants owner approval.')
    def blind_review_package(self,task,revision):
        with self.store.tx() as db:
            t=self.store._task(db,task);self.store._current(db,t)
            if t['revision']!=revision:raise AgentError('Stale artifact.')
            row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,revision)).fetchone()
            if not row:raise AgentError('Artifact missing.')
        envelope=json.loads(row[0])
        if envelope.get('provenance')!='local_inference':raise AgentError('Blind benchmark export requires actual local-inference provenance.')
        body=json.loads(envelope['summary'])
        # Model identifiers/settings are omitted from the reviewer package.
        return dict(artifact=body['artifact'],artifact_sha256=hashlib.sha256(encode(body['artifact']).encode()).hexdigest(),
                    rubric='Use existing eight-dimension creative rubric; quotes and named human review required.')
