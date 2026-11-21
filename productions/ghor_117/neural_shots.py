"""Optional anonymous Wan2.2 motion enhancement. Stop on first quota/unknown result.
Each input is an original CPU-rendered consistent puppet reference, never unrelated stock.
"""
import json,sys,shutil
from pathlib import Path
from redpad_pipeline.drama_animation import frame,probe
from redpad_pipeline.remote_gpu import generate,GPUError
P=Path(__file__).parent;R=P.parents[1]/'redpad_media'/'drama'/'ghor117_ep01';R.mkdir(parents=True,exist_ok=True)
# Dialogue/reaction coverage first; do not submit title or repeat a pending request.
plan=json.loads((P/'plan.json').read_text())
for idx in [7,18,6,2,8,10,16,19,20,24,26,28,30,32,33,34,35,36,38,39,4,5,9,11,12,13,14,15,17,21,22,27,0,1,23,25,29,31,37]:
 s=plan['shots'][idx];prefix=R/(s['id']+'.neural');out=prefix.with_suffix('.neural.mp4');marker=R/(s['id']+'.neural.json')
 if out.exists():continue
 if marker.exists():print('Existing uncertain/failed shot: stopping',s['id'],flush=True);break
 source=R/(s['id']+'.reference.png');frame(s,1.8,.2).save(source)
 motion={'fear':'He recoils slightly, eyes widen, he turns his head toward the locked door.','sad':'The person lowers their gaze and breathes quietly, small natural hand gesture.','smile':'The person smiles gently and gestures while talking.','phone':'The person holds their phone and speaks softly, listening between phrases.','concern':'The woman listens anxiously on the phone, her eyebrows lift.','warn':'The older woman warns gently, raising her hand.'}.get(s['action'],'The characters interact with restrained expressive gestures, small head turns and natural breathing, speaking to each other.')
 prompt='Keep the exact same illustrated Bangladeshi characters, clothing, room and 2D graphic novel style. '+motion+' Stable identity, subtle camera push. No new objects, no letters or text changes.'
 marker.write_text(json.dumps(dict(stage='submitting',cost=0,input=str(source.name))))
 try:
  made=generate(source.read_bytes(),prompt,R/'neural_jobs');shutil.copyfile(made,out)
  marker.write_text(json.dumps(dict(stage='complete',model='Wan2.2 FP8 AOTI',provider='anonymous Hugging Face ZeroGPU',seconds=float(probe(out)['format']['duration']),cost=0)))
  print('NEURAL SHOT',s['id'],flush=True)
 except GPUError as e:
  marker.write_text(json.dumps(dict(stage='blocked',error=str(e),cost=0)));print('STOP',s['id'],str(e),flush=True);break
