"""Optional local Indic Parler-TTS. No cloning, network service or model download."""
from .resource_guard import serialized

import importlib.util,json,os,re,subprocess,sys,time,unicodedata
from pathlib import Path
from uuid import uuid4
from .agents import AgentError
from .agent_media_bridge import MediaBlocked
from .offline_media import MODEL_ROOT,checkpoint_manifest,sha,digest,ROOT

MODEL='ai4bharat/indic-parler-tts'
PRESETS=['Arjun','Aditi','Tapan','Rashmi','Arnav','Riya']
STYLES={'neutral':'A calm neutral conversational delivery.','warm':'A warm restrained conversational delivery.',
        'sad':'A quietly sad restrained delivery.','nervous':'A hesitant slightly nervous delivery.','amused':'A gently amused delivery without exaggerated laughter.'}


def approve_speech(owner,license_note,confirmed=False):
    if confirmed is not True or not owner.strip() or not license_note.strip():raise AgentError('Owner confirmation and model/component license review required.')
    root=MODEL_ROOT/'bengali-tts';manifest=checkpoint_manifest(root,index='config.json')
    if not (root/'description_tokenizer').is_dir():raise AgentError('Offline description tokenizer bundle required.')
    record={'model':MODEL,'owner':owner,'license_note':license_note,'approved':True,'manifest':manifest}
    (MODEL_ROOT/'bengali-tts.approval.json').write_text(json.dumps(record,indent=2));return record


def speech_approval(verify=False):
    p=MODEL_ROOT/'bengali-tts.approval.json'
    if not p.is_file() or p.is_symlink():raise MediaBlocked('Approved local Bengali TTS backend unavailable; weights/license/component approval required.')
    r=json.loads(p.read_text())
    if r.get('model')!=MODEL or r.get('approved') is not True:raise MediaBlocked('Speech approval invalid.')
    if verify and checkpoint_manifest(MODEL_ROOT/'bengali-tts',index='config.json')!=r['manifest']:raise MediaBlocked('Speech checkpoint changed after approval.')
    return r


def preflight():
    blockers=[]
    try:speech_approval()
    except (AgentError,ValueError,OSError) as exc:blockers.append(str(exc))
    for name in ('torch','parler_tts','transformers','numpy'):
        if importlib.util.find_spec(name) is None:blockers.append('Missing dependency: '+name)
    return {'model':MODEL,'adapter_implemented':True,'ready':not blockers,'blockers':blockers,
            'actual_inference_verified':False,'listening_review_completed':False,'bangladeshi_pronunciation_verified':False,
            'voice_cloning':False,'device':'CPU micro-test only; CUDA use requires a separately reviewed configuration'}


@serialized
def synthesize(request,sidecar,timeout=240):
    status=preflight()
    if not status['ready']:raise MediaBlocked('; '.join(status['blockers']))
    if not isinstance(request,dict) or request.get('preset') not in PRESETS or request.get('style','neutral') not in STYLES:raise AgentError('Select a documented synthetic Bengali preset and bounded style; no reference voice upload.')
    text=request.get('text')
    seed=request.get('seed',42)
    if type(seed) is not int or not 0<=seed<=2147483647:raise AgentError('Bounded speech seed required.')
    if not isinstance(text,str) or not 1<=len(text)<=300 or not re.search('[\u0980-\u09ff]',text):raise AgentError('Short Bengali transcript required (1–300 characters).')
    if type(timeout) is not int or not 30<=timeout<=600:raise AgentError('Invalid speech timeout.')
    approval=speech_approval(True);root=Path(sidecar).parent/'agent_media/offline_speech'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe speech workspace.')
    job=root/uuid4().hex;job.mkdir(parents=True)
    transcript=unicodedata.normalize('NFC',text)
    caption=request['preset']+' speaks in Bengali. '+STYLES[request.get('style','neutral')]+' Clear close recording without background noise.'
    payload={'checkpoint':str((MODEL_ROOT/'bengali-tts').resolve()),'text':transcript,'description':caption,'seed':seed,'output':str((job/'speech.wav').resolve())}
    state={'state':'running','model':MODEL,'preset':request['preset'],'style':request.get('style','neutral'),'seed':seed,'max_new_tokens':1024,'manifest_sha256':approval['manifest']['sha256'],
           'text_sha256':digest(transcript),'actual_generation':False,'listening_review_completed':False,'bangladeshi_pronunciation_verified':False,'lip_sync_verified':False}
    def save():(job/'evidence.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
    (job/'request.json').write_text(json.dumps(payload,ensure_ascii=False));save();started=time.monotonic()
    try:
        env=os.environ.copy();env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='-1')
        with (job/'worker.log').open('w') as log:subprocess.run([sys.executable,'-m','redpad_pipeline.speech_worker',str(job/'request.json')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=timeout,check=True)
        from .specialist_inspection import inspect_clip
        output=job/'speech.wav';relative=str(output.relative_to(Path(sidecar).parent/'agent_media'));info=inspect_clip(relative,sidecar)
        if not .1<=info['duration']<=30 or not any(s.get('codec_type')=='audio' for s in info['streams']):raise AgentError('Speech duration/stream validation failed.')
        if speech_approval(True)['manifest']!=approval['manifest']:raise AgentError('Speech checkpoint changed during inference.')
        state['model_identity_verified']=True
        state.update(state='technical_output_validated',actual_generation=True,output_sha256=sha(output),inspection=info)
        return {'path':relative,'model':MODEL,'actual_generation':True,'metadata':state}
    except Exception:
        state.update(state='failed',error='Offline speech worker failed or timed out; partial files retained, no remote fallback.');raise MediaBlocked(state['error']) from None
    finally:
        marker=job/'worker_state.json'
        if marker.is_file():
            try:state['worker_inference']=json.loads(marker.read_text())
            except ValueError:state['worker_inference']={'inference_completed':False,'partial_marker_retained':True}
        completed=state.get('worker_inference',{}).get('inference_completed',False)
        if completed and not state.get('model_identity_verified'):
            try:state['model_identity_verified']=speech_approval(True)['manifest']==approval['manifest']
            except (AgentError,ValueError,OSError,KeyError):state['model_identity_verified']=False
        state['actual_inference_verified']=completed and state.get('model_identity_verified',False)
        state['wall_seconds']=round(time.monotonic()-started,3);save()
