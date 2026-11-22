"""Strict no-network finishing: scene-timed dialogue, music, ambience and Foley.
Consumes accepted real media only. Never stretches a short clip into a whole scene.
"""
from __future__ import annotations
import json,math,subprocess,wave
from pathlib import Path
import numpy as np
from .drama_quality import QualityError,Studio,file_hash,media_info,canonical,digest
from .media import ff,timestamp

def _write_wave(path,a,rate=48000):
 with wave.open(str(path),'wb') as w:
  w.setparams((2,2,rate,0,'NONE','not compressed'));w.writeframes((np.clip(a,-.95,.95)*32767).astype('<i2').tobytes())

def compose_cue(path,cue):
 """Original melodic/harmonic sketch for a specific cue, not an approved final score."""
 if cue.get('treatment')!='composed':raise QualityError('This cue intentionally uses ambience/silence, not a music asset.')
 seconds=cue['end']-cue['start']
 if not 1<=seconds<=180:raise QualityError('Compose a bounded musical cue of 1–180 seconds.')
 rate=48000;a=np.zeros((int(seconds*rate),2),dtype=np.float32)
 # Minor/add9 voicings evolve under a sparse four-note motif. No continuous drone.
 tempo=float(cue.get('tempo',54));beat=60/tempo;motif=cue.get('notes',[62,69,64,65]);voicings=cue.get('voicings',[[50,57,64],[46,53,62],[48,55,64],[45,52,61]])
 if not 30<=tempo<=120 or len(motif)>16 or any(not isinstance(n,int) or not 24<=n<=96 for n in motif):raise QualityError('Invalid composition controls.')
 def note(midi,start,dur,gain,pan,plucked=True):
  if start>=seconds:return
  n=min(int(dur*rate),len(a)-int(start*rate));t=np.arange(n)/rate;hz=440*2**((midi-69)/12)
  env=(1-np.exp(-t/(.012 if plucked else .4)))*np.exp(-t/(1.7 if plucked else max(dur/2,1)))
  env*=np.minimum(1,(dur-t)/.35)
  sig=np.zeros(n)
  for h in range(1,7):sig+=np.sin(2*np.pi*hz*h*t+.001*h*np.sin(2*np.pi*3*t))*math.exp(-h*.7)/(h**.8)
  sig*=env*gain
  at=int(start*rate);a[at:at+n,0]+=sig*math.sqrt((1-pan)/2);a[at:at+n,1]+=sig*math.sqrt((1+pan)/2)
 for bar in range(math.ceil(seconds/(beat*4))):
  start=bar*beat*4
  for i,n in enumerate(voicings[bar%len(voicings)]):note(n,start+i*.08,beat*3.5,.09,-.4+i*.4,False)
  # Alternating rests leave dialogue and reactions space.
  if bar%3!=2:
   for i,n in enumerate(motif):note(n,start+(i*.75+.5)*beat,beat*1.5,.17 if i==0 else .1,.2 if i%2 else -.2)
 fade=np.minimum(1,np.arange(len(a))/rate/1.3)*np.minimum(1,(len(a)-np.arange(len(a)))/rate/2)
 a*=fade[:,None];_write_wave(path,a)
 return {'engine':'REDPAD original modal-motif composer','output_kind':'composed_music','cost_usd':0,'paid_api':False,'rights_scope':'publication','rights_url':'https://github.com/REDPADSTUDIO-UX/blank-app','rights_note':'Original code-synthesized musical sketch; no third-party recording or melody sampled. Editorial musicality/story-fit review still required.','instrumentation':cue['instrumentation'],'motif':cue['motif'],'harmony':cue['harmony']}

