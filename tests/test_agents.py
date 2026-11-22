import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AGENTS, CATALOG, AgentStore, AgentError

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3')
    def output(self,key='story'):
        return dict(schema_version=1,kind=AGENTS[key]['output_contract']['kind'],summary='Fixture only',artifacts=[],provenance='simulation')
    def test_registry_and_dependency_dag(self):
        self.assertEqual(len(CATALOG),21); self.assertEqual(len({a['id'] for a in CATALOG}),21)
        def visit(k,trail=()):
            self.assertNotIn(k,trail)
            for dep in AGENTS[k]['dependencies']: visit(dep,trail+(k,))
        for a in CATALOG:
            visit(a['key'])
            for module in a['existing_modules']: self.assertTrue(Path(module).is_file())
    def test_independent_configuration_and_restart(self):
        self.s.configure('story','local-test:7b')
        fresh=AgentStore(self.s.path)
        self.assertEqual(fresh.status('story')['configuration'],'Configured')
        self.assertEqual(fresh.status('script')['configuration'],'Not configured')
        self.assertEqual(fresh.status('story')['connection'],'Model Not Connected')
        with self.assertRaises(AgentError): self.s.configure('story','model-cloud')
    def test_all_agent_output_contracts_offline(self):
        with patch('socket.socket',side_effect=AssertionError('No network')):
            for key in AGENTS:
                tid=self.s.assign(key,'Test')
                self.s.submit(tid,self.output(key),0)
        self.assertEqual(len(self.s.tasks()),21)
    def test_approval_and_stale_handoff(self):
        tid=self.s.assign('story','Test'); self.s.submit(tid,self.output(),0)
        for actor in ('director','qc','story'):
            with self.assertRaises(AgentError): self.s.review(tid,1,'Approve','evidence',actor)
        with self.assertRaises(AgentError): self.s.review(tid,1,'Approve','evidence','owner')
        self.s.review(tid,1,'Recommend','manual QC evidence','qc')
        self.s.review(tid,1,'Approve','owner review','owner')
        child=self.s.assign('script','Use approved story',[tid],actor='director')
        with self.assertRaises(AgentError): self.s.submit(tid,self.output(),1)
        self.s.review(tid,1,'Request revision','Target story only','owner')
        with self.assertRaises(AgentError): self.s.submit(child,self.output('script'),0)
        self.s.submit(tid,self.output(),1)
        with self.assertRaises(AgentError): self.s.review(tid,1,'Recommend','old','qc')
        self.assertTrue(any(x['action']=='handoff' for x in self.s.history()))
    def test_errors_and_qc_independence(self):
        with self.assertRaises(AgentError): self.s.assign('qc','Test',actor='director')
        with self.assertRaises(AgentError): self.s.assign('unknown','Test')
        with self.assertRaises(AgentError): self.s.assign('story','')
        with self.assertRaises(AgentError): AgentStore(Path(self.tmp.name)/'redpad_studio.db')
        tid=self.s.assign('qc','Review'); self.s.submit(tid,self.output('qc'),0)
        with self.assertRaises(AgentError): self.s.review(tid,1,'Recommend','self','qc')
    def test_rejection_and_false_inference(self):
        tid=self.s.assign('story','Test'); out=self.output(); out['provenance']='actual_inference'
        with self.assertRaises(AgentError): self.s.submit(tid,out,0)
        self.s.submit(tid,self.output(),0); self.s.review(tid,1,'Reject','Fix hook','qc')
        self.s.submit(tid,self.output(),1)
        self.assertEqual(self.s.tasks()[0]['revision'],2)

if __name__=='__main__': unittest.main()
