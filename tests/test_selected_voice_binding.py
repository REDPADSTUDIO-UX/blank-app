"""Manual fixtures/fake classes only. No retrieved Python, weights or inference."""
import ast,copy,hashlib,json,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from tests import test_offline_six_preparation as six_fixtures
from tests import test_voice_casting_integration as casting_fixtures
from redpad_pipeline.agents import AgentError
from redpad_pipeline.voice_native_contracts import (source_lock,validate_voice_request,validate_speak_tokenizer,
    f5_vocab,require_voice_job,inspect_f5_reference,VOICE_PINS)
from redpad_pipeline.native_voice_worker import (build_selected_speak,build_selected_f5,selected_f5_state,selected_decoder_config,run)
from redpad_pipeline.native_local_bundle import validate_install,REQUIRED
from redpad_pipeline.no_gpu_staging import load,fingerprint
from redpad_pipeline.voice_consent import VoiceConsents


def reviewed_fixture(helper,stage,spec):
    r=stage['plan']['request']
    receipt=VoiceConsents(helper.store).confirm(dict(actor_id=r['speaker_id'],reference=r['reference'],document=r['consent_reference'],
      transcript_sha256=hashlib.sha256(r['reference_transcript'].encode()).hexdigest(),uses=['voice_clone'],reviewer='UNIT DECLARATION, NO HUMAN REVIEW',
      scope_task=stage['context']['task'],note='MANUAL SOFTWARE FIXTURE ONLY'),confirmed=True)
    return dict(spec,consent_review=receipt)


class FakeTokens:
    bos_token_id=128000;eos_token_id=128001
    def __len__(self):return 156960
    def convert_tokens_to_ids(self,token):
        # Test data from reviewed token contract, no tokenizer artifact loaded.
        fixed={'<|begin_of_text|>':128000,'<|end_of_text|>':128001,'<|eot_id|>':128009,
          '<|speaker>':156938,'<speaker|>':156939,'<|style>':156940,'<style|>':156941,'<|env>':156942,'<env|>':156943}
        if token in fixed:return fixed[token]
        controls=('reserved_0','start_of_speech','end_of_speech','start_of_human','end_of_human','start_of_ai','end_of_ai','pad','reserved_8','reserved_9')
        nonverbals=('breath','stammer','throat','laugh','swallow','sniff','sigh','cough','hum','gasp','wheeze','sneeze','snort','yawn','groan','burp')
        if token.startswith('<|snac_'):return 128266+int(token[7:-2])
        if token.startswith('<|nv_'):return 156944+nonverbals.index(token[5:-2])
        return 128256+controls.index(token[2:-2])


