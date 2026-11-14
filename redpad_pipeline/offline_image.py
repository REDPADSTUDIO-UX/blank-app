"""Prospective SDXL reference-image worker. No downloads or identity-lock claim.
Checkpoint/license and compute approval remain explicit prerequisites.
"""
from .resource_guard import serialized

import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError
from .agent_media_bridge import MediaBlocked
from .offline_media import ROOT,MODEL_ROOT,checkpoint_manifest,sha,digest

MODEL='stabilityai/stable-diffusion-xl-base-1.0'
ENGINE='sdxl-base-1.0'

def approve_checkpoint(owner,license_note,confirmed=False):
    if confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Explicit owner approval of this SDXL variant/license is required.')
    folder=MODEL_ROOT/ENGINE;manifest=checkpoint_manifest(folder)
    for component in ('unet','vae','text_encoder','text_encoder_2','tokenizer','tokenizer_2'):
        if not (folder/component).is_dir():raise AgentError('Complete local SDXL pipeline component missing: '+component)
    for component in ('unet','vae','text_encoder','text_encoder_2'):
        if not list((folder/component).glob('*.fp16.safetensors')):raise AgentError('Reviewed image worker requires explicit FP16 component weights: '+component)
    config=json.loads((folder/'model_index.json').read_text())
    if config.get('_class_name')!='StableDiffusionXLPipeline':raise AgentError('Only the fixed SDXL base pipeline is supported.')
    record={'model':MODEL,'owner':owner,'license_note':license_note,'approved':True,'manifest':manifest}
    MODEL_ROOT.mkdir(parents=True,exist_ok=True);(MODEL_ROOT/(ENGINE+'.approval.json')).write_text(json.dumps(record,indent=2)+'\n')
    return record

def approval(verify=False):
    p=MODEL_ROOT/(ENGINE+'.approval.json')
    if not p.is_file() or p.is_symlink():raise MediaBlocked('Approved SDXL checkpoint/license unavailable; no download attempted.')
    r=json.loads(p.read_text())
    if r.get('approved') is not True or r.get('model')!=MODEL:raise MediaBlocked('SDXL approval differs from this exact model.')
    if verify and checkpoint_manifest(MODEL_ROOT/ENGINE)!=r['manifest']:raise MediaBlocked('Image checkpoint changed after approval.')
    return r

def preflight():
    blockers=[]
    try:approval()
    except (AgentError,OSError,ValueError) as exc:blockers.append(str(exc))
    for name in ('torch','diffusers','transformers','accelerate'):
        if importlib.util.find_spec(name) is None:blockers.append('Missing local dependency: '+name)
    if importlib.util.find_spec('torch'):
        import torch
        if not torch.cuda.is_available():blockers.append('CUDA GPU unavailable.')
        elif torch.cuda.get_device_properties(0).total_memory/2**30<12:blockers.append('Below unmeasured 12 GiB planning budget for this SDXL configuration.')
    else:blockers.append('CUDA memory cannot be verified.')
    return {'model':MODEL,'adapter_implemented':True,'ready':not blockers,'blockers':blockers,
            'actual_inference_verified':False,'visual_review_completed':False,'identity_conditioning_implemented':False,
            'memory_scope':'12 GiB is a conservative planning gate, not a measured minimum.'}

def validate_request(r):
    if not isinstance(r,dict) or set(r)!={'prompt','width','height','steps','seed'}:raise AgentError('Only fixed local SDXL text-to-image controls are supported; no remote/code/identity controls.')
    if not isinstance(r['prompt'],str) or not 1<=len(r['prompt'].strip())<=1600:raise AgentError('Bounded original image brief required.')
    if any(type(r[k]) is not int or r[k] not in (512,768,1024) for k in ('width','height')):raise AgentError('Use 512, 768 or 1024 image dimensions.')
    if r['steps']!=30 or type(r['steps']) is not int or type(r['seed']) is not int or not 0<=r['seed']<=2147483647:raise AgentError('Use fixed 30-step, bounded-seed micro benchmark.')
    return r

@serialized
def generate(request,sidecar,timeout=300):
    validate_request(request)
    if type(timeout) is not int or not 30<=timeout<=900:raise AgentError('Bounded image timeout required.')
    status=preflight()
    if not status['ready']:raise MediaBlocked('; '.join(status['blockers']))
    approved=approval(True);root=Path(sidecar).parent/'agent_media/offline_images'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe image workspace.')
    job=root/uuid4().hex;job.mkdir(parents=True)
    payload={'request':request,'checkpoint':str((MODEL_ROOT/ENGINE).resolve()),'output':str((job/'image.png').resolve())}
    (job/'request.json').write_text(json.dumps(payload,ensure_ascii=False))
    state={'state':'running','model':MODEL,'model_manifest_sha256':approved['manifest']['sha256'],'request_sha256':digest(request),
           'actual_generation':False,'actual_inference_verified':False,'technical_output_validated':False,'visual_review_completed':False,'identity_lock':False}
    def save():(job/'evidence.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    save();start=time.monotonic()
    try:
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
        with (job/'worker.log').open('w') as log:
            subprocess.run([sys.executable,'-m','redpad_pipeline.image_worker',str(job/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=timeout,check=True)
        from PIL import Image
        path=job/'image.png'
        with Image.open(path) as im:
            if im.format!='PNG' or im.size!=(request['width'],request['height']):raise AgentError('Generated image dimensions/format differ.')
            im.verify()
        marker=json.loads((job/'worker_state.json').read_text())
        if marker.get('inference_completed') is not True:raise AgentError('No completed actual image inference marker.')
        if approval(True)['manifest']!=approved['manifest']:raise AgentError('Image model changed during generation.')
        state.update(state='technical_output_validated',actual_generation=True,actual_inference_verified=True,
                     model_identity_verified=True,technical_output_validated=True,output_sha256=sha(path),worker_inference=marker,
                     inspection={'width':request['width'],'height':request['height'],'format':'PNG'})
        return {'path':str(path.relative_to(Path(sidecar).parent/'agent_media')),'model':MODEL,'actual_generation':True,'metadata':state}
    except Exception:
        state.update(state='failed',error='Owned image inference/validation failed or timed out; retained files are not substituted output.')
        raise MediaBlocked(state['error']) from None
    finally:
        state['wall_seconds']=round(time.monotonic()-start,3);save()
