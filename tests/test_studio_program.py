import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.studio_program import StudioProgram
from redpad_pipeline.agents import AgentError

class ProgramTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.patcher=patch('redpad_pipeline.studio_program.PROGRAM_ROOT',Path(self.tmp.name));self.patcher.start();self.addCleanup(self.patcher.stop)
  self.program=StudioProgram('project');self.program.create('ফেরার কথা','Original test fixture, not a generated screenplay',30,300)
 def test_hierarchy_project_reopen_and_owner_notes_no_inference_claim(self):
  p=self.program;summary=p.summary();self.assertEqual(sum(n['kind']=='episode' for n in summary['hierarchy']),30)
  self.assertEqual(len(summary['workstreams']),10);self.assertEqual(summary['registered_agents'],20)
  p.note('script','বিলের সংলাপ সংযত রাখুন।');self.assertEqual(p.summary()['owner_notes'][0]['provenance'],'owner_note_not_AI_output')
  p.create('ফেরার কথা','Original test fixture, not a generated screenplay',30,300)
  with self.assertRaises(AgentError):p.create('changed','new',30,300)
  self.assertFalse(p.summary()['production_ready'])
 def test_hierarchy_validation_and_immutable_nodes(self):
  p=self.program;seq=p.add_node('episode1','sequence',1,{'purpose':'test'})
  scene=p.add_node(seq,'scene',1,{'action':'দরজা বন্ধ হয়।'})
  self.assertEqual(p.add_node(seq,'scene',1,{'action':'দরজা বন্ধ হয়।'}),scene)
  with self.assertRaises(AgentError):p.add_node('episode1','shot',1,{})
  with self.assertRaises(AgentError):p.add_node(seq,'scene',1,{'action':'changed'})
 def test_no_giant_thirty_episode_call_or_unapproved_handoff(self):
  with patch.object(self.program.engine,'enqueue') as provider:
   with self.assertRaises(AgentError):self.program.queue_creative('story')
   with self.assertRaises(AgentError):self.program.queue_specialists()
   provider.assert_not_called()
 def _approved(self,role,data,deps=()):
  p=self.program;rid=p.engine.enqueue(role,data,list(deps),mode='software');self.assertEqual(p.engine.execute(rid),'Awaiting QC')
  task=next(r['task'] for r in p.engine.runs() if r['id']==rid)
  p.store.review(task,1,'Recommend','Simulated independent test review','qc');p.store.review(task,1,'Approve','Simulated owner fixture approval','owner')
  return rid,task
 def seed_approved_creative(self):
  from tests.test_creative import samples,request
  d=samples();story,st=self._approved('story',request('season',d['season']))
  director,dt=self._approved('director',request('direction',d['direction_story'],source={'$from':st,'path':['artifact']}),[st])
  script,sc=self._approved('script',request('screenplay',d['screenplay'],source={'$from':st,'path':['artifact']}),[st,dt])
  final,di=self._approved('director',request('direction',d['direction_script'],source={'$from':sc,'path':['artifact']}),[sc])
  with self.program.store.tx() as db:
   for label,rid in [('story',story),('director_story',director),('script:episode1',script),('director_script:episode1',final)]:db.execute('INSERT INTO studio_links VALUES (?,?)',(label,rid))
  return sc,di
 def test_seventeen_internal_tasks_generated_from_exact_sources_idempotently(self):
  from redpad_pipeline.specialists import example
  sc,di=self.seed_approved_creative();p=self.program;plan=p.queue_specialists();before=len(p.store.tasks());self.assertEqual(p.queue_specialists(),plan);self.assertEqual(len(p.store.tasks()),before)
  self.assertEqual(len(plan['tasks']),17);self.assertFalse(plan['auto_publish'])
  runs={r['id']:r for r in p.engine.runs()}
  for role,rid in plan['runs'].items():
   self.assertEqual(runs[rid]['mode'],'local');data=json.loads(runs[rid]['inputs']);self.assertEqual(data['records'],[])
   self.assertEqual(data['sources']['screenplay']['$from'],sc)
  rid=plan['runs']['character'];prompts=[]
  def fixture(system,prompt):prompts.append(prompt);return {'records':example('character')['records']}
  self.assertEqual(p.engine.execute(rid,complete=fixture),'Awaiting QC');self.assertIn('SPECIALIST RECORD SCHEMA',prompts[0])
  out=next(o for o in p.store.outputs() if o['task']==plan['tasks']['character']);self.assertEqual(json.loads(out['payload'])['provenance'],'simulation')
  with self.assertRaises(AgentError):p.store.review(plan['tasks']['character'],1,'Approve','No QC shortcut','owner')
 def test_stale_approved_source_blocks_new_internal_queue(self):
  sc,_=self.seed_approved_creative();self.program.store.review(sc,1,'Request revision','Targeted correction','owner')
  with self.assertRaises(AgentError):self.program.queue_specialists()
 def test_checkpoint_binds_source_without_claiming_readiness(self):
  c=self.program.checkpoint('2'*40,{'test':'fixture'})
  self.assertEqual(c['source_commit'],'2'*40);self.assertFalse(c['summary']['production_ready'])
  self.assertNotIn('owner_notes',c['summary'])
  self.assertEqual(StudioProgram('project').summary()['project'],self.program.summary()['project'])
 def test_recovery_updates_link_and_needs_explicit_retry(self):
  from tests.test_agent_foundation import fixture
  rid=self.program.engine.enqueue('story',fixture('story'))
  with self.program.store.tx() as db:
   db.execute("UPDATE agent_runs SET state='Running' WHERE id=?",(rid,));db.execute('INSERT INTO studio_links VALUES (?,?)',('recover',rid))
  with self.assertRaises(AgentError):self.program.recover(rid)
  recovered=self.program.recover(rid,True)
  with self.program.store.tx() as db:self.assertEqual(db.execute("SELECT run FROM studio_links WHERE label='recover'").fetchone()[0],recovered)
  self.assertEqual(self.program.engine.runs()[0]['state'],'Failed');self.program.engine.retry(recovered)
  self.assertEqual(self.program.engine.runs()[0]['state'],'Ready for Input')
 def test_local_failure_is_not_automatically_retried_by_tick(self):
  from tests.test_agent_foundation import fixture
  rid=self.program.engine.enqueue('story',fixture('story'),mode='local')
  result=self.program.tick();self.assertEqual(result[rid],'Blocked');self.assertEqual(self.program.tick(),{})
 def test_runtime_digest_normalization_real_ollama_format(self):
  from redpad_pipeline.model_routing import inventory
  from tests.test_cpu_creative import response
  raw='a'*64
  with patch('urllib.request.OpenerDirector.open',return_value=response({'models':[{'name':'qwen:4b','digest':raw}]})):
   self.assertEqual(inventory(),{'qwen:4b':'sha256:'+raw})
 def test_unified_ui_creates_project_without_inference_and_all_five_areas_render(self):
  from streamlit.testing.v1 import AppTest
  with patch('redpad_pipeline.studio_program_ui.StudioProgram',wraps=StudioProgram),patch('redpad_pipeline.model_routing_ui.run_case') as inference:
   at=AppTest.from_string('from redpad_pipeline.studio_program_ui import show_studio_program\nshow_studio_program()').run();self.assertFalse(at.exception)
   at.text_input(key='master_project_id').set_value('ui')
   at.text_input(key='master_title').set_value('UI fixture');at.text_area(key='master_brief').set_value('Original test brief')
   next(b for b in at.button if b.label=='Create unified project').click().run();self.assertFalse(at.exception)
   for area in ['Creative Studio','Production Studio','Post-Production Studio','Project Management','Admin / Advanced']:
    at.radio(key='master_nav').set_value(area).run();self.assertFalse(at.exception)
   inference.assert_not_called()
