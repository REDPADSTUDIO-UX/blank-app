"""Digest-pinned offline media jobs. No downloads, remote inference or provisioning.

A successful software/mocked test is not model inference. Actual execution uses
an owned subprocess, bounded lifetime and immutable source/model manifests.
"""
from .resource_guard import serialized

import hashlib,importlib.util,json,os,re,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError
from .agent_media_bridge import MediaBlocked

ROOT=Path(__file__).resolve().parents[1]
MODEL_ROOT=ROOT/'phase3_models/offline'
CATALOG=json.loads((ROOT/'assets/offline/engines.json').read_text())


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def checkpoint_manifest(folder,index="model_index.json"):
    folder=Path(folder)
    if not folder.is_dir() or any(p.is_symlink() for p in (folder,*folder.parents)):raise AgentError('Checkpoint must be a real local directory.')
    files={}
    for p in sorted(folder.rglob('*')):
        if p.is_symlink():raise AgentError('Checkpoint symlinks are not accepted; materialize approved files.')
        if not p.is_file():continue
        if p.suffix in ('.py','.bin','.pkl','.pickle','.sh','.so'):raise AgentError('Executable/pickle checkpoint components are prohibited.')
        files[str(p.relative_to(folder))]={'bytes':p.stat().st_size,'sha256':sha(p)}
    if index not in files or not any(k.endswith('.safetensors') for k in files):raise AgentError('Complete Diffusers model_index and safetensors weights required.')
    return {'files':files,'sha256':digest(files)}