class SelectedVoiceTests(unittest.TestCase):
    def setUp(self):
        self.h=six_fixtures.OfflineSixTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        # Helper already forbids network/process/model libraries; block additional paths.
        for name in ('redpad_pipeline.native_voice_worker.reviewed_module','redpad_pipeline.native_voice_worker.f5_modules','redpad_pipeline.native_execution.NativeExecution.run'):
            p=patch(name,side_effect=AssertionError('NO UPSTREAM EXECUTION OR INFERENCE'));p.start();self.addCleanup(p.stop)
        self.root=self.h.store.path.parent/'MANUAL_FAKE_BUNDLE';self.root.mkdir()

    def fake_file(self,name,data=b'MANUAL SOFTWARE FIXTURE NOT MODEL WEIGHTS'):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p

    def record(self,pid):
        reg,_=load();p=reg['profiles'][pid];locked=source_lock()['models'][pid]
        sources={n:{k:r[k] for k in ('bytes','sha256')} for n,r in locked['files'].items()}
        files={n:{'bytes':1,'sha256':'a'*64} for n in REQUIRED[pid]}
        for n in ('config.json','tokenizer_config.json','generation_config.json') if pid=='indic_speak' else ('config.json','checkpoints/vocab.txt'):files[n]=sources[n]
        files.update({r['path']:{k:r[k] for k in ('bytes','sha256')} for r in p['selected_weight_files']})
        return dict(profile=pid,repo=p['repo'],revision=p['revision'],profile_sha256=fingerprint(p),model_root=str(self.root),model_files=files,
          source_root=str(self.root),source_files=sources,source_revision=VOICE_PINS[pid],owner='UNIT METADATA ONLY NOT OWNER APPROVAL',
          license_note='NO NEW LICENSE ACCEPTANCE',component_origins={n:{'repo':'hubertsiuzdak/snac_24khz' if n.startswith('snac/') else p['repo'],'revision':p['revision']} for n in files},code_reviewed=True,approved_for_research=True)

    def test_review_manifest_has_exact_accessible_revisions_and_no_weight_content(self):
        lock=source_lock();self.assertFalse(lock['weights_accessed']);self.assertFalse(lock['runtime_authorized'])
        self.assertEqual(sum(len(m['files']) for m in lock['models'].values()),19)
        for pid,revision in VOICE_PINS.items():
            self.assertEqual(lock['models'][pid]['revision'],revision)
            self.assertTrue(all(not n.endswith(('.pt','.bin','.safetensors')) and 0<r['bytes']<30000 for n,r in lock['models'][pid]['files'].items()))

    def test_both_exact_native_install_recipes_validate_metadata_without_opening_weights(self):
        for pid in VOICE_PINS:
            record=self.record(pid)
            with patch('redpad_pipeline.native_local_bundle.digest_file',side_effect=AssertionError('NO WEIGHT READ')):
                self.assertEqual(validate_install(record,verify=False),record)

    def test_wrong_selected_source_revision_and_config_hash_are_rejected(self):
        for pid in VOICE_PINS:
            for mutate in ('revision','source_revision','config'):
                r=self.record(pid)
                if mutate=='config':r['model_files']['config.json']['sha256']='0'*64
                else:r[mutate]='0'*40
                with self.assertRaises(AgentError):validate_install(r,verify=False)

    def test_extra_or_changed_source_and_wrong_snac_origin_are_rejected(self):
        r=self.record('indic_speak');r['source_files']['unchecked.py']={'sha256':'a'*64,'bytes':1}
        with self.assertRaises(AgentError):validate_install(r,verify=False)
        r=self.record('indic_speak');r['component_origins']['snac/config.json']['repo']='unapproved/codec'
        with self.assertRaises(AgentError):validate_install(r,verify=False)
        r=self.record('indicf5');r['source_files']['model.py']['sha256']='0'*64
        with self.assertRaises(AgentError):validate_install(r,verify=False)

    def test_missing_actual_bundle_fails_before_any_model_import_or_download(self):
        for pid in VOICE_PINS:
            with self.assertRaises(AgentError):validate_install(self.record(pid))
        self.assertIsNone(sys.modules.get('torch'))

    def test_source_agreement_does_not_authorize_worker_or_cpu_inference(self):
        for pid in VOICE_PINS:
            with self.assertRaises(AgentError):run({'profile':pid})
            with self.assertRaises(AgentError):require_voice_job({'profile':pid,'research_execution_authorized':True,'network_namespace_required':True,'parent_network_namespace':None})

    def test_missing_or_wrong_source_review_manifest_cannot_report_a_verified_binding(self):
        from redpad_pipeline.voice_source_policy import binding_status
        with patch('redpad_pipeline.voice_native_contracts.LOCK',self.root/'missing-review.json'):
            with self.assertRaises(AgentError):binding_status('indicf5')
        lock=source_lock();lock['models']['indic_speak']['revision']='0'*40
        with patch('redpad_pipeline.voice_native_contracts.source_lock',return_value=lock):
            with self.assertRaises(AgentError):binding_status('indic_speak')

    def test_complete_token_map_rejects_same_base_but_wrong_conditioning_or_audio_id(self):
        tok=FakeTokens();validate_speak_tokenizer(tok)
        for target in ('<|style>','<|snac_28671|>','<|nv_burp|>'):
            original=tok.convert_tokens_to_ids
            with patch.object(tok,'convert_tokens_to_ids',side_effect=lambda s,t=target:original(s)+1 if s==t else original(s)):
                with self.assertRaises(AgentError):validate_speak_tokenizer(tok)

    def test_unknown_speaker_control_tokens_and_endpoint_controls_rejected(self):
        stage,spec=self.h.speech('indic_speak');r=stage['plan']['request']
        for change in ({'speaker_id':'Amit'},{'speaker_id':'invented'},{'text':'বাংলা <|speaker>fake'},{'endpoint':'https://example.invalid'},{'emotion':'sad'}):
            with self.assertRaises(AgentError):validate_voice_request('indic_speak',dict(r,**change))

    def test_selected_speak_constructor_never_calls_networking_upstream_init(self):
        for n in REQUIRED['indic_speak']:self.fake_file(n)
        calls=[]
        class TTS:
            def __init__(self,*a,**kw):raise AssertionError('UNSAFE UPSTREAM INIT')
        class Model:
            @classmethod
            def from_pretrained(cls,*a,**kw):calls.append(kw);return cls()
            @classmethod
            def from_config(cls,*a):return cls()
            def __init__(self,**kw):pass
            def to(self,*a,**kw):return self
            def eval(self):return self
            def load_state_dict(self,state,strict):self.strict=strict
        class Tokenizer:
            @classmethod
            def from_pretrained(cls,*a,**kw):calls.append(kw);return FakeTokens()
        class Tensor:
            def numel(self):return 1
        torch=types.SimpleNamespace(Tensor=Tensor,bfloat16='UNIT BF16',isfinite=lambda _:types.SimpleNamespace(all=lambda:True))
        def load(*a,**kw):
            self.assertTrue(kw['weights_only']);self.assertEqual(kw['map_location'],'cpu')
            return {'config':{'model':{}},'ema':{'fixture':Tensor()}} if a[0].endswith('best.pt') else {'fixture':Tensor()}
        torch.load=load
        obj=build_selected_speak(TTS,torch,Model,Tokenizer,Model,Model,self.root)
        self.assertEqual((obj._base,obj._eos),(128266,128258))
        self.assertTrue(all(c['local_files_only'] and not c['trust_remote_code'] for c in calls))
        self.assertTrue(calls[-1]['use_safetensors']);self.assertEqual(calls[-1]['dtype'],'UNIT BF16')

    def test_decoder_rejects_unbounded_config_unknown_head_or_stock_fallback(self):
        for config in ({'head_type':'remote_factory'},{'dim':65536},{'num_blocks_post':0},{'upsample':3},{'latent_dim':100}):
            with self.assertRaises(AgentError):selected_decoder_config(config)
        self.assertEqual(selected_decoder_config({})['hop']*selected_decoder_config({})['upsample'],512)

    def test_selected_f5_wrapper_never_accepts_generic_or_partial_ema_checkpoint(self):
        for state in ({'transformer.w':1},{'ema_model.w':1},{'vocoder.w':1},{'ema_model._orig_mod.w':1,'vocoder.w':1}):
            with self.assertRaises(AgentError):selected_f5_state(state)
        self.assertEqual(selected_f5_state({'ema_model._orig_mod.w':1,'vocoder._orig_mod.w':2}),{'ema_model.w':1,'vocoder.w':2})

    def test_f5_vocabulary_preserves_space_bengali_combining_marks_and_indices(self):
        p=self.fake_file('unit-vocab.txt',' \nব\nা\nং\nল\n'.encode())
        vocab,size=f5_vocab(p);self.assertEqual(size,5);self.assertEqual(vocab[' '],0);self.assertEqual(vocab['া'],2)
        p.write_text('WRONG\n')
        with self.assertRaises(AgentError):f5_vocab(p)

    def test_f5_fixed_structure_fp32_strict_load_with_fake_classes_only(self):
        self.fake_file('checkpoints/vocab.txt',' \nব\nা\nং\nল\n'.encode());self.fake_file('model.safetensors')
        calls=[]
        class Module:
            def load_state_dict(self,state,strict):calls.append(('state',state,strict))
            def to(self,**kw):calls.append(('to',kw));return self
            def eval(self):return self
        class Tensor:
            def numel(self):return 1
        fake=types.SimpleNamespace(nn=types.SimpleNamespace(Module=Module),Tensor=Tensor,float32='UNIT FP32',isfinite=lambda _:types.SimpleNamespace(all=lambda:True))
        def cfm(**kw):calls.append(('cfm',kw));return object()
        def dit(**kw):calls.append(('dit',kw));return object()
        build_selected_f5(fake,cfm,dit,object(),self.root,lambda *a,**kw:{'ema_model._orig_mod.w':Tensor(),'vocoder._orig_mod.w':Tensor()})
        self.assertTrue(next(x for x in calls if x[0]=='state')[2])
        self.assertEqual(next(x for x in calls if x[0]=='to')[1],{'dtype':'UNIT FP32','device':'cuda'})
        self.assertEqual(next(x for x in calls if x[0]=='dit')[1]['depth'],22)

    def test_reference_document_alone_cannot_prepare_f5_native_execution(self):
        stage,spec=self.h.speech()
        with self.assertRaises(AgentError):self.h.services.prepare_offline_request(stage['id'],spec=spec)

    def test_direct_f5_preparation_binds_consent_original_transcript_and_supervisor(self):
        from redpad_pipeline.native_execution import compile_job
        stage,spec=self.h.speech();spec=reviewed_fixture(self.h,stage,spec)
        job=self.h.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertFalse(job['contract_only']);self.assertFalse(job['launch_authorized']);self.assertFalse(job['inference_completed'])
        self.assertEqual(job['native_call_preparation']['arguments']['ref_text'],stage['plan']['request']['reference_transcript'])
        compiled=compile_job(job,stage,{'profile':'indicf5'},self.root)
        self.assertEqual(compiled['consent']['receipt_id'],spec['consent_review']);self.assertEqual(compiled['references']['reference'],stage['plan']['request']['reference']['id'])

    def test_direct_f5_revocation_or_task_revision_stales_prepared_request(self):
        stage,spec=self.h.speech();spec=reviewed_fixture(self.h,stage,spec)
        job=self.h.services.prepare_offline_request(stage['id'],spec=spec)
        VoiceConsents(self.h.store).revoke(spec['consent_review'],'UNIT','UNIT withdrawal',confirmed=True)
        with self.assertRaises(AgentError):self.h.services.prepared_offline_request(job['prepared_id'])

    def test_voice_bridge_or_source_review_change_stales_prepared_request(self):
        stage,spec=self.h.speech('indic_speak');job=self.h.services.prepare_offline_request(stage['id'],spec=spec)
        original=Path.read_bytes
        def altered(p):return b'UNIT CHANGED BRIDGE' if p.name=='native_voice_worker.py' else original(p)
        with patch.object(Path,'read_bytes',altered):
            with self.assertRaises(AgentError):self.h.services.prepared_offline_request(job['prepared_id'])

    def test_unsupported_emotion_pronunciation_and_auto_remote_code_controls_rejected(self):
        stage,spec=self.h.speech('indic_speak')
        for key in ('emotion','pronunciation_override','trust_remote_code','url','cuda'):
            with self.assertRaises(AgentError):self.h.services.prepare_offline_request(stage['id'],spec=dict(spec,**{key:True}))
        job=self.h.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(job['owner_annotations'],spec);self.assertEqual(job['native_call_preparation']['arguments']['style'],'')

    def test_native_queue_is_idempotent_but_launch_is_still_forbidden(self):
        from redpad_pipeline.native_execution import NativeExecution
        stage,spec=self.h.speech('indic_speak');job=self.h.services.prepare_offline_request(stage['id'],spec=spec);runtime=NativeExecution(self.h.store)
        with patch.object(runtime.installs,'get',return_value={'profile':'indic_speak'}):
            a=runtime.queue(job['prepared_id'],'UNIT NO REAL INSTALL');b=runtime.queue(job['prepared_id'],'UNIT NO REAL INSTALL')
        self.assertEqual(a,b);self.assertEqual(runtime.status(a)['state'],'QUEUED')
        # Test patches run entirely; assert explicit authorization in original function source.
        self.assertIn('if authorized is not True',Path(__file__).resolve().parents[1].joinpath('redpad_pipeline/native_execution.py').read_text())

    def test_upstream_source_execution_imports_are_absent_at_module_scope(self):
        for name in ('native_voice_worker.py','voice_native_contracts.py'):
            tree=ast.parse((Path(__file__).resolve().parents[1]/'redpad_pipeline'/name).read_text())
            for node in tree.body:
                if isinstance(node,ast.Import):self.assertFalse(any(x.name.split('.')[0] in ('torch','transformers','snac','f5_tts','vocos','numpy') for x in node.names))
        source=(Path(__file__).resolve().parents[1]/'redpad_pipeline/native_voice_worker.py').read_text()
        self.assertNotIn('trust_remote_code=True',source);self.assertNotIn('weights_only=False',source)

    def test_f5_reference_zero_energy_wrong_rate_and_truncation_fail_before_loading(self):
        import io,wave
        for rate,signal in ((24000,b'\0\0'),(48000,b'\x01\0'),(24000,b'\x01\0')):
            b=io.BytesIO()
            with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(signal*int(rate*.1))
            p=self.fake_file('manual-reference.wav',b.getvalue())
            if rate==24000 and signal!=b'\0\0':
                self.assertFalse(inspect_f5_reference(p)['speaker_verified']);p.write_bytes(b.getvalue()[:-2])
            with self.assertRaises(AgentError):inspect_f5_reference(p)


