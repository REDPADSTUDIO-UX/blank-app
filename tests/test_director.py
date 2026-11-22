import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.director import Director,validate


def fixture():
    return {'vision':'ঢাকার পুরোনো বাড়ির বাস্তবধর্মী রহস্য','tone':'সংযত ভয়',
        'scenes':[{'id':'s1','seconds':30,'visual':'রাফি দরজার নিচে আলো দেখে।',
        'performance':'স্থির শরীর, চোখে দ্বিধা','camera':'স্থির মিডিয়াম শট','sound':'বৃষ্টির শব্দ','continuity':'নেভি শার্ট; দরজা বন্ধ'}],
        'assignments':[{'agent':'script','brief':'প্রথমে দৃশ্যমান action, তারপর স্বাভাবিক বাংলা সংলাপ','scene_ids':['s1']}],
        'risks':['অভিনয় ও মুখের consistency বাস্তব footage দিয়ে পরীক্ষা প্রয়োজন']}

class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.d=Director(self.s)
    def test_manual_approval_dispatch_and_revision(self):
        pid=self.d.create('রাতের দরজা',30,manual=fixture())
        with self.assertRaises(AgentError):self.d.dispatch(pid)
        for actor in ('director','qc'):
            with self.assertRaises(AgentError):self.d.review(pid,'Approve','ok',actor)
        with self.assertRaises(AgentError):self.d.review(pid,'Approve','ok','owner')
        self.d.review(pid,'Recommend','independent review','qc');self.d.review(pid,'Approve','owner review','owner')
        ids=self.d.dispatch(pid);self.assertEqual(ids,self.d.dispatch(pid));self.assertEqual(len(self.s.tasks()),1)
        self.d.review(pid,'Request revision','change camera only','owner')
        payload=dict(schema_version=1,kind='screenplay',summary='fixture',artifacts=[],provenance='manual')
        with self.assertRaises(AgentError):self.s.submit(ids[0],payload,0)
        prompts=[]
        def revise(system,prompt):
            prompts.append(prompt); return fixture()
        newer=self.d.create('বদল',30,complete=revise,revision_of=pid)
        self.assertIn('change camera only',prompts[0])
        self.assertIn('previous_plan',prompts[0])
        self.assertNotEqual(newer,pid);self.assertEqual(len(self.d.plans()),2)
    def test_malformed_and_authority_fields(self):
        for key,value in [('seconds',True),('seconds',31),('visual','')]:
            p=fixture();p['scenes'][0][key]=value
            with self.assertRaises(AgentError):validate(p,30)
        for a in ('qc','director','invalid'):
            p=fixture();p['assignments'][0]['agent']=a
            with self.assertRaises(AgentError):validate(p,30)
        p=fixture();p['approved']=True
        with self.assertRaises(AgentError):validate(p,30)
        p=fixture();p['assignments'][0]['scene_ids']=['missing']
        with self.assertRaises(AgentError):validate(p,30)
    def test_simulation_is_not_inference_and_restart(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            self.d.create('brief',30,complete=lambda *_:fixture())
        d=Director(AgentStore(self.s.path))
        self.assertEqual(d.plans()[0]['provenance'],'simulation')
    def test_missing_model_no_fallback(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            with self.assertRaises(AgentError):self.d.create('brief',30)
        self.assertEqual(self.d.plans(),[])
    def test_invalid_response_no_partial_write(self):
        with self.assertRaises(AgentError):self.d.create('brief',30,complete=lambda *_:{})
        self.assertEqual(self.d.plans(),[])

    def test_targeted_revision_preserves_owner_locked_content_after_restart(self):
        pid=self.d.create('brief',30,manual=fixture())
        self.d.review(pid,'Request revision','camera only','owner',allowed_changes=['/scenes/0/camera'])
        self.d=Director(AgentStore(self.s.path))
        changed=fixture();changed['scenes'][0]['camera']='হাতে ধরা ক্লোজ শট'
        bad=copy.deepcopy(changed);bad['scenes'][0]['continuity']='লাল শার্ট; দরজা খোলা'
        with self.assertRaises(AgentError):self.d.create('brief',30,manual=bad,revision_of=pid)
        self.assertEqual(len(self.d.plans()),1)
        newer=self.d.create('brief',30,manual=changed,revision_of=pid)
        self.assertEqual(self.d.plans()[0]['state'],'Awaiting QC')
        with self.assertRaises(AgentError):self.d.dispatch(newer)

    def test_revision_scope_cannot_change_scene_identity_or_expand_itself(self):
        pid=self.d.create('brief',30,manual=fixture())
        for paths in ([],['/scenes'],['/scenes/0/id'],['/scenes/9/camera'],['/vision','/vision']):
            with self.assertRaises(AgentError):
                self.d.review(pid,'Request revision','scope','owner',allowed_changes=paths)
        self.d.review(pid,'Request revision','camera only','owner',allowed_changes=['/scenes/0/camera'])
        changed=fixture();changed['scenes'][0]['id']='replacement'
        changed['assignments'][0]['scene_ids']=['replacement']
        with self.assertRaises(AgentError):self.d.create('brief',30,manual=changed,revision_of=pid)

    def test_only_owner_can_set_explicit_revision_scope(self):
        pid=self.d.create('brief',30,manual=fixture())
        with self.assertRaises(AgentError):
            self.d.review(pid,'Reject','scope','qc',allowed_changes=['/vision'])

    def test_revision_rechecks_latest_owner_scope_before_saving(self):
        pid=self.d.create('brief',30,manual=fixture())
        self.d.review(pid,'Request revision','camera','owner',allowed_changes=['/scenes/0/camera'])
        def changed_during_inference(*_):
            self.d.review(pid,'Request revision','sound instead','owner',allowed_changes=['/scenes/0/sound'])
            plan=fixture();plan['scenes'][0]['camera']='নতুন ক্লোজ শট';return plan
        with self.assertRaises(AgentError):
            self.d.create('brief',30,complete=changed_during_inference,revision_of=pid)
        self.assertEqual(len(self.d.plans()),1)

if __name__=='__main__':unittest.main()
