"""No GPU/inference/weights. Labeled 2x2 images and tiny metadata are test fixtures."""
import copy,io,json,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.shared_model_services import SharedServices
from redpad_pipeline.producer_references import References
from redpad_pipeline.no_gpu_staging import readiness,load,resolve_profile
from redpad_pipeline.offline_department_contracts import inspection_spec,visual_response,state_findings,temporal_spec,voice_metadata,cue_manifest,edit_manifest,casting_evidence,critic_control
from redpad_pipeline.offline_preparation import verify_existing_bundle
from redpad_pipeline.screenwriter import LocalUnavailable
from tests.test_no_gpu_staging import request


class OfflineElevenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.store=AgentStore(self.root/'agent_control.sqlite3');self.engine=Engine(self.store);self.services=SharedServices(self.store);self.refs=References(self.store)
        from PIL import Image
        b=io.BytesIO();Image.new('RGB',(2,2)).save(b,format='PNG')
        self.image=self.refs.put('manual-fixture.png',b.getvalue(),'location',source='MANUAL 2x2 UNIT FIXTURE',rights='fictional_ai')
        for target in ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open','redpad_pipeline.kaggle_runtime.probe','redpad_pipeline.shared_model_services.SharedServices.execute','redpad_pipeline.screenwriter.LocalWriter.__call__'):
            p=patch(target,side_effect=AssertionError('NO RESOURCE / INFERENCE PERMITTED'));p.start();self.addCleanup(p.stop)
        p=patch.dict('sys.modules',{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bitsandbytes':None});p.start();self.addCleanup(p.stop)

    def image_stage(self,role):
        pin={'id':self.image['id'],'version':self.image['version']};run=self.engine.enqueue(role,{'fixture':True})
        stage=self.services.stage_request(run,'vision7','image_inspection',dict(images=[pin],question='Inspect visible evidence only',seed=117))
        spec={'reference_ids':[pin['id']],'dimensions':['spatial','framing','lighting','prop'],'source_scope':'supplied_references_only','metadata':{}}
        return stage,spec

    def test_all_five_visual_department_bindings_build_existing_local_worker_payload(self):
        for role in ('qc','location','cinematographer','continuity','editing'):
            with self.subTest(role=role):
                staged,spec=self.image_stage(role);job=self.services.prepare_offline_request(staged['id'],spec=spec)
                self.assertEqual(job['worker_module'],'redpad_pipeline.vision_worker')
                self.assertEqual(job['payload']['images'][0]['sha256'],self.image['sha256'])
                self.assertFalse(job['launch_authorized']);self.assertFalse(job['inference_completed'])
                self.assertEqual(job['status'],'RUNTIME BLOCKED');self.assertFalse(Path(job['payload']['output']).exists())

    def test_location_cannot_claim_real_world_verification_or_unbound_references(self):
        stage,spec=self.image_stage('location')
        for bad in (dict(spec,source_scope='verified_real_location'),dict(spec,reference_ids=['invented'])):
            with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=bad)

    def test_cinematography_lens_needs_source_metadata(self):
        stage,spec=self.image_stage('cinematographer');spec['metadata']={'lens_mm':35}
        with self.assertRaises(AgentError):self.services.prepare_offline_request(stage['id'],spec=spec)
        spec['metadata']['lens_source']='supplied camera metadata, not pixel inference'
        self.assertFalse(self.services.prepare_offline_request(stage['id'],spec=spec)['launch_authorized'])

    def test_grounded_response_contract_abstention_and_seeded_false_positive(self):
        _,spec=self.image_stage('qc')
        clean='{"findings":[],"abstain":true}'
        self.assertTrue(critic_control(clean,spec,[])['control_pass'])
        f={'category':'prop','reference_id':self.image['id'],'region':[0,0,1,1],'observation':'MANUAL TEST ASSERTION','certainty':'visible'}
        raw=json.dumps({'findings':[f],'abstain':False})
        self.assertFalse(critic_control(raw,spec,[])['control_pass'])
        uncertain=json.dumps({'findings':[dict(f,certainty='inferred')],'abstain':False})
        self.assertFalse(critic_control(uncertain,spec,[])['control_pass'])
        self.assertTrue(critic_control(raw,spec,['prop'])['control_pass'])
        self.assertFalse(visual_response(raw,spec)['judgment_accuracy_verified'])
        for bad in (dict(f,reference_id='unknown'),dict(f,region=[0,0,2,1])):
            with self.assertRaises(AgentError):visual_response(json.dumps({'findings':[bad],'abstain':False}),spec)
        with self.assertRaises(AgentError):visual_response('{"findings":[],"abstain":true,"approved":true}',spec)

    def test_consistent_states_abstain_and_contradictory_supplied_states_are_flagged(self):
        r=dict(entity='bag',kind='prop',scene='s1',time_ms=0,property='color',value='blue',evidence_id='fixture1')
        self.assertEqual(state_findings([r,dict(r,evidence_id='fixture2')])['findings'],[])
        self.assertEqual(len(state_findings([r,dict(r,value='red',evidence_id='fixture2')])['findings']),1)
        self.assertEqual(state_findings([r,dict(r,value='red',time_ms=1000)])['findings'],[])

    def test_temporal_sampling_does_not_claim_physics_or_acting_judgment(self):
        r=dict(source_video={'id':'fixture','version':1},duration_ms=2000,frame_times_ms=[0,1000],checks=['contact','gesture'])
        self.assertFalse(temporal_spec(r)['temporal_judgment_verified'])
        for times in ([0,0],[0,2000],[[1],2]):
            with self.assertRaises(AgentError):temporal_spec(dict(r,frame_times_ms=times))

    def test_bengali_voice_normalization_keeps_original_annotations_and_consent_pending(self):
        r=dict(original_text='শুধু পরীক্ষা',language='bn',speaker_id='fictional-unit',pronunciation_notes='Owner note',style_notes='restrained',reference=None,consent_reference=None)
        out=voice_metadata(r);self.assertEqual(out['original_text'],r['original_text']);self.assertFalse(out['consent_verified'])
        with self.assertRaises(AgentError):voice_metadata(dict(r,reference={'id':'voice-fixture','version':1}))

    def test_scene_cues_validate_duration_and_beat_but_do_not_generate_audio(self):
        r=dict(scene_id='s1',scene_duration_ms=2000,cues=[dict(id='a',kind='music',start_ms=0,end_ms=2000,beat='quiet realization',source_reference=None)])
        self.assertFalse(cue_manifest(r)['audio_generated'])
        bad=copy.deepcopy(r);bad['cues'][0]['end_ms']=3000
        with self.assertRaises(AgentError):cue_manifest(bad)

    def edit(self):
        return dict(duration_ms=1000,tolerance_ms=20,sources=[dict(reference={'id':'clip','version':1},duration_ms=2000,streams=['video','audio'])],cuts=[dict(source_id='clip',track=t,in_ms=0,out_ms=1000,timeline_ms=0) for t in ('video','audio')])

    def test_edit_manifest_bounds_streams_and_av_sync_without_rendering(self):
        r=self.edit();self.assertFalse(edit_manifest(r)['rendered'])
        for mutate in (lambda x:x['cuts'][0].update(out_ms=3000),lambda x:x['cuts'][1].update(out_ms=900),lambda x:x['cuts'][0].update(source_id='unknown')):
            bad=copy.deepcopy(r);mutate(bad)
            with self.assertRaises(AgentError):edit_manifest(bad)

    def test_edit_and_cue_checks_are_integrated_but_missing_actual_sources_fail_closed(self):
        run=self.engine.enqueue('editing',{'fixture':True})
        with self.assertRaises(AgentError):self.services.stage_tool_request(run,'edit_manifest',self.edit())
        run=self.engine.enqueue('music',{'fixture':True})
        r=dict(scene_id='s1',scene_duration_ms=1000,cues=[dict(id='a',kind='sfx',start_ms=0,end_ms=900,beat='door',source_reference=None)])
        stage=self.services.stage_tool_request(run,'cue_manifest',r)
        self.assertEqual(stage,self.services.staged_request(stage['id']))

    def test_casting_separates_appearance_from_acting_voice_chemistry_and_locks(self):
        r=dict(actor_id='fictional-unit',identity_kind='fictional',image_references=[{'id':self.image['id'],'version':1}],voice_reference=None,performance_reference=None,partner_actor_id=None,consent_reference=None)
        result=casting_evidence(r);self.assertFalse(result['acting_verified']);self.assertTrue(result['existing_casting_director_inspection_and_producer_lock_required'])
        with self.assertRaises(AgentError):casting_evidence(dict(r,identity_kind='authorized_person'))
        with self.assertRaises(AgentError):casting_evidence(dict(r,partner_actor_id='someone'))
        run=self.engine.enqueue('casting',{'fixture':True});stage=self.services.stage_tool_request(run,'casting_evidence',r)
        self.assertEqual(stage,self.services.staged_request(stage['id']))

    def test_native_wan_and_svd_keep_supported_worker_controls(self):
        from redpad_pipeline.offline_media import validate_request
        for pid,op in [('wan22_5','text_to_video'),('svd_xt','image_to_video')]:
            run=self.engine.enqueue('video',{'fixture':True});r=request(op,pid)
            if op=='image_to_video':r['reference']={'id':self.image['id'],'version':1}
            stage=self.services.stage_request(run,pid,op,r);job=self.services.prepare_offline_request(stage['id'])
            validate_request(job['payload']['engine'],job['payload']['request'])
            self.assertEqual(job['worker_module'],'redpad_pipeline.offline_worker');self.assertFalse(job['launch_authorized'])

    def test_parler_and_stable_audio_prepare_only_their_existing_local_payloads(self):
        for role,pid,op,module in [('voice','indic_parler','text_to_audio','speech_worker'),('music','stable_audio_small','sound_effect','audio_worker')]:
            run=self.engine.enqueue(role,{'fixture':True});stage=self.services.stage_request(run,pid,op,request(op,pid))
            job=self.services.prepare_offline_request(stage['id']);self.assertEqual(job['worker_module'],'redpad_pipeline.'+module)
            self.assertFalse(job['inference_completed'])

    def test_unverified_new_families_remain_contract_only_and_never_name_an_executable_worker(self):
        for role,pid,op in [('performance','wan_animate2','reference_video'),('video','ltx25','text_to_video'),('voice','indic_speak','text_to_audio'),('voice','indicf5','reference_voice'),('music','ace15','music')]:
            # Pure descriptor fixture; reference rights are enforced when creating real staged rows.
            stage={'id':'fixture','plan':{'role':role,'profile':pid,'request':request(op,pid)}}
            from redpad_pipeline.offline_preparation import prepare_native
            job=prepare_native(stage,self.store);self.assertTrue(job['contract_only']);self.assertIsNone(job['worker_module'])

    def test_absent_model_bundle_fails_without_importing_or_downloading_anything(self):
        with self.assertRaises(LocalUnavailable):verify_existing_bundle('vision7',self.root/'absent',self.root/'absent.approval.json')
        stage,spec=self.image_stage('qc')
        with patch('redpad_pipeline.offline_media.MODEL_ROOT',self.root/'empty_models'):
            with self.assertRaises(LocalUnavailable):self.services.prepare_offline_request(stage['id'],spec=spec,verify_bundle=True)

    def test_exact_bundle_binding_uses_manual_metadata_fixture_not_model_weights(self):
        from redpad_pipeline.offline_media import checkpoint_manifest
        registry,_=load();p=resolve_profile('vision7',registry);p=copy.deepcopy(p)
        b=b'MANUAL UNIT FIXTURE NOT MODEL WEIGHTS';folder=self.root/'manual_bundle';folder.mkdir()
        (folder/'config.json').write_text('{}');(folder/'part.safetensors').write_bytes(b)
        (folder/'redpad_model_origin.json').write_text(json.dumps({'repo':p['repo'],'revision':p['revision']}))
        p['selected_weight_files']=[{'path':'part.safetensors','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}]
        approval=self.root/'manual.approval.json';approval.write_text(json.dumps(dict(approved=True,model=p['repo'],owner='UNIT FIXTURE',license_note='NOT ACTUAL LICENSE ACCEPTANCE',manifest=checkpoint_manifest(folder,'config.json'))))
        with patch('redpad_pipeline.offline_preparation.resolve_profile',return_value=p):
            bound=verify_existing_bundle('vision7',folder,approval);self.assertFalse(bound['actual_runtime_verified'])
            (folder/'part.safetensors').write_bytes(b'changed fixture')
            with self.assertRaises(AgentError):verify_existing_bundle('vision7',folder,approval)

    def test_scope_and_readiness_separate_engineering_from_inference(self):
        r=readiness();self.assertEqual(sum(x['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for x in r.values()),13)
        for k in ('qc','location','cinematographer','continuity','editing'):self.assertEqual(r[k]['engineering_status'],'NO-GPU ENGINEERING COMPLETE');self.assertFalse(r[k]['runtime_verified'])
        for k in ('performance','motion','video','voice','music','casting'):self.assertEqual(r[k]['engineering_status'],'PARTIAL')

    def test_prepared_requests_survive_restart_are_idempotent_and_invalidate_with_source(self):
        stage,spec=self.image_stage('continuity');job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(job,self.services.prepare_offline_request(stage['id'],spec=spec))
        self.assertEqual(job,SharedServices(self.store).prepared_offline_request(job['prepared_id']))
        self.refs.path(self.image).write_bytes(b'changed manual fixture')
        with self.assertRaises(AgentError):self.services.prepared_offline_request(job['prepared_id'])

    def test_spec_changes_do_not_overwrite_previous_preparation_and_payload_tamper_fails(self):
        stage,spec=self.image_stage('qc');a=self.services.prepare_offline_request(stage['id'],spec=spec)
        spec['dimensions']=['prop'];b=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertNotEqual(a['prepared_id'],b['prepared_id']);self.assertNotEqual(a['payload']['output'],b['payload']['output'])
        with self.store.tx() as db:db.execute("UPDATE offline_prepared_requests SET payload='{}' WHERE id=?",(a['prepared_id'],))
        with self.assertRaises(AgentError):self.services.prepared_offline_request(a['prepared_id'])

    def test_stable_audio_small_does_not_use_older_sampler_cfg_or_step_defaults(self):
        from redpad_pipeline.offline_audio import STABLE_AUDIO_SMALL_RECIPE,validate
        from redpad_pipeline.no_gpu_staging import prepare
        self.assertEqual(STABLE_AUDIO_SMALL_RECIPE,{'steps':8,'cfg_scale':1.0,'sampler_type':'pingpong'})
        r=request('sound_effect','stable_audio_small');validate('stable-audio-small',r)
        self.assertFalse(prepare('music','stable_audio_small','sound_effect',r)['inference_verified'])
        with self.assertRaises(AgentError):prepare('music','stable_audio_small','sound_effect',dict(r,steps=50))

    def test_motion_frame_binding_does_not_become_a_temporal_physics_critic(self):
        stage,spec=self.image_stage('motion');job=self.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(job['worker_module'],'redpad_pipeline.vision_worker')
        self.assertFalse(job['inference_completed']);self.assertEqual(readiness()['motion']['engineering_status'],'PARTIAL')
