"""Manually authored structural controls; never a candidate story or real inference."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline import story_quality as s
from redpad_pipeline.intelligence import assess
from redpad_pipeline.filmmaking_knowledge import digest

def control():
 a={k:'ম্যানুয়াল সফটওয়্যার নিয়ন্ত্রণ: '+k for k in ['logline','dramatic_question','theme','conflict_stakes','relationship_dynamics','treatment','ending_consequence','filmability']}
 a.update(schema_version=1,characters=[dict(id=c,**{k:c+' authored '+k for k in ['name','biography','want','need','fear','contradiction','relationship','internal_conflict','behavior','emotional_change']}) for c in ['daughter','father']],initial_knowledge={'daughter':[],'father':['ticket']},beats=[],assumptions=['Authored fixture, not an authentic Bangladeshi story'],unresolved_questions=[],self_critique=[{'beat':'b1','weakness':'Manual fixture lacks artistic intent','suggestion':'Requires actual selected-model output and human review'}])
 for n in range(1,13):
  a['beats'].append(dict(id=f'b{n}',act=1 if n<=4 else 2 if n<=8 else 3,actor='daughter' if n%2 else 'father',goal=f'authored goal {n}',choice=f'authored choice {n}',cause='brief' if n==1 else f'b{n-1}',consequence=f'authored consequence {n}',action=f'visible fixture action {n}',location='fictional room',sound='fictional ambience',emotion=f'fixture emotion {n}',before={'step':str(n-1),'key_holder':'father'},after={'step':str(n),'key_holder':'father'},requires={'daughter':['ticket']} if n>5 else {},learns={'daughter':['ticket']} if n==5 else {},plants=['ticket_hint'] if n==2 else [],payoffs=['ticket_hint'] if n==5 else [],emotion_setups=['b2'] if n in [6,10] else [],subtle_emotion=n in [6,10],humor='authored awkwardness control' if n==4 else '',humor_motivation='conflicting habits control' if n==4 else ''))
 return a

class StoryQualityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.engine=Engine(self.store)
 def run_story(self,a=None,**kwargs):
  rid=self.engine.enqueue('story',s.request(a or control()),**kwargs)
  self.assertEqual(self.engine.execute(rid),'Awaiting QC',self.engine.runs()[0]['error'])
  return self.engine.runs()[0]
 def test_pinned_model_and_existing_case_are_unchanged(self):
  p=s.spec();self.assertEqual(len(p['rubric']),15);self.assertEqual(len(p['adversarial']),7)
  self.assertEqual(p['model_revision'],'fc05daec18b0a78c049392ed2e771dde82bdf654')
  self.assertEqual(p['budget']['max_calls_including_failed_attempts'],7)
  self.assertEqual(s.canary_request()['max_new_tokens'],384)
 def test_existing_story_bridge_queues_resumes_and_revises_same_task(self):
  from redpad_pipeline.studio_program import StudioProgram
  from redpad_pipeline.story_bridge import StoryBridge
  with patch('redpad_pipeline.studio_program.PROGRAM_ROOT',Path(self.tmp.name)/'projects'):
   p=StudioProgram('story_quality');p.create('Authored control project','Not a generated story',1,660)
   bridge=StoryBridge(p);rid=bridge.queue_benchmark(control())
   self.assertEqual(bridge.queue_benchmark(control()),rid)
   self.assertEqual(p.engine.execute(rid),'Awaiting QC')
   task=p.engine.runs()[0]['task'];p.store.review(task,1,'Request revision','Change b6 only','owner')
   a=control();a['beats'][5]['action']='Revised authored control'
   revised=bridge.queue_benchmark(a,task=task,targets=['b6'])
   self.assertEqual(p.engine.execute(revised),'Awaiting QC')
   self.assertEqual(len([r for r in p.store.outputs() if r['task']==task]),2)
 def test_complete_structure_is_not_creative_acceptance(self):
  report=s.validate(control());self.assertTrue(report['technical_compliance'])
  self.assertFalse(report['semantic_causality_verified']);self.assertEqual(report['human_review'],'pending')
 def test_bounded_sections_compile_losslessly_without_new_inference(self):
  a=control();foundation={k:v for k,v in a.items() if k not in s.REFLECTION|{'beats'}};reflection={k:a[k] for k in s.REFLECTION}
  acts=[[b for b in a['beats'] if b['act']==n] for n in (1,2,3)]
  result=s.assemble_sections(foundation,acts,reflection)
  self.assertEqual(result['artifact'],a);self.assertEqual(len(result['section_sha256']),5)
  self.assertFalse(result['owner_acceptance'])
  with self.assertRaises(AgentError):s.assemble_sections(foundation,acts[::-1],reflection)
 def test_knowledge_requires_earlier_disclosure(self):
  a=control();a['beats'][2]['requires']={'daughter':['ticket']}
  with self.assertRaisesRegex(AgentError,'Secret knowledge'):s.validate(a)
 def test_no_self_justified_knowledge_in_same_beat(self):
  a=control();a['beats'][4]['requires']={'daughter':['ticket']}
  with self.assertRaises(AgentError):s.validate(a)
 def test_cause_state_and_repeat_controls(self):
  for change in ['cause','state','unchanged','character']:
   a=control()
   if change=='cause':a['beats'][3]['cause']='b10'
   if change=='state':a['beats'][3]['before']['key_holder']='daughter'
   if change=='unchanged':a['beats'][3]['after']=a['beats'][3]['before']
   if change=='character':a['beats'][3]['actor']='unknown'
   with self.subTest(change=change),self.assertRaises(AgentError):s.validate(a)
  a=control();a['beats'][3]['choice']=a['beats'][2]['choice']
  self.assertIn('repeated_choice',{f['code'] for f in s.validate(a)['findings']})
 def test_setup_payoff_and_reveal_must_be_earned(self):
  a=control();a['beats'][4]['payoffs']=['unplanted']
  with self.assertRaises(AgentError):s.validate(a)
  a=control();a['beats'][1]['payoffs']=['ticket_hint']
  with self.assertRaises(AgentError):s.validate(a)
 def test_emotion_humor_and_flat_character_controls(self):
  a=control();a['beats'][5]['emotion_setups']=[];a['beats'][3]['humor_motivation']=''
  self.assertEqual({f['code'] for f in s.validate(a)['findings']},{'unprepared_emotion','unsupported_humor'})
  a['characters'][0]['fear']=''
  with self.assertRaises(AgentError):s.validate(a)
 def test_missing_deliverables_acts_and_duplicate_ids_fail(self):
  for key in ['treatment','dramatic_question','ending_consequence','filmability']:
   a=control();del a[key]
   with self.subTest(key=key),self.assertRaises(AgentError):s.validate(a)
  a=control();a['beats'][1]['id']='b1'
  with self.assertRaises(AgentError):s.validate(a)
 def test_exact_source_research_and_owner_locks(self):
  a=control();source={'ending':a['ending_consequence']};data=s.request(a,sources={'task':source},locks=[{'source_task':'task','source_path':['ending'],'target_path':['ending_consequence']}])
  sources={'task':{'artifact':source}}
  s.prepare('story',data,sources)
  data['artifact']['ending_consequence']='Contradicts owner source'
  with self.assertRaisesRegex(AgentError,'lock conflict'):s.prepare('story',data,sources)
  data=s.request(control(),research=[{'kind':'verified_source','claim':'invented audience views'}])
  with self.assertRaises(AgentError):s.prepare('story',data,{})
 def test_source_swap_and_wrong_role_rejected(self):
  data=s.request(control(),sources={'task':{'facts':'changed'}})
  with self.assertRaises(AgentError):s.prepare('story',data,{'task':{'artifact':{'facts':'original'}}})
  with self.assertRaises(AgentError):s.prepare('script',s.request(control()),{})
 def test_targeted_revision_preserves_other_beats_and_metadata(self):
  before=control();after=copy.deepcopy(before);after['beats'][5]['action']='Revised fixture gesture'
  data=s.request(after,base=before,targets=['b6'])
  result=s.prepare('story',data,{},before)
  self.assertEqual(result['comparison']['targets'],['b6'])
  self.assertIsNone(s.comparison(before,after)['measured_creative_improvement'])
  after['beats'][1]['action']='Untargeted alteration'
  with self.assertRaises(AgentError):s.prepare('story',data,{},before)
 def test_revision_cannot_silently_change_character_or_treatment(self):
  a=control();b=copy.deepcopy(a);b['characters'][0]['fear']='changed'
  with self.assertRaises(AgentError):s.prepare('story',s.request(b,base=a,targets=['b1']),{},a)
 def test_revision_cannot_drop_its_original_source_locks(self):
  source=self.store.assign('story','Authored lock control')
  value={'agent':'story','artifact':{'ending':control()['ending_consequence']}}
  self.store.submit(source,dict(schema_version=1,kind='story',summary=json.dumps(value),artifacts=[],provenance='manual'),0)
  self.store.review(source,1,'Recommend','Authored control','qc');self.store.review(source,1,'Approve','Authored control','owner')
  data=s.request(control(),sources={source:{'$from':source,'path':['artifact']}},locks=[{'source_task':source,'source_path':['ending'],'target_path':['ending_consequence']}])
  rid=self.engine.enqueue('story',data,[source])
  self.assertEqual(self.engine.execute(rid),'Awaiting QC');task=self.engine.runs()[0]['task']
  self.store.review(task,1,'Request revision','Fixture request','owner')
  changed=copy.deepcopy(data);changed.update(base=control(),targets=['b1'],locks=[])
  with self.assertRaisesRegex(AgentError,'cannot drop source locks'):self.engine.enqueue('story',changed,[source],task=task)
 def test_engine_software_path_and_15_criterion_review_intake(self):
  run=self.run_story();packet=self.engine.quality_packet(run['task'],1)
  self.assertEqual(len(packet['rubric']),15);self.assertEqual(packet['provenance'],'manually_authored_fixture')
  report=self.engine.record_quality_review(run['task'],1,[],reviewer='Independent fixture reviewer',receipts=[])
  self.assertEqual(len(report['unassessed_criteria']),15);self.assertFalse(report['owner_approval'])
 def test_simulation_prompt_retention_never_real_model(self):
  rid=self.engine.enqueue('story',s.request(),mode='local');seen=[]
  def provider(system,prompt):seen.append(system);return control()
  self.assertEqual(self.engine.execute(rid,complete=provider),'Awaiting QC')
  self.assertIn('costly protagonist decision',seen[0])
  with self.store.tx() as db:
   row=db.execute('SELECT provenance,raw_output FROM creative_model_attempts WHERE run=?',(rid,)).fetchone()
  self.assertEqual(row['provenance'],'simulation');self.assertEqual(json.loads(row['raw_output']),control())
  self.assertTrue(any(e['action']=='story_benchmark_request' for e in self.store.history()))
 def test_real_runtime_blocks_before_any_provider_or_model_import(self):
  rid=self.engine.enqueue('story',s.request(),mode='local')
  with patch('redpad_pipeline.agent_engine.LocalWriter',side_effect=AssertionError('No model launch')):
   self.assertEqual(self.engine.execute(rid),'Blocked')
  self.assertIn('kernel-isolated',self.engine.runs()[0]['error'])
 def test_raw_failed_output_retained_and_not_repaired(self):
  rid=self.engine.enqueue('story',s.request(),mode='local')
  self.assertEqual(self.engine.execute(rid,complete=lambda *_:{'not':'story'}),'Failed')
  with self.store.tx() as db:self.assertEqual(json.loads(db.execute('SELECT raw_output FROM creative_model_attempts').fetchone()[0]),{'not':'story'})
  self.assertEqual(self.store.outputs(),[])
 def test_bible_handoff_is_approved_source_bound_and_idempotent(self):
  run=self.run_story();task=run['task']
  with self.assertRaises(AgentError):s.queue_bible_handoff(self.engine,task)
  self.store.review(task,1,'Recommend','Authored control QC','qc');self.store.review(task,1,'Approve','Authored control owner','owner')
  rid=s.queue_bible_handoff(self.engine,task)
  self.assertEqual(s.queue_bible_handoff(self.engine,task),rid)
  self.assertEqual(self.engine.execute(rid),'Awaiting QC')
  self.store.review(task,1,'Request revision','Test stale source','owner')
  with self.assertRaises(AgentError):s.queue_bible_handoff(self.engine,task)
 def test_preflight_no_model_import_network_or_allocation(self):
  with patch('redpad_pipeline.story_quality.shutil.which',return_value=None),patch('socket.socket',side_effect=AssertionError('No network')):
   p=s.preflight(self.store)
  self.assertFalse(p['gpu_allocated']);self.assertFalse(p['inference_authorized']);self.assertFalse(p['approved_install_receipt_present']);self.assertTrue(p['blockers'])
 def test_full_review_requires_exact_story_quote_and_independence(self):
  a=control();f=dict(id='f',criterion='story.creative.2',target='b1',medium='text',source_sha256=digest(a),severity='warning',confidence=.7,explanation='Authored control only',correction='Review causal choice',responsible_agent='story',retest='Compare affected beat',evidence=a['beats'][0]['choice'],score=2)
  receipts=[dict(reviewer='reviewer',source_sha256=digest(a),medium='text',target='b1',inspected=True,reference='Authored fixture review')]
  kwargs=dict(creator='story',reviewer='reviewer',receipts=receipts,provenance='manually_authored_fixture',benchmark_id='intelligence.story.v1')
  r=assess('story',a,[f],**kwargs);self.assertEqual(r['decision'],'abstain')
  with self.assertRaises(AgentError):assess('story',a,[dict(f,evidence='invented',score=5)],**kwargs)
  with self.assertRaises(AgentError):assess('story',a,[dict(f,target='missing')],**kwargs)
  with self.assertRaises(AgentError):assess('story',a,[dict(f,evidence=a['beats'][4]['choice'])],**kwargs)

if __name__=='__main__':unittest.main()
