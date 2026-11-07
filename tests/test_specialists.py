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
    def test_storyboard_shot_revision_preserves_other_shots(self):
        data=example('storyboard');base=prepare('storyboard',data)['artifact'];data.update(base=base,targets=['shot2']);data['records'][1]['composition']='Close-up of key'
        result=prepare('storyboard',data);self.assertEqual(result['revision_changes'],['shot2']);self.assertEqual(result['artifact']['records'][0],base['records'][0])
        self.assertEqual(result['artifact']['derived']['reference_status'],'Not generated')
        data['records'][0]['order']=9
        with self.assertRaises(AgentError):prepare('storyboard',data)
    def test_performance_transition_and_intensity(self):
        data=example('performance');row=copy.deepcopy(data['records'][0]);row.update(id='p2',emotion_from='joyful');data['records'].append(row)
        self.assertTrue(prepare('performance',data)['findings'])
        row['intensity']=11
        with self.assertRaises(AgentError):prepare('performance',data)
    def test_cinematography_axis(self):
        data=example('cinematographer');data['records'][-1]['axis_side']='B'
        self.assertEqual(len(prepare('cinematographer',data)['findings']),1)
        data['records'][-1]['axis_reset']=True;self.assertFalse(prepare('cinematographer',data)['findings'])
    def test_motion_contact_and_pose(self):
        data=example('motion');self.assertFalse(prepare('motion',data)['findings']);data['records'][-1]['contact']='none'
        self.assertEqual(prepare('motion',data)['findings'][0]['code'],'missing_support')
        data['records'][-1]['from_pose']='sitting';data['records'][-1]['to_pose']='walking'
        self.assertTrue(any(f['code']=='impossible_pose_transition' for f in prepare('motion',data)['findings']))
    def test_continuity_revision_impact(self):
        data=example('continuity');data['records'][-1]['value']='white';result=prepare('continuity',data)
        self.assertEqual(result['artifact']['derived']['affected_shots'],['shot3'])
        data['records'][-1]['change_reason']='পরদিন';self.assertFalse(prepare('continuity',data)['findings'])
    def test_video_capabilities(self):
        data=example('video');data['records'][0]['mode']='text_to_video'
        with self.assertRaises(AgentError):prepare('video',data)
        data['records'][0]['provider']='wan-local';result=prepare('video',data)
        self.assertTrue(result['artifact']['derived']['provider_capabilities']['wan-local']['installed_adapter'])
        self.assertFalse(result['media_generated'])
    def test_voice_lexicon_and_speaker_identity(self):
        data=example('voice');data['records'][0]['lexicon']={'খালা':'খা-লা'}
        self.assertIn('খা-লা',prepare('voice',data)['artifact']['derived']['lip_sync_cues'][0]['synthesis_text'])
        data['records'][1]['speaker']='voice-rafi'
        with self.assertRaises(AgentError):prepare('voice',data)
    def test_music_reference_and_license(self):
        data=example('music');data['records'][0]['asset']='https://external/audio.wav'
        with self.assertRaises(AgentError):prepare('music',data)
        data['records'][0]['asset']='pending';data['records'][0]['license']='unknown'
        self.assertEqual(prepare('music',data)['findings'][0]['severity'],'blocker')
    def test_edit_subtitle_source_and_missing_assets(self):
        data=example('editing');result=prepare('editing',data)
        self.assertEqual(result['artifact']['derived']['duration_seconds'],6);self.assertIsNone(result['artifact']['derived']['export_path'])
        self.assertTrue(result['findings']);data['records'][0]['subtitle_end']=3
        with self.assertRaises(AgentError):prepare('editing',data)
    def test_synthetic_media_inspection_not_generation(self):
        import subprocess
        from redpad_pipeline.specialist_inspection import inspect_clip
        root=Path(self.tmp.name)/'agent_media';root.mkdir();path=root/'synthetic-test.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=64x64:r=8','-t','0.5','-c:v','libx264','-pix_fmt','yuv420p',str(path)],check=True)
        report=inspect_clip(path.name,self.s.path);self.assertEqual(report['streams'][0]['width'],64)
        rid=self.e.enqueue('video',{'operation':'inspect_clip','asset':path.name},mode='media');self.assertEqual(self.e.execute(rid),'Awaiting QC')
        body=json.loads(json.loads(self.s.outputs()[0]['payload'])['summary']);self.assertFalse(body['model_inference']);self.assertFalse(body['media_generated'])
        with self.assertRaises(AgentError):inspect_clip('../escape.mp4',self.s.path)
        path.write_text('not a video')
        with self.assertRaises(AgentError):inspect_clip(path.name,self.s.path)
    def test_production_graph_resource_and_cycles(self):
        data=example('production_manager')
        with patch('redpad_pipeline.readiness.inspect_resources',return_value={'cuda_device':False}):
            result=prepare('production_manager',data)['artifact']['derived']
        self.assertIn('job-video',result['resource_blocked']);self.assertIn('job-art',result['ready']);self.assertEqual(result['critical_path_estimate_seconds'],70)
        data['records'][0]['dependencies']=['job-video']
        with self.assertRaises(AgentError):prepare('production_manager',data)
    def test_growth_concept_comparison_and_limits(self):
        data=example('growth');self.assertEqual(len(prepare('growth',data)['artifact']['derived']['concept_comparison']),2)
        data['records'][0]['title_bn']='a'*101
        with self.assertRaises(AgentError):prepare('growth',data)
    def test_youtube_prepare_only_no_network(self):
        data=example('youtube')
        with patch('socket.socket',side_effect=AssertionError('No network')):
            result=prepare('youtube',data)['artifact']['derived'];self.assertFalse(result['publish']);self.assertFalse(result['upload'])
            for action in ('publish','upload','schedule'):
                data['records'][0]['action']=action
                with self.assertRaises(AgentError):prepare('youtube',data)
        data['records'][0]['action']='prepare';data['records'][0]['oauth_scope']='youtube.upload'
        with self.assertRaises(AgentError):prepare('youtube',data)
