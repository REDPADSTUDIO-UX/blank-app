import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AGENTS,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.departments import contract,prepare
from tests.test_screenwriter import sample
from tests.test_director import fixture as direction


def fixture(key):
    if key=='casting':
        from redpad_pipeline.specialists import example
        return example('casting')
    if key=='director':return {'plan':direction(),'seconds':30}
    if key=='script':return {'screenplay':sample(),'seconds':30}
    data=contract(key)
    if key in ('storyboard','qc','production_manager'):return data
    label=next(k for k in data if k!='project')
    row=data[label][0];row['id']='r1';data['project']='দরজার ওপাশে — fictional test'
    for k,v in row.items():
        if v=='none':row[k]='রাফি — supplied test '+k
    if key=='performance':row['intensity']=3
    if key=='video':row.update(seconds=3,fps=8,width=256,height=256)
    if key=='music':row['kind']='ambience'
    if key=='youtube':row['channel_id']='UC'+'a'*22
    return data


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.e=Engine(self.s)
    def run_task(self,key,data=None,deps=None,mode='software'):
        rid=self.e.enqueue(key,fixture(key) if data is None else data,deps,mode)
        state=self.e.execute(rid)
        run=next(r for r in self.e.runs() if r['id']==rid)
        return run,state
    def approve(self,tid):
        task=next(t for t in self.s.tasks() if t['id']==tid)
        if task['agent']!='qc':self.s.review(tid,task['revision'],'Recommend','Test-only independent reviewer evidence','qc')
        self.s.review(tid,task['revision'],'Approve','Test-only owner action','owner')
    def test_all_twenty_pipeline_and_media_blocks(self):
        order=['story','script','director','character','art','location','costume','storyboard','performance','cinematographer','motion','video','continuity','voice','music','editing','qc','production_manager','growth','youtube']
        previous=None;ids={}
        with patch('socket.socket',side_effect=AssertionError('External request forbidden')):
            for key in order:
                data=fixture(key)
                deps=[previous] if previous else []
                if key=='storyboard':
                    deps.append(ids['script'])
                    data['script']={'$from':ids['script'],'path':['artifact','formatted']}
                run,state=self.run_task(key,data,deps)
                self.assertEqual(state,'Awaiting QC',(key,run['error']))
                ids[key]=run['task'];self.approve(run['task']);previous=run['task']
            self.assertEqual(len(self.s.outputs()),20)
            for out in self.s.outputs():
                body=json.loads(json.loads(out['payload'])['summary'])
                self.assertFalse(body['model_inference']);self.assertFalse(body['media_generated'])
            for key in ('video','voice','music','editing'):
                run,state=self.run_task(key,mode='media')
                self.assertEqual(state,'Blocked');self.assertEqual(run['blocker'],'Environment/model')
    def test_dependency_scheduler_and_revision_scope(self):
        first,state=self.run_task('story');tid=first['task']
        child=self.e.enqueue('script',fixture('script'),[tid]);self.assertEqual(self.e.execute(child),'Blocked')
        self.approve(tid);self.e.tick()
        self.assertEqual(next(r for r in self.e.runs() if r['id']==child)['state'],'Awaiting QC')
        child_tid=next(r for r in self.e.runs() if r['id']==child)['task'];self.approve(child_tid)
        unrelated,_=self.run_task('art');self.approve(unrelated['task'])
        self.s.review(tid,1,'Request revision','Target story only','owner')
        with self.assertRaises(AgentError):self.s.assign('editing','Use stale child',[child_tid])
        self.assertEqual(next(t for t in self.s.tasks() if t['id']==unrelated['task'])['state'],'Approved')
        revision=self.e.enqueue('story',fixture('story'),task=tid)
        self.assertEqual(self.e.execute(revision),'Awaiting QC')
        self.assertEqual(len([x for x in self.s.outputs() if x['task']==tid]),2)
        self.assertEqual(json.loads(self.s.outputs()[0]['payload'])['provenance'],'software')
    def test_all_missing_models_block_without_network(self):
        with patch('socket.socket',side_effect=AssertionError('No fallback allowed')):
            for key in AGENTS:
                run,state=self.run_task(key,mode='local')
                self.assertEqual(state,'Blocked',key)
        self.assertEqual(self.s.outputs(),[])
    def test_revision_refreshes_dependency_versions(self):
        parent,_=self.run_task('story');self.approve(parent['task'])
        child,_=self.run_task('art',deps=[parent['task']]);self.approve(child['task'])
        self.s.review(child['task'],1,'Request revision','source will change','owner')
        self.s.review(parent['task'],1,'Request revision','update story','owner')
        rid=self.e.enqueue('story',fixture('story'),task=parent['task']);self.e.execute(rid);self.approve(parent['task'])
        rid=self.e.enqueue('art',fixture('art'),[parent['task']],task=child['task'])
        self.assertEqual(self.e.execute(rid),'Awaiting QC')
        t=next(t for t in self.s.tasks() if t['id']==child['task'])
        self.assertEqual(json.loads(t['refs'])[0]['revision'],2)
    def test_media_bridge_isolation_and_preconditions(self):
        from redpad_pipeline.agent_media_bridge import execute_media,MediaBlocked
        with self.assertRaises(MediaBlocked):execute_media('editing',{'operation':'render_quality_project','project_id':'test'},self.s.path)
        with self.assertRaises(AgentError):execute_media('editing',{'operation':'render_quality_project','project_id':'../production'},self.s.path)
        with self.assertRaises(MediaBlocked):execute_media('voice',{},self.s.path)
    def test_fail_retry_and_recovery(self):
        run,state=self.run_task('story',{})
        self.assertEqual(state,'Failed');self.assertEqual(len(self.s.outputs()),0)
        self.e.retry(run['id'],inputs=fixture('story'));self.assertEqual(self.e.execute(run['id']),'Awaiting QC')
        with self.assertRaises(AgentError):self.e.retry(run['id'])
        rid=self.e.enqueue('art',fixture('art'))
        with self.s.tx() as db:db.execute("UPDATE agent_runs SET state='Running' WHERE id=?",(rid,))
        with self.assertRaises(AgentError):self.e.retry(rid)
        new=self.e.recover(rid);self.assertNotEqual(new,rid)
        with self.assertRaises(AgentError):self.e.execute(rid)
        self.e.retry(new);self.assertEqual(self.e.execute(new),'Awaiting QC')
    def test_model_missing_and_simulation_disclosure(self):
        with patch('socket.socket',side_effect=AssertionError('No fallback')):
            run,state=self.run_task('story',mode='local');self.assertEqual(state,'Blocked')
            self.e.retry(run['id'])
            self.assertEqual(self.e.execute(run['id'],complete=lambda *_:fixture('story')),'Awaiting QC')
        body=json.loads(json.loads(self.s.outputs()[0]['payload'])['summary'])
        self.assertEqual(body['provenance'],'simulation');self.assertFalse(body['model_inference'])
    def test_cycles_and_unauthorized_bindings(self):
        parent,_=self.run_task('story');self.approve(parent['task'])
        child,_=self.run_task('art',deps=[parent['task']]);self.approve(child['task'])
        self.s.review(parent['task'],1,'Request revision','target','owner')
        with self.assertRaises(AgentError):self.e.enqueue('story',fixture('story'),[child['task']],task=parent['task'])
        bad=fixture('story');bad['project']={'$from':'unapproved','path':[]}
        run,state=self.run_task('story',bad);self.assertEqual(state,'Blocked')
    def test_quality_checks_and_owner_qc_review(self):
        q=fixture('qc');q['checks'][0]['result']='fail'
        run,state=self.run_task('qc',q)
        out=json.loads(json.loads(self.s.outputs()[0]['payload'])['summary'])
        self.assertEqual(out['artifact']['recommendation'],'Revision Required')
        with self.assertRaises(AgentError):self.s.review(run['task'],1,'Recommend','self','qc')
        with self.assertRaises(AgentError):self.s.review(run['task'],1,'Approve','director','director')
        self.approve(run['task'])
    def test_continuity_and_edit_checks(self):
        data=fixture('continuity');row=copy.deepcopy(data['observations'][0]);row.update(id='r2',value='different',change_reason='none');data['observations'].append(row)
        self.assertTrue(prepare('continuity',data)['findings'])
        data=fixture('editing');row=copy.deepcopy(data['clips'][0]);row['id']='r2';data['clips'].append(row)
        self.assertTrue(prepare('editing',data)['findings'])
    def test_restart_preserves_runs(self):
        run,_=self.run_task('growth')
        fresh=Engine(AgentStore(self.s.path));self.assertEqual(fresh.runs()[0]['id'],run['id'])
    def test_source_change_during_inference_discards_output(self):
        parent,_=self.run_task('story');self.approve(parent['task'])
        rid=self.e.enqueue('art',fixture('art'),[parent['task']],mode='local')
        def complete(*_):
            self.s.review(parent['task'],1,'Request revision','changed while running','owner')
            return fixture('art')
        self.assertEqual(self.e.execute(rid,complete=complete),'Failed')
        self.assertEqual(len(self.s.outputs()),1)


def individual_test(key):
    def test(self):
        with patch('socket.socket',side_effect=AssertionError('No network')):
            run,state=self.run_task(key)
        self.assertEqual(state,'Awaiting QC',run['error'])
        result=json.loads(json.loads(self.s.outputs()[0]['payload'])['summary'])
        self.assertEqual(result['agent'],key);self.assertIn('artifact',result)
    return test
for key in AGENTS:setattr(FoundationTests,'test_department_'+key,individual_test(key))

if __name__=='__main__':unittest.main()
