"""Prospective local visual criticism, with original images/response retained.
Image/frame inspection is not human review or validated cinematic judgment.
"""
import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError
from .agent_media_bridge import MediaBlocked
from .offline_media import ROOT,MODEL_ROOT,checkpoint_manifest,media_path,sha,digest
from .resource_guard import serialized

MODEL='Qwen/Qwen2.5-VL-7B-Instruct';ENGINE='qwen25-vl-7b'

def approve(owner,license_note,confirmed=False):
    if confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Exact local vision model/components and explicit owner/license approval required.')
    manifest=checkpoint_manifest(MODEL_ROOT/ENGINE,'config.json')
    r={'approved':True,'model':MODEL,'manifest':manifest,'owner':owner,'license_note':license_note}
    (MODEL_ROOT/(ENGINE+'.approval.json')).write_text(json.dumps(r,indent=2));return r

def approval(verify=False):
    p=MODEL_ROOT/(ENGINE+'.approval.json')
    if not p.is_file() or any(v.is_symlink() for v in (p,*p.parents)):raise MediaBlocked('Approved local visual critic checkpoint/license missing; no download attempted.')
    r=json.loads(p.read_text())
    if r.get('approved') is not True or r.get('model')!=MODEL:raise MediaBlocked('Vision approval identity differs.')
    if verify and checkpoint_manifest(MODEL_ROOT/ENGINE,'config.json')!=r['manifest']:raise MediaBlocked('Vision checkpoint changed.')
    return r

def preflight():
    blockers=[]
    try:approval(True)
    except (AgentError,OSError,ValueError) as e:blockers.append(str(e))
    for name in ('torch','transformers','accelerate','PIL'):
        if importlib.util.find_spec(name) is None:blockers.append('Missing dependency: '+name)
    if importlib.util.find_spec('torch'):
        import torch
        if not torch.cuda.is_available():blockers.append('CUDA unavailable for this bounded vision configuration.')
        elif torch.cuda.get_device_properties(0).total_memory<16*2**30:blockers.append('Below unmeasured conservative 16 GiB vision budget.')
    return {'model':MODEL,'adapter_implemented':True,'ready':not blockers,'blockers':blockers,'actual_inference_verified':False,'judgment_accuracy_verified':False,'human_review_completed':False}

def frames(sidecar,video,timestamps):
    from .specialist_inspection import inspect_clip
    if not isinstance(timestamps,list) or not 1<=len(timestamps)<=3:raise AgentError('Select one to three explicit frame timestamps.')
    info=inspect_clip(video,sidecar);source=media_path(sidecar,video);original=sha(source)
    if not any(s['codec_type']=='video' for s in info['streams']):raise AgentError('Actual video required for frame extraction.')
    if any(type(t) not in (int,float) or not 0<=t<info['duration'] for t in timestamps):raise AgentError('Frame timestamps outside inspected video.')
    root=Path(sidecar).parent/'agent_media/inspection_frames'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe frame workspace.')
    job=root/uuid4().hex;job.mkdir(parents=True);result=[]
    for i,t in enumerate(timestamps):
        path=job/f'frame-{i}.png'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-protocol_whitelist','file,pipe','-ss',str(t),'-f','mov','-i',str(source),'-frames:v','1','-vf','scale=512:-2','-threads','1',str(path)],capture_output=True,timeout=30,check=True)
        if not path.is_file():raise AgentError('Requested frame was not decoded.')
        result.append({'path':str(path.relative_to(Path(sidecar).parent/'agent_media')),'sha256':sha(path),'seconds':t})
    if sha(source)!=original:raise AgentError('Source video changed during frame extraction.')
    value={'source':video,'source_sha256':original,'frames':result,'human_review_completed':False,'model_inference':False}
    (job/'receipt.json').write_text(json.dumps(value,indent=2));return value

@serialized
def inspect(request,sidecar,timeout=300):
    if not isinstance(request,dict) or set(request)!={'images','question','seed'} or not isinstance(request['images'],list) or not 1<=len(request['images'])<=3 or not isinstance(request['question'],str) or not 1<=len(request['question'])<=1200 or type(request['seed']) is not int or not 0<=request['seed']<=2147483647:raise AgentError('One to three local images and a bounded visual question/seed required.')
    if type(timeout) is not int or not 30<=timeout<=600:raise AgentError('Bounded visual inference timeout required.')
    from PIL import Image
    images=[]
    for relative in request['images']:
        path=media_path(sidecar,relative)
        if path.stat().st_size>10*1024*1024:raise AgentError('Inspection image exceeds 10 MB.')
        with Image.open(path) as im:
            if im.format not in ('PNG','JPEG') or im.width*im.height>4_000_000:raise AgentError('Bounded PNG/JPEG image required.')
            im.verify()
        images.append({'path':str(path.resolve()),'sha256':sha(path),'relative':relative})
    status=preflight()
    if not status['ready']:raise MediaBlocked('; '.join(status['blockers']))
    approved=approval(True);root=Path(sidecar).parent/'agent_media/offline_vision'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe visual critic workspace.')
    job=root/uuid4().hex;job.mkdir(parents=True)
    payload={'checkpoint':str((MODEL_ROOT/ENGINE).resolve()),'images':images,'request':request,'output':str((job/'response.txt').resolve())}
    (job/'request.json').write_text(json.dumps(payload));start=time.monotonic();state={'state':'running','model':MODEL,'model_manifest_sha256':approved['manifest']['sha256'],'input_images':images,'actual_inference_verified':False,'judgment_accuracy_verified':False,'human_review_completed':False}
    def save():(job/'evidence.json').write_text(json.dumps(state,indent=2))
    save()
    try:
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        with (job/'worker.log').open('w') as log:subprocess.run([sys.executable,'-m','redpad_pipeline.vision_worker',str(job/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=timeout,check=True)
        raw=(job/'response.txt').read_text();marker=json.loads((job/'worker_state.json').read_text())
        if not raw.strip() or marker.get('inference_completed') is not True:raise AgentError('No completed vision inference response.')
        if approval(True)['manifest']!=approved['manifest'] or any(sha(Path(i['path']))!=i['sha256'] for i in images):raise AgentError('Model/image changed during visual inference.')
        state.update(state='technical_output_validated',model_identity_verified=True,actual_inference_verified=True,inference_completed=True,worker_inference=marker,
                     raw_sha256=sha(job/'response.txt'),model_digest=approved['manifest']['sha256'])
        return {'model':MODEL,'actual_generation':False,'raw_text':raw,'metadata':state,'source_images':images,'visual_observations_are_unverified':True}
    except Exception:state.update(state='failed',error='Visual critic worker/validation failed; original images and partial response retained.');raise MediaBlocked(state['error']) from None
    finally:state['wall_seconds']=round(time.monotonic()-start,3);save()
