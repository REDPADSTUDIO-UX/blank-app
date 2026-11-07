"""Authored production and real codec fixtures; zero artistic/model claims."""
import copy,json,shutil,sqlite3,subprocess,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
import numpy as np
from redpad_pipeline.agents import AgentError
from redpad_pipeline.studio_program import StudioProgram
from redpad_pipeline.pre_gpu_project import run_fixture,screenplay,bible,departments
from redpad_pipeline.story_bridge import StoryBridge
from redpad_pipeline.production_execution import ProductionOps
from redpad_pipeline.delivery import Delivery
from redpad_pipeline.grounded_review import review,calibrate
from redpad_pipeline.creative import digest
from redpad_pipeline import offline_audio

class PreGpuCompletion(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=tempfile.TemporaryDirectory()
  with patch('redpad_pipeline.studio_program.PROGRAM_ROOT',Path(cls.base.name)):
   cls.template=StudioProgram('fixture');cls.evidence=run_fixture(cls.template)
 @classmethod
 def tearDownClass(cls):cls.base.cleanup()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);(root/'fixture').mkdir()
  with sqlite3.connect(self.template.store.path) as source,sqlite3.connect(root/'fixture/agent_control.sqlite3') as dest:source.backup(dest)
  self.patcher=patch('redpad_pipeline.studio_program.PROGRAM_ROOT',root);self.patcher.start();self.addCleanup(self.patcher.stop)
  self.p=StudioProgram('fixture');self.ops=ProductionOps(self.p);self.e=copy.deepcopy(self.evidence)
 def approve(self,rid):
  self.assertEqual(self.p.engine.execute(rid),'Awaiting QC');run=next(r for r in self.p.engine.runs() if r['id']==rid)
  tid=run['task'];t=next(t for t in self.p.store.tasks() if t['id']==tid)
  self.p.store.review(tid,t['revision'],'Recommend','SIMULATED fixture QC','qc');self.p.store.review(tid,t['revision'],'Approve','SIMULATED fixture owner','owner');return tid
 def test_shared_original_project_routes_all_twenty_departments(self):
  self.assertEqual(len(self.e['agents_exercised']),20);self.assertEqual(len(self.e['log']),54)
  self.assertEqual(self.e['new_real_model_inference'],0);self.assertEqual(self.e['new_human_reviews'],0)
  self.assertEqual(len(self.e['shot_packet']['identities']),2);self.assertEqual(len(self.e['voice_packet']['lines']),7)
  self.assertFalse(self.p.summary()['production_ready']);self.assertTrue(all(x['provenance']=='software' for x in self.e['log']))
 def test_staged_local_provider_is_simulation_and_failed_state_is_retained(self):
  p=StudioProgram('local-fixture');p.create('ফিরতি টিকিট',bible()['premise'],30,180);bridge=StoryBridge(p)
  rid=bridge.queue('bible');self.assertEqual(p.engine.execute(rid,complete=lambda *_:{'records':[bible()]}),'Awaiting QC')
  body=json.loads(json.loads(p.store.outputs()[0]['payload'])['summary']);self.assertEqual(body['provenance'],'simulation');self.assertFalse(body['model_inference'])
  with p.store.tx() as db:self.assertEqual(db.execute('SELECT count(*) FROM creative_model_attempts').fetchone()[0],1)
 def test_bounded_scene_assembly_preserves_original_beats_and_blocks_tampering(self):
  from redpad_pipeline.episode_scenes import EpisodeScenes
  from redpad_pipeline.screenwriter import WritingError
  bridge=StoryBridge(self.p);draft=EpisodeScenes(self.p,1);script=screenplay()
  draft.create({'story':bridge._linked('story'),'director':bridge._linked('director_story')},[{k:v for k,v in s.items() if k!='beats'} for s in script['scenes']],script['characters'],['s1','s3'])
  for s in script['scenes']:
   result={'heading':s['heading'],'beats':s['beats']}
   r=draft.run_scene(s['id'],model='synthetic-provider-not-installed',complete=lambda *_,result=result:result)
   self.assertEqual(r['status'],'validated_stage');self.assertEqual(r['provenance'],'simulation')
  rid=draft.compile();tid=self.approve(rid);self.assertEqual(self.p.current_output(tid)['artifact']['scenes'][0]['beats'],script['scenes'][0]['beats'])
  path=draft.folder/'scene_s1.json';r=json.loads(path.read_text());r['result']['beats'][0]['text']='tampered';path.write_text(json.dumps(r))
  with self.assertRaises(AgentError):draft.compile()
 def test_source_fanout_is_checked_once_per_transaction_and_cycles_fail(self):
  statements=[]
  with self.p.store.tx() as db:
   db.set_trace_callback(statements.append);t=self.p.store._task(db,self.e['tasks']['youtube']);self.p.store._current(db,t)
  self.assertLess(sum('SELECT * FROM tasks' in s for s in statements),200)
  tid=self.e['script_task']
  with self.p.store.tx() as db:db.execute('UPDATE tasks SET refs=? WHERE id=?',(json.dumps([{'id':tid,'revision':1}]),tid))
  with self.assertRaises(AgentError):self.p.current_output(tid)
 def test_story_stage_cannot_overwrite_or_skip_approved_predecessor(self):
  bridge=StoryBridge(self.p);before=len(self.p.engine.runs());changed=bible();changed['initial_state']['event']='different'
  with self.assertRaises(AgentError):bridge.queue('bible',records=[changed])
  self.assertEqual(len(self.p.engine.runs()),before)
  tid=bridge._linked('bridge:outline:1');self.p.store.review(tid,1,'Request revision','Fixture changes episode1 state','owner')
  with self.assertRaises(AgentError):bridge._linked('bridge:outline:2')
  with self.assertRaises(AgentError):self.ops.packet(self.e['shot_packet']['id'])
 def test_targeted_arc_revision_preserves_locked_rows_and_needs_owner_request(self):
  bridge=StoryBridge(self.p);tid=bridge._linked('bridge:arcs');rows=copy.deepcopy(self.p.current_output(tid)['artifact']['records']);rows[0]['want']='প্রাপ্তবয়স্ক সিদ্ধান্তে সাহায্য নেওয়া'
  with self.assertRaises(AgentError):bridge.queue('arcs',records=rows,task=tid,targets=[rows[0]['id']])
  self.p.store.review(tid,1,'Request revision','SIMULATED target arc-nira only','owner')
  wrong=copy.deepcopy(rows);wrong[1]['want']='unauthorized change'
  with self.assertRaises(AgentError):bridge.queue('arcs',records=wrong,task=tid,targets=[rows[0]['id']])
  rid=bridge.queue('arcs',records=rows,task=tid,targets=[rows[0]['id']]);self.assertEqual(self.p.engine.execute(rid),'Awaiting QC')
  self.assertEqual(next(t['revision'] for t in self.p.store.tasks() if t['id']==tid),2)
 def test_global_compute_lease_blocks_other_threads_and_releases_after_failure(self):
  from redpad_pipeline.resource_guard import serialized,ResourceBusy
  from concurrent.futures import ThreadPoolExecutor
  @serialized
  def nested():return 'nested allowed in same owned pipeline'
  @serialized
  def held():
   self.assertEqual(nested(),'nested allowed in same owned pipeline')
   with ThreadPoolExecutor(max_workers=1) as pool:
    with self.assertRaises(ResourceBusy):pool.submit(nested).result()
   raise ValueError('synthetic worker failure')
  with self.assertRaises(ValueError):held()
  self.assertEqual(nested(),'nested allowed in same owned pipeline')
 def test_shot_rejects_unsupported_conditioning_and_wrong_native_timing(self):
  r={'mode':'text_to_video','prompt':'Original fictional action','width':832,'height':480,'frames':17,'fps':24,'steps':50,'seed':42}
  with self.assertRaises(AgentError):self.ops.queue_video(self.e['shot_packet']['id'],'wan-local',r,['identity_lock'])
  with self.assertRaises(AgentError):self.ops.queue_video(self.e['shot_packet']['id'],'wan-local',r)
  self.assertFalse(self.e['shot_packet']['technical_requirements']['physics_simulation'])
 def test_voice_uses_exact_screenplay_and_explicit_supported_presets(self):
  packet=self.ops.packet(self.e['voice_packet']['id']);line=packet['lines'][0]
  self.assertEqual(line['request']['preset'],'Aditi');self.assertEqual(line['original'],screenplay()['scenes'][0]['beats'][1]['text'])
  rid=self.ops.queue_speech(packet['id'],line['id']);self.assertEqual(rid,self.ops.queue_speech(packet['id'],line['id']))
  from redpad_pipeline.specialist_adapters import LocalSpeechAdapter
  request=departments(screenplay())['voice']['records'][0]
  with patch('redpad_pipeline.offline_speech.synthesize',return_value={}) as synth:
   with self.assertRaises(AgentError):LocalSpeechAdapter().synthesize(request,self.p.store.path)
   LocalSpeechAdapter().synthesize(request,self.p.store.path,preset='Aditi',style='warm')
   self.assertEqual(synth.call_args.args[0]['text'],request['text']);self.assertNotIn('pauses',synth.call_args.args[0])
 def test_grounded_criticism_retains_false_quotes_and_calibrates_controls(self):
  source=screenplay();target=source['scenes'][2];quote=target['beats'][1]['text']
  finding=dict(id='f1',target='s3',quote=quote,observation='Manual test observation',interpretation='Unverified interpretation',category='subjective',severity='warning',confidence=.5,decision='revise',target_agent='script',instruction='Manual test revision proposal only')
  good=review(source,[finding],'director');self.assertFalse(good['owner_approval']);self.assertIn('s1',good['unassessed_targets'])
  fake=dict(finding,quote='এই কথা মূল দৃশ্যে নেই।');bad=review(source,[fake],'qc');self.assertEqual(len(bad['unsupported']),1)
  ann={'annotator':'manually authored software control','provenance':'manually_authored_fixture','source_sha256':digest(source),'defects':[]}
  self.assertEqual(calibrate(good,ann)['fp'],1);self.assertEqual(calibrate(review(source,[],'qc'),ann)['fp'],0)
 def test_thirty_episode_director_review_uses_bounded_calls_then_software_compilation(self):
  with self.p.store.tx() as db:db.execute("DELETE FROM studio_links WHERE label='director_story'")
  for n in range(1,31):
   rid=self.p.queue_creative('director_story');run=next(r for r in self.p.engine.runs() if r['id']==rid)
   self.assertTrue(json.loads(run['inputs'])['grounded_review_v1']);self.assertLess(len(run['inputs']),2000)
   finding=dict(id='f'+str(n),target='episode_'+str(n),quote='',observation='Synthetic clear control',interpretation='No artistic judgment inferred',category='contract',severity='info',confidence=.5,decision='clear',target_agent='story',instruction='No automatic rewrite')
   self.assertEqual(self.p.engine.execute(rid,complete=lambda *_,f=finding:{'findings':[f]}),'Awaiting QC')
   self.p.store.review(run['task'],1,'Recommend','SIMULATED control QC','qc');self.p.store.review(run['task'],1,'Approve','SIMULATED owner control','owner')
  rid=self.p.queue_creative('director_story');run=next(r for r in self.p.engine.runs() if r['id']==rid)
  self.assertEqual(run['mode'],'software');self.assertEqual(self.p.engine.execute(rid),'Awaiting QC')
  out=next(o for o in self.p.store.outputs() if o['task']==run['task']);body=json.loads(json.loads(out['payload'])['summary'])
  self.assertEqual(body['artifact_type'],'grounded_season_review');self.assertEqual(len(body['artifact']['episode_reports']),30);self.assertFalse(body['model_inference']);self.assertTrue(body['artifact']['specialist_visual_direction_pending'])
 def test_real_codec_import_edl_receipts_render_and_tamper_guard(self):
  root=self.p.root/'agent_media/imports';root.mkdir(parents=True)
  video=root/'codec-fixture.mp4';audio=root/'signal-fixture.wav'
  subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=c=gray:s=256x144:r=8:d=2','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(video)],check=True)
  with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(np.zeros(16000,dtype='<i2').tobytes())
  delivery=Delivery(self.p)
  v=delivery.register('imports/codec-fixture.mp4','SIMULATED test owner','Original synthetic codec fixture; not neural film',True,origin='manually_authored_fixture')
  a=delivery.register('imports/signal-fixture.wav','SIMULATED test owner','Original silence signal fixture; not acting',True,origin='manually_authored_fixture')
  rows=self.p.current_output(self.e['tasks']['editing'])['artifact']['records'];bindings={r['shot']:{'video':v,'audio':a} for r in rows}
  rid=delivery.queue_edl(self.e['tasks']['editing'],bindings,{r['shot']:2 for r in rows});tid=self.approve(rid)
  receipts={'imports/codec-fixture.mp4':v,'imports/signal-fixture.wav':a}
  with self.assertRaises(AgentError):delivery.render(tid,receipts)
  with self.assertRaises(AgentError):delivery.render(tid,receipts,evaluation_only='true')
  result=delivery.render(tid,receipts,evaluation_only=True);self.assertEqual(result['metadata']['state'],'technical_output_validated')
  self.assertAlmostEqual(result['metadata']['inspection']['duration'],18,delta=.2);self.assertFalse(result['metadata']['professional_quality_verified'])
  audio.write_bytes(b'changed');self.assertRaises(AgentError,delivery.asset,a)
 def test_feedback_is_versioned_attributed_and_never_approval_or_training(self):
  tid=self.e['script_task'];quote=screenplay()['scenes'][0]['beats'][1]['text']
  r=self.ops.feedback(tid,1,'SIMULATED reviewer','test fixture only','creative',{'quote':quote},'Synthetic correction','correct',provenance='simulation',dataset_consent=True)
  self.assertFalse(r['grants_approval']);export=self.ops.feedback_export();self.assertFalse(export['future_dataset_candidates']);self.assertFalse(export['weight_training_performed'])
  with self.assertRaises(AgentError):self.ops.feedback(tid,1,'fixture','fixture','creative',{'quote':'invented absent quotation'},'Correction','reject',provenance='simulation')
 def test_receipt_bound_audio_mix_uses_real_samples_without_claiming_speech_quality(self):
  from redpad_pipeline.audio_post import mix
  root=self.p.root/'agent_media/imports';root.mkdir(parents=True);path=root/'synthetic.wav'
  values=(np.sin(np.arange(8000)*2*np.pi*440/8000)*3000).astype('<i2')
  with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(values.tobytes())
  d=Delivery(self.p);id=d.register('imports/synthetic.wav','SIMULATED owner','Tone fixture, no real voice or music claim',True,origin='manually_authored_fixture')
  def source_task(role,records):
   old=self.e['tasks'][role];data={'specialist_v1':True,'project':'ফিরতি টিকিট — synthetic signal mix test','records':records,'sources':{role:{'$from':old,'path':['artifact']}},'base':None,'targets':[]}
   return self.approve(self.p.engine.enqueue(role,data,[old],mode='software'))
  line=copy.deepcopy(departments(screenplay())['voice']['records'][0]);line.update(start=0,seconds=1,audio_receipt=id)
  voice=source_task('voice',[line]);cue=copy.deepcopy(departments(screenplay())['music']['records'][0]);cue.update(asset='imports/synthetic.wav',license='original',kind='music',start=0,seconds=1)
  music=source_task('music',[cue]);r=mix(self.p,music,voice,{'imports/synthetic.wav':id},1)
  self.assertEqual(r['metadata']['state'],'technical_output_validated');self.assertFalse(r['metadata']['listening_review_completed']);self.assertFalse(r['metadata']['actual_neural_inference']);self.assertTrue(r['metadata']['evaluation_only'])
  rid=self.p.engine.enqueue('music',{'operation':'mix_dialogue_cues'},[music,voice],mode='media')
  with patch('redpad_pipeline.agent_engine.execute_media',return_value=r):tid=self.approve(rid)
  derived=d.register(r['path'],'SIMULATED owner','Derived tone fixture remains a fixture',True,run_id=rid)
  self.assertEqual(d.asset(derived)['origin'],'manually_authored_fixture')
 def test_audio_backends_block_without_weights_and_reject_unimplemented_controls(self):
  for engine in offline_audio.ENGINES:
   self.assertFalse(offline_audio.preflight(engine)['ready'])
   with self.assertRaises(AgentError):offline_audio.validate(engine,{'prompt':'x','seconds':1,'steps':50,'seed':1,'lyrics':'unsupported'})
   from redpad_pipeline.agent_media_bridge import MediaBlocked
   with self.assertRaises(MediaBlocked):offline_audio.generate(engine,{'prompt':'Original cue','seconds':1,'steps':50,'seed':1},self.p.store.path)
 def test_visual_critic_blocks_without_weights_and_frame_extraction_is_not_inference(self):
  from redpad_pipeline import offline_vision
  from PIL import Image
  root=self.p.root/'agent_media';root.mkdir(parents=True);Image.new('RGB',(32,32),'gray').save(root/'synthetic.png')
  rid=self.p.engine.enqueue('director',{'operation':'offline_vision','request':{'images':['synthetic.png'],'question':'Inspect this synthetic transport fixture; not creative evidence.','seed':42}},mode='media')
  self.assertEqual(self.p.engine.execute(rid),'Blocked');self.assertFalse(offline_vision.preflight()['ready'])
  video=root/'synthetic.mp4';subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=c=gray:s=256x144:r=8:d=2','-c:v','libx264','-threads','1',str(video)],check=True)
  receipt=offline_vision.frames(self.p.store.path,'synthetic.mp4',[.2,1.2]);self.assertEqual(len(receipt['frames']),2);self.assertFalse(receipt['model_inference']);self.assertFalse(receipt['human_review_completed'])
 def test_inference_worker_limit_and_explicit_stopped_recovery(self):
  from tests.test_agent_foundation import fixture
  old=self.p.engine.enqueue('story',fixture('story'),mode='local');new=self.p.engine.enqueue('story',fixture('story'),mode='local')
  with self.p.store.tx() as db:db.execute("UPDATE agent_runs SET state='Running' WHERE id=?",(old,))
  with patch('redpad_pipeline.agent_engine.LocalWriter') as infer:self.assertEqual(self.p.engine.execute(new),'Blocked');infer.assert_not_called()
  recovered=self.p.recover(old,True);self.p.engine.retry(recovered)
  self.assertEqual(next(r['state'] for r in self.p.engine.runs() if r['id']==recovered),'Ready for Input')
 def test_silent_shots_have_no_fabricated_subtitles(self):
  from redpad_pipeline.specialists import prepare
  data=departments(screenplay())['editing'];self.assertTrue(all(r['subtitle']=='' for r in data['records']))
  prepare('editing',data)
 def test_preparation_ui_renders_without_models_reviews_or_media_calls(self):
  from streamlit.testing.v1 import AppTest
  script='from redpad_pipeline.studio_program import StudioProgram\nfrom redpad_pipeline.pre_gpu_ui import story_bridge,preparation,deliveries,feedback,scene_drafting\np=StudioProgram("fixture")\nstory_bridge(p)\nscene_drafting(p)\npreparation(p)\ndeliveries(p)\nfeedback(p)'
  with patch('redpad_pipeline.agent_engine.Engine.execute') as execute,patch('redpad_pipeline.offline_audio.generate') as generate:
   at=AppTest.from_string(script).run(timeout=20);self.assertFalse(at.exception);execute.assert_not_called();generate.assert_not_called()
