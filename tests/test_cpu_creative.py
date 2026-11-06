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
   self.assertEqual(call('trial_test','story','same'),result)
 def test_uninstalled_runtime_never_downloads(self):
  from redpad_pipeline.local_ollama_session import local_cpu_session
  with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.local_ollama_session.ROOT',Path(d)):
   with self.assertRaises(WritingError):
    with local_cpu_session():pass
