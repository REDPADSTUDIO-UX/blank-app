import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError,AGENTS
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.specialists import example,prepare,IMPLEMENTED

class Integration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.e=Engine(self.s)
    def approve(self,tid):
        t=next(t for t in self.s.tasks() if t['id']==tid)
        if t['agent']!='qc':self.s.review(tid,t['revision'],'Recommend','Independent metadata fixture review','qc')
        self.s.review(tid,t['revision'],'Approve','Manual fixture owner action','owner')
    def task(self,key,data=None,deps=None):
        rid=self.e.enqueue(key,data or example(key),deps);state=self.e.execute(rid)
        self.assertEqual(state,'Awaiting QC',next(r['error'] for r in self.e.runs() if r['id']==rid))
        return next(r['task'] for r in self.e.runs() if r['id']==rid)
    def artifact(self,tid):
        out=[o for o in self.s.outputs() if o['task']==tid][-1]
        return json.loads(json.loads(out['payload'])['summary'])['artifact']
    def test_each_specialist_revisions_approval_sources_and_recovery(self):
        for key in sorted(IMPLEMENTED):
            with self.subTest(agent=key):
                tid=self.task(key);old=self.artifact(tid)
                with self.assertRaises(AgentError):self.s.review(tid,1,'Approve','No QC','model')
                self.approve(tid);self.s.review(tid,1,'Request revision','Target first record only','owner')
                data=example(key);data.update(base=old,targets=[data['records'][0]['id']])
                # A targeted correction may preserve the record if the reviewer verifies it as-is.
                rid=self.e.enqueue(key,data,task=tid);self.assertEqual(self.e.execute(rid),'Awaiting QC')
                self.assertEqual(len([o for o in self.s.outputs() if o['task']==tid]),2)
                self.assertEqual(self.artifact(tid)['records'][1:],old['records'][1:])
                self.approve(tid)
                child=example('production_manager');child['sources']={key:{'$from':tid,'path':['artifact']}}
                cr=self.e.enqueue('production_manager',child,[tid]);self.assertEqual(self.e.execute(cr),'Awaiting QC')
                self.s.review(tid,2,'Request revision','Invalidate current version','owner')
                child2=self.e.enqueue('production_manager',child,[tid]);self.assertEqual(self.e.execute(child2),'Blocked')
    def test_approved_screenplay_to_shots_and_department_handoffs(self):
        from tests.test_creative import samples,request
        d=samples();story=self.task('story',request('season',d['season']));self.approve(story)
        direction=self.task('director',request('direction',d['direction_story'],source={'$from':story,'path':['artifact']}),[story]);self.approve(direction)
        script=self.task('script',request('screenplay',d['screenplay'],source={'$from':story,'path':['artifact']}),[story,direction]);self.approve(script)
        character=self.task('character');self.approve(character);location=self.task('location');self.approve(location)
        board=example('storyboard');board['sources']={'screenplay':{'$from':script,'path':['artifact']},'character':{'$from':character,'path':['artifact']},'location':{'$from':location,'path':['artifact']}}
        tid=self.task('storyboard',board,[script,character,location]);self.approve(tid)
        video=example('video');video['sources']={'storyboard':{'$from':tid,'path':['artifact']},'character':{'$from':character,'path':['artifact']}}
        self.task('video',video,[tid,character]);video['records'][0]['shot']='forged'
        rid=self.e.enqueue('video',video,[tid,character]);self.assertEqual(self.e.execute(rid),'Failed')
    def test_parallel_unrelated_software_continues_with_resource_block(self):
        blocked=self.e.enqueue('video',example('video'),mode='local')
        self.assertEqual(self.e.execute(blocked),'Blocked')
        runs=[self.e.enqueue(k,example(k)) for k in ('character','art','location')]
        results=self.e.tick_parallel();self.assertTrue(all(results[r]=='Awaiting QC' for r in runs));self.assertNotIn(blocked,results)
    def test_model_adapter_cannot_replace_revision_envelope(self):
        tid=self.task('art');self.approve(tid);self.s.review(tid,1,'Request revision','Only set1','owner')
        data=example('art');data.update(base=self.artifact(tid),targets=['set1'])
        rid=self.e.enqueue('art',data,mode='local',task=tid)
        self.assertEqual(self.e.execute(rid,complete=lambda *_:{'records':data['records'],'base':None}),'Failed')
        self.e.retry(rid);self.assertEqual(self.e.execute(rid,complete=lambda *_:{'records':data['records']}),'Awaiting QC')
        body=json.loads(json.loads([o for o in self.s.outputs() if o['task']==tid][-1]['payload'])['summary']);self.assertEqual(body['provenance'],'simulation');self.assertFalse(body['model_inference'])
    def test_qc_detects_source_defects_and_routes_exact_revision(self):
        from redpad_pipeline.specialist_review import route_revision
        char=example('character');char['records'][0]['scene_states'][0]['hair']='white'
        tid=self.task('character',char);self.approve(tid)
        qc=example('qc');qc['sources']={'character':{'$from':tid,'path':['artifact']}}
        review=self.task('qc',qc,[tid])
        with self.assertRaises(AgentError):route_revision(self.s,review,tid)
        self.approve(review);route_revision(self.s,review,tid)
        self.assertEqual(next(t['state'] for t in self.s.tasks() if t['id']==tid),'Revision requested')
        qc=example('qc');qc['records'][0].update(subject_agent='video',criterion='media_spec',actual={'fps':0,'width':63,'height':256,'seconds':-1})
        result=prepare('qc',qc);self.assertEqual(result['artifact']['derived']['recommendation'],'block')
        self.assertTrue(any(f['code']=='invalid_fps' for f in result['findings']))
    def test_local_backend_boundaries_and_safe_errors(self):
        from redpad_pipeline.specialist_adapters import LocalVideoAdapter,LocalSpeechAdapter,ReadOnlyAnalyticsAdapter
        from redpad_pipeline.agent_media_bridge import MediaBlocked
        for name in ('wan-local','ltx-local'):
            adapter=LocalVideoAdapter(name);request=example('video')['records'][0];request.update(provider=name,mode='text_to_video')
            self.assertFalse(adapter.preflight()['ready'])
            with self.assertRaises(MediaBlocked):adapter.generate(request,self.s.path)
        with self.assertRaises(MediaBlocked):LocalSpeechAdapter().synthesize(example('voice')['records'][0],self.s.path)
        with self.assertRaises(MediaBlocked):ReadOnlyAnalyticsAdapter().query('channel_profile','UC'+'a'*22)
        with self.assertRaises(AgentError):ReadOnlyAnalyticsAdapter().query('publish','UC'+'a'*22)
        def broken(*_):raise RuntimeError('SECRET must not escape')
        with self.assertRaises(MediaBlocked) as cm:ReadOnlyAnalyticsAdapter(broken).query('channel_profile','UC'+'a'*22)
        self.assertNotIn('SECRET',str(cm.exception))
    def test_qc_model_observation_remains_unverified(self):
        data=example('qc');rid=self.e.enqueue('qc',data,mode='local')
        self.assertEqual(self.e.execute(rid,complete=lambda *_:{'records':data['records']}),'Awaiting QC')
        tid=next(r['task'] for r in self.e.runs() if r['id']==rid)
        self.assertEqual(self.artifact(tid)['records'][0]['evidence_kind'],'unverified_model')
        with self.s.tx() as db:record=db.execute('SELECT provenance,raw_output FROM specialist_model_attempts').fetchone()
        self.assertEqual(record[0],'simulation');self.assertIn('objective_metadata',record[1])
    def test_branched_project_queue_is_idempotent_and_approval_gated(self):
        from redpad_pipeline.specialist_project import queue_project,DEPENDENCIES
        from tests.test_creative import samples,request
        d=samples();story=self.task('story',request('season',d['season']));self.approve(story)
        director=self.task('director',request('direction',d['direction_story'],source={'$from':story,'path':['artifact']}),[story]);self.approve(director)
        script=self.task('script',request('screenplay',d['screenplay'],source={'$from':story,'path':['artifact']}),[story,director]);self.approve(script)
        inputs={key:example(key) for key in DEPENDENCIES}
        project=queue_project(self.e,inputs,[script,director]);count=len(self.s.tasks())
        again=queue_project(self.e,inputs,[script,director]);self.assertEqual(again,project);self.assertEqual(count,len(self.s.tasks()))
        first=self.e.tick_parallel();self.assertEqual(first[project['runs']['character']],'Awaiting QC');self.assertEqual(first[project['runs']['costume']],'Blocked')
        for key in ('character','art'):self.approve(project['tasks'][key])
        second=self.e.tick_parallel();self.assertEqual(second[project['runs']['costume']],'Awaiting QC')
        self.assertEqual(len(AGENTS),20)
    def test_recovery_preserves_idempotent_run_identity(self):
        rid=self.e.enqueue('art',example('art'),idempotency_key='project:art')
        self.assertEqual(self.e.enqueue('art',example('art'),idempotency_key='project:art'),rid)
        with self.assertRaises(AgentError):self.e.enqueue('character',example('character'),idempotency_key='project:art')
        with self.s.tx() as db:db.execute("UPDATE agent_runs SET state='Running' WHERE id=?",(rid,))
        recovered=self.e.recover(rid);self.assertEqual(self.e.enqueue('art',example('art'),idempotency_key='project:art'),recovered)
    def test_approved_screenplay_generates_bounded_coverage_draft(self):
        from redpad_pipeline.specialist_workflows import screenplay_breakdown
        from tests.test_creative import samples
        screenplay=samples()['screenplay'];rows=screenplay_breakdown(screenplay)
        self.assertEqual(sum(r['seconds'] for r in rows),300);self.assertEqual({r['scene'] for r in rows},{'s1','s2','s3'})
        self.assertEqual(rows,screenplay_breakdown(screenplay))
        data=example('storyboard');data['records']=rows
        result=prepare('storyboard',data);self.assertEqual(len(result['artifact']['derived']['studio_board']['shots']),len(rows))
        screenplay['scenes'][0]['beats']=[]
        with self.assertRaises(AgentError):screenplay_breakdown(screenplay)
    def test_existing_svd_native_mapping_and_output_contract(self):
        from redpad_pipeline.specialist_adapters import LocalVideoAdapter
        request=example('video')['records'][0]
        adapter=LocalVideoAdapter('local-svd')
        with patch.object(adapter,'preflight',return_value={'ready':True}),patch('redpad_pipeline.specialist_adapters.execute_media') as call:
            with self.assertRaises(AgentError):adapter.generate(request,self.s.path)
            call.assert_not_called()
            request.update(width=1024,height=576,fps=7,seconds=25/7)
            call.return_value={'path':'local_animation/synthetic-test/animation.mp4','actual_generation':True,'model':'local-svd-xt'}
            info={'streams':[{'codec_type':'video','width':1024,'height':576}],'duration':25/7}
            with patch('redpad_pipeline.specialist_inspection.inspect_clip',return_value=info):
                result=adapter.generate(request,self.s.path)
            self.assertEqual(call.call_args.args[1]['reference'],'rafi.png')
            self.assertFalse(result['identity_quality_verified']);self.assertIn('editorial guidance',result['prompt_control'])
    def test_simulation_never_marks_inference_verified_even_with_matching_model_name(self):
        self.s.configure('art','injected-test-provider');data=example('art')
        rid=self.e.enqueue('art',data,mode='local')
        self.assertEqual(self.e.execute(rid,complete=lambda *_:{'records':data['records']}),'Awaiting QC')
        self.assertFalse(self.s.status('art')['real_inference_verified']);self.assertEqual(self.s.status('art')['connection'],'Model Not Connected')
