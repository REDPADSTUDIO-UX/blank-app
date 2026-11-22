"""CPU-only authored controls; never real model/artistic evidence."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AGENTS,AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline import intelligence as q
from redpad_pipeline.filmmaking_knowledge import digest
from tests.test_agent_foundation import fixture

class IntelligenceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.engine=Engine(self.store)
 def output(self,role,data=None,**kwargs):
  rid=self.engine.enqueue(role,data or fixture(role),**kwargs)
  self.assertEqual(self.engine.execute(rid),'Awaiting QC',next(r for r in self.engine.runs() if r['id']==rid))
  run=next(r for r in self.engine.runs() if r['id']==rid)
  row=next(o for o in self.store.outputs() if o['task']==run['task'])
  return run,json.loads(json.loads(row['payload'])['summary'])
 def test_exact_21_profiles_and_bound_future_cases(self):
  self.assertEqual(set(q.load()['profiles']),set(AGENTS));self.assertEqual(len(q.future_queue()),21)
  for r in q.future_queue():
   self.assertFalse(r['execution_enabled']);self.assertEqual(len(r['revision']),40)
   self.assertEqual(r['max_concurrent_models'],1)
   p=q.profile(r['agent']);self.assertEqual(p['input_contract'],AGENTS[r['agent']]['input_contract'])
   self.assertTrue(p['benchmark']['adversarial']);self.assertEqual(len(p['criteria']),4)
  self.assertIn('600–720',q.profile('director')['benchmark']['realistic'])
 def test_schema_rejects_missing_role_and_faked_acceptance(self):
  data=q.load()
  for bad in ('role','status','criterion'):
   changed=copy.deepcopy(data)
   if bad=='role':del changed['profiles']['casting']
   elif bad=='status':changed['profiles']['script']['capability_status']['model']='passed'
   else:changed['profiles']['voice']['criteria'][0]['anchors']={}
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'intelligence.json';path.write_text(json.dumps(changed))
    path.with_name('intelligence.schema.json').write_text(q.CATALOG.with_name('intelligence.schema.json').read_text())
    with patch.object(q,'CATALOG',path),self.assertRaises(AgentError):q.load()
 def test_professional_trial_snapshots_role_rubric_without_execution(self):
  from redpad_pipeline.professional_readiness import ProfessionalLab
  lab=ProfessionalLab(self.store)
  trial=lab.plan('story',['writer9'],'Test whether source-bound context preserves causal knowledge across the story.',
                 'No character learns a secret before the disclosure event.',max_calls=1)
  self.assertEqual(trial['intelligence']['profile_sha256'],q.digest(q.profile('story')))
  packet,key=lab.blind_packet(trial['id'])
  self.assertEqual(packet['intelligence']['benchmark']['id'],'intelligence.story.v1')
  self.assertEqual(packet['samples'],[]);self.assertEqual(key,{})
  self.assertFalse(packet['human_review_completed'])
 def test_all_agents_integrated_without_network_or_inference(self):
  from redpad_pipeline.screenwriter import render
  from tests.test_screenwriter import sample
  with patch('socket.socket',side_effect=AssertionError('network forbidden')),patch('redpad_pipeline.agent_engine.LocalWriter',side_effect=AssertionError('inference forbidden')):
   for role in AGENTS:
    data=fixture(role)
    if role=='storyboard':data['script']=render(sample())
    run,body=self.output(role,data)
    e=body['intelligence_evidence']
    self.assertEqual(e['benchmark_id'],q.profile(role)['benchmark']['id'])
    self.assertFalse(e['professional_acceptance']);self.assertIsNone(e['artistic_scores'])
    self.assertEqual(e['layers']['owner'],'pending')
    self.assertEqual([s['stage'] for s in e['stages']],list(q.STAGES))
    self.assertFalse(body['model_inference'])
    packet=Engine(self.store).quality_packet(run['task'],1)
    self.assertEqual(packet['provenance'],'manually_authored_fixture')
    self.assertNotIn('model',packet)
 def test_prompt_consumes_profile_but_provider_is_simulation(self):
  data=fixture('story');seen=[]
  rid=self.engine.enqueue('story',data,mode='local')
  def provider(system,prompt):seen.append(system);return copy.deepcopy(data)
  self.assertEqual(self.engine.execute(rid,complete=provider),'Awaiting QC')
  self.assertIn('CREATIVE QUALITY CONTRACT',seen[0]);self.assertIn('causality and stakes',seen[0])
  self.assertEqual(self.engine.quality_packet(self.engine.runs()[0]['task'],1)['provenance'],'manually_authored_fixture')
 def test_context_reuses_bible_and_exact_revision(self):
  source={'artifact':{'story_bible':{'single_key':True},'character_bible':{'age':27},'owner_approvals':['locked']}}
  c=q.context({'a':source},[{'id':'a','revision':2}])
  self.assertEqual(c['memory']['story_bible'][0]['value'],{'single_key':True})
  self.assertEqual(c['sources'][0]['sha256'],digest(source));self.assertIn('voice_locks',c['missing_context'])
  with self.assertRaises(AgentError):q.context({'a':source},[{'id':'a','revision':0}])
 def test_snapshot_resume_idempotency_and_tamper(self):
  data=fixture('story');rid=self.engine.enqueue('story',data,idempotency_key='once')
  a=q.snapshot(self.store,rid,'story',data,{},[])
  self.assertEqual(self.engine.enqueue('story',data,idempotency_key='once'),rid)
  with patch.object(q,'profile',side_effect=AssertionError('reuse immutable profile')):
   self.assertEqual(q.snapshot(self.store,rid,'story',data,{},[]),a)
  with self.assertRaises(AgentError):q.snapshot(self.store,rid,'script',data,{},[])
  with self.store.tx() as db:db.execute("UPDATE events SET detail=json_set(detail,'$.sha256','bad') WHERE action='intelligence_snapshot'")
  with self.assertRaises(AgentError):q.snapshot(self.store,rid,'story',data,{},[])
 def finding(self,medium='text',score=None):
  return dict(id='f1',criterion='story.1',target='s1',medium=medium,source_sha256=digest({'s1':'lost key'}),severity='error',confidence=.8,explanation='Key reappears without a cause',correction='Restore the established possession event',responsible_agent='story',retest='Compare possession before and after s1',evidence='lost key',score=score)
 def test_unseen_medium_abstains_and_score_rejected(self):
  source={'s1':'lost key'}
  for medium in ('text','image','audio','video'):
   f=self.finding(medium)
   role={'text':'story','image':'art','audio':'voice','video':'video'}[medium];f['criterion']=role+'.1'
   report=q.assess(role,source,[f],creator=role,reviewer='independent reviewer',receipts=[],provenance='manually_authored_fixture')
   self.assertEqual(report['decision'],'abstain');self.assertEqual(report['findings'][0]['status'],'abstain')
   f['score']=4
   with self.assertRaises(AgentError):q.assess(role,source,[f],creator=role,reviewer='independent reviewer',receipts=[],provenance='manually_authored_fixture')
   if medium!='text':
    disguised=dict(f,medium='text',score=None)
    with self.assertRaises(AgentError):q.assess(role,source,[disguised],creator=role,reviewer='independent reviewer',receipts=[],provenance='manually_authored_fixture')
 def test_review_independence_staleness_and_invalid_values(self):
  source={'s1':'lost key'};f=self.finding(score=2)
  receipt=dict(reviewer='reviewer',source_sha256=digest(source),medium='text',target='s1',inspected=True,reference='authored control')
  kwargs=dict(creator='story',reviewer='reviewer',receipts=[receipt],provenance='manually_authored_fixture')
  self.assertEqual(q.assess('story',source,[f],**kwargs)['findings'][0]['status'],'supported')
  for key,value in [('source_sha256','stale'),('confidence',float('nan')),('score',True),('responsible_agent','ghost')]:
   bad=dict(f,**{key:value})
   with self.assertRaises(AgentError):q.assess('story',source,[bad],**kwargs)
  with self.assertRaises(AgentError):q.assess('story',source,[f],**dict(kwargs,reviewer='story'))
  with self.assertRaises(AgentError):q.assess('story',source,[f,f],**kwargs)
 def test_fact_attribution_and_interpretation_are_separate(self):
  source={'text':'fictional fact','verification':'reviewer_attested','attribution':'authored control'}
  f={'kind':'verified_source','claim':'fictional fact','source':'a','quote':'fictional fact','source_sha256':digest(source)}
  self.assertEqual(q.validate_facts([f],{'a':source}),[f])
  with self.assertRaises(AgentError):q.validate_facts([dict(f,quote='fabricated')],{'a':source})
  with self.assertRaises(AgentError):q.validate_facts([dict(f,source_sha256='stale')],{'a':source})
  self.assertEqual(q.validate_facts([{'kind':'assumption','claim':'Audience may prefer silence'}],{}),[{'kind':'assumption','claim':'Audience may prefer silence'}])
 def test_partial_inspection_cannot_be_hidden_by_criterion_coverage(self):
  source={'s1':'lost key'}
  findings=[dict(self.finding(),id=c['id'],criterion=c['id'],severity='info') for c in q.profile('story')['criteria']]
  findings.append(dict(self.finding(),id='unseen',target='s2'))
  receipt=dict(reviewer='reviewer',source_sha256=digest(source),medium='text',target='s1',inspected=True,reference='authored control')
  report=q.assess('story',source,findings,creator='story',reviewer='reviewer',receipts=[receipt],provenance='manually_authored_fixture')
  self.assertEqual(report['unassessed_criteria'],[])
  self.assertEqual(report['decision'],'abstain')
  plan=q.revision_requests(report)
  self.assertEqual(plan['requests'],[])
  self.assertEqual(plan['evidence_required_for'],['unseen'])
 def test_qc_handoffs_route_all_roles_without_revision_authority(self):
  source={'s1':'lost key'}
  findings=[dict(self.finding(),id=role,responsible_agent=role) for role in AGENTS]
  receipt=dict(reviewer='reviewer',source_sha256=digest(source),medium='text',target='s1',inspected=True,reference='authored control')
  report=q.assess('story',source,findings,creator='story',reviewer='reviewer',receipts=[receipt],provenance='manually_authored_fixture')
  plan=q.revision_requests(report)
  self.assertEqual({r['responsible_agent'] for r in plan['requests']},set(AGENTS))
  self.assertFalse(plan['grants_revision_authority'])
  for request in plan['requests']:
   self.assertEqual(request['targets'],['s1'])
   self.assertEqual(request['source_sha256'],digest(source))
   self.assertEqual(request['required_re_evaluation'],[findings[0]['retest']])
   self.assertFalse(request['execution_enabled'])
  findings[0]['evidence']='tampered caller data'
  self.assertEqual(report['findings'][0]['evidence'],'lost key')
  plan['requests'][0]['findings'][0]['evidence']='tampered handoff'
  self.assertEqual(report['findings'][0]['evidence'],'lost key')
 def test_targeted_revision_preserves_untouched_records_and_owner_lock(self):
  base=[{'id':'a','age':27},{'id':'b','line':'hello'}]
  new=[{'id':'b','line':'wait'}]
  plan=q.targeted_revision(base,new,['b'],locked=['a'])
  self.assertEqual(plan['records'][0],base[0]);self.assertEqual(plan['history']['before'],base)
  self.assertFalse(plan['owner_approval']);self.assertEqual(base[1]['line'],'hello')
  with self.assertRaises(AgentError):q.targeted_revision(base,[{'id':'a','age':29}],['a'],locked=['a'])
  with self.assertRaises(AgentError):q.targeted_revision(base,new,['a'])
 def test_every_role_benchmark_evidence_revision_and_handoff_controls(self):
  for role in AGENTS:
   with self.subTest(role=role):
    source={'id':'s1','observation':'original authored control'}
    findings=[];receipts=[]
    for n,c in enumerate(q.profile(role)['criteria']):
     f=self.finding(score=3)
     f.update(id=str(n),criterion=c['id'],medium=c['required_medium'],source_sha256=digest(source),evidence='original authored control',responsible_agent=role)
     findings.append(f)
    receipts=[dict(reviewer='independent control reviewer',source_sha256=digest(source),medium=medium,target='s1',inspected=True,reference='authored control') for medium in {f['medium'] for f in findings}]
    kwargs=dict(creator=role,reviewer='independent control reviewer',provenance='manually_authored_fixture')
    self.assertEqual(q.assess(role,source,findings,receipts=receipts,**kwargs)['decision'],'defects_present')
    with self.assertRaises(AgentError):q.assess(role,source,findings,receipts=[],**kwargs)
    plan=q.targeted_revision([source,{'id':'locked','value':'preserve'}],[dict(source,observation='revised')],['s1'],locked=['locked'])
    self.assertEqual(plan['records'][1]['value'],'preserve')
    self.assertFalse(q.review_packet(role,source,provenance='manually_authored_fixture')['owner_approval'])
    with self.assertRaises(AgentError):q.context({'source':source},[{'id':'different','revision':1}])
 def test_persisted_review_and_owner_requested_revision_use_existing_engine(self):
  from redpad_pipeline.specialists import example
  run,body=self.output('art',example('art'));task=run['task']
  report=self.engine.record_quality_review(task,1,[],reviewer='independent human',receipts=[])
  self.assertEqual(report['decision'],'abstain')
  self.assertEqual(report['targeted_revision_requests']['requests'],[])
  event=next(h for h in self.store.history() if h['action']=='intelligence_review')
  self.assertEqual(json.loads(event['detail'])['report']['targeted_revision_requests'],report['targeted_revision_requests'])
  self.assertEqual(self.store.tasks()[0]['state'],'Awaiting QC')
  rows=body['artifact']['records'];replacement=copy.deepcopy(rows[0]);replacement['style']='Restrained original style'
  with self.assertRaises(AgentError):self.engine.enqueue_targeted_revision(task,1,[replacement],[replacement['id']])
  self.store.review(task,1,'Request revision','Change only the style record','owner')
  rid=self.engine.enqueue_targeted_revision(task,1,[replacement],[replacement['id']])
  self.assertEqual(self.engine.execute(rid),'Awaiting QC')
  with self.assertRaises(AgentError):self.engine.quality_packet(task,1)
  self.assertTrue(any(h['action']=='intelligence_review' for h in self.store.history()))
 def test_stale_downstream_handoff_and_approval_preservation(self):
  parent,_=self.output('story');tid=parent['task']
  child=self.engine.enqueue('script',fixture('script'),[tid])
  self.assertEqual(self.engine.execute(child),'Blocked')
  self.store.review(tid,1,'Recommend','QC fixture','qc');self.store.review(tid,1,'Approve','Owner fixture','owner')
  self.engine.record_quality_review(tid,1,[],reviewer='external reviewer',receipts=[])
  self.assertEqual(next(t for t in self.store.tasks() if t['id']==tid)['state'],'Approved')
  self.store.review(tid,1,'Request revision','Target the premise','owner')
  self.assertEqual(self.engine.runs()[0]['state'],'Blocked')

if __name__=='__main__':unittest.main()
