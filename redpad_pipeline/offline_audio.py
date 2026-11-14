"""Prospective fixed local ACE music / Stable Audio SFX workers; no downloads.
Backend packages, safetensors bundles, auxiliary components and license approval
must already exist. Real model/API compatibility remains unverified until run.
"""
from .resource_guard import serialized

import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError
from .agent_media_bridge import MediaBlocked
from .offline_media import MODEL_ROOT,ROOT,checkpoint_manifest,sha,digest

# Official Stable Audio Open Small recipe; package/runtime compatibility remains unverified.
STABLE_AUDIO_SMALL_RECIPE={'steps':8,'cfg_scale':1.0,'sampler_type':'pingpong'}

ENGINES={'ace-step-v1':{'model':'ACE-Step/ACE-Step-v1-3.5B','index':'ace_step_transformer/config.json','module':'acestep','vram':12,'max_seconds':30},
         'stable-audio-small':{'model':'stabilityai/stable-audio-open-small','index':'model_config.json','module':'stable_audio_tools','vram':4,'max_seconds':11}}

def approve(engine,owner,license_note,confirmed=False):
    if engine not in ENGINES or confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Exact model/component license and explicit owner approval required.')
    spec=ENGINES[engine];folder=MODEL_ROOT/engine;manifest=checkpoint_manifest(folder,spec['index'])
    if engine=='ace-step-v1' and not all((folder/n).is_dir() for n in ('music_dcae_f8c8','music_vocoder','ace_step_transformer','umt5-base')):raise AgentError('Complete local ACE component recipe required.')
    if engine=='stable-audio-small' and not (folder/'model.safetensors').is_file():raise AgentError('Exact Stable Audio safetensors required; pickle is not accepted.')
    value={'model':spec['model'],'owner':owner,'license_note':license_note,'approved':True,'manifest':manifest}
    (MODEL_ROOT/(engine+'.approval.json')).write_text(json.dumps(value,indent=2));return value

def approval(engine,verify=False):
    if engine not in ENGINES:raise AgentError('Unknown local audio backend.')
    p=MODEL_ROOT/(engine+'.approval.json')
    if not p.is_file() or any(x.is_symlink() for x in (p,*p.parents)):raise MediaBlocked('Approved local audio/license record absent; no download attempted.')
    r=json.loads(p.read_text());spec=ENGINES[engine]
    if r.get('approved') is not True or r.get('model')!=spec['model']:raise MediaBlocked('Audio approval identity differs.')
    if verify and checkpoint_manifest(MODEL_ROOT/engine,spec['index'])!=r['manifest']:raise MediaBlocked('Audio checkpoint changed after approval.')
    return r

def preflight(engine):
    if engine not in ENGINES:raise AgentError('Unknown local audio backend.')
    blockers=[]
    try:approval(engine,True)
    except (AgentError,OSError,ValueError) as exc:blockers.append(str(exc))
    for name in ('torch','safetensors','soundfile',ENGINES[engine]['module']):
        if importlib.util.find_spec(name) is None:blockers.append('Missing dependency: '+name)
    if importlib.util.find_spec('torch'):
        import torch
        if not torch.cuda.is_available():blockers.append('CUDA unavailable for reviewed audio configuration.')
        elif torch.cuda.get_device_properties(0).total_memory<ENGINES[engine]['vram']*2**30:blockers.append('Below unmeasured audio planning budget.')
    return {'engine':engine,'adapter_implemented':True,'ready':not blockers,'blockers':blockers,'actual_inference_verified':False,'listening_review_completed':False,'backend_api_compatibility':'prospective; actual installed package/checkpoint compatibility unverified'}

def validate(engine,request):
    if engine not in ENGINES or not isinstance(request,dict) or set(request)!={'prompt','seconds','seed','steps'}:raise AgentError('Fixed instrumental/SFX controls only; no lyrics, cloning, remote endpoint or LoRA.')
    if not isinstance(request['prompt'],str) or not 1<=len(request['prompt'])<=1000:raise AgentError('Bounded audio prompt required.')
    if type(request['seconds']) not in (float,int) or not .5<=request['seconds']<=ENGINES[engine]['max_seconds']:raise AgentError('Audio duration exceeds the model micro-test scope.')
    minimum_steps=8 if engine=='stable-audio-small' else 10
    if type(request['seed']) is not int or not 0<=request['seed']<=2147483647 or type(request['steps']) is not int or not minimum_steps<=request['steps']<=100:raise AgentError('Bounded audio seed/steps required.')

@serialized
def generate(engine,request,sidecar,timeout=600):
    validate(engine,request)
    if type(timeout) is not int or not 30<=timeout<=900:raise AgentError('Bounded audio timeout required.')
    ready=preflight(engine)
    if not ready['ready']:raise MediaBlocked('; '.join(ready['blockers']))
    approved=approval(engine,True);root=Path(sidecar).parent/'agent_media/offline_audio'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe audio workspace.')
    job=root/uuid4().hex;job.mkdir(parents=True);output=job/'audio.wav'
    payload={'engine':engine,'request':request,'checkpoint':str((MODEL_ROOT/engine).resolve()),'output':str(output.resolve())}
    state={'state':'running','model':ENGINES[engine]['model'],'model_manifest_sha256':approved['manifest']['sha256'],'request_sha256':digest(request),
        'actual_generation':False,'actual_inference_verified':False,'listening_review_completed':False,'musicality_verified':False}
    def save():(job/'evidence.json').write_text(json.dumps(state,indent=2))
    (job/'request.json').write_text(json.dumps(payload));save();start=time.monotonic()
    try:
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
        with (job/'worker.log').open('w') as log:subprocess.run([sys.executable,'-m','redpad_pipeline.audio_worker',str(job/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,check=True,timeout=timeout)
        marker=json.loads((job/'worker_state.json').read_text())
        if marker.get('inference_completed') is not True:raise AgentError('Missing completed audio inference marker.')
        from .specialist_inspection import inspect_clip
        from .audio_evaluation import measure
        relative=str(output.relative_to(Path(sidecar).parent/'agent_media'));info=inspect_clip(relative,sidecar)
        if abs(info['duration']-request['seconds'])>.25:raise AgentError('Actual audio duration differs from requested cue.')
        if approval(engine,True)['manifest']!=approved['manifest']:raise AgentError('Audio model changed during generation.')
        state.update(state='technical_output_validated',actual_generation=True,actual_inference_verified=True,model_identity_verified=True,technical_output_validated=True,
            output_sha256=sha(output),worker_inference=marker,inspection=info,pcm_metrics=measure(relative,sidecar))
        return {'path':relative,'model':ENGINES[engine]['model'],'actual_generation':True,'metadata':state}
    except Exception:
        state.update(state='failed',error='Offline audio backend/validation failed or timed out; partial files retained, no substitute cue.')
        raise MediaBlocked(state['error']) from None
    finally:state['wall_seconds']=round(time.monotonic()-start,3);save()
