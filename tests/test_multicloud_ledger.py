"""Focused persistence/authorization guards. Fixtures are NOT model outputs."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from redpad_pipeline.agents import AgentStore,AgentError,encode
from redpad_pipeline.multicloud_ledger import CloudExperiments
from redpad_pipeline.kaggle_benchmark import KaggleLab

class CloudLedgerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.store=AgentStore(self.root/'agent_control.sqlite3');self.lab=CloudExperiments(self.store)
  self.spec={'case':{'id':'SOFTWARE_FIXTURE'},'model':{'repo':'fixture-only','revision':'unverified'},'settings':{'seed':117},'source_sha256':'a'*64}
  self.id=self.lab.register(self.spec)
  self.permission=dict(account_authorized=True,model_install_approved=True,persistence_approved=True,actual_runtime_observed=True,payload_egress_approved=True,free_only_verified=True,timeout_seconds=30,remaining_seconds=200)
 def sample(self):
  p=self.root/'fixture.txt';p.write_bytes(b'UNIT FIXTURE - NOT AN AI OUTPUT')
  return p,{'actual_output_received':True,'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 def test_identity_is_provider_neutral_and_strict(self):
  self.lab.blocked(self.id,'lightning','No signed-in account',authorization=True)
  self.assertEqual(self.lab.register(copy.deepcopy(self.spec)),self.id)
  for bad in ({**self.spec,'provider':'colab'},{**self.spec,'source_sha256':'unknown'}):
   with self.assertRaises(AgentError):self.lab.register(bad)
 def test_reuses_existing_canonical_job_without_execution(self):
  k=KaggleLab(self.store);job=k.plan(['qwen35_9'],['natural_dialogue'],'Compare stronger writing only after exact resources and installation approval.')[0]
  p=json.loads(k.jobs()[0]['payload'])
  spec={'case':p['case'],'model':{x:p[x] for x in ('repo','revision')},'settings':p['settings'],'source_sha256':p['suite_sha256']};spec['model']['profile']=p['profile']
  self.assertEqual(self.lab.register(spec,existing_kaggle_job=job),job)
  with self.store.tx() as db:db.execute("UPDATE kaggle_trial_jobs SET state='Failed — Evidence Preserved',output='{}' WHERE id=?",(job,))
  # Existing imported state must not silently become eligible to run again.
  new_id=job+'-failed'
  with self.store.tx() as db:db.execute('INSERT INTO kaggle_trial_jobs(id,payload,state,output) SELECT ?,payload,state,output FROM kaggle_trial_jobs WHERE id=?',(new_id,job))
  self.assertEqual(self.lab.get(self.lab.register(spec,existing_kaggle_job=new_id))['state'],'Failed With Evidence')
  with self.store.tx() as db:db.execute("UPDATE kaggle_trial_jobs SET state='Completed',output='{}' WHERE id=?",(job,))
  with self.assertRaises(AgentError):self.lab.register(spec,existing_kaggle_job=job)
 def test_completed_sample_skips_even_without_new_provider_auth(self):
  p,o=self.sample();self.lab.retain_hosted_sample(self.id,'hugging_face',p,o)
  self.assertTrue(self.lab.begin(self.id,'colab',{})['skip_completed'])
  self.lab.blocked(self.id,'colab','Not logged in',authorization=True)
  self.assertEqual(self.lab.get(self.id)['state'],'Human Review Pending')
 def test_paid_and_unknown_free_allocations_fail_closed(self):
  with self.assertRaises(AgentError):self.lab.begin(self.id,'lightning',{**self.permission,'payload_egress_approved':False})
  with self.assertRaises(AgentError):self.lab.begin(self.id,'runpod',self.permission)
  with self.assertRaises(AgentError):self.lab.begin(self.id,'lightning',{**self.permission,'free_only_verified':False})
  with self.assertRaises(AgentError):self.lab.begin(self.id,'runpod',{**self.permission,'paid_owner_approved':True,'approval_reference':'fixture','max_usd':float('nan')})
  with self.assertRaises(AgentError):self.lab.begin(self.id,'lightning',{**self.permission,'remaining_seconds':float('nan')})
 def test_inflight_and_failed_calls_never_blindly_retry(self):
  a=self.lab.begin(self.id,'lightning',self.permission)
  with self.assertRaises(AgentError):self.lab.begin(self.id,'colab',self.permission)
  self.lab.fail(a['attempt'],{'reason':'fixture unknown completion; investigate first'})
  with self.assertRaises(AgentError):self.lab.begin(self.id,'colab',self.permission)
 def test_hosted_receipt_cannot_become_winner_or_replace_output(self):
  p,o=self.sample();result=self.lab.retain_hosted_sample(self.id,'hugging_face',p,o)
  for flag in ('selection_eligible','reproducible_benchmark_verified','human_review_completed'):self.assertFalse(result[flag])
  self.assertEqual(result,self.lab.retain_hosted_sample(self.id,'hugging_face',p,o))
  p.write_bytes(b'changed fixture');o['output_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  with self.assertRaises(AgentError):self.lab.retain_hosted_sample(self.id,'hugging_face',p,o)
 def test_hash_mismatch_and_symlink_rejected(self):
  p,o=self.sample();o['output_sha256']='0'*64
  with self.assertRaises(AgentError):self.lab.retain_hosted_sample(self.id,'hugging_face',p,o)
  link=self.root/'link';link.symlink_to(p);o['output_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  with self.assertRaises(AgentError):self.lab.retain_hosted_sample(self.id,'hugging_face',link,o)
 def test_blocker_history_is_append_only(self):
  for provider in ('lightning','colab'):self.lab.blocked(self.id,provider,'Login required',authorization=True)
  e=self.lab.export();self.assertEqual(len(e['attempts']),2)
  self.assertFalse(e['provisions_compute']);self.assertFalse(e['automatic_billing']);self.assertFalse(e['automatic_retries'])
  self.lab.blocked(self.id,'hugging_face','Rejected poll; submission uncertain',authorization=True,evidence={'completion_unknown':True})
  with self.assertRaises(AgentError):self.lab.begin(self.id,'colab',self.permission)

if __name__=='__main__':unittest.main()
