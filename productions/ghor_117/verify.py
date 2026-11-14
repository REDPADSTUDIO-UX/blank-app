"""Acoustic/visual checks of the real output; no assertions of human-grade acting."""
import json,hashlib,subprocess,re,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from redpad_pipeline.drama_animation import probe
P=Path(__file__).parent;R=P.parents[1]/'redpad_media'/'drama'/'ghor117_ep01';F=R/'Ghor_117_EP01_Animated_Drama.mp4';plan=json.loads((P/'plan.json').read_text())
info=probe(F);seconds=float(info['format']['duration'])
cmd=['ffmpeg','-hide_banner','-i',str(F),'-vf','blackdetect=d=0.5:pix_th=0.04,freezedetect=n=-55dB:d=2.0','-af','silencedetect=n=-60dB:d=1.0','-f','null','-']
r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
(R/'qa_decode.log').write_text(r.stderr)
black=re.findall('black_start:[^\n]+',r.stderr);freeze=re.findall('freeze_start:[^\n]+',r.stderr);silent=re.findall('silence_start:[^\n]+',r.stderr)
# Check movement inside the actor's face/arms, independent of weather and camera labels.
movement=[];thumbs=[]
for i in (2,5,6,7,8,18,25,26,30,32,34,38,39):
 s=plan['shots'][i];frames=[]
 for off in (1.2,3.6):
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(s['start']+off),'-i',str(F),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
  arr=np.frombuffer(raw,dtype=np.uint8).reshape(720,1280,3);frames.append(arr)
 delta=float(np.abs(frames[0][130:570,530:900].astype(float)-frames[1][130:570,530:900].astype(float)).mean())
 movement.append(dict(shot=s['id'],actor_region_mean_difference=round(delta,3)))
 thumbs.append(Image.fromarray(frames[1]).resize((320,180)))
contact=Image.new('RGB',(1280,180*4),'#14212b')
for i,im in enumerate(thumbs):contact.paste(im,((i%4)*320,(i//4)*180))
contact.save(R/'qa_contact_sheet.jpg',quality=92)
voice=[]
for s in plan['shots']:
 if not s['text']:continue
 f=R/(s['id']+'.wav');raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-f','s16le','-ar','24000','-ac','1','-'])
 a=np.frombuffer(raw,dtype='<i2').astype(float)/32768
 voice.append(dict(shot=s['id'],rms_db=round(float(20*np.log10(max(np.sqrt(np.mean(a*a)),1e-9))),1),active_samples=int(np.sum(np.abs(a)>.008))))
passed=r.returncode==0 and abs(seconds-300)<.2 and not black and not freeze and not silent and all(x['actor_region_mean_difference']>.15 for x in movement) and all(x['active_samples']>5000 for x in voice)
report=dict(passed=passed,file=F.name,sha256=hashlib.sha256(F.read_bytes()).hexdigest(),seconds=seconds,resolution='1280x720',fps=12,shots=40,dialogue_shots=len(voice),full_decode_exit=r.returncode,black_events=black,freeze_events=freeze,silent_events=silent,actor_movement_checks=movement,voice_checks=voice,subtitle_tracks=[s.get('tags',{}) for s in info['streams'] if s['codec_type']=='subtitle'],animation='Original procedural articulated 2D character rigs',models_used_in_final=['Microsoft consumer Edge speech: bn-BD-PradeepNeural / bn-BD-NabanitaNeural'],neural_video_in_final=False,neural_tests='Anonymous Wan2.2 generated two puppet clips; excluded for prop continuity/text defects. A separate cassette motion test succeeded. Quota blocked further submissions.',cost_usd=0,paid_api_calls=0,original_render_changed=False,limits=['Limited synthetic vocal emotion; Hazera and Mina share one underlying female voice.','Mouth animation follows speech energy, not phoneme-accurate lip-sync.','Procedural 2D animation and synthesized score/foley, not photorealistic generated actors.','Automated QA verifies media integrity, movement and audio activity; it does not prove audience enjoyment or perfect Bangla pronunciation.'])
(R/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:report[k] for k in ['passed','seconds','resolution','sha256','black_events','freeze_events','silent_events']}))
if not passed:sys.exit(1)
