"""Real codec/mixing contract using clearly labelled synthetic test patterns.
It does not establish photorealistic generation or actor performance.
"""
import tempfile,unittest,subprocess,wave,json
from pathlib import Path
from unittest.mock import patch
import numpy as np
from redpad_pipeline.drama_quality import Studio,file_hash,media_info
from redpad_pipeline.drama_finish import render

class FinishContractTests(unittest.TestCase):
 def test_real_codec_finish_preserves_layers_and_records_reviewable_export(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);s=Studio(root/'test.db',root/'media');pid=s.create('Synthetic codec contract fixture',16)
   folder=s.root/pid;folder.mkdir();entries={};assets=[]
   for i,color in enumerate(['white','red'],1):
    path=folder/f'fixture{i}.mp4';subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',f'testsrc2=size=320x180:rate=12:duration=8','-vf',f'hue=h={i*45}','-an','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',str(path)],check=True)
    key=f'Q{i}';entries['shot/'+key]={'payload':{'order':i,'seconds':8}}
    assets.append(dict(id=key,kind='shot',target=key,path=str(path),sha=file_hash(path),current=True,selected=True,metadata={'probe':media_info(path)}))
   rate=24000;t=np.arange(rate*2)/rate;a=np.sin(2*np.pi*220*t)*.08
   dialogue=folder/'codec_tone.wav'
   with wave.open(str(dialogue),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes((a*32767).astype('<i2').tobytes())
   entries['line/L']={'payload':{'start':1,'end':3,'text':'এটি শুধুই codec test; অভিনয়ের নমুনা নয়।'}}
   assets.append(dict(id='voice_fixture',kind='voice',target='L',path=str(dialogue),sha=file_hash(dialogue),current=True,selected=True,metadata={}))
   # A continuous quiet ambience prevents an unintended silent gap in this contract.
   ambience=folder/'ambience.wav';t=np.arange(rate*16)/rate;a=np.sin(2*np.pi*90*t)*.003
   with wave.open(str(ambience),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes((a*32767).astype('<i2').tobytes())
   entries['sfx/A']={'payload':{'global_start':0,'duration':16,'level_db':0}}
   assets.append(dict(id='ambience_fixture',kind='ambience',target='A',path=str(ambience),sha=file_hash(ambience),current=True,selected=True,metadata={}))
   # Bypass editorial gates only inside this codec test; production never does this.
   with patch.object(s,'gates',return_value={'full_render':{'passed':True}}),patch.object(s,'entries',return_value=entries),patch.object(s,'assets',return_value=assets),patch.object(s,'source_hash',return_value='fixture-source'):
    final=render(s,pid)
   self.assertTrue(final.is_file());info=media_info(final);self.assertAlmostEqual(info['seconds'],16,delta=.2)
   self.assertTrue(any(st['codec_type']=='subtitle' for st in info['streams']))
   for layer in ('dialogue','music','foley','ambience'):self.assertTrue((final.parent/(layer+'.wav')).is_file())
   with s.tx() as db:row=db.execute('SELECT qa,manifest FROM dq_exports WHERE project=?',(pid,)).fetchone()
   self.assertTrue(json.loads(row['qa'])['passed']);self.assertEqual(json.loads(row['manifest'])['minimum_source_height'],180)
   self.assertFalse(any(p.name=='episode.mp4' for p in root.glob('episode.mp4')))

if __name__=='__main__':unittest.main()