def approve_checkpoint(engine,owner,license_note,confirmed=False):
    if engine not in CATALOG or confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Explicit owner approval and reviewed variant-specific terms required.')
    folder=MODEL_ROOT/engine;manifest=checkpoint_manifest(folder)
    record={'engine':engine,'model':CATALOG[engine]['model'],'owner':owner,'license_note':license_note,'manifest':manifest,'approved':True}
    MODEL_ROOT.mkdir(parents=True,exist_ok=True)
    (MODEL_ROOT/(engine+'.approval.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
    return record


def approved(engine,verify=False):
    if engine not in CATALOG:raise AgentError('Unknown offline engine.')
    p=MODEL_ROOT/(engine+'.approval.json')
    if not p.is_file() or p.is_symlink():raise MediaBlocked('Approved local checkpoint/license record unavailable; no download attempted.')
    r=json.loads(p.read_text())
    if r.get('approved') is not True or r.get('model')!=CATALOG[engine]['model']:raise MediaBlocked('Checkpoint approval invalid.')
    if verify and checkpoint_manifest(MODEL_ROOT/engine)!=r['manifest']:raise MediaBlocked('Checkpoint files changed since owner approval.')
    return r


def preflight(engine,verify=False):
    if engine not in CATALOG:raise AgentError('Unknown offline engine.')
    folder=MODEL_ROOT/engine
    status={'engine':engine,'model':CATALOG[engine]['model'],'adapter_implemented':True,'installation_configuration_ready':True,
       'installed':folder.is_dir() and (folder/'model_index.json').is_file(),'runtime_available':False,
       'actual_inference_verified':False,'technical_output_validated':False,'cinematic_quality_reviewed':False,'owner_approved_output':False,'ready':False,'blockers':[]}
    try:approved(engine,verify)
    except (AgentError,ValueError,OSError) as exc:status['blockers'].append(str(exc))
    for module in ('torch','diffusers','transformers','accelerate','imageio_ffmpeg'):
        if importlib.util.find_spec(module) is None:status['blockers'].append('Missing local dependency: '+module)
    if importlib.util.find_spec('torch') is not None:
        import torch
        if not torch.cuda.is_available():status['blockers'].append('Compatible CUDA GPU unavailable.')
        else:
            if engine!='local-svd' and not torch.cuda.is_bf16_supported():status['blockers'].append('GPU bfloat16 unsupported for this configuration.')
            vram=torch.cuda.get_device_properties(0).total_memory/2**30;status['vram_gib']=vram
            if vram<CATALOG[engine]['budget_vram_gib']:status['blockers'].append('GPU below reviewed conservative budget; no automatic retry/offload substitution.')
    else:status['blockers'].append('CUDA runtime cannot be verified.')
    status['ready']=not status['blockers'];status['runtime_available']=status['ready']
    return status


def validate_request(engine,request):
    if engine not in CATALOG or not isinstance(request,dict):raise AgentError('Invalid offline media request.')
    allowed={'mode','prompt','negative_prompt','width','height','frames','fps','steps','seed','reference','editorial_guidance'}
    if set(request)-allowed:raise AgentError('Unsupported model controls; identity, lip-sync and camera conditioning are not implemented.')
    spec=CATALOG[engine]
    if request.get('mode') not in spec['modes']:raise AgentError('Mode is not supported by this exact engine.')
    for field,low,high in [('width',256,1280),('height',256,720),('frames',9,81),('fps',spec['fps'],spec['fps']),('steps',spec['steps'],spec['steps']),('seed',0,2147483647)]:
        if type(request.get(field)) is not int or not low<=request[field]<=high:raise AgentError('Invalid bounded '+field)
    if engine=='local-svd':
        if (request['width'],request['height'],request['frames'])!=(1024,576,25):raise AgentError('SVD-XT native contract is 1024×576, 25 frames at 7 fps.')
    elif request['width']%32 or request['height']%32 or (request['frames']-1)%spec['frames_mod']:raise AgentError('Unsupported spatial/frame grid for this model.')
    if not isinstance(request.get('prompt',''),str) or len(request.get('prompt',''))>1600:raise AgentError('Prompt exceeds bound.')
    if engine!='local-svd' and not request.get('prompt','').strip():raise AgentError('Text-conditioned engine requires a prompt.')
    if not isinstance(request.get('negative_prompt',''),str) or len(request.get('negative_prompt',''))>1000:raise AgentError('Invalid negative prompt.')
    if request['mode']=='image_to_video' and not isinstance(request.get('reference'),str):raise AgentError('Approved local image reference required.')
    if 'editorial_guidance' in request:
        from .agents import encode
        encode(request['editorial_guidance'])
    return request


def media_path(sidecar,relative):
    from .specialist_media import asset
    asset(relative,pending=False);root=Path(sidecar).parent/'agent_media';p=root/relative
    if any(x.is_symlink() for x in (p,*p.parents)) or not p.resolve().is_relative_to(root.resolve()):raise AgentError('Unsafe isolated media path.')
    if not p.is_file():raise MediaBlocked('Local media reference unavailable.')
    return p


def inspect_output(path,request,sidecar):
    from .specialist_inspection import inspect_clip
    root=Path(sidecar).parent/'agent_media';relative=str(Path(path).relative_to(root))
    info=inspect_clip(relative,sidecar)
    video=next((s for s in info['streams'] if s.get('codec_type')=='video'),{})
    if (video.get('width'),video.get('height'))!=(request['width'],request['height']) or abs(info['duration']-request['frames']/request['fps'])>max(.15,1/request['fps']):raise AgentError('Encoded video dimensions/duration differ from the requested native output.')
    subprocess.run(['ffmpeg','-v','error','-protocol_whitelist','file,pipe','-i',str(path),'-f','null','-'],capture_output=True,check=True,timeout=60)
    return info


@serialized
def generate(engine,request,sidecar,timeout=900):
    validate_request(engine,request)
    if type(timeout) is not int or not 30<=timeout<=1800:raise AgentError('Invalid bounded media timeout.')
    status=preflight(engine,verify=True)
    if not status['ready']:raise MediaBlocked('; '.join(status['blockers']))
    image=None
    if request['mode']=='image_to_video':
        image=check_reference(sidecar,request['reference'])
        if image.stat().st_size>10*1024*1024:raise AgentError('Reference exceeds 10 MB.')
        from PIL import Image
        with Image.open(image) as im:
            if im.format not in ('PNG','JPEG') or im.width*im.height>20_000_000:raise AgentError('Invalid reference image.')
            im.verify()
    root=Path(sidecar).parent/'agent_media'/'offline_jobs'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe media job directory.')
    job=root/uuid4().hex;job.mkdir(parents=True)
    approval=approved(engine)
    data={'engine':engine,'request':request,'checkpoint':str((MODEL_ROOT/engine).resolve()),'reference':str(image.resolve()) if image else None,'output':str((job/'clip.mp4').resolve())}
    state={'state':'running','engine':engine,'request_sha256':digest(request),'model_manifest_sha256':approval['manifest']['sha256'],
       'input_sha256':sha(image) if image else None,'actual_generation':False,'technical_output_validated':False,'cinematic_quality_reviewed':False,'owner_approved_output':False}
    (job/'request.json').write_text(json.dumps(data,ensure_ascii=False))
    def save():(job/'evidence.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
    save();started=time.monotonic()
    try:
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
        with (job/'worker.log').open('w') as log:
            subprocess.run([sys.executable,'-m','redpad_pipeline.offline_worker',str(job/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=timeout,check=True)
        output=job/'clip.mp4';info=inspect_output(output,request,sidecar)
        # Recheck immutable sources after generation; no stale media promotion.
        if approved(engine,verify=True)['manifest']!=approval['manifest'] or (image and sha(image)!=state['input_sha256']):raise AgentError('Model/reference changed during inference.')
        state['model_identity_verified']=True
        state.update(state='technical_output_validated',actual_generation=True,technical_output_validated=True,output_sha256=sha(output),inspection=info)
        return {'path':str(output.relative_to(Path(sidecar).parent/'agent_media')),'actual_generation':True,'model':CATALOG[engine]['model'],'metadata':state}
    except subprocess.TimeoutExpired:
        state.update(state='failed',error='Owned inference worker timed out and was stopped; partial files retained.');raise MediaBlocked(state['error']) from None
    except Exception:
        state.update(state='failed',error='Offline inference or technical validation failed; inspect retained job evidence. No substituted clip.');raise MediaBlocked(state['error']) from None
    finally:
        marker=job/'worker_state.json'
        if marker.is_file():
            try:state['worker_inference']=json.loads(marker.read_text())
            except ValueError:state['worker_inference']={'inference_completed':False,'partial_marker_retained':True}
        completed=state.get('worker_inference',{}).get('inference_completed',False)
        if completed and not state.get('model_identity_verified'):
            try:state['model_identity_verified']=approved(engine,verify=True)['manifest']==approval['manifest'] and (not image or sha(image)==state['input_sha256'])
            except (AgentError,ValueError,OSError,KeyError):state['model_identity_verified']=False
        state['actual_inference_verified']=completed and state.get('model_identity_verified',False)
        state['wall_seconds']=round(time.monotonic()-started,3);save()


def recover_stopped_job(sidecar,job_id,confirmed=False):
    if confirmed is not True or not re.fullmatch(r'[a-f0-9]{32}',job_id):raise AgentError('Confirm the prior worker is stopped before recovery.')
    path=Path(sidecar).parent/'agent_media/offline_jobs'/job_id/'evidence.json'
    if any(p.is_symlink() for p in (path,*path.parents)):raise AgentError('Unsafe recovery path.')
    state=json.loads(path.read_text())
    if state['state']!='running':raise AgentError('Only abandoned running jobs need recovery.')
    state.update(state='interrupted',error='Owner confirmed stopped worker; partial files retained. Explicit new request required.')
    path.write_text(json.dumps(state,indent=2));return state


def approve_reference(sidecar,relative,reviewer,rights_note,confirmed=False):
    if confirmed is not True or not reviewer.strip() or not rights_note.strip():raise AgentError('Explicit reference review and usage-rights note required.')
    path=media_path(sidecar,relative)
    if path.stat().st_size>10*1024*1024:raise AgentError('Reference too large.')
    from PIL import Image
    with Image.open(path) as image:
        if image.format not in ('PNG','JPEG') or image.width*image.height>20_000_000:raise AgentError('Unsupported reference image.')
        image.verify()
    ledger=Path(sidecar).parent/'agent_media/approved_references.json'
    if ledger.is_symlink():raise AgentError('Unsafe reference ledger.')
    records=json.loads(ledger.read_text()) if ledger.exists() else {}
    records[relative]={'sha256':sha(path),'reviewer':reviewer,'rights_note':rights_note,'approved':True,'identity_consistency_verified':False}
    ledger.write_text(json.dumps(records,ensure_ascii=False,indent=2));return records[relative]


def check_reference(sidecar,relative):
    path=media_path(sidecar,relative);ledger=Path(sidecar).parent/'agent_media/approved_references.json'
    if not ledger.is_file() or ledger.is_symlink():raise MediaBlocked('Reference image needs explicit owner review before generation.')
    r=json.loads(ledger.read_text()).get(relative,{})
    if r.get('approved') is not True or r.get('sha256')!=sha(path):raise MediaBlocked('Reference approval missing or stale after asset change.')
    return path
