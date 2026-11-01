"""Normalize dialogue activity without cutting pauses or regenerating voices."""
import json,wave,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from redpad_pipeline.drama_animation import run
P=Path(__file__).parent;R=P.parents[1]/'redpad_media'/'drama'/'ghor117_ep01'
def polish():
 measurements=[]
 for s in json.loads((P/'plan.json').read_text())['shots']:
  if not s['text']:continue
  f=R/(s['id']+'.wav')
  with wave.open(str(f),'rb') as w:rate=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
  active=a[np.abs(a)>.004];rms=float(np.sqrt(np.mean(active*active)));gain=min(.11/rms,.83/max(np.max(np.abs(a)),1e-9))
  a=np.clip(a*gain,-.85,.85)
  with wave.open(str(f),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes((a*32767).astype('<i2').tobytes())
  clip=R/(s['id']+'.mp4');tmp=R/(s['id']+'.polish.mp4')
  run(['-i',clip,'-i',f,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-t',7.5,tmp]);tmp.replace(clip)
  measurements.append(dict(shot=s['id'],gain=round(gain,3),active_rms_before=round(rms,4)))
 (R/'dialogue_normalization.json').write_text(json.dumps(measurements,indent=2))
if __name__=='__main__':polish()
