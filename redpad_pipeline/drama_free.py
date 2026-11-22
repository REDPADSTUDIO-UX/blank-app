"""Bounded, anonymous existing ZeroGPU adapters. No paid endpoints or fallback.
Network discovery does not count as successful inference or sufficient episode quota.
"""
from __future__ import annotations
import importlib.util,json,shutil,time
from pathlib import Path
import requests
from .drama_quality import Studio,QualityError,media_info
from .remote_gpu import BASE,SPACE,generate,GPUError
VOICE_BASE='https://ai4bharat-indic-parler-tts.hf.space'
VIDEO_RIGHTS='https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B'
VOICE_RIGHTS='https://huggingface.co/ai4bharat/indic-parler-tts'

def probe(studio:Studio,pid):
 """Read-only access checks, saved with exact status and no fabricated quota."""
 results={}
 for kind,base,rights in [('video',BASE,VIDEO_RIGHTS),('voice',VOICE_BASE,VOICE_RIGHTS)]:
  record={'provider':SPACE if kind=='video' else 'ai4bharat/indic-parler-tts','endpoint':base,'rights_url':rights,'cost_usd':0,'paid_api':False,'access':'unverified','production_rights':'needs_review','quota':'unknown','checked_at':time.time(),'remaining_gpu_seconds':None,'estimated_job_gpu_seconds':None,'notes':[]}
  try:
   r=requests.get(base+'/gradio_api/info',timeout=(8,25));record['http_status']=r.status_code
   if r.status_code==200:
    names=list(r.json().get('named_endpoints',{}));record['api_names']=names;record['access']='endpoint_reachable';record['notes'].append('Endpoint discovery succeeded; this does not prove inference, quota or dialogue quality.')
   else:record['notes'].append('Service discovery returned HTTP '+str(r.status_code)+'. No inference submitted.')
  except (requests.RequestException,ValueError):record['notes'].append('Endpoint discovery failed; no inference submitted.')
  if kind=='voice':record['notes'].append('Model download is gated; no access terms were accepted on the user’s behalf. Public demo availability is checked separately.')
  key='capability/'+kind;old=studio.entries(pid).get(key,{});studio.save(pid,'capability',kind,record,old.get('revision',0));results[kind]=record
 results['local']={'cuda_device':bool(shutil.which('nvidia-smi')),'torch_installed':importlib.util.find_spec('torch') is not None,'tts_checkpoint_provisioned':False,'paid_fallback':False}
 folder=studio.root/pid;folder.mkdir(exist_ok=True);(folder/'capability_probe.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 return results

def visual_sample(studio:Studio,pid,shot_id,reference_asset):
 gates=studio.gates(pid)
 if not gates['development']['passed']:raise QualityError('Finish researched screenplay development before submitting the visual sample.')
 entries=studio.entries(pid);shot=entries['shot/'+shot_id]['payload'];cap=entries.get('capability/video',{}).get('payload',{})
 if cap.get('cost_usd')!=0 or cap.get('paid_api') is not False or cap.get('access') not in ('endpoint_reachable','verified'):raise QualityError('Existing free video endpoint has not been verified as reachable.')
 ref=next((a for a in studio.assets(pid) if a['id']==reference_asset and a['kind']=='reference' and a['current']),None)
 if not ref or ref['target'] not in shot['reference_ids'] or ref['metadata'].get('output_kind')!='photorealistic_reference':raise QualityError('Use this shot’s actual current photorealistic character/location reference.')
 studio.require_disclosure(pid,BASE)
 jid=studio.start_job(pid,'shot',shot_id);folder=studio.root/pid/'samples';folder.mkdir(exist_ok=True)
 prompt=('Photorealistic Bangladeshi live-action cinematic scene. Preserve the exact person, face, dark shirt, age and location in the reference. '+shot['action']+' '+shot['camera_reason']+' Natural restrained acting and physical motion. No cartoon, anime, illustration, subtitles, text, logos, extra people, extra hands or floating objects.')[:1500]
 try:
  studio.job_state(jid,'running','One anonymous existing ZeroGPU submission; no paid fallback.')
  # Existing reviewed adapter is anonymous unless a previously verified free token exists.
  made=generate(Path(ref['path']).read_bytes(),prompt,folder,seconds=min(float(shot['seconds']),5),seed=int(__import__('hashlib').sha256((pid+shot_id).encode()).hexdigest()[:8],16))
  imported=studio.import_bytes(pid,made.name,made.read_bytes())
  aid=studio.register_asset(pid,'shot',shot_id,imported,{'engine':'Wan2.2 FP8 AOTI on existing anonymous ZeroGPU Space','output_kind':'photorealistic_neural_video','rights_url':VIDEO_RIGHTS,'rights_note':'Base model card lists Apache-2.0. Full wrapper/adapter rights and output quality require recorded review. Sample only, not final approval.','rights_scope':'internal_test','cost_usd':0,'paid_api':False,'source_reference_sha256':ref['sha'],'sample_only':True})
  studio.job_state(jid,'complete','Generated sample '+aid+'; editorial realism/continuity/movement review remains pending.')
  return aid
 except Exception as exc:
  detail=str(exc) if isinstance(exc,(QualityError,GPUError)) else 'Free visual inference failed or status uncertain; inspect checkpoint, no resubmission.'
  studio.job_state(jid,'blocked',detail);raise QualityError(detail) from None

def voice_sample(studio:Studio,pid,line_id):
 if not studio.gates(pid)['development']['passed']:raise QualityError('Finish screenplay development before auditioning dialogue.')
 e=studio.entries(pid);p=e['line/'+line_id]['payload'];cap=e.get('capability/voice',{}).get('payload',{})
 if cap.get('cost_usd')!=0 or cap.get('paid_api') is not False or cap.get('access') not in ('endpoint_reachable','verified'):raise QualityError('Free expressive voice service is unavailable. No robotic/paid fallback will be substituted.')
 studio.require_disclosure(pid,VOICE_BASE)
 jid=studio.start_job(pid,'voice',line_id);folder=studio.root/pid/'voice_samples';folder.mkdir(exist_ok=True)
 try:
  from gradio_client import Client
  client=Client(VOICE_BASE,hf_token=False,verbose=False,analytics_enabled=False,download_files=str(folder.resolve()),httpx_kwargs={'timeout':45})
  api='/generate_finetuned'
  if api not in cap.get('api_names',[]):raise QualityError('The reviewed voice endpoint changed. No inference submitted.')
  speaker=e['bible/'+p['speaker']]['payload'].get('voice_speaker','Arjun')
  description=(speaker+' speaks Bengali. '+p['intention']+'. Emotion: '+p['emotion']+'. '+p['pace']+'. Very clear close-mic audio, no music, natural conversational delivery, restrained acting.')[:1000]
  studio.job_state(jid,'running','One anonymous Indic Parler speech audition; no voice cloning.')
  result=client.submit(studio.spoken_line(pid,line_id),description,api_name=api).result(timeout=180)
  paths=[]
  def collect(v):
   if isinstance(v,str):paths.append(v)
   elif isinstance(v,dict):
    for k in ('path','value'):collect(v.get(k))
   elif isinstance(v,(list,tuple)):
    for x in v:collect(x)
  collect(result)
  source=next((Path(p).resolve() for p in paths if Path(p).suffix.lower() in ('.wav','.mp3') and Path(p).is_file() and Path(p).resolve().is_relative_to(folder.resolve())),None)
  if source is None:raise QualityError('Voice endpoint did not return a supported audio file.')
  imported=studio.import_bytes(pid,source.name,source.read_bytes());aid=studio.register_asset(pid,'voice',line_id,imported,{'engine':'AI4Bharat Indic Parler-TTS existing public ZeroGPU demo','output_kind':'neural_dialogue','rights_url':VOICE_RIGHTS,'rights_note':'Model card lists Apache-2.0; demo terms and output performance require review. No gated weights downloaded or terms accepted.','rights_scope':'internal_test','cost_usd':0,'paid_api':False,'description':description})
  studio.job_state(jid,'complete','Audition '+aid+'; clarity, pronunciation and performance are not yet approved.');return aid
 except Exception as exc:
  detail=str(exc) if isinstance(exc,QualityError) else 'Free voice audition failed or quota unavailable; no paid/robotic fallback. Inspect before retry.'
  studio.job_state(jid,'blocked',detail);raise QualityError(detail) from None


def produce_missing(studio:Studio,pid):
 """Resume a bounded existing-free-service batch only after actual preflight passes.
 Existing assets, including unreviewed takes, are preserved rather than regenerated.
 Each new result still requires editorial review; no automatic quality acceptance.
 """
 gate=studio.gates(pid)['production_start']
 if not gate['passed']:raise QualityError('Production preflight blocked: '+'; '.join(gate['issues'][:6]))
 e=studio.entries(pid);source=studio.source_hash(pid)
 refs=[a for a in studio.assets(pid) if a['kind']=='reference' and a['selected'] and a['current']]
 for key,r in sorted(e.items()):
  if not key.startswith(('shot/','line/')):continue
  if studio.source_hash(pid)!=source:raise QualityError('Source changed during batch; cached assets retained.')
  component,target=key.split('/');kind='shot' if component=='shot' else 'voice'
  if any(a['kind']==kind and a['target']==target and a['current'] for a in studio.assets(pid)):continue
  if kind=='voice':voice_sample(studio,pid,target);continue
  shot=r['payload']
  if shot['seconds']>5:raise QualityError('Split this shot into motivated coverage within the free model duration; no loop/stretch fallback.')
  people=[x for x in shot['reference_ids'] if e['bible/'+x]['payload'].get('voice_speaker')]
  candidates=[a for a in refs if a['metadata'].get('shot_id')==target]
  if len(people)>1 and not candidates:raise QualityError('A multi-character shot needs an accepted composition reference for that exact shot; single-image I2V cannot silently invent a second identity.')
  ref=next(iter(candidates),None) or next((a for a in refs if a['target'] in people),None)
  if not ref:raise QualityError('Missing reviewed character/composition reference for '+target)
  visual_sample(studio,pid,target,ref['id'])
 return 'Batch complete or cached; review actual takes before final rendering.'
