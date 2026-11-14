"""Authenticated future local installs. No downloader, inference import or probe.

These routines are NOT called on actual model files during no-GPU engineering.
Approval is explicit and separate from the immutable candidate registry.
"""
import hashlib,json,re
from pathlib import Path
from .agents import AgentError,encode
from .no_gpu_staging import fingerprint,load,resolve_profile
from .offline_specialist_preparation import PINS,LTX_SLOTS,LTX_AUXILIARY,relative

SUPPORTED={'ltx25','wan_animate2','ace15','indic_parler','wan22_5','svd_xt','stable_audio_small','indic_speak','indicf5'}
REQUIRED={
 'ltx25':list(LTX_SLOTS.values())+[LTX_AUXILIARY['path']],
 'wan_animate2':['wan_animate_2/wan_animate_2_bf16.safetensors','videomodel/Wan-AI/models_t5_umt5-xxl-enc-bf16.pth','videomodel/Wan-AI/vae.pth','videomodel/Wan-AI/models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth'],
 'ace15':['acestep-v15-turbo/model.safetensors','acestep-v15-turbo/config.json','acestep-v15-turbo/silence_latent.pt','Qwen3-Embedding-0.6B/model.safetensors','Qwen3-Embedding-0.6B/config.json','Qwen3-Embedding-0.6B/tokenizer.json','vae/config.json','vae/diffusion_pytorch_model.safetensors'],
 'indic_parler':['config.json','tokenizer_config.json','description_tokenizer/tokenizer_config.json'],
 'wan22_5':['model_index.json'],'svd_xt':['model_index.json'],'stable_audio_small':['model_config.json'],
 'indic_speak':['config.json','generation_config.json','tokenizer.json','tokenizer_config.json','model.safetensors','vocos/best.pt','snac/config.json','snac/pytorch_model.bin'],
 'indicf5':['config.json','checkpoints/vocab.txt','model.safetensors']}
SOURCE_FILES={
 'ltx25':['packages/ltx-pipelines/src/ltx_pipelines/distilled.py','packages/ltx-pipelines/src/ltx_pipelines/utils/model_paths.py','packages/ltx-core/src/ltx_core/text_encoders/gemma/gemma_assets.py'],
 'wan_animate2':['infer/wan_animate_2.yaml','pipelines/wan_animate_2_pipeline.py','wanxiang/eval_i2v.py'],
 'ace15':['acestep/handler.py','acestep/inference.py','acestep/models/turbo/modeling_acestep_v15_turbo.py','acestep/models/turbo/configuration_acestep_v15.py','acestep/models/common/configuration_acestep_v15.py']}


def local_path(root,name,*,exists=True):
    root=Path(root)
    if not root.is_absolute():raise AgentError('Absolute local installation root required.')
    p=root/relative(name)
    if any(x.is_symlink() for x in (p,*p.parents)):raise AgentError('Symlink installation/input/output prohibited.')
    if exists and not p.is_file():raise AgentError('Missing local component: '+name)
    return p


def digest_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def verify_tree(root,files):
    if not isinstance(files,dict) or not files:raise AgentError('Complete approved file manifest required.')
    for name,row in files.items():
        if set(row)!={'bytes','sha256'} or type(row['bytes']) is not int or row['bytes']<1 or not re.fullmatch('[0-9a-f]{64}',row['sha256']):raise AgentError('Exact component size/SHA256 required; unknown metadata cannot authorize loading.')
        p=local_path(root,name)
        if p.stat().st_size!=row['bytes'] or digest_file(p)!=row['sha256']:raise AgentError('Approved component changed: '+name)
    # Complete file coverage prevents unmanifested Python/config/weight injection.
    for p in Path(root).rglob('*'):
        if '.git' in p.relative_to(root).parts:continue
        if '__pycache__' in p.relative_to(root).parts or p.suffix=='.pyc':raise AgentError('Precompiled unreviewed Python bytecode prohibited in native bundle.')
        if p.is_symlink():raise AgentError('Symlink component prohibited.')
        if p.is_file() and p.relative_to(root).as_posix() not in files:raise AgentError('Unmanifested file in local bundle: '+p.name)