def sound_event(path,cue):
 """Action-specific source sounds. Event offsets are applied only by the timeline mixer."""
 kind=cue.get('sound');seconds=float(cue.get('duration',1));rate=48000
 if not .02<=seconds<=600:raise QualityError('Invalid event duration.')
 t=np.arange(int(seconds*rate))/rate;rng=np.random.default_rng(117);a=np.zeros_like(t)
 if kind=='rain':
  noise=rng.normal(0,1,len(t));a=np.convolve(noise,np.ones(15)/15,mode='same')*.08
 elif kind=='room_tone':
  noise=rng.normal(0,1,len(t));a=np.convolve(noise,np.ones(40)/40,mode='same')*.025
 elif kind in ('cup','keys','switch','tape_stop','tape_play'):
  a=(np.sin(2*np.pi*(1600 if kind in ('cup','keys') else 180)*t)+.35*np.sin(2*np.pi*2371*t))*np.exp(-t*35)*.22
 elif kind in ('knock','footstep'):
  for at in cue.get('hits',[0]):
   d=t-at;env=np.where(d>=0,np.exp(-np.maximum(d,0)*30),0);a+=(np.sin(2*np.pi*110*d)+rng.normal(0,.2,len(t)))*env*.18
 elif kind=='drip':a=np.sin(2*np.pi*(1200*t-1800*t*t))*np.exp(-t*32)*.2
 elif kind=='original_phone':
  envelope=(np.mod(t,2.6)<1.1).astype(float)*(0.6+0.4*np.sin(2*np.pi*14*t))
  a=(np.sin(2*np.pi*660*t)+.4*np.sin(2*np.pi*880*t))*.13*envelope
 elif kind=='tape_hiss':a=rng.normal(0,.016,len(t))
 else:raise QualityError('No generic transition fallback; select an event source or import licensed Foley.')
 distance=cue.get('distance','near');gain={'near':1,'medium':.55,'far':.25}.get(distance,.5)
 if distance=='far':a=np.convolve(a,np.ones(24)/24,mode='same')
 stereo=np.stack([a*gain*.9,a*gain],axis=1);_write_wave(path,stereo)
 return {'engine':'REDPAD original synthetic practical-sound approximation','output_kind':cue['kind'],'cost_usd':0,'paid_api':False,'rights_scope':'publication','rights_url':'https://github.com/REDPADSTUDIO-UX/blank-app','rights_note':'Original synthesized sound; no third-party recording. Timing and perspective need editorial review.'}

def technical_qa(path,target):
 info=media_info(path)
 p=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-vf','blackdetect=d=0.5:pix_th=0.04,freezedetect=n=-55dB:d=2','-af','silencedetect=n=-60dB:d=2','-f','null','-'],capture_output=True,text=True,timeout=max(120,int(target)*3))
 video=next((s for s in info['streams'] if s['codec_type']=='video'),{})
 audio_raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-f','f32le','-ac','2','-ar','24000','-'],timeout=max(120,int(target)*2))
 samples=np.frombuffer(audio_raw,dtype='<f4');peak=float(np.max(np.abs(samples))) if len(samples) else 0
 clipped=int(np.sum(np.abs(samples)>=1.0))
 events={key:[x for x in p.stderr.splitlines() if token in x] for key,token in [('black','black_start:'),('freeze','freeze_start:'),('silence','silence_start:')]}
 return {'passed':p.returncode==0 and abs(info['seconds']-target)<.25 and video.get('width',0)>=1280 and video.get('height',0)>=720 and any(s['codec_type']=='audio' for s in info['streams']) and not any(events.values()) and clipped==0,'audio_peak':peak,'clipped_samples':clipped,'decode_exit':p.returncode,'duration':info['seconds'],'width':video.get('width'),'height':video.get('height'),'events':events,'sha256':file_hash(path),'note':'Intentional silence/static holds require explicit editorial reconciliation; they are not silently ignored.'}

def _stem(path,assets,entries,total,kind):
 rate=48000;mix=np.zeros((int(total*rate),2),dtype=np.float32)
 for asset in assets:
  if asset['kind'] not in kind:continue
  comp={'voice':'line','music':'music','foley':'sfx','ambience':'sfx','designed':'sfx'}[asset['kind']];p=entries[comp+'/'+asset['target']]['payload']
  if comp=='line':start=float(p['start']);end=float(p['end'])
  elif comp=='music':start=float(p['start']);end=float(p['end'])
  else:
   start=float(p['global_start']);end=start+float(p['duration'])
  if not 0<=start<end<=total+.01:raise QualityError('Audio event lies outside the approved timeline.')
  effect=['-af','highpass=f=250,lowpass=f=3400'] if comp=='line' and p.get('speaker','').endswith('echo') else []
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',asset['path'],*effect,'-f','f32le','-ar',str(rate),'-ac','2','-'],timeout=90)
  a=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
  if len(a)/rate>end-start+.15:raise QualityError('An audio take exceeds its performance slot; select/rewrite it instead of silently speeding or truncating it.')
  if comp=='line':
   active=a[np.abs(a)>.002];rms=float(np.sqrt(np.mean(active*active))) if len(active) else 0
   if rms==0:raise QualityError('Dialogue take contains no audible activity.')
   a=a*min(4.,.14/rms,.88/max(float(np.max(np.abs(a))),1e-9))
  at=round(start*rate);n=min(len(a),len(mix)-at);level=float(p.get('level_db',0 if comp=='line' else -8))
  if not -45<=level<=6:raise QualityError('Audio level outside supported range.')
  mix[at:at+n]+=a[:n]*10**(level/20)
 _write_wave(path,mix)

