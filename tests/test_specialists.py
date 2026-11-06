import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError,AGENTS
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.specialists import prepare,example,IMPLEMENTED

class SpecialistTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.e=Engine(self.s)
    def approve(self,tid):
        t=next(t for t in self.s.tasks() if t['id']==tid)
        if t['agent']!='qc':self.s.review(tid,t['revision'],'Recommend','Fixture metadata reviewed','qc')
        self.s.review(tid,t['revision'],'Approve','Fixture owner approval','owner')
    def test_every_specialist_positive_negative_recovery_and_model_block(self):
        for key in sorted(IMPLEMENTED):
            with self.subTest(agent=key),patch('socket.socket',side_effect=AssertionError('Network prohibited')):
                data=example(key);result=prepare(key,data)
                self.assertEqual(result['artifact']['department'],key);self.assertFalse(result['model_inference'])
                bad=copy.deepcopy(data);bad['records'][0]['id']=''
                with self.assertRaises(AgentError):prepare(key,bad)
                rid=self.e.enqueue(key,bad);self.assertEqual(self.e.execute(rid),'Failed')
                self.e.retry(rid,inputs=data);self.assertEqual(self.e.execute(rid),'Awaiting QC')
                run=next(r for r in self.e.runs() if r['id']==rid);self.approve(run['task'])
                mid=self.e.enqueue(key,data,mode='local');self.assertEqual(self.e.execute(mid),'Blocked')
        self.assertEqual(len(AGENTS),20)
    def test_character_and_versioned_approved_handoff(self):
        data=example('character');rid=self.e.enqueue('character',data);self.e.execute(rid)
        tid=next(r for r in self.e.runs() if r['id']==rid)['task']
        child=example('costume');child['sources']={'character':{'$from':tid,'path':['artifact']}}
        cr=self.e.enqueue('costume',child,[tid]);self.assertEqual(self.e.execute(cr),'Blocked')
        self.approve(tid);self.e.tick();self.assertEqual(next(r for r in self.e.runs() if r['id']==cr)['state'],'Awaiting QC')
        fake=example('costume');fake['sources']={'character':{'records':[]}}
        fr=self.e.enqueue('costume',fake);self.assertEqual(self.e.execute(fr),'Failed')
    def test_art_targeted_revision_and_impact(self):
        data=example('art');base=prepare('art',data)['artifact'];data.update(base=base,targets=['set1']);data['records'][0]['props']['key']='steel'
        result=prepare('art',data);self.assertEqual(result['artifact']['derived']['affected_scenes'],['s1','s2'])
        data['targets']=['unknown']
        with self.assertRaises(AgentError):prepare('art',data)
    def test_location_contradictory_door(self):
        data=example('location');data['records'][2]['openings'][0]['id']='d1'
        self.assertTrue(any(f['code']=='door_destination_conflict' for f in prepare('location',data)['findings']))
    def test_costume_change_and_justification(self):
        data=example('costume');data['records'][2]['outfit']='white'
        self.assertEqual(len(prepare('costume',data)['findings']),1)
        data['records'][2]['change_reason']='পরদিন সকালে বদলেছে';self.assertFalse(prepare('costume',data)['findings'])
    def test_qc_evidence_and_routes(self):
        data=example('qc');data['records'][0]['actual']='white';result=prepare('qc',data)
        self.assertIn('character',result['artifact']['derived']['revision_routes']);self.assertFalse(result['artifact']['derived']['owner_approval'])
        data['records'][0]['subject_agent']='qc'
        with self.assertRaises(AgentError):prepare('qc',data)
