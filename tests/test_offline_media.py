import io,json,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from redpad_pipeline.agents import AgentError
from redpad_pipeline.agent_media_bridge import MediaBlocked
from redpad_pipeline import offline_media as media

class OfflineMediaTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  p=patch('redpad_pipeline.offline_media.MODEL_ROOT',self.root/'models');p.start();self.addCleanup(p.stop)
  self.sidecar=self.root/'project/agent_control.sqlite3';self.sidecar.parent.mkdir()
 def request(self,engine='wan-local',mode='text_to_video'):
  w,h,f={'wan-local':(1280,704,81),'ltx-local':(704,480,49),'local-svd':(1024,576,25)}[engine]
  return dict(mode=mode,prompt='An adult fictional person slowly closes a door.',width=w,height=h,frames=f,fps=media.CATALOG[engine]['fps'],steps=media.CATALOG[engine]['steps'],seed=42,reference='references/test.png')
 def checkpoint(self,engine):
  folder=media.MODEL_ROOT/engine;folder.mkdir(parents=True);(folder/'model_index.json').write_text('{}');(folder/'model.safetensors').write_bytes(b'fixture, not actual model weights')
  return media.approve_checkpoint(engine,'test owner','unit fixture license attestation',True)
 def image(self):
  path=self.sidecar.parent/'agent_media/references/test.png';path.parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(64,64),'blue').save(path);return path
 def test_three_engines_have_explicit_capabilities_and_all_block_without_weights(self):
  self.assertEqual(set(media.CATALOG),{'wan-local','ltx-local','local-svd'})
  for key in media.CATALOG:
   status=media.preflight(key);self.assertFalse(status['ready']);self.assertFalse(status['actual_inference_verified'])
   with self.assertRaises(MediaBlocked):media.generate(key,self.request(key,'image_to_video' if key=='local-svd' else 'text_to_video'),self.sidecar)
  self.assertFalse((self.sidecar.parent/'agent_media').exists())
 def test_native_shapes_and_unsupported_conditioning_rejected(self):
  for key in media.CATALOG:media.validate_request(key,self.request(key,'image_to_video' if key=='local-svd' else 'text_to_video'))
  for r in [dict(self.request(),frames=80),dict(self.request(),identity_lock=True),dict(self.request(),fps=30),dict(self.request(),seed=True)]:
   with self.assertRaises(AgentError):media.validate_request('wan-local',r)
  with self.assertRaises(AgentError):media.validate_request('local-svd',self.request('local-svd'))
 def test_checkpoint_hashes_detect_mutation_no_unreviewed_terms(self):
  self.checkpoint('wan-local');self.assertTrue(media.approved('wan-local',True)['approved'])
  (media.MODEL_ROOT/'wan-local/model.safetensors').write_bytes(b'changed')
  with self.assertRaises(MediaBlocked):media.approved('wan-local',True)
  with self.assertRaises(AgentError):media.approve_checkpoint('wan-local','owner','terms',False)
 def test_checkpoint_cannot_load_remote_code_pickle_or_symlinks(self):
  self.checkpoint('ltx-local');folder=media.MODEL_ROOT/'ltx-local'
  (folder/'bad.py').write_text('raise Exception()')
  with self.assertRaises(AgentError):media.checkpoint_manifest(folder)
  (folder/'bad.py').unlink();(folder/'link').symlink_to('/tmp')
  with self.assertRaises(AgentError):media.checkpoint_manifest(folder)
 def test_reference_review_is_hash_bound_and_path_isolated(self):
  p=self.image()
  with self.assertRaises(MediaBlocked):media.check_reference(self.sidecar,'references/test.png')
  media.approve_reference(self.sidecar,'references/test.png','test reader','fictional test fixture',True)
  self.assertEqual(media.check_reference(self.sidecar,'references/test.png'),p)
  p.write_bytes(b'changed')
  with self.assertRaises(MediaBlocked):media.check_reference(self.sidecar,'references/test.png')
  with self.assertRaises(AgentError):media.media_path(self.sidecar,'../production.sqlite3')
 def test_timeout_retains_failed_job_and_no_actual_generation_claim(self):
  self.checkpoint('wan-local')
  import subprocess
  with patch('redpad_pipeline.offline_media.preflight',return_value={'ready':True}),patch('redpad_pipeline.offline_media.subprocess.run',side_effect=subprocess.TimeoutExpired('owned worker',30)):
   with self.assertRaises(MediaBlocked):media.generate('wan-local',self.request(),self.sidecar,timeout=30)
  p=next((self.sidecar.parent/'agent_media/offline_jobs').glob('*/evidence.json'));r=json.loads(p.read_text())
  self.assertEqual(r['state'],'failed');self.assertFalse(r['actual_generation']);self.assertFalse(r['technical_output_validated'])
  self.assertTrue(p.with_name('request.json').exists())
 def test_recovery_requires_stopped_worker_and_preserves_outputs(self):
  job=self.sidecar.parent/'agent_media/offline_jobs'/('a'*32);job.mkdir(parents=True);(job/'evidence.json').write_text(json.dumps({'state':'running'}));(job/'partial.bin').write_bytes(b'partial')
  with self.assertRaises(AgentError):media.recover_stopped_job(self.sidecar,'a'*32)
  self.assertEqual(media.recover_stopped_job(self.sidecar,'a'*32,True)['state'],'interrupted');self.assertTrue((job/'partial.bin').exists())
 def test_worker_calls_only_fixed_local_pipelines_and_preserves_frame_counts(self):
  from redpad_pipeline.offline_worker import run
  for key in ('wan-local','ltx-local','local-svd'):
   called={}
   class Pipeline:
    vae=types.SimpleNamespace(enable_tiling=lambda:None);unet=types.SimpleNamespace(enable_forward_chunking=lambda:None)
    @classmethod
    def from_pretrained(cls,path,**kw):called['load']=kw;called['path']=path;return cls()
    def enable_model_cpu_offload(self):called['offload']=True
    def __call__(self,**kw):called['args']=kw;return types.SimpleNamespace(frames=[[Image.new('RGB',(64,64))]*kw['num_frames']])
   mode='image_to_video' if key=='local-svd' else 'text_to_video';r=self.request(key,mode)
   fake_torch=types.SimpleNamespace(float16='fp16',bfloat16='bf16',Generator=lambda **kw:types.SimpleNamespace(manual_seed=lambda n:n))
   diff=types.SimpleNamespace(**{spec['image_pipeline']:Pipeline for spec in media.CATALOG.values()},WanPipeline=Pipeline,LTXPipeline=Pipeline)
   output=self.root/(key+'.mp4');image=self.image() if mode=='image_to_video' else None
   job=self.root/(key+'.json');job.write_text(json.dumps({'engine':key,'request':r,'checkpoint':str(self.root/'fixture'),'reference':str(image) if image else None,'output':str(output)}))
   def export(frames,path,fps):called['fps']=fps;Path(path).write_bytes(b'codec fixture, not AI media')
   with patch.dict('sys.modules',{'torch':fake_torch,'diffusers':diff,'diffusers.utils':types.SimpleNamespace(export_to_video=export)}):run(job)
   self.assertTrue(called['load']['local_files_only']);self.assertFalse(called['load']['trust_remote_code']);self.assertEqual(called['args']['num_frames'],r['frames'])
   self.assertTrue(json.loads(job.with_name('worker_state.json').read_text())['inference_completed'])
   self.assertTrue(called['offload']);self.assertNotIn('prompt',called['args']) if key=='local-svd' else self.assertIn('prompt',called['args'])
 def test_offline_speech_no_backend_no_cloning_no_remote_fallback(self):
  from redpad_pipeline.offline_speech import preflight,synthesize
  with patch('redpad_pipeline.offline_speech.MODEL_ROOT',self.root/'absent'):
   self.assertFalse(preflight()['ready'])
   with self.assertRaises(MediaBlocked):synthesize({'text':'একটি বাংলা বাক্য','preset':'Arjun'},self.sidecar)
  self.assertFalse((self.sidecar.parent/'agent_media/offline_speech').exists())
 def test_speech_worker_uses_local_tokenizers_and_rejects_silence(self):
  import numpy as np,wave
  from contextlib import nullcontext
  from redpad_pipeline.speech_worker import run
  calls=[];signal=.1*np.sin(np.arange(3200)*2*np.pi*220/16000)
  class Model:
   config=types.SimpleNamespace(sampling_rate=16000)
   @classmethod
   def from_pretrained(cls,path,**kw):calls.append(('model',path,kw));return cls()
   def to(self,device):self.device=device;return self
   def generate(self,**kw):return types.SimpleNamespace(cpu=lambda:types.SimpleNamespace(numpy=lambda:signal))
  class Tokenizer:
   @classmethod
   def from_pretrained(cls,path,**kw):calls.append(('tokenizer',path,kw));return cls()
   def __call__(self,*a,**kw):return types.SimpleNamespace(input_ids=[1],attention_mask=[1])
  job=self.root/'speech-job.json';output=self.root/'speech-fixture.wav';job.write_text(json.dumps({'checkpoint':str(self.root/'model'),'text':'বাংলা পরীক্ষার বাক্য','description':'Arjun speaks calmly','output':str(output)}))
  seeds=[]
  modules={'torch':types.SimpleNamespace(inference_mode=nullcontext,manual_seed=seeds.append),'parler_tts':types.SimpleNamespace(ParlerTTSForConditionalGeneration=Model),'transformers':types.SimpleNamespace(AutoTokenizer=Tokenizer)}
  with patch.dict('sys.modules',modules):
   run(job)
   with wave.open(str(output),'rb') as f:self.assertEqual((f.getframerate(),f.getnchannels()),(16000,1))
   signal=np.zeros(3200)
   with self.assertRaises(ValueError):run(job)
  self.assertTrue(all(c[2]['local_files_only'] for c in calls))
  self.assertEqual(seeds,[42,42])
  self.assertTrue(any(c[1].endswith('description_tokenizer') for c in calls))
 def test_completed_inference_separate_from_failed_codec_validation(self):
  self.checkpoint('wan-local')
  def mocked_worker(command,**kwargs):
   job=Path(command[-1]);r=json.loads(job.read_text());job.with_name('worker_state.json').write_text(json.dumps({'inference_completed':True}));Path(r['output']).write_bytes(b'invalid codec unit fixture')
  with patch('redpad_pipeline.offline_media.preflight',return_value={'ready':True}),patch('redpad_pipeline.offline_media.subprocess.run',side_effect=mocked_worker),patch('redpad_pipeline.offline_media.inspect_output',side_effect=AgentError('bad codec')):
   with self.assertRaises(MediaBlocked):media.generate('wan-local',self.request(),self.sidecar)
  r=json.loads(next((self.sidecar.parent/'agent_media/offline_jobs').glob('*/evidence.json')).read_text())
  self.assertTrue(r['actual_inference_verified']);self.assertFalse(r['technical_output_validated']);self.assertFalse(r['cinematic_quality_reviewed'])