def render(studio:Studio,pid):
 gates=studio.gates(pid)
 if not gates['full_render']['passed']:raise QualityError('Full render blocked: '+'; '.join(gates['full_render']['issues'][:8]))
 source=studio.source_hash(pid);entries=studio.entries(pid);assets=[a for a in studio.assets(pid) if a['current'] and a['selected']]
 shots=sorted([(k,v['payload']) for k,v in entries.items() if k.startswith('shot/')],key=lambda x:x[1]['order'])
 if len({a['sha'] for a in assets if a['kind']=='shot'})!=len(shots):raise QualityError('Repeated footage is not permitted as unique shot coverage.')
 assembly=digest({'source':source,'assets':{a['id']:a['sha'] for a in assets}});folder=studio.root/pid/'renders'/assembly;folder.mkdir(parents=True,exist_ok=True);parts=[];clock=0
 for key,p in shots:
  target=key.split('/')[1];a=next(a for a in assets if a['kind']=='shot' and a['target']==target);info=a['metadata']['probe']
  if abs(info['seconds']-p['seconds'])>.25:raise QualityError('Shot '+target+' does not match its planned duration. Split or regenerate coverage; no stretching fallback.')
  dest=folder/(target+'.mp4')
  if not dest.exists():ff(['-i',a['path'],'-an','-vf','scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p','-t',p['seconds'],'-c:v','libx264','-preset','veryfast','-crf','20',dest])
  parts.append(dest);clock+=p['seconds']
 for name,kinds in [('dialogue',{'voice'}),('music',{'music'}),('foley',{'foley','designed'}),('ambience',{'ambience'})]:_stem(folder/(name+'.wav'),assets,entries,clock,kinds)
 subs=[]
 for _,r in sorted(((k,r) for k,r in entries.items() if k.startswith('line/')),key=lambda kv:kv[1]['payload']['start']):
  p=r['payload'];subs.append(f'{len(subs)+1}\n{timestamp(p["start"])} --> {timestamp(p["end"])}\n{p["text"]}\n')
 (folder/'subtitles.bn.srt').write_text('\n'.join(subs));(folder/'concat.txt').write_text(''.join("file '"+p.name+"'\n" for p in parts))
 final=folder/'episode.mp4'
 ff(['-f','concat','-safe','0','-i',folder/'concat.txt','-i',folder/'dialogue.wav','-i',folder/'music.wav','-i',folder/'foley.wav','-i',folder/'ambience.wav','-i',folder/'subtitles.bn.srt','-filter_complex','[1:a]asplit=2[d][sc];[2:a][sc]sidechaincompress=threshold=0.025:ratio=3:attack=40:release=500[m];[d][m][3:a][4:a]amix=inputs=4:normalize=0,alimiter=limit=0.92[a]','-map','0:v','-map','[a]','-map','5:0','-t',clock,'-c:v','copy','-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=ben','-movflags','+faststart',final],timeout=max(240,int(clock)*3))
 qa=technical_qa(final,clock);(folder/'technical_qa.json').write_text(canonical(qa))
 if studio.source_hash(pid)!=source:raise QualityError('Project changed during finishing; final registration blocked.')
 manifest={'assets':{a['id']:a['sha'] for a in assets},'source_hash':source,'cost_usd':0,'neural_video':True,'minimum_source_height':min(next(s['height'] for s in a['metadata']['probe']['streams'] if s['codec_type']=='video') for a in assets if a['kind']=='shot')}
 with studio.tx() as db:db.execute('INSERT OR REPLACE INTO dq_exports VALUES (?,?,?,?,?,?,?)',(pid,str(final),file_hash(final),source,canonical(manifest),canonical(qa),__import__('time').time()))
 # A render is reviewable, never automatically approved or published.
 if not qa['passed']:raise QualityError('Final technical QA failed; diagnostic output preserved but not approved.')
 return final


def local_cue(studio:Studio,pid,component,target):
 if component not in ('music','sfx'):raise QualityError('Only local sound cues are composed here.')
 p=studio.entries(pid)[component+'/'+target]['payload'];kind='music' if component=='music' else p['kind']
 existing=next((a for a in studio.assets(pid) if a['kind']==kind and a['target']==target and a['current']),None)
 if existing:return existing['id']
 folder=studio.root/pid/'local_sound';folder.mkdir(exist_ok=True);path=folder/(target+'_'+studio.fingerprint(pid,component+'/'+target)[:12]+'.wav')
 metadata=compose_cue(path,p) if component=='music' else sound_event(path,p)
 return studio.register_asset(pid,kind,target,path,metadata)
