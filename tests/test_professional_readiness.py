"""Synthetic wire/media fixtures test the evidence gates, not creative capability.
No reviewer, model inference or professional acceptance is real in this module.
"""
import copy,hashlib,json,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
import numpy as np
from redpad_pipeline.agents import AgentStore,AgentError,encode
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.model_routing import ModelRoutes
from redpad_pipeline.professional_readiness import ProfessionalLab,suite,models,audit,file_sha,trial_context
from redpad_pipeline.audio_evaluation import measure
from redpad_pipeline import offline_image
from tests.test_agent_foundation import fixture
from tests.test_cpu_creative import response

TAG='qwen3.5:9b-q4_K_M';DIGEST='sha256:'+'a'*64

class ProfessionalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.engine=Engine(self.store);self.lab=ProfessionalLab(self.store)
  self.patcher=patch('redpad_pipeline.model_routing.inventory',return_value={TAG:DIGEST});self.patcher.start();self.addCleanup(self.patcher.stop)
  ModelRoutes(self.store).approve_installed(TAG,DIGEST,'Synthetic license/owner fixture, not a real approval','synthetic test',True)
  for role in ('story','script','director','qc'):self.store.configure(role,TAG)
 def plan(self,role='story',max_calls=4,**extra):
  return self.lab.plan(role,['writer9'],'A different candidate may reduce grounded causality errors in unseen Bengali scenes.','Independent reviewer compares causal continuity and natural dialogue.',max_calls=max_calls,**extra)
 def sample(self,trial,index=1):
  data=fixture('story');data['project']='synthetic trial output '+str(index)
  rid=self.engine.enqueue('story',data,mode='local');self.lab.bind(trial['id'],rid,'sample'+str(index))
  wire={'model':TAG,'done':True,'done_reason':'stop','message':{'content':json.dumps(data,ensure_ascii=False)},'eval_count':12}
  with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),response(wire)]):self.assertEqual(self.engine.execute(rid),'Awaiting QC')
  return self.lab.capture_text(trial['id'],rid)
 def review(self,trial,samples):
  return {'reviewer_type':'human','reviewer':'synthetic reviewer fixture','expertise':'synthetic test-only qualifications','independent':True,'qualified_for_role':True,
          'modes':['text'],'examined_samples':[s['id'] for s in samples],
          'criteria':{k:{'passed':True,'finding':'Synthetic gate test, not an artistic judgment','evidence':[{'sample':samples[0]['id'],'quote':'synthetic'}]} for k in trial['case']['criteria']}}
 def test_audit_never_promotes_software_or_knowledge_to_intelligence(self):
  data=audit();self.assertEqual(len(data['agents']),20);self.assertEqual(data['professional_ready_count'],0)
  self.assertFalse(any(r['production_capable'] or r['professional_intelligence_verified'] for r in data['agents']))
  for role,spec in suite()['agents'].items():
   self.assertTrue(spec['expertise_required']);self.assertTrue(spec['minimum_counts'])
   self.assertTrue(all(m in models() for m in spec['candidate_models']))
 def test_weak_four_b_requires_actual_fix_and_cannot_reset_identical_budget(self):
  args=('story',['legacy4'],'Test an observed state bug after a demonstrable code fix.','Reviewer verifies that tracked states change causally.')
  with self.assertRaises(AgentError):self.lab.plan(*args)
  from redpad_pipeline.professional_readiness import ROOT
  fix={'path':'redpad_pipeline/series_ledger.py','sha256':file_sha(ROOT/'redpad_pipeline/series_ledger.py')}
  self.lab.plan(*args,change_type='state_fix',fix_ref=fix,max_calls=2)
  with self.assertRaises(AgentError):self.lab.plan(*args,change_type='state_fix',fix_ref=fix,max_calls=2)
  with self.assertRaises(AgentError):self.lab.plan(*args,change_type='state_fix',fix_ref=dict(fix,sha256='bad'),max_calls=2)
 def test_binding_must_precede_inference_and_requires_approved_candidate(self):
  trial=self.plan();rid=self.engine.enqueue('story',fixture('story'),mode='local')
  with self.assertRaises(AgentError):self.lab.capture_text(trial['id'],rid)
  ModelRoutes(self.store).revoke(TAG)
  with self.assertRaises(AgentError):self.lab.bind(trial['id'],rid,'one')
 def test_injected_simulation_is_not_real_inference(self):
  trial=self.plan();data=fixture('story');rid=self.engine.enqueue('story',data,mode='local')
  self.lab.bind(trial['id'],rid,'one');self.assertEqual(self.engine.execute(rid,complete=lambda *_:data),'Awaiting QC')
  with self.assertRaises(AgentError):self.lab.capture_text(trial['id'],rid)
 def test_duplicate_run_budget_and_retry_cannot_trigger_extra_call(self):
  trial=self.plan(max_calls=1);rid=self.engine.enqueue('story',fixture('story'),mode='local');self.lab.bind(trial['id'],rid,'one')
  other=self.engine.enqueue('story',fixture('story'),mode='local')
  with self.assertRaises(AgentError):self.lab.bind(trial['id'],other,'two')
  with patch('urllib.request.OpenerDirector.open',side_effect=OSError('Synthetic transport outage')):self.assertEqual(self.engine.execute(rid),'Blocked')
  self.engine.retry(rid)
  with patch('redpad_pipeline.agent_engine.LocalWriter') as transport:
   self.assertEqual(self.engine.execute(rid),'Failed');transport.assert_not_called()
 def test_real_wire_evidence_not_schema_pass_controls_readiness(self):
  trial=self.plan();sample=self.sample(trial)
  self.assertTrue(sample['technical_pass']);self.assertFalse(self.lab.status(trial['id'])['expert_accepted_this_benchmark_only'])
  self.assertEqual(self.lab.capture_text(trial['id'],sample['run']),sample)
  packet,key=self.lab.blind_packet(trial['id']);self.assertNotIn(TAG,json.dumps(packet));self.assertIn(TAG,json.dumps(key))
  self.assertFalse(packet['human_review_completed'])
 def test_actual_review_needs_minimum_samples_exact_quotes_and_qualification(self):
  trial=self.plan();samples=[self.sample(trial,n) for n in (1,2,3)];review=self.review(trial,samples)
  for change in ('model','independence','quote','qualification','examined'):
   bad=copy.deepcopy(review)
   if change=='model':bad['reviewer_type']='model'
   if change=='independence':bad['independent']=False
   if change=='qualification':bad['qualified_for_role']=False
   if change=='examined':bad['examined_samples']=[]
   if change=='quote':next(iter(bad['criteria'].values()))['evidence'][0]['quote']='invented source excerpt'
   with self.assertRaises(AgentError,msg=change):self.lab.expert_review(trial['id'],bad,True)
  out=self.lab.expert_review(trial['id'],review,True)
  self.assertTrue(out['expert_accepted_this_benchmark_only']);self.assertFalse(out['professional_ready']);self.assertFalse(out['production_ready'])
  self.sample(trial,4);self.assertFalse(self.lab.status(trial['id'])['expert_accepted_this_benchmark_only'])
 def test_source_revision_or_raw_tampering_invalidates_review(self):
  trial=self.plan();sample=self.sample(trial)
  with self.store.tx() as db:
   p=json.loads(db.execute('SELECT payload FROM professional_samples WHERE id=?',(sample['id'],)).fetchone()[0]);p['raw']='tampered'
   db.execute('UPDATE professional_samples SET payload=? WHERE id=?',(encode(p),sample['id']))
  with self.assertRaises(AgentError):self.lab.status(trial['id'])
 def test_own_revised_output_cannot_reuse_prior_expert_acceptance(self):
  trial=self.plan();sample=self.sample(trial)
  with self.store.tx() as db:db.execute('UPDATE tasks SET revision=revision+1 WHERE id=(SELECT task FROM agent_runs WHERE id=?)',(sample['run'],))
  with self.assertRaises(AgentError):self.lab.status(trial['id'])
 def test_missing_visual_media_cannot_be_replaced_by_a_review_claim(self):
  trial=self.plan('director');review={'reviewer_type':'human','reviewer':'synthetic','expertise':'synthetic','independent':True,'qualified_for_role':True,'modes':['text','visual'],'examined_samples':[],
         'criteria':{k:{'passed':True,'finding':'fixture','evidence':[{'sample':'invented','quote':'fake'}]} for k in trial['case']['criteria']}}
  with self.assertRaises(AgentError):self.lab.expert_review(trial['id'],review,True)
  self.assertFalse(self.lab.status(trial['id'])['representative_outputs_complete'])

