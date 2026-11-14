"""CPU-only original fixtures; no generated speech, inference or human acceptance."""
import ast,copy,hashlib,io,json,sys,types,unittest,wave
from pathlib import Path
from unittest.mock import patch
from tests.test_producer_control import ProducerTests
from tests.test_no_gpu_staging import request
from redpad_pipeline.agents import AgentError
from redpad_pipeline.voice_consent import VoiceConsents
from redpad_pipeline.voice_source_policy import binding_status,require_selected_source
from redpad_pipeline.native_voice_worker import run,validate_wav,build_public_engine,safe_vocos


class VoiceCastingTests(unittest.TestCase):
    task=ProducerTests.task;approve=ProducerTests.approve;body=ProducerTests.body
    image=ProducerTests.image;casting=ProducerTests.casting;lock=ProducerTests.lock
    def setUp(self):
        ProducerTests.setUp(self)
        for target in ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open','redpad_pipeline.screenwriter.LocalWriter.__call__','redpad_pipeline.native_execution.NativeExecution.run','redpad_pipeline.kaggle_runtime.probe'):
            p=patch(target,side_effect=AssertionError('NO NETWORK/MODEL/GPU/PROCESS'));p.start();self.addCleanup(p.stop)
        p=patch.dict(sys.modules,{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bodhan_genai':None,'snac':None});p.start();self.addCleanup(p.stop)
        self.w=self.c.casting.voice_workflow()
    def spec(self):return dict(style_notes='Owner cue only; not inferred performance',pronunciation_notes='বাংলাদেশি উচ্চারণ এখনও পরীক্ষিত নয়',reference_metadata=None,permission=None)
    def draft(self,pid='indic_speak',cast=None):
        cast=cast or self.casting()[0];r=request('text_to_audio',pid)
        return self.w.prepare(cast,'candidate-rafi',pid,r,self.spec())
    def pin(self,r):return {'id':r['id'],'version':r['version']}
    def audio(self,rate=24000,channels=1):
        b=io.BytesIO()
        with wave.open(b,'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(b'\0\0'*int(rate*.2)*channels)
        return b.getvalue()

    def test_public_source_and_exact_selected_gated_sources_are_separate(self):
        speak=binding_status('indic_speak');self.assertTrue(speak['adapter_implemented']);self.assertFalse(speak['source_blocked']);self.assertIsNone(speak['fallback'])
        self.assertFalse(binding_status('indicf5')['source_blocked']);self.assertFalse(binding_status('indic_parler')['source_blocked'])
        for pid in ('indic_speak','indicf5'):
            require_selected_source(pid)
            self.assertFalse(binding_status(pid)['launch_authorized'])

    def test_unreviewed_selected_voice_fails_before_any_model_import(self):
        with self.assertRaises(AgentError):run({'install':{},'request':{}})
        self.assertIsNone(sys.modules['torch'])

    def test_missing_source_casting_draft_abstains_without_hidden_fallback(self):
        from redpad_pipeline.voice_source_policy import PUBLIC_SOURCE
        with patch.dict(PUBLIC_SOURCE['indic_speak'],selected_source_verified=False):
            d=self.draft();self.assertTrue(d['abstain']);self.assertFalse(d['professional_accepted']);self.assertEqual(d['plan']['profile'],'indic_speak')
            h=self.w.handoff(d['id']);self.assertIsNotNone(h['voice_run'])
            with self.assertRaises(AgentError):self.w.stage(d['id'])
            self.assertEqual(self.e.execute(h['voice_run']),'Blocked')

    def test_persistent_idempotent_casting_handoff_uses_existing_store(self):
        d=self.draft();h=self.w.handoff(d['id']);self.assertEqual(h,self.w.handoff(d['id']))
        from redpad_pipeline.casting_voice import CastingVoice
        self.assertEqual(h,CastingVoice(self.c.casting).get(d['id']))
        self.assertEqual(h['snapshot']['actor_id'],'actor-rafi');self.assertEqual(h['snapshot']['character_id'],'rafi')

    def test_explicit_parler_department_choice_stages_existing_worker_without_generation(self):
        d=self.draft('indic_parler');job=self.w.stage(d['id'])
        self.assertEqual(job['worker_module'],'redpad_pipeline.speech_worker');self.assertFalse(job['inference_completed'])
        self.assertEqual(d['plan']['profile'],'indic_parler');self.assertIn('explicit choice',d['candidate_origin'])
        self.assertEqual(job['payload']['text'],d['plan']['request']['text'])

    def test_candidate_identity_and_unknown_model_fail_closed(self):
        cast=self.casting()[0]
        for candidate,pid in [('missing','indic_speak'),('candidate-rafi','new-voice-model')]:
            with self.assertRaises(AgentError):self.w.prepare(cast,candidate,pid,request('text_to_audio','indic_speak'),self.spec())

    def test_casting_reference_metadata_change_stales_audition(self):
        d=self.draft('indic_parler');pin=d['snapshot']['references'][0]
        self.c.refs.update(pin['id'],pin['version'],notes='changed UNIT rights context')
        with self.assertRaises(AgentError):self.w.get(d['id'])

    def test_casting_reference_bytes_change_stales_prepared_native_request(self):
        from redpad_pipeline.shared_model_services import SharedServices
        d=self.draft('indic_parler');job=self.w.stage(d['id']);pin=d['snapshot']['references'][0]
        self.c.refs.path(pin).write_bytes(b'MANUAL CORRUPTED IMAGE')
        with self.assertRaises(AgentError):SharedServices(self.s).prepared_offline_request(job['prepared_id'])

    def test_casting_source_revision_changes_invalidate_voice_handoff(self):
        d=self.draft('indic_parler');h=self.w.handoff(d['id']);cast=d['snapshot']['task']
        with self.s.tx() as db:db.execute('UPDATE tasks SET revision=revision+1 WHERE id=?',(cast,))
        with self.assertRaises(AgentError):self.w.get(d['id'])
        self.assertEqual(self.e.execute(h['voice_run']),'Blocked')

    def test_director_inspection_contains_explicit_voice_blocker_without_approval(self):
        d=self.draft();rid=self.c.casting.queue_review(d['snapshot']['task'])
        with self.s.tx() as db:r=db.execute('SELECT inputs FROM agent_runs WHERE id=?',(rid,)).fetchone()
        packet=json.loads(r[0])['context']['voice_auditions'][0]
        self.assertFalse(packet['voice_source_blocked']);self.assertFalse(packet['voice_accepted']);self.assertFalse(packet['chemistry_accepted'])

    def test_voice_plan_change_stales_prior_director_inspection(self):
        cast=self.casting()[0];rid=self.c.casting.queue_review(cast)
        self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='MANUAL DIRECTOR FIXTURE',delegations=[],risks=[])),'Awaiting QC')
        task=next(r['task'] for r in self.e.runs() if r['id']==rid)
        self.draft(cast=cast)
        with self.s.tx() as db:
            with self.assertRaises(AgentError):self.s._current(db,self.s._task(db,task))

    def test_mock_or_unrelated_native_voice_output_cannot_be_attached_as_real(self):
        from redpad_pipeline.native_execution import NativeExecution
        d=self.draft('indic_parler');self.w.stage(d['id']);mock=NativeExecution(self.s).queue_fixture()
        with self.assertRaises(AgentError):self.w.attach_result(d['id'],mock)

    def test_director_qc_producer_lock_still_required(self):
        cast=self.casting()[0];self.draft(cast=cast)
        with self.assertRaises(AgentError):self.c.casting.lock(cast,'missing-director',['candidate-rafi'],'UNIT')
        with self.assertRaises(AgentError):self.s.review(cast,1,'Approve','UNIT direct bypass','owner')

    def test_uploaded_consent_document_does_not_create_review(self):
        cast=self.casting()[0];audio=self.c.refs.put('manual.wav',self.audio(),'audio',source='MANUAL SILENCE NOT REAL VOICE',rights='fictional_ai')
        doc=self.c.refs.put('review.txt',b'MANUAL FIXTURE NOT CONSENT','casting',source='UNIT',rights='reference_only')
        spec=dict(actor_id='actor-rafi',reference=self.pin(audio),document=self.pin(doc),transcript_sha256=hashlib.sha256('পরীক্ষা'.encode()).hexdigest(),uses=['voice_clone'],reviewer='UNIT reviewer, NOT HUMAN ACCEPTANCE',scope_task=cast,note='SOFTWARE FIXTURE ONLY')
        consent=VoiceConsents(self.s)
        with self.assertRaises(AgentError):consent.confirm(spec)
        return_value=consent.confirm(spec,confirmed=True)
        with self.s.tx() as db:r=json.loads(db.execute('SELECT payload FROM voice_consent_reviews WHERE id=?',(return_value,)).fetchone()[0])
        self.assertFalse(r['legal_authenticity_verified'])

    def consent(self):
        cast=self.casting()[0];audio=self.c.refs.put('manual.wav',self.audio(),'audio',source='MANUAL SILENCE NOT REAL SPEECH',rights='fictional_ai');doc=self.c.refs.put('manual-consent.txt',b'UNIT NOT CONSENT','casting',source='MANUAL UNIT DOC')
        spec=dict(actor_id='actor-rafi',reference=self.pin(audio),document=self.pin(doc),transcript_sha256=hashlib.sha256('পরীক্ষা'.encode()).hexdigest(),uses=['voice_clone'],reviewer='UNIT MOCK REVIEWER',scope_task=cast,note='NO REAL CONSENT OR HUMAN REVIEW')
        consent=VoiceConsents(self.s);id=consent.confirm(spec,confirmed=True)
        args=dict(actor_id='actor-rafi',reference=self.pin(audio),document=self.pin(doc),transcript='পরীক্ষা',scope_task=cast)
        return consent,id,args

    def test_consent_actor_transcript_audio_and_task_cannot_be_reused(self):
        consent,id,args=self.consent();self.assertFalse(consent.require(id,**args)['artistic_accepted'])
        for k,v in [('actor_id','other-actor'),('transcript','অন্য কথা'),('reference',dict(id='missing',version=1))]:
            with self.assertRaises(AgentError):consent.require(id,**dict(args,**{k:v}))

    def test_revoked_or_changed_consent_evidence_invalidates_review(self):
        consent,id,args=self.consent();consent.revoke(id,'UNIT owner','UNIT withdrawal',confirmed=True)
        with self.assertRaises(AgentError):consent.require(id,**args)
        consent,id,args=self.consent();row=self.c.refs.get(args['document']['id']);self.c.refs.path(row).write_bytes(b'CHANGED UNIT DOC')
        with self.assertRaises(AgentError):consent.require(id,**args)

    def test_consent_scope_revision_change_is_not_silently_reused(self):
        consent,id,args=self.consent()
        with self.s.tx() as db:db.execute('UPDATE tasks SET revision=revision+1 WHERE id=?',(args['scope_task'],))
        with self.assertRaises(AgentError):consent.require(id,**args)

    def test_wav_format_rate_channels_and_truncation_checked_without_listening(self):
        p=self.s.path.parent/'manual.wav';p.write_bytes(self.audio());out=validate_wav(p,24000)
        self.assertFalse(out['speaker_verified']);self.assertFalse(out['listening_reviewed'])
        with self.assertRaises(AgentError):validate_wav(p,44100)
        p.write_bytes(self.audio(channels=2))
        with self.assertRaises(AgentError):validate_wav(p,24000)
        p.write_bytes(self.audio()[:-50])
        with self.assertRaises(AgentError):validate_wav(p,24000)

    def test_voice_and_casting_logs_do_not_capture_raw_upstream_diagnostics(self):
        from redpad_pipeline.native_execution import worker_log_targets
        import subprocess
        a,b=object(),object()
        self.assertEqual(worker_log_targets('voice','indic_parler',a,b),(subprocess.DEVNULL,subprocess.DEVNULL))
        self.assertEqual(worker_log_targets('casting','wan_animate2',a,b),(subprocess.DEVNULL,subprocess.DEVNULL))
        self.assertEqual(worker_log_targets('video','ltx25',a,b),(a,b))

    def test_public_worker_imports_no_heavy_model_library_at_module_scope(self):
        p=Path(__file__).resolve().parents[1]/'redpad_pipeline/native_voice_worker.py'
        for n in ast.parse(p.read_text()).body:
            if isinstance(n,ast.Import):self.assertFalse(any(a.name in ('torch','transformers','snac','bodhan_genai') for a in n.names))

    def test_public_engine_uses_local_only_explicit_codec_and_no_model_fallback(self):
        calls=[]
        class Backend:pass
        class Obj:
            @classmethod
            def from_pretrained(cls,*a,**kw):calls.append(kw);return cls()
            def eval(self):return self
        class Engine:
            def __init__(self,*a,**kw):self.kw=kw
        fake_torch=types.SimpleNamespace(bfloat16='BF16 SOFTWARE FIXTURE')
        root=self.s.path.parent;engine=build_public_engine(Engine,Backend,fake_torch,Obj,Obj,Obj,lambda c:c,lambda s,v:(s,v),root)
        self.assertTrue(all(x['local_files_only'] and x['trust_remote_code'] is False for x in calls))
        self.assertEqual(engine.kw['device'],'cuda');self.assertFalse(engine.kw['vocos'])
        # Missing codec files fail before any loader/downloader could run.
        with self.assertRaises(AgentError):engine.kw['snac_loader'](str(root/'snac'),device='cuda')

    def test_unsafe_vocos_pickle_or_custom_config_is_rejected_without_loading_weights(self):
        p=self.s.path.parent/'manual.pt';p.write_bytes(b'UNIT NOT MODEL WEIGHTS');calls=[]
        def loader(*a,**kw):calls.append(kw);return {'config':{'model':{'unsafe':{}}}}
        fake=types.SimpleNamespace(load=loader)
        with self.assertRaises(AgentError):safe_vocos(fake,p,lambda cfg:None,'cuda')
        self.assertTrue(calls[0]['weights_only']);self.assertEqual(calls[0]['map_location'],'cpu')

    def test_bengali_original_text_kept_separate_from_normalized_worker_payload(self):
        cast=self.casting()[0];r=request('text_to_audio','indic_parler');r['text']='বড়ো কথা নয়—পরীক্ষা।'
        d=self.w.prepare(cast,'candidate-rafi','indic_parler',r,self.spec());job=self.w.stage(d['id'])
        self.assertEqual(self.w.get(d['id'])['plan']['request']['text'],r['text']);self.assertFalse(job['inference_completed'])

    def test_other_seventeen_profiles_and_director_script_records_preserved(self):
        root=Path(__file__).resolve().parents[1];b=json.loads((root/'verification/voice_casting/preservation_baseline.json').read_text());reg=json.loads((root/'assets/professional/phase3_candidates.json').read_text());ledger=json.loads((root/'assets/professional/phase3_19agent_no_gpu_staging.json').read_text())
        def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        for k,h in b['untouched_agents'].items():self.assertEqual(sha(reg['agents'][k]),h)
        for row in ledger['roles']:
            if row['agent'] in b['untouched_rows']:self.assertEqual(sha(row),b['untouched_rows'][row['agent']])
        self.assertEqual(sha(reg['profiles']),b['profiles_sha256'])

    def assessment_spec(self,cast):
        candidate=self.body(cast)['artifact']['records'][0]
        return dict(actor_id=candidate['actor_id'],character_id=candidate['character'],portrait=candidate['image_refs'][0],performance=None,voice=None,voice_transcript=None,partner_actor_id=None,partner_performance=None,consent_reference=None,identity_kind='fictional',findings=[])

    def test_casting_assessment_is_bound_to_real_character_candidate_and_single_existing_store(self):
        cast=self.casting()[0];spec=self.assessment_spec(cast);a=self.w.assess(cast,'candidate-rafi',spec)
        self.assertEqual(a,self.w.assess(cast,'candidate-rafi',spec));self.assertFalse(a['artistic_accepted'])
        self.assertFalse(a['check_result']['acting_verified'])
        bad=dict(spec,character_id='invented-character')
        with self.assertRaises(AgentError):self.w.assess(cast,'candidate-rafi',bad)

    def test_pair_casting_requires_current_partner_and_actual_performance_refs(self):
        cast=self.casting()[0];spec=self.assessment_spec(cast)
        for partner in ('actor-hazera','unknown-partner'):
            with self.assertRaises(AgentError):self.w.assess(cast,'candidate-rafi',dict(spec,partner_actor_id=partner))
        portrait_claim=dict(spec,findings=[dict(category='performance',reference_ids=[spec['portrait']['id']],observation='MANUAL INVALID ASSERTION',certainty='observed')])
        with self.assertRaises(AgentError):self.w.assess(cast,'candidate-rafi',portrait_claim)

    def test_performance_assessment_and_voice_handoff_share_revision_and_stale_media_guards(self):
        cast=self.casting()[0];spec=self.assessment_spec(cast)
        clip=self.c.refs.put('manual.mp4',b'\x00\x00\x00\x18ftypisomUNIT HEADER NOT GENERATED VIDEO','casting',source='MANUAL HEADER UNIT FIXTURE',rights='fictional_ai')
        spec['performance']=self.pin(clip);a=self.w.assess(cast,'candidate-rafi',spec)
        d=self.w.prepare(cast,'candidate-rafi','indic_parler',request('text_to_audio','indic_parler'),self.spec(),assessment_id=a['id'])
        job=self.w.stage(d['id']);self.assertFalse(job['inference_completed'])
        self.c.refs.path(clip).write_bytes(b'CHANGED MANUAL VIDEO HEADER')
        with self.assertRaises(AgentError):self.w.get(d['id'])
        from redpad_pipeline.shared_model_services import SharedServices
        with self.assertRaises(AgentError):SharedServices(self.s).prepared_offline_request(job['prepared_id'])

    def test_readiness_casting_complete_with_explicit_voice_blocker_not_false_readiness(self):
        from redpad_pipeline.no_gpu_staging import readiness
        r=readiness();self.assertEqual(sum(x['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for x in r.values()),19)
        self.assertEqual(r['voice']['engineering_status'],'NO-GPU ENGINEERING COMPLETE');self.assertEqual(r['casting']['engineering_status'],'NO-GPU ENGINEERING COMPLETE')
        self.assertFalse(r['casting']['voice_binding_status']['indic_speak']['source_blocked'])
        self.assertFalse(r['casting']['runtime_verified']);self.assertFalse(r['casting']['production_ready'])

    def test_shared_source_lock_matches_authoritative_git_blob_correction(self):
        root=Path(__file__).resolve().parents[1];c=json.loads((root/'verification/voice_casting/source_lock_correction.json').read_text());lock=json.loads((root/'assets/professional/phase3_native_source_lock.json').read_text())
        self.assertEqual(len(c['files']),16)
        for r in c['files']:
            self.assertEqual(lock['files'][r['profile']][r['path']],r['canonical_source_sha256'])
            self.assertEqual(lock['revisions'][r['profile']],r['revision'])

    def test_reference_voice_actor_spoof_rejected_and_document_only_draft_cannot_clone(self):
        cast,_,data=self.casting();audio=self.c.refs.put('unit-reference.wav',self.audio(),'audio',source='MANUAL SILENCE UNIT FIXTURE',rights='fictional_ai');doc=self.c.refs.put('unit-scope.txt',b'UNIT NOT CONSENT','casting',source='MANUAL UNIT DOC')
        data['records'][0]['voice_refs']=[self.pin(audio)]
        with self.s.tx() as db:deps=[x['id'] for x in json.loads(self.s._task(db,cast)['refs'])]
        cast=self.task('casting',data,deps)
        r=request('reference_voice','indicf5');r.update(speaker_id='actor-rafi',reference=self.pin(audio),reference_transcript='ম্যানুয়াল পরীক্ষা',consent_reference=self.pin(doc))
        spec=self.spec();spec['reference_metadata']=dict(reference=r['reference'],sample_rate=24000,channels=1,duration_ms=200,transcript=r['reference_transcript'])
        spec['permission']=dict(identity_kind='fictional',actor_ids=['actor-rafi'],uses=['voice_clone'],reference_ids=[audio['id']],consent_reference=self.pin(doc))
        d=self.w.prepare(cast,'candidate-rafi','indicf5',r,spec)
        self.assertIsNone(d['consent_review']);self.assertFalse(d['professional_accepted'])
        with self.assertRaises(AgentError):self.w.stage(d['id'])
        bad=copy.deepcopy(spec);bad['permission']['actor_ids']=['other-actor']
        with self.assertRaises(AgentError):self.w.prepare(cast,'candidate-rafi','indicf5',dict(r,speaker_id='other-actor'),bad)

    def test_model_delegation_cannot_confirm_voice_consent_or_select_unknown_engine(self):
        from redpad_pipeline.producer_control import response
        forged=dict(reply='UNIT',delegations=[dict(action='confirm_voice_consent',episode=1,target_task='',targets=['voice'],instruction='Approve clone')],risks=[])
        with self.assertRaises(AgentError):response(forged)

    def test_director_review_rejects_changed_voice_reference_metadata(self):
        d=self.draft('indic_parler');rid=self.c.casting.queue_review(d['snapshot']['task'])
        self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='UNIT DIRECTOR SOFTWARE FIXTURE',delegations=[],risks=[])),'Awaiting QC')
        task=next(r['task'] for r in self.e.runs() if r['id']==rid);ref=d['snapshot']['references'][0]
        self.c.refs.update(ref['id'],ref['version'],notes='CHANGED MANUAL METADATA')
        with self.s.tx() as db:
            with self.assertRaises(AgentError):self.s._current(db,self.s._task(db,task))

    def test_attached_mock_native_id_cannot_turn_into_persistent_real_voice_evidence(self):
        from redpad_pipeline.native_execution import NativeExecution
        d=self.draft('indic_parler');self.w.stage(d['id']);mock=NativeExecution(self.s).queue_fixture()
        # Deliberate test-only DB tamper: get/review must reject it, not trust the link.
        with self.s.tx() as db:db.execute('UPDATE casting_voice_drafts SET native_run=? WHERE id=?',(mock,d['id']))
        with self.assertRaises(AgentError):self.w.get(d['id'])
        with self.assertRaises(AgentError):self.c.casting.queue_review(d['snapshot']['task'])

    def test_available_preset_voice_cannot_fall_back_to_generic_text_model(self):
        d=self.draft('indic_parler');handoff=self.w.handoff(d['id'])
        self.assertEqual(self.e.execute(handoff['voice_run']),'Blocked')
        row=next(r for r in self.e.runs() if r['id']==handoff['voice_run'])
        self.assertIn('native worker',row['error'])

    def test_voice_source_profile_revision_cannot_drift_to_an_unreviewed_checkpoint(self):
        from redpad_pipeline.no_gpu_staging import load
        registry,roles=load();bad=copy.deepcopy(registry);bad['profiles']['indic_speak']['revision']='0'*40
        with patch('redpad_pipeline.no_gpu_staging.load',return_value=(bad,roles)):
            with self.assertRaises(AgentError):binding_status('indic_speak')

    def test_casting_handoff_cannot_drop_approved_character_source(self):
        cast=self.casting()[0]
        with self.s.tx() as db:db.execute("UPDATE tasks SET refs='[]' WHERE id=?",(cast,))
        with self.assertRaises(AgentError):self.draft(cast=cast)

    def test_prepared_native_voice_stales_if_casting_dependency_pins_are_dropped(self):
        d=self.draft('indic_parler');job=self.w.stage(d['id'])
        with self.s.tx() as db:db.execute("UPDATE tasks SET refs='[]' WHERE id=?",(d['snapshot']['task'],))
        from redpad_pipeline.shared_model_services import SharedServices
        with self.assertRaises(AgentError):SharedServices(self.s).prepared_offline_request(job['prepared_id'])
