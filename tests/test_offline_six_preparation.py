"""Software-only fixtures. No generated artistic/model evidence."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentError
from redpad_pipeline.screenwriter import LocalUnavailable
from redpad_pipeline.shared_model_services import SharedServices
from redpad_pipeline.offline_specialist_preparation import component_inventory,video_spec,speech_spec,music_spec,casting_assessment,permission,relative
from redpad_pipeline.offline_preparation import prepare_native
from tests.test_offline_11_preparation import OfflineElevenTests
from tests.test_no_gpu_staging import request


class OfflineSixTests(unittest.TestCase):
    setUp=OfflineElevenTests.setUp

    def pin(self,row):return {'id':row['id'],'version':row['version']}

    def video(self):
        # Container-header fixture, never decoded or represented as real footage.
        return self.refs.put('manual.mp4',b'\x00\x00\x00\x18ftypisomMANUAL UNIT FIXTURE','casting',source='MANUAL HEADER ONLY, NOT GENERATED MEDIA',rights='fictional_ai')

    def doc(self):return self.refs.put('consent.txt',b'MANUAL UNIT FIXTURE: NOT REAL CONSENT','casting',source='NOT HUMAN REVIEW',rights='reference_only')

    def anim(self,role='performance'):
        portrait=self.pin(self.image);video=self.pin(self.video());r=request('reference_video','wan_animate2')
        r.update(seconds=3,image_reference=portrait,video_reference=video)
        spec=dict(width=512,height=512,fps=24,frames=73,reference_prompt='Fictional actor motion fixture',actor_id='fictional-unit',
                  permission=dict(identity_kind='fictional',actor_ids=['fictional-unit'],uses=['likeness','motion_transfer'],reference_ids=[portrait['id'],video['id']],consent_reference=None),
                  driving_metadata=dict(reference=video,width=512,height=512,fps=24,frames=73,duration_ms=3042,evidence='MANUAL SUPPLIED METADATA, NOT DECODED'),
                  frame_sequence=[],interactions=[dict(subject='actor',object='chair',start_ms=0,end_ms=2000,constraint='owner supplied contact specification; no physics score')])
        run=self.engine.enqueue(role,{'fixture':True});stage=self.services.stage_request(run,'wan_animate2','reference_video',r)
        return stage,spec

    def ltx(self):
        r=request('text_to_video','ltx25');r['seconds']=3
        run=self.engine.enqueue('video',{'fixture':True});stage=self.services.stage_request(run,'ltx25','text_to_video',r)
        spec=dict(width=512,height=512,fps=24,frames=73,reference_prompt='',driving_metadata=None,actor_id=None,permission=None,frame_sequence=[],interactions=[])
        return stage,spec

    def test_shared_native_wan_preparation_for_all_three_roles_is_not_acting_critic(self):
        for role in ('performance','motion','casting'):
            stage,spec=self.anim(role);job=self.services.prepare_offline_request(stage['id'],spec=spec)
            self.assertEqual(job['native_call_preparation']['arguments']['clip_len'],73)
            self.assertEqual(job['native_call_preparation']['call'],'WanAnimate2MPIPipeline.__call__')
            self.assertFalse(job['launch_authorized']);self.assertEqual(job['worker_module'],'redpad_pipeline.native_local_worker')
            self.assertFalse(job['consent_verified']);self.assertFalse(job['production_ready'])

    def test_wan_rejects_mismatched_fps_duration_and_short_motion_source(self):
        stage,spec=self.anim();r=stage['plan']['request']
        for delta in ({'fps':30},{'frames':72},{'width':513},{'frames':121}):
            with self.assertRaises(AgentError):video_spec(dict(spec,**delta),r,'wan_animate2')
        bad=copy.deepcopy(spec);bad['driving_metadata']['frames']=2
        with self.assertRaises(AgentError):video_spec(bad,r,'wan_animate2')

    def test_real_person_requires_specific_scoped_consent_document(self):
        stage,spec=self.anim();spec['permission']['identity_kind']='authorized_person'
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=spec)
        spec['permission']['consent_reference']=self.pin(self.doc())
        job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(len(job['extra_reference_pins']),1);self.assertFalse(job['consent_verified'])
        bad=copy.deepcopy(spec);bad['permission']['actor_ids']=['different-actor']
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=bad)

    def test_consent_permission_cannot_reuse_different_media_or_use(self):
        stage,spec=self.anim();r=stage['plan']['request']
        for field,value in [('uses',['voice_clone']),('reference_ids',['different'])]:
            bad=copy.deepcopy(spec);bad['permission'][field]=value
            with self.assertRaises(AgentError):video_spec(bad,r,'wan_animate2')

    def test_temporal_sequence_requires_distinct_source_bound_ordered_frames(self):
        stage,spec=self.anim();r=stage['plan']['request'];a=self.pin(self.image)
        spec['frame_sequence']=[dict(reference=a,time_ms=0,source_video=r['video_reference']),dict(reference=a,time_ms=1000,source_video=r['video_reference'])]
        with self.assertRaises(AgentError):video_spec(spec,r,'wan_animate2')
        spec['frame_sequence'][1]['reference']={'id':'different-frame','version':1}
        spec['frame_sequence'][1]['source_video']={'id':'different-video','version':1}
        with self.assertRaises(AgentError):video_spec(spec,r,'wan_animate2')

    def test_object_interaction_outside_clip_or_unrequested_score_rejected(self):
        stage,spec=self.anim();r=stage['plan']['request']
        for delta in ({'end_ms':4000},{'physics_score':99}):
            bad=copy.deepcopy(spec);bad['interactions'][0].update(delta)
            with self.assertRaises(AgentError):video_spec(bad,r,'wan_animate2')

    def test_ltx_exact_split_preparation_has_no_guessed_upsampler_or_executable_argv(self):
        stage,spec=self.ltx();job=self.services.prepare_offline_request(stage['id'],spec=spec)
        call=job['native_call_preparation'];self.assertIn('ModelPaths.from_split',call['call'])
        self.assertIsNone(call['spatial_upsampler']);self.assertFalse(job['launch_authorized'])
        self.assertEqual(job['source_revision'],'f0f2f8607189c78a72420b2b63cb1975b5eca179')
        self.assertNotIn('argv',job);self.assertFalse(job['contract_only']);self.assertTrue(job['native_worker_implemented'])

    def test_ltx_rejects_motion_transfer_quantization_and_hidden_endpoint_controls(self):
        stage,spec=self.ltx();r=stage['plan']['request']
        for field,value in [('quantization','int8'),('endpoint','https://example.invalid'),('driving_metadata',{'invented':True})]:
            with self.assertRaises(AgentError):video_spec(dict(spec,**{field:value}),r,'ltx25')

    def test_ltx_component_inventory_uses_stat_only_never_reads_weight_bytes(self):
        folder=self.root/'stat_only';folder.mkdir()
        path=folder/'diffusion_models';path.mkdir();(path/'ltx-2.5-22b-distilled-transformer-bf16.safetensors').write_bytes(b'MANUAL FIXTURE')
        original=Path.open
        def deny_weights(p,*args,**kwargs):
            if str(p).endswith(('.safetensors','.pt','.pth')):raise AssertionError('WEIGHTS MUST NEVER BE OPENED')
            return original(p,*args,**kwargs)
        with patch.object(Path,'open',deny_weights):out=component_inventory('ltx25',folder)
        self.assertTrue(out['files'][0]['present']);self.assertFalse(out['files'][0]['size_matches'])
        self.assertFalse(out['ready_to_load']);self.assertFalse(out['weights_opened'])
        self.assertIn('spatial',out['unresolved_components'][0])

    def test_all_five_candidate_inventories_missing_files_fail_closed_without_download(self):
        for pid in ('wan_animate2','ltx25','indic_speak','indicf5','ace15'):
            out=component_inventory(pid,self.root/'absent');self.assertFalse(out['ready_to_load'])
            self.assertTrue(all(not f['present'] and not f['hash_verified'] for f in out['files']))

    def test_component_inventory_rejects_symlink_and_path_traversal(self):
        target=self.root/'real';target.mkdir();alias=self.root/'alias';alias.symlink_to(target,target_is_directory=True)
        with self.assertRaises(AgentError):component_inventory('ace15',alias)
        for s in ('../model.pt','/tmp/model','https://bad/model','a\\b','a//b'):
            with self.assertRaises(AgentError):relative(s)

    def speech(self,pid='indicf5'):
        op='reference_voice' if pid=='indicf5' else 'text_to_audio';r=request(op,pid)
        spec=dict(style_notes='Owner cue: restrained; unsupported native style stays annotation',pronunciation_notes='বাংলাদেশি উচ্চারণ এখনও পরীক্ষিত নয়',reference_metadata=None,permission=None)
        if pid=='indicf5':
            import io,wave
            b=io.BytesIO()
            with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\x01\0'*2400)
            audio=self.refs.put('manual-signal.wav',b.getvalue(),'audio',source='MANUAL PCM TEST SIGNAL; NOT AI OR HUMAN SPEECH',rights='fictional_ai')
            r.update(reference=self.pin(audio),consent_reference=self.pin(self.doc()),reference_transcript='ম্যানুয়াল পরীক্ষার লেখা')
            spec['reference_metadata']=dict(reference=r['reference'],sample_rate=24000,channels=1,duration_ms=100,transcript=r['reference_transcript'])
            spec['permission']=dict(identity_kind='fictional',actor_ids=[r['speaker_id']],uses=['voice_clone'],reference_ids=[r['reference']['id']],consent_reference=r['consent_reference'])
        run=self.engine.enqueue('voice',{'fixture':True});stage=self.services.stage_request(run,pid,op,r)
        return stage,spec

    def test_indicf5_reference_transcript_consent_and_original_bengali_preserved(self):
        stage,spec=self.speech()
        from tests.test_selected_voice_binding import reviewed_fixture
        spec=reviewed_fixture(self,stage,spec);job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(job['original_request']['text'],stage['plan']['request']['text'])
        self.assertEqual(job['native_call_preparation']['sample_rate'],24000)
        self.assertEqual(job['native_call_preparation']['entry'],'redpad_pipeline.native_voice_worker.build_selected_f5');self.assertFalse(job['consent_verified'])
        bad=copy.deepcopy(spec);bad['reference_metadata']['transcript']='different'
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=bad)

    def test_indicf5_cannot_substitute_consent_or_enable_remote_custom_code(self):
        stage,spec=self.speech();bad=copy.deepcopy(spec);bad['permission']['consent_reference']=None
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=bad)
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=dict(spec,trust_remote_code=True))

    def test_indic_speak_keeps_native_entry_unbound_until_exact_revision_verified(self):
        stage,spec=self.speech('indic_speak');job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(job['native_call_preparation']['entry'],'inference.TTS.__call__');self.assertEqual(job['source_revision'],'76e0814f189321efe550011850cd288dae366aad')
        with self.assertRaises(AgentError):speech_spec(dict(spec,reference_metadata={'reference':'fake'}),stage['plan']['request'],'indic_speak')

    def music(self):
        r=request('music','ace15');r['seconds']=3
        run=self.engine.enqueue('music',{'fixture':True});stage=self.services.stage_request(run,'ace15','music',r)
        spec=dict(task_type='text2music',instrumental=True,lyrics='',thinking=False,sample_rate=48000,cue=dict(scene_id='fixture-scene',scene_duration_ms=4000,cues=[dict(id='cue',kind='music',start_ms=1000,end_ms=4000,beat='owner supplied scene beat',source_reference=None)]))
        return stage,spec

    def test_ace15_exact_native_params_and_deny_auto_download_sync_policy(self):
        stage,spec=self.music();job=self.services.prepare_offline_request(stage['id'],spec=spec)
        call=job['native_call_preparation'];self.assertEqual(call['entry'],'acestep.inference.generate_music')
        self.assertTrue(call['arguments']['params']['instrumental']);self.assertFalse(call['arguments']['params']['thinking'])
        self.assertFalse(call['initialization_policy']['automatic_download']);self.assertFalse(call['initialization_policy']['model_code_sync'])
        self.assertIn('weights_only=True',call['unsafe_auxiliary_policy']['expected_loader'])
        self.assertFalse(job['contract_only']);self.assertEqual(job['worker_module'],'redpad_pipeline.native_local_worker')

    def test_ace_rejects_cover_vocals_sfx_substitution_and_cue_duration_mismatch(self):
        stage,spec=self.music();r=stage['plan']['request']
        for k,v in [('task_type','cover'),('instrumental',False),('thinking',True),('sample_rate',24000)]:
            with self.assertRaises(AgentError):music_spec(dict(spec,**{k:v}),r)
        for k,v in [('kind','sfx'),('end_ms',3500)]:
            bad=copy.deepcopy(spec);bad['cue']['cues'][0][k]=v
            with self.assertRaises(AgentError):music_spec(bad,r)

    def casting(self):
        return dict(actor_id='fictional-unit',character_id='fictional-character',portrait=self.pin(self.image),performance=None,voice=None,voice_transcript=None,partner_actor_id=None,partner_performance=None,consent_reference=None,identity_kind='fictional',findings=[])

    def test_casting_portrait_cannot_prove_acting_voice_or_chemistry(self):
        spec=self.casting()
        for category in ('performance','voice','chemistry'):
            bad=copy.deepcopy(spec);bad['findings']=[dict(category=category,reference_ids=[spec['portrait']['id']],observation='MANUAL ASSERTION',certainty='observed')]
            with self.assertRaises(AgentError):casting_assessment(bad)
        out=casting_assessment(spec);self.assertFalse(out['production_ready']);self.assertFalse(out['acting_verified'])

    def test_casting_pair_performance_and_voice_need_real_reference_bindings(self):
        spec=self.casting();spec['partner_actor_id']='other'
        with self.assertRaises(AgentError):casting_assessment(spec)
        spec=self.casting();spec['voice']=self.pin(self.doc());spec['voice_transcript']='fixture'
        with self.assertRaises(AgentError):casting_assessment(spec)

    def test_casting_assessment_task_handoff_persists_but_never_creates_approval(self):
        spec=self.casting();run=self.engine.enqueue('casting',{'fixture':True})
        stage=self.services.stage_tool_request(run,'casting_assessment',spec)
        self.assertEqual(stage,self.services.staged_request(stage['id']))
        result=stage['plan']['check_result'];self.assertTrue(result['independent_qc_required']);self.assertTrue(result['director_inspection_required']);self.assertTrue(result['producer_identity_lock_required'])

    def test_prepared_six_requests_restart_and_spec_change_keep_separate_ids(self):
        stage,spec=self.ltx();a=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(a,SharedServices(self.store).prepared_offline_request(a['prepared_id']))
        self.assertEqual(a,self.services.prepare_offline_request(stage['id'],spec=spec))
        other=dict(spec,width=640);b=self.services.prepare_offline_request(stage['id'],spec=other)
        self.assertNotEqual(a['prepared_id'],b['prepared_id'])

    def test_extra_consent_evidence_change_stales_existing_preparation(self):
        stage,spec=self.anim();spec['permission']['consent_reference']=self.pin(self.doc())
        job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.refs.path(self.refs.get(spec['permission']['consent_reference']['id'])).write_bytes(b'changed fixture')
        with self.assertRaises(AgentError):self.services.prepared_offline_request(job['prepared_id'])

    def test_source_bridge_change_stales_prepared_requests(self):
        stage,spec=self.ltx();job=self.services.prepare_offline_request(stage['id'],spec=spec)
        old=Path.read_bytes
        def changed(p):return b'changed source fixture' if p.name=='offline_specialist_preparation.py' else old(p)
        with patch.object(Path,'read_bytes',changed):
            with self.assertRaises(AgentError):self.services.prepared_offline_request(job['prepared_id'])

    def test_unknown_native_family_bundle_verification_must_not_be_silently_ignored(self):
        stage,spec=self.ltx()
        with self.assertRaises(LocalUnavailable):self.services.prepare_offline_request(stage['id'],spec=spec,verify_bundle=True)

    def test_registry_profiles_and_other_thirteen_agents_preserved(self):
        import hashlib
        root=Path(__file__).resolve().parents[1];b=json.loads((root/'verification/offline_6/preservation_baseline.json').read_text())
        reg=json.loads((root/'assets/professional/phase3_candidates.json').read_text());led=json.loads((root/'assets/professional/phase3_19agent_no_gpu_staging.json').read_text())
        def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(sha(reg['profiles']),b['profiles_sha256'])
        for k,h in b['untouched_agents'].items():self.assertEqual(sha(reg['agents'][k]),h)
        for row in led['roles']:
            if row['agent'] in b['untouched_rows']:self.assertEqual(sha(row),b['untouched_rows'][row['agent']])
        self.assertEqual(hashlib.sha256((root/'assets/professional/models.json').read_bytes()).hexdigest(),b['models_sha256'])

    def test_voice_wav_metadata_checked_without_transcript_or_speaker_claim(self):
        stage,spec=self.speech();job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertTrue(job['reference_audio_header']['metadata_checked'])
        self.assertFalse(job['reference_audio_header']['transcript_verified'])
        bad=copy.deepcopy(spec);bad['reference_metadata']['sample_rate']=48000
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=bad)

    def test_real_portrait_cannot_be_declared_fictional_for_wan_or_casting(self):
        self.image=self.refs.update(self.image['id'],self.image['version'],rights='authorized_person')
        stage,spec=self.anim()
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=spec)
        r=self.casting();run=self.engine.enqueue('casting',{'fixture':True})
        with self.assertRaises(AgentError):self.services.stage_tool_request(run,'casting_assessment',r)

    def test_ltx_upsampler_is_same_pinned_repository_but_not_approved_or_downloaded(self):
        from redpad_pipeline.offline_specialist_preparation import LTX_AUXILIARY
        self.assertEqual(LTX_AUXILIARY['repo'],'Lightricks/LTX-2.5')
        self.assertEqual(LTX_AUXILIARY['revision'],'49b093a39c19169a8a81721dcc541e07e945232f')
        self.assertIn('spatial',LTX_AUXILIARY['path']);self.assertIsNone(LTX_AUXILIARY['sha256'])
        self.assertFalse(LTX_AUXILIARY['download_approved']);self.assertFalse(LTX_AUXILIARY['license_approved'])

    def test_inventory_unsupported_candidate_uses_deterministic_error_not_fallback(self):
        for pid in ('unknown-model','wan22_5','indic_parler'):
            with self.assertRaises(AgentError):component_inventory(pid,self.root/'absent')
