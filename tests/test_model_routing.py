import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError,AGENTS
from redpad_pipeline.screenwriter import WritingError,LocalUnavailable,LocalWriter
from redpad_pipeline.model_routing import ModelRoutes,RoutedWriter,local_id
from redpad_pipeline.model_benchmark import *
from redpad_pipeline.staged_writing import SYSTEM

A='alpha:4b';B='beta:3b';DA='sha256:'+'a'*64;DB='sha256:'+'b'*64

class RoutingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.routes=ModelRoutes(self.store)
  self.probe=patch('redpad_pipeline.model_routing.inventory',return_value={A:DA,B:DB});self.probe.start();self.addCleanup(self.probe.stop)
  for n,d in [(A,DA),(B,DB)]:self.routes.approve_installed(n,d,'Apache-2.0 test fixture','test owner',True)
 def test_local_identifiers_cloud_urls_and_mutable_digest_approval(self):
  for n in ['x-cloud:4b','https://api/remote:model','model','host:123/model']:
   with self.assertRaises(AgentError):local_id(n)
  with self.assertRaises(AgentError):self.routes.approve_installed(A,DB,'terms','owner',True)
  with self.assertRaises(AgentError):self.routes.approve_installed(A,DA,'terms','owner',False)
 def test_different_roles_and_production_fallback_each_need_acceptance(self):
  self.routes.configure('story',[A]);self.routes.configure('script',[B,A])
  self.assertEqual(self.store.status('story')['model'],A);self.assertEqual(self.store.status('script')['model'],B)
  self.assertEqual(len(AGENTS),20)
  for role in ['story','script','director','qc']:
   with self.assertRaises(AgentError):self.routes.configure(role,[A,B],'production')
 def test_route_snapshot_preserves_pending_run_policy(self):
  self.routes.configure('story',[A,B]);old=self.routes.snapshot('run1','story')
  self.routes.configure('story',[B]);self.assertEqual(self.routes.snapshot('run1','story'),old)
 def test_runtime_failure_only_fallback_logged_actual_model_and_partial(self):
  self.routes.configure('story',[A,B])
  class Fake:
   last_thinking_output='synthetic model trace'
   def __init__(self,model,**kw):self.model=model;self.last_raw_output='partial '+model;self.last_evidence={'model':model}
   def __call__(self,*args):
    if self.model==A:raise LocalUnavailable('runtime timeout')
    self.last_raw_output='{"ok":true}';return {'ok':True}
  w=RoutedWriter(self.routes,'run','story')
  with patch('redpad_pipeline.model_routing.LocalWriter',Fake):self.assertTrue(w('system','prompt')['ok'])
  self.assertEqual(w.model,B)
  self.assertEqual(w.last_evidence['untrusted_runtime_thinking'],'synthetic model trace')
  with self.store.tx() as db:rows=db.execute('SELECT model,raw,error FROM routed_model_attempts ORDER BY id').fetchall()
  self.assertEqual([r['model'] for r in rows],[A,B]);self.assertIn('partial',rows[0]['raw']);self.assertTrue(rows[0]['error'])
 def test_bad_schema_or_identity_never_falls_back(self):
  self.routes.configure('script',[A,B]);w=RoutedWriter(self.routes,'run','script')
  class Bad:
   last_raw_output='bad';last_evidence={}
   def __init__(self,*a,**k):pass
   def __call__(self,*a):raise WritingError('schema invalid')
  with patch('redpad_pipeline.model_routing.LocalWriter',Bad):
   with self.assertRaises(WritingError):w('system','prompt')
  self.assertEqual(w.model,A)
  with patch('redpad_pipeline.model_routing.inventory',return_value={A:DB,B:DB}):
   with self.assertRaises(WritingError):w('system','prompt')
  self.assertEqual(w.model,A)
 def test_revocation_blocks_snapshot_and_removes_acceptance(self):
  self.routes.configure('qc',[A,B]);w=RoutedWriter(self.routes,'run','qc');self.routes.revoke(A)
  with self.assertRaises(WritingError):w('system','prompt')
  self.assertEqual(w.model,A)
 def test_all_unavailable_stays_blocked_without_remote(self):
  self.routes.configure('director',[A,B]);w=RoutedWriter(self.routes,'run','director')
  with patch('redpad_pipeline.model_routing.inventory',side_effect=OSError('down')):
   with self.assertRaises(LocalUnavailable):w('system','prompt')
  with self.store.tx() as db:self.assertEqual(db.execute('SELECT count(*) FROM routed_model_attempts').fetchone()[0],2)
 def test_engine_routes_existing_workflows_and_logs_fallback_identity(self):
  from redpad_pipeline.agent_engine import Engine
  from tests.test_agent_foundation import fixture
  self.routes.configure('story',[A,B]);data=fixture('story')
  class Fake:
   def __init__(self,m,**kw):self.model=m;self.last_raw_output='';self.last_evidence={}
   def __call__(self,*a):
    if self.model==A:raise LocalUnavailable('down')
    self.last_raw_output=json.dumps(data);self.last_evidence={'model':B,'inference_completed':True};return data
  e=Engine(self.store);rid=e.enqueue('story',data,mode='local')
  with patch('redpad_pipeline.model_routing.LocalWriter',Fake):self.assertEqual(e.execute(rid),'Awaiting QC')
  result=json.loads(json.loads(self.store.outputs()[0]['payload'])['summary']);self.assertEqual(result['model'],B)
  self.assertEqual(e.runs()[0]['model'],B)
  with self.store.tx() as db:
   self.assertEqual(db.execute('SELECT model FROM local_inference_evidence').fetchone()[0],B)
  self.assertFalse(result.get('creative_quality_verified',False))
 def test_legacy_single_model_stays_without_route(self):
  self.store.configure('music','old:local');self.assertIsNone(self.routes.policy('music'))
  self.assertEqual(self.store.status('music')['model'],'old:local')
 def test_dashboard_reads_archived_failures_without_retrying_or_inference(self):
  from streamlit.testing.v1 import AppTest
  root=Path(self.tmp.name);folder=root/'verification/approved_comparison/fixture';folder.mkdir(parents=True)
  manifest={'model':A,'digest':DA,'suite_sha256':suite_hash(),'options':OPTIONS,'candidate':'fixture'}
  (folder/'manifest.json').write_text(json.dumps(manifest))
  for case in cases():(folder/(case['id']+'.json')).write_text(json.dumps({'raw':'','result':None,'status':'failed'}))
  code='from redpad_pipeline.model_routing_ui import show_model_routes\nfrom redpad_pipeline.agents import AgentStore\nshow_model_routes(AgentStore('+repr(str(root/'agent_control.sqlite3'))+'))'
  with patch('redpad_pipeline.model_routing_ui.ROOT',root),patch('redpad_pipeline.model_routing_ui.run_case') as infer:
   at=AppTest.from_string(code).run();self.assertFalse(at.exception);infer.assert_not_called()
   self.assertTrue(any('Archived failures' in c.value for c in at.caption))
   self.assertFalse(any('Reset failed' in b.label for b in at.button))
  self.assertEqual(json.loads((folder/'story.json').read_text())['status'],'failed')
  self.routes.revoke(A);self.routes.revoke(B)
  with patch('redpad_pipeline.model_routing_ui.ROOT',root),patch('redpad_pipeline.model_routing_ui.run_case') as infer:
   at=AppTest.from_string(code).run();self.assertFalse(at.exception);infer.assert_not_called()
   self.assertTrue(any('Archived failures' in c.value for c in at.caption))