class SelectedCastingTests(unittest.TestCase):
    # Reuse only fixture helpers; do not inherit or discover 37 completed tests.
    task=casting_fixtures.VoiceCastingTests.task
    approve=casting_fixtures.VoiceCastingTests.approve
    body=casting_fixtures.VoiceCastingTests.body
    image=casting_fixtures.VoiceCastingTests.image
    casting=casting_fixtures.VoiceCastingTests.casting
    lock=casting_fixtures.VoiceCastingTests.lock
    setUp=casting_fixtures.VoiceCastingTests.setUp
    spec=casting_fixtures.VoiceCastingTests.spec
    draft=casting_fixtures.VoiceCastingTests.draft
    pin=casting_fixtures.VoiceCastingTests.pin
    audio=casting_fixtures.VoiceCastingTests.audio

    def test_f5_casting_uses_same_scoped_receipt_and_revocation_stales_handoff(self):
        from tests.test_no_gpu_staging import request
        cast,_,data=self.casting();manual=bytearray(self.audio());manual[44:]=b'\x01\0'*(len(manual[44:])//2)
        audio=self.c.refs.put('unit-reference.wav',bytes(manual),'audio',source='MANUAL PCM TEST SIGNAL NOT VOICE',rights='fictional_ai')
        doc=self.c.refs.put('unit-consent.txt',b'UNIT NOT REAL CONSENT','casting',source='MANUAL TEST DOC')
        data['records'][0]['voice_refs']=[self.pin(audio)]
        with self.s.tx() as db:deps=[x['id'] for x in json.loads(self.s._task(db,cast)['refs'])]
        cast=self.task('casting',data,deps)
        r=request('reference_voice','indicf5');r.update(speaker_id='actor-rafi',reference=self.pin(audio),reference_transcript='ম্যানুয়াল পরীক্ষা',consent_reference=self.pin(doc))
        spec=self.spec();spec['reference_metadata']=dict(reference=r['reference'],sample_rate=24000,channels=1,duration_ms=200,transcript=r['reference_transcript'])
        spec['permission']=dict(identity_kind='fictional',actor_ids=['actor-rafi'],uses=['voice_clone'],reference_ids=[audio['id']],consent_reference=self.pin(doc))
        receipt=VoiceConsents(self.s).confirm(dict(actor_id='actor-rafi',reference=r['reference'],document=r['consent_reference'],transcript_sha256=hashlib.sha256(r['reference_transcript'].encode()).hexdigest(),uses=['voice_clone'],reviewer='UNIT NOT HUMAN REVIEW',scope_task=cast,note='MANUAL FIXTURE ONLY'),confirmed=True)
        d=self.w.prepare(cast,'candidate-rafi','indicf5',r,spec,consent_review=receipt);job=self.w.stage(d['id'])
        self.assertEqual(job['native_call_preparation']['consent']['receipt_id'],receipt)
        self.assertEqual(self.w.get(d['id'])['prepared_id'],job['prepared_id'])
        VoiceConsents(self.s).revoke(receipt,'UNIT','UNIT revoked',confirmed=True)
        with self.assertRaises(AgentError):self.w.get(d['id'])
        from redpad_pipeline.shared_model_services import SharedServices
        with self.assertRaises(AgentError):SharedServices(self.s).prepared_offline_request(job['prepared_id'])

    def test_selected_speak_casting_stages_exact_worker_keeps_director_qc_producer_pending(self):
        d=self.draft();job=self.w.stage(d['id'])
        self.assertTrue(job['native_worker_implemented']);self.assertFalse(job['launch_authorized']);self.assertFalse(job['inference_completed'])
        packet=self.w.packets(d['snapshot']['task'])[0]
        self.assertFalse(packet['voice_source_blocked']);self.assertFalse(packet['voice_accepted']);self.assertFalse(packet['chemistry_accepted'])
        self.assertTrue(packet['human_review_pending'])
