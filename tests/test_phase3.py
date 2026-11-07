import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentError
from redpad_pipeline.phase3 import Lab,shape,cases
from redpad_pipeline.screenwriter import LocalWriter,WritingError

class FakeResponse(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

def response(data):return FakeResponse(json.dumps(data).encode())

class Phase3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'phase3_runs'
        self.mock=patch('redpad_pipeline.phase3.LAB_ROOT',self.root);self.mock.start();self.addCleanup(self.mock.stop)
        self.lab=Lab('test')
    def test_isolation_and_symlink_block(self):
        for name in ('../production','/absolute','bad/path'):
            with self.assertRaises(AgentError):Lab(name)
        (self.root/'unsafe').symlink_to(self.root/'test',target_is_directory=True)
        with self.assertRaises(AgentError):Lab('unsafe')
    def test_original_benchmarks_do_not_seed_manual_story_prose(self):
        spec,request=self.lab.request('family_architecture')
        self.assertNotIn('মেঘলা',json.dumps(request['artifact'],ensure_ascii=False));self.assertIn('<original generated text',json.dumps(request['artifact']))
        self.assertEqual(spec['brief']['episodes'],5)
        spec,request=self.lab.request('horror_architecture_30');self.assertEqual(spec['brief']['episodes'],30)
    def test_missing_model_blocks_without_download_or_fake_output(self):
        rid=self.lab.queue('family_architecture','local-test:4b')
        with patch('urllib.request.OpenerDirector.open',side_effect=OSError('no runtime')):
            self.assertEqual(self.lab.run(rid),'Blocked')
        summary=self.lab.summary();self.assertEqual(summary['real_inference_completed'],0);self.assertEqual(summary['structurally_validated_outputs'],0)
        self.assertEqual(summary['blocked_preflight_or_dependency'],1);self.assertIsNone(summary['playable_cinematic_export']);self.assertFalse(self.lab.store.outputs())
    def test_idempotency_and_budget(self):
        rid=self.lab.queue('family_architecture','local-test:4b')
        self.assertEqual(self.lab.queue('family_architecture','local-test:4b'),rid)
        for n in range(5):self.lab.queue('family_architecture','different'+str(n))
        with self.assertRaises(AgentError):self.lab.queue('family_architecture','over-budget')
    def test_source_requirements_cannot_use_manual_fixture_fallback(self):
        for case in ('director_review','episode_5min','weak_script_rewrite','continuity_audit'):
            with self.assertRaises(AgentError):self.lab.queue(case,'local-test')
        self.assertFalse(self.lab.store.outputs())
    def test_cloud_and_empty_model_rejected(self):
        for model in ('paid-cloud',''):
            with self.assertRaises(AgentError):self.lab.queue('family_architecture',model)
    def test_two_attempt_limit(self):
        rid=self.lab.queue('family_architecture','local-test')
        with patch('urllib.request.OpenerDirector.open',side_effect=OSError()):
            for _ in range(2):self.lab.run(rid);self.lab.engine.retry(rid)
        with self.assertRaises(AgentError):self.lab.run(rid)
    def test_raw_invalid_json_is_preserved_in_engine_evidence(self):
        rid=self.lab.queue('family_architecture','local-test')
        metadata={'details':{'quantization_level':'Q4_K_M'},'model_info':{'key':'value'}}
        runtime={'model':'local-test','done':True,'done_reason':'stop','message':{'content':'not valid json'}}
        with patch('urllib.request.OpenerDirector.open',side_effect=[response(metadata),response(runtime)]):
            self.assertEqual(self.lab.run(rid),'Blocked')
        evidence=self.lab.summary();self.assertEqual(evidence['runtime_records'][0]['raw_text'],'not valid json')
        self.assertEqual(evidence['real_inference_completed'],1) # mocked transport contract, not a real model test
        self.assertEqual(evidence['structurally_validated_outputs'],0);self.assertFalse(self.lab.store.outputs())
    def test_truncation_and_identity_mismatch_not_success(self):
        for done,model in [('length','local-test'),('stop','different-model')]:
            writer=LocalWriter('local-test')
            payload={'model':model,'done':True,'done_reason':done,'message':{'content':'{"partial":true}'}}
            with patch('urllib.request.OpenerDirector.open',side_effect=[response({}),response(payload)]):
                with self.assertRaises(WritingError):writer('system','prompt')
            self.assertFalse(writer.last_evidence['inference_completed']);self.assertTrue(writer.last_raw_output)
    def test_cloud_metadata_and_oversize_reply_block(self):
        writer=LocalWriter('local-test')
        with patch('urllib.request.OpenerDirector.open',return_value=response({'remote_host':'external'})) as call:
            with self.assertRaises(WritingError):writer('system','prompt')
            self.assertEqual(call.call_count,1)
        with patch('urllib.request.OpenerDirector.open',return_value=FakeResponse(b'x'*(2*1024*1024+1))):
            with self.assertRaises(WritingError):writer('system','prompt')
    def test_no_scores_without_real_artifact_and_explicit_human(self):
        with self.assertRaises(AgentError):self.lab.review('unknown',1,{},'model',False)
        self.assertEqual(self.lab.summary()['review_count'],0)
        self.assertFalse(self.lab.summary()['independent_editorial_review_verified'])
    def test_queued_comparison_keeps_exact_model_after_other_configuration(self):
        first=self.lab.queue('family_architecture','candidate-one')
        self.lab.queue('family_architecture','candidate-two')
        with patch('urllib.request.OpenerDirector.open',side_effect=OSError()) as call:
            self.assertEqual(self.lab.run(first),'Blocked')
            requested=json.loads(call.call_args.args[0].data)
        self.assertEqual(requested['model'],'candidate-one')
        self.assertEqual(next(r['model'] for r in self.lab.engine.runs() if r['id']==first),'candidate-one')
    def test_recovered_lab_preserves_budget_and_idempotency(self):
        rid=self.lab.queue('family_architecture','local-test')
        with self.lab.store.tx() as db:db.execute("UPDATE agent_runs SET state='Running',attempt=1 WHERE id=?",(rid,))
        new_id=self.lab.recover(rid);self.assertNotEqual(new_id,rid)
        self.assertEqual(self.lab.queue('family_architecture','local-test'),new_id)
        self.lab.engine.retry(new_id)
        with patch('urllib.request.OpenerDirector.open',side_effect=OSError()):self.assertEqual(self.lab.run(new_id),'Blocked')
    def test_engine_recovery_checkpoint_gap_repairs_case_mapping(self):
        rid=self.lab.queue('family_architecture','local-test')
        with self.lab.store.tx() as db:db.execute("UPDATE agent_runs SET state='Running' WHERE id=?",(rid,))
        new_id=self.lab.engine.recover(rid)
        self.assertEqual(self.lab.queue('family_architecture','local-test'),new_id)
    def test_director_and_script_use_the_selected_sources_actual_brief(self):
        from tests.test_creative import samples,request
        data=samples();brief=data['romance_brief']
        rid=self.lab.engine.enqueue('story',request('season',data['romance_season'],brief))
        self.assertEqual(self.lab.engine.execute(rid),'Awaiting QC')
        tid=next(r['task'] for r in self.lab.engine.runs() if r['id']==rid)
        self.lab.store.review(tid,1,'Recommend','Manual fixture review','qc');self.lab.store.review(tid,1,'Approve','Owner fixture approval','owner')
        _,req=self.lab.request('director_review',tid);self.assertEqual(req['brief'],brief)
        _,req=self.lab.request('episode_5min',tid);self.assertEqual(req['brief']['genre'],brief['genre'])