class ImageAudioTests(unittest.TestCase):
 def test_owned_image_result_requires_marker_correct_pixels_and_unchanged_checkpoint(self):
  from PIL import Image
  from redpad_pipeline.agent_media_bridge import MediaBlocked
  with tempfile.TemporaryDirectory() as d:
   sidecar=Path(d)/'agent_control.sqlite3';approved={'manifest':{'sha256':'fixture-manifest','files':{}}}
   def worker(args,**kwargs):
    payload=Path(args[-1]);data=json.loads(payload.read_text())
    Image.new('RGB',(512,512),'gray').save(data['output'])
    payload.with_name('worker_state.json').write_text(json.dumps({'inference_completed':True}))
   request={'prompt':'Synthetic transport/codec fixture, not model generation','width':512,'height':512,'steps':30,'seed':42}
   with patch('redpad_pipeline.offline_image.preflight',return_value={'ready':True}),patch('redpad_pipeline.offline_image.approval',return_value=approved),patch('subprocess.run',side_effect=worker):
    result=offline_image.generate(request,sidecar)
   self.assertTrue(result['metadata']['technical_output_validated']);self.assertFalse(result['metadata']['visual_review_completed'])
   self.assertFalse(result['metadata']['identity_lock'])
   with patch('redpad_pipeline.offline_image.preflight',return_value={'ready':True}),patch('redpad_pipeline.offline_image.approval',side_effect=[approved,{'manifest':{'sha256':'changed'}}]),patch('subprocess.run',side_effect=worker):
    with self.assertRaises(MediaBlocked):offline_image.generate(request,sidecar)
   receipts=list((Path(d)/'agent_media/offline_images').glob('*/evidence.json'))
   self.assertEqual(len(receipts),2);self.assertEqual(sorted(json.loads(p.read_text())['state'] for p in receipts),['failed','technical_output_validated'])
 def test_image_worker_blocks_without_new_weights_and_rejects_fake_controls(self):
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.offline_image.MODEL_ROOT',Path(d)):
   self.assertFalse(offline_image.preflight()['ready'])
   valid={'prompt':'Original fictional Dhaka room','width':512,'height':512,'steps':30,'seed':42}
   from redpad_pipeline.agent_media_bridge import MediaBlocked
   with self.assertRaises(MediaBlocked):offline_image.generate(valid,Path(d)/'agent_control.sqlite3')
   with self.assertRaises(AgentError):offline_image.validate_request(dict(valid,identity_lock=True))
   with self.assertRaises(AgentError):offline_image.validate_request(dict(valid,width=True))
   self.assertFalse((Path(d)/'offline_images').exists())
 def test_actual_pcm_measurements_are_not_listening_approval(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'agent_media';root.mkdir();p=root/'fixture.wav'
   values=np.array([0,0,32767,-32768]*2000,dtype='<i2')
   with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(values.tobytes())
   r=measure('fixture.wav',Path(d)/'agent_control.sqlite3')
   self.assertEqual(r['duration_seconds'],1);self.assertEqual(r['sample_full_scale_fraction'],.5)
   self.assertFalse(r['listening_review_completed']);self.assertFalse(r['musicality_verified'])
   (root/'link.wav').symlink_to(p)
   with self.assertRaises(AgentError):measure('link.wav',Path(d)/'agent_control.sqlite3')
 def test_image_department_uses_owned_media_boundary(self):
  with tempfile.TemporaryDirectory() as d:
   engine=Engine(AgentStore(Path(d)/'agent_control.sqlite3'))
   rid=engine.enqueue('character',{'operation':'offline_image','request':{'prompt':'test','width':512,'height':512,'steps':30,'seed':42}},mode='media')
   with patch('redpad_pipeline.offline_image.preflight',return_value={'ready':False,'blockers':['No approved weights/GPU']}):
    self.assertEqual(engine.execute(rid),'Blocked')
 def test_new_readiness_ui_is_read_only_on_open(self):
  from streamlit.testing.v1 import AppTest
  with patch('redpad_pipeline.professional_readiness.ProfessionalLab.bind') as bind,patch('redpad_pipeline.agent_engine.Engine.execute') as infer:
   at=AppTest.from_string('from redpad_pipeline.professional_ui import show_summary\nshow_summary()').run()
   self.assertFalse(at.exception);bind.assert_not_called();infer.assert_not_called()
