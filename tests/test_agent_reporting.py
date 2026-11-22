"""CPU metadata fixtures only; no GPU, inference, downloads or publication."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import CATALOG,AGENTS,AgentError,AgentStore,validate_catalog
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.agent_reporting import build_matrix,validate_matrix,load_matrix,qc_report,dashboard,sha
from redpad_pipeline.specialists import example
from tests.test_agent_foundation import fixture

class RegistryReportingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.engine=Engine(self.store)
 def test_registry_and_current_matrix_include_casting(self):
  self.assertEqual(len(CATALOG),21);m=load_matrix();self.assertEqual(len(m['agents']),len(CATALOG))
  self.assertIn('redpad.agent.casting',{a['id'] for a in m['agents']})
  self.assertEqual(set(AGENTS),{a['key'] for a in m['agents']})
 def test_consistency_rejects_missing_extra_duplicate_ids_and_stale_counts(self):
  for kind in ('missing','extra','duplicate','count','hash','name','malformed'):
   m=copy.deepcopy(build_matrix())
   if kind=='missing':m['agents'].pop()
   elif kind=='extra':m['agents'].append(dict(m['agents'][0],id='redpad.agent.unknown',key='unknown'))
   elif kind=='duplicate':m['agents'][-1]=copy.deepcopy(m['agents'][0])
   elif kind=='count':m['registered_agents']=20
   elif kind=='hash':m['registry_sha256']='stale'
   elif kind=='name':m['agents'][0]['name']='Wrong name'
   else:m['agents'][0]['id']=123
   with self.subTest(kind=kind),self.assertRaises(AgentError):validate_matrix(m)
  with self.assertRaises(AgentError):validate_matrix([])
 def test_registry_duplicate_ids_keys_are_rejected_before_dictionary_collapse(self):
  for key in ('id','key'):
   c=copy.deepcopy(CATALOG);c[-1][key]=c[0][key]
   with self.assertRaises(AgentError):validate_catalog(c)
  c=copy.deepcopy(CATALOG);c.append(dict(c[-1],id='redpad.agent.future',key='future'))
  with self.assertRaises(AgentError):validate_matrix(build_matrix(),c)
 def test_unattested_engineering_is_not_fabricated_and_models_never_promoted(self):
  m=build_matrix()
  for a in m['agents']:
   self.assertEqual(a['engineering']['status'],'implemented_references_not_retested')
   self.assertEqual(a['inference']['selected_model_validation'],'not_verified_by_this_audit')
   self.assertFalse(a['production']['ready'])
  bad={'all_registry_cpu_workflows':True,'registry_sha256':'stale','failures':0,'errors':0}
  self.assertEqual(build_matrix(bad)['agents'][0]['engineering']['status'],'implemented_references_not_retested')
 def test_all_registry_cpu_workflows_and_qc_coverage(self):
  from redpad_pipeline.screenwriter import render
  from tests.test_screenwriter import sample
  with patch('socket.socket',side_effect=AssertionError('No network')),patch('redpad_pipeline.agent_engine.LocalWriter',side_effect=AssertionError('No inference')):
   for role in AGENTS:
    data=fixture(role)
    if role=='storyboard':data['script']=render(sample())
    rid=self.engine.enqueue(role,data,mode='software')
    self.assertEqual(self.engine.execute(rid),'Awaiting QC',(role,self.engine.runs()[0]['error']))
  report=qc_report(self.store)
  self.assertEqual(report['registered_agents'],len(AGENTS));self.assertEqual({r['agent'] for r in report['agents']},set(AGENTS))
  for r in report['agents']:self.assertEqual(r['tasks'],1);self.assertEqual(r['awaiting_qc'],1)
  self.assertIn('casting',report['revision_recipients']);self.assertNotIn('qc',report['revision_recipients'])
  d=dashboard(self.store);self.assertEqual(len(d['agents']),21);self.assertEqual(d['production_ready'],0)
  for o in self.store.outputs():self.assertFalse(json.loads(json.loads(o['payload'])['summary'])['model_inference'])
 def test_qc_findings_cover_every_reviewable_registry_agent(self):
  for role in set(AGENTS)-{'qc'}:
   data=example('qc');data['records'][0].update(subject_agent=role,expected='locked fixture',actual='different fixture',evidence='Authored text defect control only')
   rid=self.engine.enqueue('qc',data);self.assertEqual(self.engine.execute(rid),'Awaiting QC')
  r=qc_report(self.store)
  for a in r['agents']:
   if a['agent']!='qc':self.assertTrue(a['findings'],a['agent'])
  self.assertEqual(r['unassigned_findings'],[])
 def test_stale_handoffs_and_findings_are_reported_without_approval_mutation(self):
  tid=self.store.assign('casting','Manual historical fixture')
  out=dict(schema_version=1,kind=AGENTS['casting']['output_contract']['kind'],summary=json.dumps({'findings':[{'target_agent':'casting','code':'fixture'}]}),artifacts=[],provenance='manual')
  self.store.submit(tid,out,0)
  r=qc_report(self.store);self.assertEqual(next(x for x in r['agents'] if x['agent']=='casting')['findings'][0]['source_task'],tid)
  with self.assertRaises(AgentError):self.store.review(tid,1,'Approve','Generic casting bypass','owner')
  rid=self.engine.enqueue('art',example('art'));self.engine.execute(rid);source=self.engine.runs()[0]['task']
  self.store.review(source,1,'Recommend','Fixture QC','qc');self.store.review(source,1,'Approve','Fixture owner','owner')
  data=example('qc');data['sources']={'art':{'$from':source,'path':['artifact']}};data['records'][0].update(subject_agent='art',expected='a',actual='b')
  cr=self.engine.enqueue('qc',data,[source]);self.assertEqual(self.engine.execute(cr),'Awaiting QC')
  self.store.review(source,1,'Request revision','Invalidate source','owner')
  r=qc_report(self.store);qc=next(x for x in r['agents'] if x['agent']=='qc');self.assertEqual(qc['stale_tasks'],1)
  art=next(x for x in r['agents'] if x['agent']=='art');self.assertFalse(art['findings'][0]['current']);self.assertFalse(art['handoffs'][0]['current'])
 def test_unknown_historical_recipient_is_visible_not_silently_dropped(self):
  tid=self.store.assign('story','Malformed legacy findings')
  self.store.submit(tid,dict(schema_version=1,kind='story',summary=json.dumps({'findings':[{'target_agent':'legacy_missing','code':'fixture'}]}),artifacts=[],provenance='manual'),0)
  r=qc_report(self.store);self.assertEqual(len(r['unassigned_findings']),1)
 def test_legacy_qc_casting_recipient_is_preserved_and_old_outputs_resolve_from_input(self):
  data={'subject_agent':'casting','checks':[{'criterion':'actor_lock','result':'unverified','evidence':'Historical metadata fixture','revision':'Request actual inspection'}]}
  rid=self.engine.enqueue('qc',data);self.assertEqual(self.engine.execute(rid),'Awaiting QC')
  task=self.engine.runs()[0]['task']
  report=qc_report(self.store);self.assertEqual(len(next(a for a in report['agents'] if a['agent']=='casting')['findings']),1)
  # Recreate the old output format in an isolated fixture DB only; original run inputs stay intact.
  with self.store.tx() as db:
   row=db.execute('SELECT payload FROM outputs WHERE task=?',(task,)).fetchone();envelope=json.loads(row[0]);body=json.loads(envelope['summary'])
   del body['artifact']['subject_agent'];del body['findings'][0]['target_agent'];envelope['summary']=json.dumps(body)
   db.execute('UPDATE outputs SET payload=? WHERE task=?',(json.dumps(envelope),task))
  report=qc_report(self.store);self.assertEqual(len(next(a for a in report['agents'] if a['agent']=='casting')['findings']),1)
  self.assertFalse(next(a for a in report['agents'] if a['agent']=='qc')['findings'])
 def test_report_ui_registry_totals_casting_and_qc_rows(self):
  from streamlit.testing.v1 import AppTest
  code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.agent_reporting_ui import show_registry_status\nshow_registry_status(AgentStore('+repr(str(self.store.path))+'))'
  at=AppTest.from_string(code).run();self.assertFalse(at.exception)
  self.assertEqual(next(m.value for m in at.metric if m.label=='Registered agents'),str(len(AGENTS)))
  self.assertEqual(len(at.dataframe[0].value),21);self.assertIn('Casting Director AI',list(at.dataframe[0].value['name']))
  self.assertEqual(len(at.dataframe[1].value),21);self.assertIn('casting',list(at.dataframe[1].value['agent']))
  self.assertEqual(next(m.value for m in at.metric if m.label=='Production verified'),'0/21')
  self.assertEqual(next(m.value for m in at.metric if m.label=='CPU workflow evidence'),str(dashboard()['engineering_verified'])+'/21')
 def test_producer_dashboard_home_shows_registry_without_creating_production_state(self):
  from streamlit.testing.v1 import AppTest
  with patch('redpad_pipeline.producer_ui.PROGRAM_ROOT',Path(self.tmp.name)/'absent'):
   at=AppTest.from_string('from redpad_pipeline.producer_ui import overview\noverview()').run()
  self.assertFalse(at.exception);self.assertEqual(next(m.value for m in at.metric if m.label=='Registered agents'),'21')
  self.assertIn('casting',list(at.dataframe[0].value['agent']))

from tests import test_producer_control as producer_fixtures
class CastingQCReportingTests(unittest.TestCase):
 setUp=producer_fixtures.ProducerTests.setUp;task=producer_fixtures.ProducerTests.task;approve=producer_fixtures.ProducerTests.approve;body=producer_fixtures.ProducerTests.body
 image=producer_fixtures.ProducerTests.image;casting=producer_fixtures.ProducerTests.casting;lock=producer_fixtures.ProducerTests.lock
 def test_legacy_qc_can_request_casting_revision_only_after_owner_approval(self):
  from redpad_pipeline.specialist_review import route_revision
  cast=self.casting()[0];self.lock(cast)
  data={'subject_agent':'casting','checks':[{'criterion':'fixture_casting_review','result':'unverified','evidence':'Authored metadata fixture','revision':'Inspect actual audition before recast'}]}
  qt=self.task('qc',data,[cast])
  with self.assertRaises(AgentError):route_revision(self.s,qt,cast)
  self.s.review(qt,1,'Approve','Owner fixture review','owner');route_revision(self.s,qt,cast)
  self.assertEqual(next(t for t in self.s.tasks() if t['id']==cast)['state'],'Revision requested')
 def test_casting_producer_lock_qc_reporting_routing_and_stale_handoff(self):
  from redpad_pipeline.specialist_review import route_revision
  cast=self.casting()[0]
  with self.assertRaises(AgentError):self.s.review(cast,1,'Approve','No Director inspection','owner')
  self.lock(cast)
  data=example('qc');data['sources']={'casting':{'$from':cast,'path':['artifact']}};data['records'][0].update(subject_agent='casting',criterion='casting_fixture_revision',expected='a',actual='b',evidence='Authored metadata comparison, no acting evaluation')
  qt=self.task('qc',data,[cast])
  with self.assertRaises(AgentError):route_revision(self.s,qt,cast)
  with self.assertRaises(AgentError):self.s.review(qt,1,'Recommend','Self-review','qc')
  self.s.review(qt,1,'Approve','Owner reviews independent QC record','owner')
  before=qc_report(self.s);row=next(a for a in before['agents'] if a['agent']=='casting');self.assertTrue(row['findings']);self.assertTrue(row['handoffs'])
  route_revision(self.s,qt,cast)
  self.assertEqual(next(t for t in self.s.tasks() if t['id']==cast)['state'],'Revision requested')
  self.assertTrue(next(a for a in qc_report(self.s)['agents'] if a['agent']=='qc')['stale_tasks'])
  with self.assertRaises(AgentError):route_revision(self.s,qt,cast)

if __name__=='__main__':unittest.main()
