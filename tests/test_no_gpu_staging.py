"""CPU-only software fixtures. Every hardware/model/network/process path forbidden."""
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from redpad_pipeline.agents import AgentStore, AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.shared_model_services import SharedServices
from redpad_pipeline.no_gpu_staging import load,prepare,readiness,tool_request,OPERATIONS
from redpad_pipeline.producer_references import References


def request(operation,profile):
    pin={'id':'fixture-ref','version':1}
    if operation=='image_inspection':return dict(images=[pin],question='SOFTWARE FIXTURE inspect only visible facts',seed=117)
    if operation=='text':return dict(system='SOFTWARE FIXTURE',prompt='TEST ONLY',max_new_tokens=32,context_tokens=512,seed=117,thinking=False,temperature=.7)
    if operation in ('text_to_image','reference_edit'):
        return dict(prompt='SOFTWARE FIXTURE',width=512,height=512,steps=9 if profile=='z_image_turbo' else 4,seed=117,references=[pin] if operation=='reference_edit' else [])
    if profile in ('wan22_5','svd_xt'):
        svd=profile=='svd_xt'
        return dict(mode=operation,prompt='' if svd else 'SOFTWARE FIXTURE',width=1024 if svd else 512,height=576 if svd else 512,frames=25 if svd else 9,fps=7 if svd else 24,steps=25 if svd else 50,seed=117,reference=pin if operation=='image_to_video' else None)
    if operation in ('reference_video','text_to_video','image_to_video','audio_video'):
        return dict(prompt='SOFTWARE FIXTURE',seconds=2,seed=117,image_reference=pin if operation in ('reference_video','image_to_video') else None,video_reference=pin if operation=='reference_video' else None)
    if profile=='indic_parler':return dict(text='শুধু পরীক্ষা',language='bn',preset='Arjun',style='neutral',seed=117)
    if operation in ('text_to_audio','reference_voice'):
        r=dict(text='শুধু পরীক্ষা',language='bn',speaker_id='Ishita' if profile=='indic_speak' else 'fictional_fixture',seed=117)
        if operation=='reference_voice':r.update(reference=pin,reference_transcript='শুধু পরীক্ষা',consent_reference={'id':'consent-fixture','version':1})
        return r
    if operation=='music':return dict(prompt='SOFTWARE FIXTURE',seconds=2,seed=117)
    if operation=='sound_effect':return dict(prompt='SOFTWARE FIXTURE',seconds=2,seed=117,steps=8)
    raise AssertionError(operation)


class NoGPUStagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3')
        self.engine=Engine(self.store);self.services=SharedServices(self.store)
        # Installing/importing model libraries, probing GPU, launching subprocesses
        # or creating network sockets would fail this entire test class.
        for target in ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open',
                       'redpad_pipeline.kaggle_runtime.probe','redpad_pipeline.shared_model_services.SharedServices.execute',
                       'redpad_pipeline.screenwriter.LocalWriter.__call__'):
            p=patch(target,side_effect=AssertionError('NO GPU / INFERENCE / NETWORK / PROCESS'));p.start();self.addCleanup(p.stop)
        p=patch.dict('sys.modules',{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bitsandbytes':None})
        p.start();self.addCleanup(p.stop)

    def test_all_19_roles_all_declared_supported_contracts_without_resources(self):
        registry,roles=load();seen=set()
        for role,row in roles.items():
            from redpad_pipeline.no_gpu_staging import capabilities,candidate_ids,resolve_profile
            for pid in candidate_ids(role,row):
                p=resolve_profile(pid,registry)
                for op in (set(OPERATIONS[role])|{'text_to_image'})&capabilities(p):
                    with self.subTest(role=role,profile=pid,operation=op):
                        draft=prepare(role,pid,op,request(op,pid));seen.add(role)
                        self.assertEqual(draft['revision'],p['revision'])
                        self.assertEqual(draft['precision'],p['precision'])
                        for flag in ('runtime_verified','inference_verified','production_ready','human_reviewed'):self.assertFalse(draft[flag])
                        self.assertIsNone(draft['fallback'])
        self.assertEqual(seen,set(roles));self.assertEqual(len(seen),19)

    def test_generator_and_text_adapter_cannot_pose_as_media_critics(self):
        for role in ('qc','cinematographer','continuity','location','editing'):
            registry,roles=load();row=roles[role]
            for pid in [row['primary_research_candidate']]+row['alternative_research_candidates']:
                with self.subTest(role=role,profile=pid):
                    with self.assertRaises(AgentError):prepare(role,pid,'image_inspection',{})
        self.assertIn('audio_inspection',readiness()['qc']['unsupported_required_operations'])

    def test_no_director_script_new_profile_or_quantized_substitution(self):
        for role,pid in [('director','qwen35_27'),('script','qwen35_27'),('story','qwen35_9'),('story','qwen35_9_approved_gguf')]:
            with self.assertRaises(AgentError):prepare(role,pid,'text',request('text',pid))

    def test_endpoint_promotion_and_invalid_scalar_controls_rejected(self):
        r=request('text','qwen35_27')
        for key,value in [('endpoint','https://example.invalid'),('approved',True),('image','private.png'),('seed',True),('temperature',float('nan'))]:
            with self.subTest(key=key):
                with self.assertRaises(AgentError):prepare('story','qwen35_27','text',dict(r,**{key:value}))

    def test_reference_edit_is_distinct_from_text_generation(self):
        with self.assertRaises(AgentError):prepare('art','z_image_turbo','reference_edit',request('reference_edit','z_image_turbo'))
        r=request('reference_edit','flux2_klein4');r['references']=[]
        with self.assertRaises(AgentError):prepare('art','flux2_klein4','reference_edit',r)

    def test_video_families_have_different_native_controls(self):
        r=request('image_to_video','svd_xt');r['prompt']='This cannot control SVD'
        with self.assertRaises(AgentError):prepare('video','svd_xt','image_to_video',r)
        with self.assertRaises(AgentError):prepare('video','svd_xt','text_to_video',request('text_to_video','svd_xt'))
        r=request('reference_video','wan_animate2');r['video_reference']=None
        with self.assertRaises(AgentError):prepare('motion','wan_animate2','reference_video',r)
        r=request('text_to_video','wan22_5');r['frames']=10
        with self.assertRaises(AgentError):prepare('video','wan22_5','text_to_video',r)
        self.assertTrue(any('explicit owner-authorized NativeExecution' in b for b in prepare('video','ltx25','text_to_video',request('text_to_video','ltx25'))['blockers']))

    def test_voice_presets_do_not_clone_and_reference_voice_needs_consent_fields(self):
        with self.assertRaises(AgentError):prepare('voice','indic_parler','reference_voice',request('reference_voice','indicf5'))
        r=request('reference_voice','indicf5');del r['consent_reference']
        with self.assertRaises(AgentError):prepare('voice','indicf5','reference_voice',r)
        draft=prepare('voice','indicf5','reference_voice',request('reference_voice','indicf5'))
        self.assertTrue(any('consent' in b for b in draft['blockers']))
        r=request('text_to_audio','indic_speak');r['language']='unknown'
        with self.assertRaises(AgentError):prepare('voice','indic_speak','text_to_audio',r)

    def test_music_15_is_not_silently_sent_to_existing_35_worker(self):
        r=request('music','ace15');draft=prepare('music','ace15','music',r)
        self.assertEqual(draft['repo'],'ACE-Step/Ace-Step1.5')
        self.assertTrue(any('No legacy replacement' in b for b in draft['blockers']))
        with self.assertRaises(AgentError):prepare('music','stable_audio_small','music',r)

    def test_staging_is_restart_safe_idempotent_and_never_changes_routes_or_task_state(self):
        run=self.engine.enqueue('story',{'fixture':'not inference'},mode='local')
        r=request('text','qwen35_27');a=self.services.stage_request(run,'qwen35_27','text',r)
        self.assertEqual(a,self.services.stage_request(run,'qwen35_27','text',r))
        self.assertEqual(a,SharedServices(self.store).staged_request(a['id']))
        self.assertIsNone(self.services.policy('story'));self.assertEqual(self.store.tasks()[0]['state'],'Assigned')
        self.assertEqual(self.store.outputs(),[])
        with self.store.tx() as db:db.execute('UPDATE tasks SET revision=1 WHERE id=?',(a['context']['task'],))
        with self.assertRaises(AgentError):self.services.staged_request(a['id'])

    def test_unapproved_dependencies_block_and_changed_source_hash_invalidates(self):
        from tests.test_agent_foundation import fixture
        source=self.engine.enqueue('story',fixture('story'));tid=self.engine.runs()[0]['task']
        child=self.engine.enqueue('character',{'fixture':True},dependencies=[tid])
        with self.assertRaises(AgentError):self.services.stage_request(child,'qwen35_27','text',request('text','qwen35_27'))
        # Manually recorded software fixture, never inferred or artistically accepted.
        with self.store.tx() as db:
            db.execute("UPDATE tasks SET state='Approved',revision=1 WHERE id=?",(tid,))
            db.execute('INSERT INTO outputs VALUES (?,?,?)',(tid,1,json.dumps({'summary':'SOFTWARE FIXTURE'})))
        a=self.services.stage_request(child,'qwen35_27','text',request('text','qwen35_27'))
        with self.store.tx() as db:db.execute('UPDATE outputs SET payload=? WHERE task=?',(json.dumps({'summary':'CHANGED FIXTURE'}),tid))
        with self.assertRaises(AgentError):self.services.staged_request(a['id'])

    def test_reference_identity_version_rights_and_bytes_are_bound(self):
        from PIL import Image
        refs=References(self.store);buf=io.BytesIO();Image.new('RGB',(2,2)).save(buf,format='PNG') # manual 2x2 unit fixture
        row=refs.put('fixture.png',buf.getvalue(),'character',source='manual unit fixture',rights='reference_only')
        run=self.engine.enqueue('art',{'fixture':True});r=request('reference_edit','flux2_klein4');r['references']=[{'id':row['id'],'version':row['version']}]
        with self.assertRaises(AgentError):self.services.stage_request(run,'flux2_klein4','reference_edit',r)
        row=refs.put('fixture2.png',buf.getvalue(),'character',source='manual unit fixture',rights='fictional_ai');r['references']=[{'id':row['id'],'version':row['version']}]
        a=self.services.stage_request(run,'flux2_klein4','reference_edit',r)
        refs.path(row).write_bytes(b'changed manual fixture')
        with self.assertRaises(AgentError):self.services.staged_request(a['id'])

    def test_staging_and_profile_tampering_is_rejected(self):
        from redpad_pipeline import no_gpu_staging as staging
        registry,roles=load();path=Path(self.tmp.name)/'registry.json';changed=copy.deepcopy(registry)
        run=self.engine.enqueue('story',{'fixture':True});a=self.services.stage_request(run,'qwen35_27','text',request('text','qwen35_27'))
        changed['profiles']['qwen35_27']['revision']='f'*40;path.write_text(json.dumps(changed))
        with patch.object(staging,'REGISTRY',path):
            with self.assertRaises(AgentError):self.services.staged_request(a['id'])
        with self.store.tx() as db:db.execute("UPDATE shared_staging_requests SET payload='{}' WHERE id=?",(a['id'],))
        with self.assertRaises(AgentError):self.services.staged_request(a['id'])

    def test_deterministic_operations_never_publish_or_fabricate_receipts(self):
        channel='UC'+'a'*22
        self.assertFalse(tool_request('youtube','read_only_analytics',dict(operation='channel_profile',channel_id=channel))['executed'])
        for op in ('upload','publish','schedule'):
            with self.assertRaises(AgentError):tool_request('youtube','read_only_analytics',dict(operation=op,channel_id=channel))
        with self.assertRaises(AgentError):tool_request('editing','assembly_receipt',{'sources':[]})
        good={'tasks':[{'id':'a','seconds':10,'depends_on':[]},{'id':'b','seconds':5,'depends_on':['a']}],'budget_seconds':15}
        self.assertFalse(tool_request('production_manager','schedule_check',good)['executed'])
        with self.assertRaises(AgentError):tool_request('production_manager','schedule_check',dict(good,budget_seconds=14))
        with self.assertRaises(AgentError):tool_request('production_manager','schedule_check',dict(good,tasks=[{'id':'a','seconds':1,'depends_on':['a']}]))

    def test_ledger_reports_real_engineering_gaps_and_never_accepts_mock_art(self):
        rows=readiness();self.assertEqual(len(rows),19)
        self.assertEqual(rows['story']['engineering_status'],'NO-GPU ENGINEERING COMPLETE')
        self.assertEqual(rows['voice']['engineering_status'],'NO-GPU ENGINEERING COMPLETE')
        for r in rows.values():
            self.assertFalse(r['production_ready']);self.assertFalse(r['runtime_verified'])
            self.assertEqual(r['gpu_status'],'GPU TEST BLOCKED');self.assertIn(r['human_status'],('OWNER REVIEW PENDING','HUMAN REVIEW PENDING'))

    def test_task_bound_tools_keep_same_approval_and_no_publishing_boundary(self):
        run=self.engine.enqueue('youtube',{'fixture':True})
        a=self.services.stage_tool_request(run,'read_only_analytics',{'operation':'channel_profile','channel_id':'UC'+'a'*22})
        self.assertEqual(a,self.services.staged_request(a['id']))
        with self.assertRaises(AgentError):self.services.stage_tool_request(run,'read_only_analytics',{'operation':'upload','channel_id':'UC'+'a'*22})
        with self.assertRaises(AgentError):self.services.stage_tool_request(run,'release_manifest',{'sources':[{'id':'invented','revision':1,'sha256':'a'*64}]})
        self.assertEqual(self.store.outputs(),[])

    def test_invalid_upstream_binding_is_rejected_before_any_staging_write(self):
        run=self.engine.enqueue('story',{'$from':'unknown','path':['artifact']})
        with self.assertRaises(AgentError):self.services.stage_request(run,'qwen35_27','text',request('text','qwen35_27'))

    def test_raw_output_review_requirements_do_not_accept_a_mock_result(self):
        draft=prepare('story','qwen35_27','text',request('text','qwen35_27'))
        self.assertTrue(draft['output_requirements']['raw_response_or_original_media_required'])
        self.assertFalse(draft['human_reviewed']);self.assertFalse(draft['production_ready'])

    def test_config_drift_and_false_promotion_claims_fail_closed(self):
        from redpad_pipeline import no_gpu_staging as staging
        original=json.loads(staging.STAGING.read_text());path=Path(self.tmp.name)/'stage.json'
        for mutate in (lambda x:x.update(roles=[]),lambda x:x.update(models_inferred=True),
                       lambda x:x['roles'][0].update(production_routing_allowed=True),
                       lambda x:x['roles'][0].update(primary_research_candidate='gemma3_12')):
            changed=copy.deepcopy(original);mutate(changed);path.write_text(json.dumps(changed))
            with patch.object(staging,'STAGING',path):
                with self.assertRaises(AgentError):load()

    def test_owner_revision_note_update_invalidates_staged_request(self):
        run=self.engine.enqueue('story',{'fixture':True});tid=self.engine.runs()[0]['task']
        with self.store.tx() as db:self.store.event(db,tid,'owner','Request revision',{'evidence':'Lock source facts; change pacing only'})
        a=self.services.stage_request(run,'qwen35_27','text',request('text','qwen35_27'))
        with self.store.tx() as db:self.store.event(db,tid,'owner','Request revision',{'evidence':'Freeze pacing too; only change final line'})
        with self.assertRaises(AgentError):self.services.staged_request(a['id'])

    def test_existing_supplemental_vision_is_explicit_pinned_and_never_an_audio_video_critic(self):
        draft=prepare('qc','vision7','image_inspection',request('image_inspection','vision7'))
        self.assertEqual(draft['repo'],'Qwen/Qwen2.5-VL-7B-Instruct')
        self.assertEqual(draft['revision'],'cc594898137f460bfe9f0759e9844b3ce807cfb5')
        for role,op in [('qc','audio_inspection'),('performance','video_inspection'),('casting','image_inspection')]:
            with self.assertRaises(AgentError):prepare(role,'vision7',op,request('image_inspection','vision7'))
        self.assertFalse(draft['runtime_verified']);self.assertTrue(any('supplemental' in b for b in draft['blockers']))

    def test_request_key_order_does_not_duplicate_staged_work(self):
        run=self.engine.enqueue('story',{'fixture':True});r=request('text','qwen35_27')
        a=self.services.stage_request(run,'qwen35_27','text',r)
        b=self.services.stage_request(run,'qwen35_27','text',dict(reversed(list(r.items()))))
        self.assertEqual(a['id'],b['id'])