class BenchmarkTests(unittest.TestCase):
 def fixture(self):
  c=cases()[0];result={k:'দামি সিদ্ধান্ত' for k in c['schema']['properties']};raw=json.dumps(result,ensure_ascii=False)
  request={'role':'story','data':c['data'],'task':c['task'],'schema':c['schema'],'dependencies':{},'model':A,'tokens':1024,'system':SYSTEM}
  r={'request':request,'request_sha256':digest(request),'provenance':'local_inference','status':'validated_stage','raw':raw,'result':result,
     'evidence':{'model':A,'model_digest':DA,'inference_completed':True,'raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),'options':{k:OPTIONS[k] for k in ('num_ctx','num_predict','temperature','seed')}}}
  benchmark={'model':A,'digest':DA,'suite_sha256':suite_hash(),'records':{'story':r}}
  human={'reviewer':'independent test reader','independent':True,'accepted':True,'ratings':{d:{'score':5,'evidence':'দামি সিদ্ধান্ত','finding':'test finding'} for d in DIMENSIONS}}
  return benchmark,human
 def test_role_selection_requires_real_integrity_and_human_evidence(self):
  b,h=self.fixture();check_selection('story',A,DA,b,h,True)
  for mutate in ['simulation','digest','raw','task','options','human','quote']:
   x,y=copy.deepcopy(b),copy.deepcopy(h)
   if mutate=='simulation':x['records']['story']['provenance']='simulation'
   if mutate=='digest':x['digest']=DB
   if mutate=='raw':x['records']['story']['raw']='{}'
   if mutate=='task':x['records']['story']['request']['task']='different'
   if mutate=='options':x['records']['story']['evidence']['options']['temperature']=.9
   if mutate=='human':y['independent']=False
   if mutate=='quote':y['ratings'][DIMENSIONS[0]]['evidence']='invented quote'
   with self.assertRaises(AgentError,msg=mutate):check_selection('story',A,DA,x,y,True)
 def test_suite_covers_all_dimensions_and_keeps_seed_truth_out_of_prompt(self):
  self.assertEqual(len(DIMENSIONS),10);self.assertEqual({c['role'] for c in cases()},{'story','script','director','qc'})
  self.assertNotIn('expected',json.dumps(cases()));self.assertEqual(len(cases()),6)
 def test_critic_ground_truth_accepts_logic_or_continuity_same_defect(self):
  for c in ('logic','continuity'):
   self.assertEqual(critic_findings({'findings':[{'line_id':'L3','category':c}]}),{('L3','prop_continuity')})
 def test_unapproved_candidate_never_calls_model(self):
  with tempfile.TemporaryDirectory() as d:
   s=AgentStore(Path(d)/'agent_control.sqlite3')
   with patch('redpad_pipeline.model_benchmark.StagedDraft') as provider:
    with self.assertRaises(AgentError):run_case(s,Path(d)/'benchmark',A,'story')
    provider.assert_not_called()
 def test_ui_open_cannot_download_select_or_infer(self):
  from streamlit.testing.v1 import AppTest
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.model_routing_ui.run_case') as execute:
   code='from redpad_pipeline.model_routing_ui import show_model_routes\nfrom redpad_pipeline.agents import AgentStore\nshow_model_routes(AgentStore('+repr(str(Path(d)/'agent_control.sqlite3'))+'))'
   at=AppTest.from_string(code).run();self.assertFalse(at.exception);execute.assert_not_called()

class AcceptedRouteTests(unittest.TestCase):
 setUp=RoutingTests.setUp
 def test_production_pins_accepted_thinking_mode_and_rejects_override(self):
  b,h=BenchmarkTests().fixture();b['think']=False
  r=b['records']['story'];r['request']['think']=False;r['request_sha256']=digest(r['request'])
  r['evidence']['thinking_control']={'requested':False}
  self.routes.accept('story',A,b,h,True)
  policy=self.routes.configure('story',[A],'production')
  self.assertIs(policy['models'][0]['think'],False)
  with self.assertRaises(AgentError):self.routes.configure('story',[A],'production',thinking_controls={A:True})
  writer=RoutedWriter(self.routes,'override','story',{'think':True})
  with patch('redpad_pipeline.model_routing.LocalWriter') as transport:
   with self.assertRaises(WritingError):writer('system','prompt')
   transport.assert_not_called()
  changed=copy.deepcopy(b);changed['records']['story']['evidence']['thinking_control']['requested']=True
  with self.assertRaises(AgentError):check_selection('story',A,DA,changed,h,True)
 def test_research_fallback_uses_its_own_pinned_thinking_mode(self):
  policy=self.routes.configure('script',[A,B],thinking_controls={A:False,B:True})
  self.assertIs(policy['models'][0]['think'],False)
  seen=[]
  class Fake:
   last_raw_output='fixture';last_evidence={}
   def __init__(self,model,**settings):self.model=model;seen.append((model,settings['think']))
   def __call__(self,*args):
    if self.model==A:raise LocalUnavailable('fixture transport failure')
    return {'ok':True}
  with patch('redpad_pipeline.model_routing.LocalWriter',Fake):
   self.assertTrue(RoutedWriter(self.routes,'thinking','script')('system','prompt')['ok'])
  self.assertEqual(seen,[(A,False),(B,True)])
  for bad in ({A:0},{'unknown:local':False},[]):
   with self.assertRaises(AgentError):self.routes.configure('story',[A],thinking_controls=bad)
 # Reuse the approval fixture; test one positive path without running a model.
 def test_accepted_primary_still_requires_separate_accepted_fallback(self):
  b,h=BenchmarkTests().fixture();self.routes.accept('story',A,b,h,True)
  self.assertEqual(self.routes.configure('story',[A],'production')['mode'],'production')
  with self.assertRaises(AgentError):self.routes.configure('story',[A,B],'production')
  self.routes.revoke(A)
  with self.assertRaises(AgentError):self.routes.configure('story',[A],'production')
 def test_export_reports_attributed_human_review_and_selected_role(self):
  b,h=BenchmarkTests().fixture();self.routes.accept('story',A,b,h,True);self.routes.configure('story',[A],'production')
  folder=Path(self.tmp.name)/'report';folder.mkdir()
  (folder/'manifest.json').write_text(json.dumps({k:b[k] for k in ('model','digest','suite_sha256')}))
  (folder/'story.json').write_text(json.dumps(b['records']['story']))
  out=report(folder,self.store)
  self.assertEqual(out['selected_roles'],['story']);self.assertEqual(out['human_reviews']['story']['reviewer'],h['reviewer'])
  self.assertNotEqual(out['human_review_status'],'not_recorded')
 def test_failed_probe_after_generation_keeps_manifest_and_raw(self):
  result={'raw':'partial fixture','result':None,'status':'failed','evidence':{}}
  with patch('redpad_pipeline.model_benchmark.inventory',side_effect=[{A:DA},OSError('runtime stopped')]),patch('redpad_pipeline.model_benchmark.StagedDraft.run',return_value=result):
   saved=run_case(self.store,Path(self.tmp.name)/'benchmark',A,'story')
  folder=next((Path(self.tmp.name)/'benchmark').iterdir())
  self.assertTrue((folder/'manifest.json').is_file());self.assertEqual(saved['raw'],'partial fixture')
  self.assertEqual(saved['status'],'failed');self.assertIn('story',report(folder)['records'])
