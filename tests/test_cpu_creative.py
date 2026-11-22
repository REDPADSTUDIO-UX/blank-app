import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.screenwriter import LocalWriter,WritingError
from redpad_pipeline.cpu_creative_trial import call

class Response(io.BytesIO):
 def __enter__(self):return self
 def __exit__(self,*args):self.close()

def response(data):return Response(json.dumps(data).encode())

class CPUCreativeTests(unittest.TestCase):
 def test_rewrite_arrays_are_valid_transport_but_primitive_json_is_not(self):
  for content,valid in [('[{"id":"s2"}]',True),('42',False)]:
   writer=LocalWriter('local-test',timeout_seconds=420)
   with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),response({'model':'local-test','done':True,'message':{'content':content}})]):
    if valid:self.assertEqual(writer('system','prompt'),[{'id':'s2'}])
    else:
     with self.assertRaises(WritingError):writer('system','prompt')
 def test_timeout_bounds(self):
  for seconds in (0,601,True):
   with self.assertRaises(WritingError):LocalWriter('local-test',timeout_seconds=seconds)
 def test_trial_preserves_raw_failure_without_approval_and_does_not_rerun(self):
  class Fake:
   last_raw_output='actual raw fixture response';last_evidence={'inference_completed':True}
   def __init__(self,*a,**k):pass
   def __call__(self,*a):return {'invalid':'contract'}
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.cpu_creative_trial.FOLDER',Path(d)),patch('redpad_pipeline.cpu_creative_trial.LocalWriter',Fake) as writer:
   result=call('trial_test','story','original brief',kind='season',brief={})
   self.assertEqual(result['state'],'Failed');self.assertEqual(result['raw'],Fake.last_raw_output)
   self.assertFalse(result['production_approved']);self.assertFalse(result['independent_human_review'])
   self.assertEqual(call('trial_test','story','original brief',kind='season',brief={}),result)
   with self.assertRaises(Exception):call('trial_test','story','different request')
 def test_uninstalled_runtime_never_downloads(self):
  from redpad_pipeline.local_ollama_session import local_cpu_session
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.local_ollama_session.ROOT',Path(d)):
   with self.assertRaises(WritingError):
    with local_cpu_session():pass
 def test_streaming_preserves_partial_and_completed_json(self):
  packets=[{'model':'local-test','message':{'content':'{"bangla":"হ্যালো"}'},'done':False},{'model':'local-test','message':{'content':''},'done':True,'done_reason':'stop','eval_count':10}]
  received=[];writer=LocalWriter('local-test',stream=True,on_chunk=received.append)
  stream=Response(('\n'.join(json.dumps(p) for p in packets)+'\n').encode())
  with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),stream]):self.assertEqual(writer('system','prompt'),{'bangla':'হ্যালো'})
  self.assertTrue(received);self.assertTrue(writer.last_evidence['inference_completed'])
  writer=LocalWriter('local-test',stream=True)
  with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),Response((json.dumps(packets[0])+'\n').encode())]):
   with self.assertRaises(WritingError):writer('system','prompt')
  self.assertIn('হ্যালো',writer.last_raw_output);self.assertFalse(writer.last_evidence['inference_completed'])
 def test_installed_manifest_detected_without_running_api(self):
  from redpad_pipeline.phase3 import audit
  import hashlib
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.phase3.ROOT',Path(d)):
   root=Path(d)/'phase3_models/ollama-weights';blobs=root/'blobs';blobs.mkdir(parents=True)
   data=b'fake fixture';digest=hashlib.sha256(data).hexdigest();(blobs/('sha256-'+digest)).write_bytes(data)
   manifests=root/'manifests/registry.ollama.ai/library/qwen3';manifests.mkdir(parents=True)
   layer={'digest':'sha256:'+digest,'size':len(data)};(manifests/'test').write_text(json.dumps({'config':layer,'layers':[layer]}))
   result=audit(False);self.assertTrue(result['model_weights_present']);self.assertTrue(result['local_model_manifests'][0]['all_blobs_present'])
 def test_micro_director_quotes_and_targeted_rewrite_are_checked(self):
  from redpad_pipeline.cpu_micro_contracts import validate_micro
  from tests.test_screenwriter import sample
  with self.assertRaises(Exception):validate_micro('direction',{'findings':[{'criterion':'dialogue','quote':'invented','issue':'bad','instruction':'fix'}]},sample())
 def test_only_integrity_checked_real_archive_counts_as_inference(self):
  import hashlib
  from redpad_pipeline.agents import archived_cpu_inference
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.agents.CPU_ARCHIVE',Path(d)):
   self.assertFalse(archived_cpu_inference('story','model'))
   raw='{"title":"বাংলা"}';record={'agent':'story','model':'model','raw':raw,'provenance':'simulation','evidence':{'inference_completed':True,'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()}}
   path=Path(d)/'trial_fixture.json';path.write_text(json.dumps(record));self.assertFalse(archived_cpu_inference('story','model'))
   record['provenance']='local_inference';path.write_text(json.dumps(record));self.assertTrue(archived_cpu_inference('story','model'))
   record['raw']='changed';path.write_text(json.dumps(record));self.assertFalse(archived_cpu_inference('story','model'))
 def test_wire_normalization_preserves_canonical_bengali_without_changing_task_ids(self):
  import unicodedata
  raw='তানিয়া s2';writer=LocalWriter('local-test')
  packets=[response({}),response({'model':'local-test','done':True,'message':{'content':'{"ok":true}'}})]
  with patch('urllib.request.OpenerDirector.open',side_effect=packets) as transport:
   writer('system',raw);sent=json.loads(transport.call_args.args[0].data)
  self.assertEqual(sent['messages'][1]['content'],unicodedata.normalize('NFC',raw))
  self.assertIn('s2',sent['messages'][1]['content']);self.assertTrue(writer.last_evidence['prompt_normalization_changed'])
 def test_canonical_quote_matching_still_rejects_invented_words(self):
  import unicodedata
  from redpad_pipeline.cpu_micro_contracts import validate_micro
  source={'text':'তানিয়া'};quote=unicodedata.normalize('NFC','তানিয়া')
  valid={'findings':[{'criterion':'identity','quote':quote,'issue':'fixture issue','instruction':'fixture instruction'}]}
  validate_micro('direction',valid,source)
  valid['findings'][0]['quote']='invented '+quote
  with self.assertRaises(Exception):validate_micro('direction',valid,source)
 def test_engine_runtime_controls_cannot_override_model_or_endpoint(self):
  from redpad_pipeline.agents import AgentStore,AgentError
  from redpad_pipeline.agent_engine import Engine
  from tests.test_agent_foundation import fixture
  with tempfile.TemporaryDirectory() as d:
   engine=Engine(AgentStore(Path(d)/'agent_control.sqlite3'));rid=engine.enqueue('story',fixture('story'),mode='local')
   for options in [{'model':'cloud'}, {'endpoint':'https://external'}, []]:
    with self.assertRaises(AgentError):engine.execute(rid,local_options=options)
   self.assertEqual(engine.runs()[0]['state'],'Ready for Input')
 def test_instruction_echo_is_flagged_without_granting_quality_approval(self):
  from redpad_pipeline.agents import AgentStore
  from redpad_pipeline.agent_engine import Engine,echoes_input
  from tests.test_agent_foundation import fixture
  with tempfile.TemporaryDirectory() as d:
   store=AgentStore(Path(d)/'agent_control.sqlite3');engine=Engine(store);data=fixture('story')
   rid=engine.enqueue('story',data,mode='local')
   self.assertEqual(engine.execute(rid,complete=lambda *_:data),'Awaiting QC')
   body=json.loads(json.loads(store.outputs()[0]['payload'])['summary'])
   self.assertTrue(any(f['code']=='input_echo' for f in body['findings']));self.assertTrue(body['human_review_required'])
   self.assertTrue(echoes_input({'name':'তানিয়া'},{'name':'তানিয়া'}))
