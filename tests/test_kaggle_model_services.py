"""Software gates only. No mocked result is real GPU/model evidence."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AGENTS,AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.shared_model_services import SharedServices,SharedWriter,catalog,profile,resource_preflight,validate_request
from redpad_pipeline.kaggle_benchmark import KaggleLab,cases,technical_validation
from redpad_pipeline.kaggle_runtime import probe,tensor_canary
from redpad_pipeline.screenwriter import LocalUnavailable
from tests.test_agent_foundation import fixture

class KaggleServices(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.s=AgentStore(self.root/'agent_control.sqlite3');self.shared=SharedServices(self.s);self.lab=KaggleLab(self.s)
 def fake_install(self):
  # Tiny manual metadata fixture, NOT an actual model and NEVER inferred.
  p=copy.deepcopy(profile('qwen35_9'));folder=self.root/'manual-checkpoint';folder.mkdir()
  raw=b'MANUAL UNIT FIXTURE NOT MODEL WEIGHTS';(folder/'part.safetensors').write_bytes(raw)
  (folder/'config.json').write_text('{}');(folder/'redpad_model_origin.json').write_text(json.dumps({'repo':p['repo'],'revision':p['revision']}))
  p['auxiliary_files']=[{'path':'config.json','bytes':2,'git_blob_sha1':hashlib.sha1(b'blob 2\0{}').hexdigest()}]
  p['selected_weight_files']=[{'path':'part.safetensors','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}]
  return p,folder
 def test_exact_21_agents_18_pinned_candidates_no_winners(self):
  c=catalog();self.assertEqual(set(c['agents']),set(AGENTS));self.assertEqual(len(c['profiles']),18)
  for role,r in c['agents'].items():
   self.assertIsNone(r['validated_selection']);self.assertEqual(r['status'],'IN PROGRESS' if role=='director' else 'Blocked — With Exact Reason');self.assertEqual(r['research_status'],'Research Shortlisted')
   self.assertIn(r['primary_candidate'],c['profiles'])
  for p in c['profiles'].values():self.assertEqual(len(p['revision']),40);self.assertFalse(p['download_approved']);self.assertFalse(p['inference_verified'])
  variants=c['evaluation_variants']
  self.assertEqual(variants['qwen35_9_approved_gguf']['base_profile'],'qwen35_9')
  self.assertIsNone(variants['gemma3_12_hosted_exploratory']['exact_weight_revision'])
  self.assertTrue(all(not v['production_approved'] for v in variants.values()))
 def test_distinct_candidate_versions_are_never_silently_aliased(self):
  self.assertEqual(profile('ltx25')['repo'],'Lightricks/LTX-2.5');self.assertEqual(profile('ltx25')['adapter'],'contract_only')
  self.assertEqual(profile('wan_animate2')['repo'],'Wan-AI/Wan2.2-Animate-2-14B')
  self.assertNotEqual(profile('ace15')['repo'],'ACE-Step/ACE-Step-v1-3.5B')
  with self.assertRaises(AgentError):profile('ltx')
 def test_download_recipes_exclude_mutually_exclusive_weight_variants(self):
  p=profile('flux2_klein4');self.assertNotIn('flux-2-klein-4b.safetensors',[f['path'] for f in p['selected_weight_files']])
  self.assertTrue(all('.fp16.safetensors' in x['path'] for x in profile('svd_xt')['selected_weight_files']))
  self.assertLess(profile('ltx25')['selected_weight_bytes'],100*10**9)
 def test_resources_do_not_pool_two_t4_cards_or_claim_verified_fit(self):
  p=profile('qwen35_27');runtime={'gpus':[dict(total_bytes=16*2**30,free_bytes=15*2**30)]*2,'host_memory':{'MemAvailable_bytes':64*2**30},'disk_free_bytes':200*2**30}
  self.assertFalse(resource_preflight(p,runtime)['eligible_for_canary_only'])
  runtime['gpus']=[dict(total_bytes=24*2**30,free_bytes=23*2**30)]
  result=resource_preflight(p,runtime);self.assertTrue(result['eligible_for_canary_only']);self.assertFalse(result['runtime_compatible_verified'])
 def test_cgroup_ram_and_disk_headroom_block_before_download(self):
  r={'gpus':[dict(total_bytes=24*2**30,free_bytes=23*2**30)],'host_memory':{'MemAvailable_bytes':128*2**30},'cgroup_available_bytes':4*2**30,'disk_free_bytes':10*2**30}
  out=resource_preflight(profile('qwen35_9'),r,download=True);self.assertGreaterEqual(len(out['blockers']),2)
 def test_no_credentials_or_quota_are_inferred_from_runtime(self):
  r=probe(self.root)
  self.assertIsNone(r['remaining_gpu_quota_hours']);self.assertIsNone(r['kaggle_account_connected']);self.assertFalse(r['free_tier_verified'])
  self.assertNotIn('KAGGLE_KEY',json.dumps(r));self.assertIn('libraries',r)
 def test_no_gpu_activation_tensor_canary_restricted_to_kaggle(self):
  with patch('redpad_pipeline.kaggle_runtime.Path.is_dir',return_value=False):
   with self.assertRaises(ValueError):tensor_canary()
 def test_install_approval_is_explicit_exact_and_change_invalidates(self):
  p,folder=self.fake_install()
  with patch('redpad_pipeline.shared_model_services.profile',return_value=p):
   with self.assertRaises(AgentError):self.shared.approve_install('qwen35_9',folder,'Owner fixture','License fixture')
   record=self.shared.approve_install('qwen35_9',folder,'Owner fixture','License fixture',True)
   self.assertFalse(record['inference_verified']);self.assertFalse(record['production_approved'])
   self.shared.installed('qwen35_9',True)
   (folder/'part.safetensors').write_bytes(b'changed')
   with self.assertRaises(LocalUnavailable):self.shared.installed('qwen35_9',True)
 def test_tokenizer_config_hash_tamper_is_rejected_before_approval(self):
  p,folder=self.fake_install();(folder/'config.json').write_text('[]')
  with patch('redpad_pipeline.shared_model_services.profile',return_value=p):
   with self.assertRaises(AgentError):self.shared.approve_install('qwen35_9',folder,'Owner fixture','License fixture',True)
 def test_origin_and_official_weight_hash_mismatch_rejected(self):
  p,folder=self.fake_install();(folder/'redpad_model_origin.json').write_text('{}')
  with patch('redpad_pipeline.shared_model_services.profile',return_value=p):
   with self.assertRaises(AgentError):self.shared.approve_install('qwen35_9',folder,'Owner fixture','License fixture',True)
 def test_same_approved_install_can_serve_multiple_research_roles(self):
  p,folder=self.fake_install()
  with patch('redpad_pipeline.shared_model_services.profile',return_value=p):
   self.shared.approve_install('qwen35_9',folder,'Owner fixture','License fixture',True)
   for role in ('script','qc','youtube'):self.shared.configure(role,'qwen35_9')
   self.assertEqual(self.shared.policy('script')['profile'],self.shared.policy('qc')['profile'])
   with self.assertRaises(AgentError):self.shared.configure('script','qwen35_9',fallback='gemma3_12')
   with self.assertRaises(AgentError):self.shared.configure('script','qwen35_9',capability='image')
 def test_production_route_cannot_be_replaced_by_research_preference(self):
  with patch('redpad_pipeline.model_routing.ModelRoutes.policy',return_value={'mode':'production'}):
   with self.assertRaisesRegex(AgentError,'Production route is locked'):self.shared.configure('script','qwen35_9')
 def test_service_snapshot_is_pinned_not_changed_by_later_preference(self):
  with self.s.tx() as db:db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('script',json.dumps({'role':'script','profile':'qwen35_9','capability':'text'})))
  first=self.shared.snapshot('run','script')
  with self.s.tx() as db:db.execute('UPDATE shared_dev_routes SET payload=?',(json.dumps({'profile':'gemma3_12'}),))
  self.assertEqual(self.shared.snapshot('run','script'),first)
 def test_engine_shared_route_blocks_without_weights_and_never_falls_back(self):
  engine=Engine(self.s)
  with self.s.tx() as db:db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('story',json.dumps({'role':'story','profile':'qwen35_27','capability':'text'})))
  rid=engine.enqueue('story',fixture('story'),mode='local')
  with patch('redpad_pipeline.agent_engine.LocalWriter.__init__',side_effect=AssertionError('Must not downgrade or call old fallback')):
   self.assertEqual(engine.execute(rid),'Blocked')
  self.assertFalse(self.s.outputs())
 def test_writing_limits_and_unsupported_media_controls_rejected(self):
  r=dict(system='x',prompt='বাংলা',max_new_tokens=100,seed=117,temperature=.7,context_tokens=4096,thinking=False)
  validate_request(profile('qwen35_9'),r)
  with self.assertRaises(AgentError):validate_request(profile('qwen35_9'),dict(r,max_new_tokens=99999))
  image=dict(prompt='Original fictional adult',width=512,height=512,steps=9,seed=117,references=[{'id':'test','version':1}])
  with self.assertRaises(AgentError):validate_request(profile('z_image_turbo'),image)
  with self.assertRaises(AgentError):validate_request(profile('wan_animate2'),{})
 def test_planning_is_idempotent_uses_identical_unseen_cases_settings(self):
  ids=self.lab.plan(['qwen35_9','gemma3_12'],['natural_dialogue','clean_abstention'],'Compare restrained Bangladeshi dialogue and grounded abstention with identical new tasks.')
  again=self.lab.plan(['qwen35_9','gemma3_12'],['natural_dialogue','clean_abstention'],'Compare restrained Bangladeshi dialogue and grounded abstention with identical new tasks.')
  self.assertEqual(ids,again);self.assertEqual(len(self.lab.jobs()),4)
  jobs=[json.loads(j['payload']) for j in self.lab.jobs()]
  self.assertEqual(jobs[0]['case'],jobs[2]['case']);self.assertEqual(jobs[0]['settings'],jobs[2]['settings'])
 def test_unknown_kaggle_account_quota_stops_before_worker(self):
  ids=self.lab.plan(['qwen35_9'],['premise'],'Test a new stronger candidate for original causal Bengali premise quality.')
  with patch.object(self.lab.services,'execute',side_effect=AssertionError('GPU forbidden without quota')):
   with self.assertRaisesRegex(AgentError,'unverified'):self.lab.run_one(ids[0])
  self.assertEqual(self.lab.jobs()[0]['state'],'Planned — Not Executed')
 def test_no_model_canary_or_settings_fabricated_on_cpu(self):
  with self.assertRaises(AgentError):self.lab.verify_runtime()
  with self.assertRaises((AgentError,LocalUnavailable)):self.lab.model_canary('qwen35_9')
  with self.assertRaises(AgentError):self.lab.record_settings({},'Fixture reviewer','https://www.kaggle.com/code/fixture/test',True)
 def test_director_clean_control_and_quotes_have_objective_calibration(self):
  clean=next(c for c in cases()['cases'] if c['id']=='clean_abstention')
  out=technical_validation(clean,json.dumps({'findings':[]}),{'truncated':False})
  self.assertEqual(out['false_positive_findings'],0);self.assertIsNone(out['artistic_scores'])
  bad={'findings':[{'quote':'Made up dialogue','code':'prop_state','category':'contract','decision':'revise'}]}
  result=technical_validation(clean,json.dumps(bad),{'truncated':False});self.assertEqual(result['unsupported_quotes'],1);self.assertEqual(result['false_positive_findings'],1)
 def test_technical_schema_success_does_not_certify_creative_quality(self):
  c=next(c for c in cases()['cases'] if c['id']=='premise')
  result=technical_validation(c,'{"premises":[]}',{'truncated':False})
  self.assertTrue(result['technical_pass']);self.assertFalse(result['professional_accepted']);self.assertIsNone(result['artistic_scores'])
  self.assertFalse(technical_validation(c,'partial text',{'truncated':True})['technical_pass'])
 def test_empty_review_packet_has_no_fabricated_samples_or_selected_primary(self):
  packet,key=self.lab.blind_packet();self.assertEqual(packet['samples'],[]);self.assertEqual(key,{})
  self.assertFalse(packet['human_review_completed']);self.assertFalse(self.lab.comparison()['winner_selected'])
 def test_persistence_gate_cannot_accept_nonmatching_or_temporary_sample(self):
  f=self.root/'fixture_raw.txt';f.write_text('SOFTWARE FIXTURE ONLY')
  with self.assertRaises(AgentError):self.lab.confirm_canary_export('qwen35_9',f,'https://www.kaggle.com/code/fixture/test',True)
  with self.assertRaises(AgentError):self.lab.confirm_canary_export('qwen35_9',f,'https://www.kaggle.com/code/fixture/test?scriptVersionId=1',True)
 def test_no_provisional_selection_from_shortlist_or_software_results(self):
  with self.assertRaises(AgentError):self.lab.comparative_sources('story',['qwen35_27','gemma3_12'])
  with self.assertRaises(AgentError):self.lab.comparative_sources('casting',['qwen35_27','flux2_klein4'])
  with self.assertRaises(AgentError):self.lab.record_editorial_comparison('story',['qwen35_27','gemma3_12'],{},True)
  with self.assertRaises(AgentError):self.lab.select_provisional('story','missing','qwen35_27','This must not select a model without real comparative evidence.',True)

 def test_selection_guard_unit_fixture_never_promotes_production_and_rejects_weak_acceptance(self):
  # Mocked comparison plumbing only: this is NOT real model output or human review.
  models=['qwen35_27','gemma3_12'];required=[c for c in cases()['cases'] if 'story' in c['roles']]
  table={(m,c['id']):{'job':m+'-'+c['id'],'raw':'SOFTWARE FIXTURE ONLY','raw_sha256':hashlib.sha256(b'SOFTWARE FIXTURE ONLY').hexdigest(),'revision':profile(m)['revision']} for m in models for c in required}
  dimensions={d for c in required for d in c['dimensions']}
  review={'reviewer_type':'human','independent':True,'qualified_for_role':True,'reviewer':'SOFTWARE FIXTURE NOT ACTUAL PERSON','expertise':'UNIT TEST ONLY','models':{m:{d:{'score':4,'accepted':True,'finding':'Unit fixture checks gate plumbing only.','evidence':[{'job':m+'-'+required[0]['id'],'quote':'SOFTWARE FIXTURE ONLY'}]} for d in dimensions} for m in models}}
  with patch.object(self.lab,'comparative_sources',return_value=(required,table)):
   review['models']['qwen35_27'][next(iter(dimensions))]['accepted']=False
   bad=self.lab.record_editorial_comparison('story',models,review,True)
   with self.assertRaises(AgentError):self.lab.select_provisional('story',bad,'qwen35_27','Manual unit-fixture preference; no genuine acceptance exists.',True)
   review['models']['qwen35_27'][next(iter(dimensions))]['accepted']=True
   id=self.lab.record_editorial_comparison('story',models,review,True)
   selected=self.lab.select_provisional('story',id,'qwen35_27','Manual unit-fixture preference; no genuine acceptance exists.',True)
   self.assertFalse(selected['production_approved']);self.assertFalse(selected['professional_ready']);self.assertIsNone(self.shared.policy('story'))

 def test_retry_cannot_switch_from_legacy_to_new_shared_preference(self):
  self.assertEqual(self.shared.choose_backend('legacy-bound','story'),'ollama')
  with self.s.tx() as db:db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('story',json.dumps({'role':'story','profile':'qwen35_27','capability':'text'})))
  self.assertEqual(self.shared.choose_backend('legacy-bound','story'),'ollama')
  self.assertEqual(self.shared.choose_backend('new-shared','story'),'shared')
 def test_shared_retry_stays_bound_when_production_policy_changes(self):
  from redpad_pipeline.model_routing import ModelRoutes
  ModelRoutes(self.s)
  with self.s.tx() as db:db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('script',json.dumps({'role':'script','profile':'qwen35_9','capability':'text'})))
  self.assertEqual(self.shared.choose_backend('shared-bound','script'),'shared')
  with self.s.tx() as db:db.execute('INSERT INTO specialist_model_routes VALUES (?,?)',('script',json.dumps({'role':'script','mode':'production','models':[]})))
  self.assertEqual(self.shared.choose_backend('shared-bound','script'),'shared')
  self.assertEqual(self.shared.choose_backend('new-production','script'),'ollama')
  with self.assertRaises(AgentError):self.shared.choose_backend('shared-bound','qc')
 def test_old_ollama_run_snapshot_wins_over_later_shared_configuration(self):
  from redpad_pipeline.model_routing import ModelRoutes
  ModelRoutes(self.s)
  with self.s.tx() as db:
   db.execute('INSERT INTO model_route_snapshots VALUES (?,?)',('old-run',json.dumps({'role':'script','mode':'research','models':[]})))
   db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('script',json.dumps({'role':'script','profile':'qwen35_9','capability':'text'})))
  self.assertEqual(self.shared.choose_backend('old-run','script'),'ollama')
 def test_engine_retry_uses_same_shared_backend_after_policy_change(self):
  from redpad_pipeline.model_routing import ModelRoutes
  engine=Engine(self.s);routes=ModelRoutes(self.s)
  with self.s.tx() as db:db.execute('INSERT INTO shared_dev_routes VALUES (?,?)',('story',json.dumps({'role':'story','profile':'qwen35_27','capability':'text'})))
  rid=engine.enqueue('story',fixture('story'),mode='local')
  self.assertEqual(engine.execute(rid),'Blocked')
  with self.s.tx() as db:db.execute('INSERT INTO specialist_model_routes VALUES (?,?)',('story',json.dumps({'role':'story','mode':'production','models':[]})))
  engine.retry(rid)
  with patch('redpad_pipeline.agent_engine.RoutedWriter.__init__',side_effect=AssertionError('A retry must not change backend')):
   self.assertEqual(engine.execute(rid),'Blocked')
  self.assertFalse(self.s.outputs())

 def test_notebook_private_gpu_off_no_downloads_no_endpoint(self):
  root=Path(__file__).resolve().parents[1]/'experiments/kaggle_phase3'
  m=json.loads((root/'kernel-metadata.template.json').read_text());self.assertTrue(m['is_private']);self.assertFalse(m['enable_gpu']);self.assertFalse(m['enable_internet'])
  n=json.loads((root/'runtime_check.ipynb').read_text());code='\n'.join(''.join(c['source']) for c in n['cells'] if c['cell_type']=='code')
  self.assertNotIn('snapshot_download',code);self.assertNotIn('ngrok',code);self.assertIn('RUN_AUTHORIZED_TENSOR_CANARY=False',code)

if __name__=='__main__':unittest.main()