def validate_install(record,*,verify=True):
    required={'profile','repo','revision','profile_sha256','model_root','model_files','source_root','source_files','source_revision','owner','license_note','component_origins','code_reviewed','approved_for_research'}
    if not isinstance(record,dict) or set(record)!=required:raise AgentError('Exact offline installation receipt required.')
    pid=record['profile']
    if pid not in SUPPORTED:raise AgentError('Native interface unavailable; no fallback or gated custom code.')
    reg,_=load();p=resolve_profile(pid,reg)
    if (record['repo'],record['revision'],record['profile_sha256'])!=(p['repo'],p['revision'],fingerprint(p)):raise AgentError('Candidate/revision/precision changed; no model substitution.')
    if record['approved_for_research'] is not True or record['code_reviewed'] is not True or any(not isinstance(record[k],str) or not record[k].strip() for k in ('owner','license_note')):raise AgentError('Existing explicit owner license/component/code review required.')
    for f in p['selected_weight_files']:
        if record['model_files'].get(f['path'])!={k:f[k] for k in ('bytes','sha256')}:raise AgentError('Pinned selected weights differ.')
    if any(n not in record['model_files'] for n in REQUIRED[pid]):raise AgentError('Incomplete native component recipe.')
    if pid=='wan_animate2':
        for folder in ('videomodel/Wan-AI/umt5-xxl/','videomodel/Wan-AI/xlm-roberta-large/'):
            if not any(n.startswith(folder) and 'tokenizer' in n for n in record['model_files']):raise AgentError('Complete local native tokenizers required.')
    if pid in ('indic_speak','indicf5'):
        from .voice_native_contracts import validate_source_receipt
        validate_source_receipt(record)
    elif pid in PINS:
        if record['source_revision']!=PINS[pid] or any(n not in record['source_files'] for n in SOURCE_FILES[pid]):raise AgentError('Exact reviewed native code checkout required.')
        expected=json.loads((Path(__file__).resolve().parents[1]/'assets/professional/phase3_native_source_lock.json').read_text())
        for n,sha in expected['files'][pid].items():
            if record['source_files'].get(n,{}).get('sha256')!=sha:raise AgentError('Reviewed native source changed.')
    elif record['source_revision'] is not None:raise AgentError('Existing Studio worker uses its own source hash, not a fabricated upstream pin.')
    # Auxiliary origins are separately approved, never inferred from a filename.
    for n in REQUIRED[pid]:
        origin=record['component_origins'].get(n)
        if not isinstance(origin,dict) or not origin.get('repo') or not re.fullmatch('[a-f0-9]{40}',origin.get('revision','')):raise AgentError('Exact auxiliary origin/revision owner review required.')
        if pid in ('indic_speak','indicf5'):
            expected_repo='hubertsiuzdak/snac_24khz' if n.startswith('snac/') else p['repo']
            if origin['repo']!=expected_repo or (expected_repo==p['repo'] and origin['revision']!=p['revision']):raise AgentError('Wrong selected voice component origin; no substitution.')
        if pid=='ltx25' and (origin['repo'],origin['revision'])!=(p['repo'],p['revision']):raise AgentError('LTX components must stay in exact pinned split repository.')
    if pid=='ltx25' and LTX_AUXILIARY['sha256'] is None:raise AgentError('Official spatial upsampler SHA/size unverified; exact weight verification gate remains blocked.')
    if verify:
        verify_tree(record['model_root'],record['model_files'])
        if pid in PINS or pid in ('indic_speak','indicf5'):verify_tree(record['source_root'],record['source_files'])
    return record


class NativeInstalls:
    def __init__(self,store):
        self.store=store
        with store.tx() as db:db.execute('CREATE TABLE IF NOT EXISTS native_local_installs(id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT)')
    def approve(self,record,*,confirmed=False):
        # Future owner action only. No actual approval is created in this assignment.
        if confirmed is not True:raise AgentError('Explicit owner confirmation required.')
        validate_install(record);raw=encode(record);id=fingerprint(record)
        with self.store.tx() as db:
            db.execute('INSERT OR IGNORE INTO native_local_installs VALUES (?,?,?)',(id,raw,hashlib.sha256(raw.encode()).hexdigest()))
            self.store.event(db,'','owner','approve_native_research_install',{'id':id,'profile':record['profile'],'production_approved':False})
        return id
    def get(self,id,*,verify=True):
        with self.store.tx() as db:row=db.execute('SELECT payload,sha256 FROM native_local_installs WHERE id=?',(id,)).fetchone()
        if not row or hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Approved native install unavailable or altered; no download.')
        record=json.loads(row['payload'])
        if fingerprint(record)!=id:raise AgentError('Native approval identity mismatch.')
        return validate_install(record,verify=verify)
