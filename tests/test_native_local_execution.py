"""CPU-only dummy processes and injected local classes, never actual inference."""
import ast,copy,hashlib,io,json,os,sys,tempfile,threading,time,types,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.native_execution import NativeExecution,compile_job,process_identity,isolated_command,validate_video_metadata
from redpad_pipeline.native_local_bundle import NativeInstalls,verify_tree,local_path,validate_install
from redpad_pipeline.native_local_worker import audit_event,safe_latent,make_ace_handler,ltx,wan


class NativeLocalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.store=AgentStore(self.root/'agent_control.sqlite3');self.runtime=NativeExecution(self.store)
        self.blocked=[]
        for target in ('socket.socket','urllib.request.OpenerDirector.open','redpad_pipeline.kaggle_runtime.probe'):
            p=patch(target,side_effect=AssertionError('NO NETWORK/GPU PROBE'));p.start();self.addCleanup(p.stop)
        p=patch.dict(sys.modules,{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'ltx_pipelines':None,'acestep':None});p.start();self.addCleanup(p.stop)
        import subprocess
        real=subprocess.Popen
        def allowed(argv,*args,**kwargs):
            if not isinstance(argv,list) or argv[:3]!=[sys.executable,'-m','redpad_pipeline.native_fixture_worker']:
                self.blocked.append(argv);raise AssertionError('ONLY FIXED CPU FIXTURE PROCESS AUTHORIZED')
            return real(argv,*args,**kwargs)
        p=patch('subprocess.Popen',side_effect=allowed);p.start();self.addCleanup(p.stop)
        self.addCleanup(lambda:self.assertEqual(self.blocked,[]))

    def test_real_dummy_process_returns_software_receipt_never_inference_or_approval(self):
        id=self.runtime.queue_fixture();out=self.runtime.run(id,authorized=True,timeout=2)
        self.assertEqual(out['state'],'CPU MOCK COMPLETE');self.assertFalse(out['result']['inference_completed']);self.assertFalse(out['production_ready'])
        self.assertTrue(out['result']['owner_acceptance_required']);self.assertTrue(out['result']['independent_qc_required'])

    def test_actual_dummy_failure_classification_preserves_raw_logs(self):
        id=self.runtime.queue_fixture('failure');out=self.runtime.run(id,authorized=True,timeout=2)
        self.assertEqual(out['state'],'FAILED');self.assertIn('EXPECTED SOFTWARE FIXTURE',(self.runtime.root/id/'stderr.txt').read_text())

    def test_actual_timeout_terminates_fixture_worker(self):
        id=self.runtime.queue_fixture('timeout');out=self.runtime.run(id,authorized=True,timeout=.2)
        self.assertEqual(out['state'],'TIMED OUT');self.assertIsNone(process_identity(self.runtime._row(id)['pid']))

    def test_process_group_timeout_cleans_spawned_dummy_descendant(self):
        id=self.runtime.queue_fixture('child');out=self.runtime.run(id,authorized=True,timeout=.5)
        self.assertEqual(out['state'],'TIMED OUT');child=json.loads((self.runtime.root/id/'fixture_child.json').read_text())['pid']
        deadline=time.monotonic()+1
        while process_identity(child) is not None and time.monotonic()<deadline:time.sleep(.01)
        self.assertIsNone(process_identity(child))

    def test_cancellation_before_launch_and_no_implicit_retry(self):
        id=self.runtime.queue_fixture();self.assertEqual(self.runtime.cancel(id)['state'],'CANCELLED')
        with self.assertRaises(AgentError):self.runtime.run(id,authorized=True)
        self.assertFalse((self.runtime.root/id).exists())

    def test_actual_running_dummy_is_cancelled_from_restarted_service(self):
        id=self.runtime.queue_fixture('timeout');results=[]
        thread=threading.Thread(target=lambda:results.append(self.runtime.run(id,authorized=True,timeout=3)));thread.start()
        try:
            deadline=time.monotonic()+1
            while not self.runtime._row(id)['pid'] and time.monotonic()<deadline:time.sleep(.01)
            NativeExecution(self.store).cancel(id)
        finally:thread.join(timeout=4)
        self.assertFalse(thread.is_alive());self.assertEqual(results[0]['state'],'CANCELLED')

    def test_worker_does_not_launch_without_explicit_authorization(self):
        id=self.runtime.queue_fixture()
        with self.assertRaises(AgentError):self.runtime.run(id)
        self.assertEqual(self.runtime.status(id)['state'],'QUEUED')

    def test_worker_source_change_is_stale_before_launch(self):
        id=self.runtime.queue_fixture();read=Path.read_bytes
        def changed(p):return b'UNIT SOURCE CHANGE' if p.name=='native_fixture_worker.py' else read(p)
        with patch.object(Path,'read_bytes',changed):out=self.runtime.run(id,authorized=True)
        self.assertEqual(out['state'],'STALE')

    def test_mock_cannot_report_model_inference_success(self):
        id=self.runtime.queue_fixture('invalid_output');out=self.runtime.run(id,authorized=True,timeout=2)
        self.assertEqual(out['state'],'FAILED');self.assertFalse(out['production_ready'])

    def test_restart_recovery_does_not_restart_abandoned_process_or_kill_reused_pid(self):
        id=self.runtime.queue_fixture()
        with self.store.tx() as db:db.execute("UPDATE native_research_runs SET state='RUNNING',pid=?,start_ticks='not-this-process' WHERE id=?",(os.getpid(),id))
        out=NativeExecution(self.store).recover(id);self.assertEqual(out['state'],'INTERRUPTED')
        with self.assertRaises(AgentError):self.runtime.run(id,authorized=True)

    def test_output_root_and_run_id_cannot_escape_or_reuse_existing_directory(self):
        with self.assertRaises(AgentError):self.runtime.status('../escape')
        id=self.runtime.queue_fixture();(self.runtime.root/id).symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(AgentError):self.runtime.run(id,authorized=True)

    def test_fixture_command_not_arbitrary_user_script_model_or_hosted_endpoint(self):
        for case in ('python -c bad','https://example.invalid','ltx25'):
            with self.assertRaises(AgentError):self.runtime.queue_fixture(case)

    def test_fixed_worker_network_denial_checked_without_real_network_attempt(self):
        id=self.runtime.queue_fixture('network');out=self.runtime.run(id,authorized=True,timeout=2)
        self.assertEqual(out['state'],'CPU MOCK COMPLETE')

    def test_kernel_isolation_argv_is_local_ro_networkless_and_no_shell(self):
        with patch('shutil.which',return_value='/usr/bin/bwrap'):
            args=isolated_command('/tmp/manual/request.json','/tmp/manual',[])
            self.assertIn('--unshare-net',args);self.assertIn('--ro-bind',args);self.assertNotIn('--dev-bind',args)
            with self.assertRaises(AgentError):isolated_command('/tmp/job','/tmp/out',['/dev/mem'])
        with patch('shutil.which',return_value=None):
            with self.assertRaises(AgentError):isolated_command('/tmp/job','/tmp/out',[])

    def test_audit_rejects_internet_shell_and_unknown_child_without_calls(self):
        for event,args in [('socket.connect',(None,('remote.invalid',443))),('os.system',('echo BAD',)),('subprocess.Popen',('/bin/sh',['sh','-c','bad']))]:
            with self.assertRaises(PermissionError):audit_event(event,args)
        audit_event('socket.connect',(None,('127.0.0.1',2345)))
        audit_event('subprocess.Popen',('/usr/bin/ffmpeg',['ffmpeg','-version']))

    def test_bundle_missing_unmanifested_changed_or_symlink_files_fail_closed(self):
        folder=self.root/'bundle';folder.mkdir();file=folder/'manual.bin';data=b'UNIT FIXTURE NOT MODEL';file.write_bytes(data)
        files={'manual.bin':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}}
        verify_tree(folder,files)
        (folder/'extra.py').write_text('manual fixture')
        with self.assertRaises(AgentError):verify_tree(folder,files)
        (folder/'extra.py').unlink();file.write_bytes(b'changed')
        with self.assertRaises(AgentError):verify_tree(folder,files)
        with self.assertRaises(AgentError):local_path(folder,'../escape')
        file.unlink();file.symlink_to(self.root/'missing')
        with self.assertRaises(AgentError):verify_tree(folder,files)

    def test_install_cannot_create_owner_license_approval_implicitly(self):
        with self.assertRaises(AgentError):NativeInstalls(self.store).approve({})
        with self.assertRaises(AgentError):NativeInstalls(self.store).get('missing')
        with self.assertRaises(AgentError):validate_install({'profile':'indicf5'})

    def test_prepared_stage_binding_rejects_hidden_fallback_and_wrong_role(self):
        base={'profile':'ltx25','prepared_id':'fixture','stage_id':'s','native_call_preparation':{}}
        stage={'id':'s','references':[],'plan':{'profile':'ltx25','role':'video','request':{}}}
        with self.assertRaises(AgentError):compile_job(base,stage,{'profile':'ace15'},self.root)
        stage['plan']['role']='director'
        with self.assertRaises(AgentError):compile_job(base,stage,{'profile':'ltx25'},self.root)

    def modules(self,values):
        for name,value in values.items():
            module=types.ModuleType(name);module.__dict__.update(value)
            p=patch.dict(sys.modules,{name:module});p.start();self.addCleanup(p.stop)

    def test_ltx_worker_calls_verified_split_api_with_no_quantization_and_local_image(self):
        calls=[]
        class MP:
            @staticmethod
            def from_split(**kw):calls.append(('paths',kw));return kw
        class Pipe:
            def __init__(self,**kw):calls.append(('construct',kw))
            def stream_chunks(self,**kw):calls.append(('stream',kw));return iter([]),73,None
        class Image:
            @staticmethod
            def at(*args):calls.append(('image',args));return args
        def encode(chunks,**kw):calls.append(('encode',kw))
        self.modules({'ltx_pipelines.distilled':{'DistilledPipeline':Pipe},'ltx_pipelines.utils.model_paths':{'ModelPaths':MP},'ltx_pipelines.utils.types':{'ImageConditioningInput':Image},'ltx_pipelines.utils.media_io':{'encode_media_segments':encode}})
        job={'install':{'model_root':str(self.root)},'output_dir':str(self.root),'call':{'arguments':{'prompt':'FICTIONAL SOFTWARE FIXTURE','seed':1,'height':512,'width':512,'num_frames':73,'frame_rate':24,'enhance_prompt':False}},'references':{'image_reference':str(self.root/'manual.png')}}
        self.assertTrue(ltx(job).endswith('output.mp4'));self.assertFalse((self.root/'output.mp4').exists())
        self.assertIsNone(calls[1][1]['quantization']);self.assertIn('text_encoder_path',calls[0][1]);self.assertEqual(calls[2][0],'image')

    def test_shared_wan_worker_uses_fixed_native_class_local_components_and_distinct_refs(self):
        calls=[]
        class Config(dict):
            def __getattr__(self,key):return self[key]
            def __setattr__(self,key,v):self[key]=v
        class OC:
            @staticmethod
            def load(path):return Config(type='pipelines.wan_animate_2_pipeline.WanAnimate2MPIPipeline',model=Config())
        class Pipe:
            def __init__(self,cfg):calls.append(cfg)
            def __call__(self,**kw):calls.append(kw);return 'MANUAL NO OUTPUT'
        self.modules({'omegaconf':{'OmegaConf':OC},'pipelines.wan_animate_2_pipeline':{'WanAnimate2MPIPipeline':Pipe}})
        job={'install':{'model_root':str(self.root),'source_root':str(self.root)},'output_dir':str(self.root),'references':{'image_reference':'portrait-fixture','video_reference':'motion-fixture'},'call':{'arguments':{'seed':1,'fps':24,'clip_len':73}}}
        self.assertEqual(wan(job),'MANUAL NO OUTPUT');self.assertIn(str(self.root),calls[0].model['t5_checkpoint'])
        self.assertNotEqual(calls[1]['refer_img_path'],calls[1]['tpl_video_path'])

    def tensor(self,**changes):
        class Tensor:
            ndim=3;shape=(1,64,2)
            def numel(self):return 128
            def is_floating_point(self):return True
            def transpose(self,*a):return self
            def to(self,*a):return self
        t=Tensor()
        for k,v in changes.items():setattr(t,k,v)
        torch=types.SimpleNamespace(Tensor=Tensor,isfinite=lambda t:types.SimpleNamespace(all=lambda:True))
        return t,torch

    def test_safe_auxiliary_tensor_checks_use_fake_loader_only_no_actual_pt_loading(self):
        path=self.root/'manual.pt';path.write_bytes(b'MANUAL NON-PICKLE UNIT FIXTURE');tensor,torch=self.tensor();calls=[]
        def fake(*a,**kw):calls.append(kw);return tensor
        self.assertIs(safe_latent(torch,path,fake),tensor);self.assertTrue(calls[0]['weights_only']);self.assertEqual(calls[0]['map_location'],'cpu')
        for bad in ({'ndim':2},{'shape':(2,64,2)},{'shape':(1,0,2)}):
            t,_=self.tensor(**bad)
            with self.assertRaises(ValueError):safe_latent(torch,path,lambda *a,**k:t)
        with self.assertRaises(ValueError):safe_latent(torch,path,lambda *a,**k:{'arbitrary':'object'})

    def test_ace_init_bridge_denies_download_sync_and_remote_custom_model_loading(self):
        class Base:
            def _ensure_models_present(self,**kw):raise AssertionError('UPSTREAM DOWNLOAD MUST NOT RUN')
            def _sync_model_code_if_needed(self,*a):raise AssertionError('UPSTREAM AUTO SYNC MUST NOT RUN')
        _,torch=self.tensor();calls=[]
        class Model:
            @classmethod
            def from_pretrained(cls,*a,**kw):calls.append(kw);return cls()
            def to(self,*a):return self
            def eval(self):return self
        h=make_ace_handler(Base,torch,Model,Model,Model,Model,Model,self.root)
        self.assertIsNone(h._ensure_models_present(checkpoint_path=self.root,config_path='acestep-v15-turbo'))
        self.assertIsNone(h._sync_model_code_if_needed('fixture',self.root))
        with self.assertRaises(ValueError):h._ensure_models_present(checkpoint_path=self.root,config_path='old-3.5B')
        h._load_text_encoder_and_tokenizer(checkpoint_dir=str(self.root),device='cuda')  # fake objects, never actual torch.
        self.assertTrue(all(x['local_files_only'] and x['trust_remote_code'] is False for x in calls))

    def test_no_model_loading_import_at_worker_module_top_level(self):
        path=Path(__file__).resolve().parents[1]/'redpad_pipeline/native_local_worker.py';tree=ast.parse(path.read_text())
        for n in tree.body:
            if isinstance(n,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in n.names] if isinstance(n,ast.Import) else [n.module]
                self.assertFalse(any(x.split('.')[0] in ('torch','diffusers','transformers','acestep','ltx_pipelines','pipelines') for x in names))

    def test_previous_thirteen_and_director_script_profiles_unchanged(self):
        root=Path(__file__).resolve().parents[1];b=json.loads((root/'verification/offline_execution/preservation_baseline.json').read_text())
        reg=json.loads((root/'assets/professional/phase3_candidates.json').read_text());ledger=json.loads((root/'assets/professional/phase3_19agent_no_gpu_staging.json').read_text())
        def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        for k,h in b['untouched_agents'].items():self.assertEqual(sha(reg['agents'][k]),h)
        for row in ledger['roles']:
            if row['agent'] in b['untouched_rows']:self.assertEqual(sha(row),b['untouched_rows'][row['agent']])
        self.assertEqual(sha(reg['profiles']),b['profiles_sha256'])

    def test_concurrent_native_request_dedup_is_atomic_and_restart_safe(self):
        ids=[];data={'software_fixture':False,'prepared_id':'UNIT ONLY','install_id':'UNIT ONLY','worker_sha256':'UNIT ONLY'}
        threads=[threading.Thread(target=lambda:ids.append(NativeExecution(self.store)._insert(data,dedup=True))) for _ in range(4)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(len(ids),4);self.assertEqual(len(set(ids)),1)
        self.assertEqual(ids[0],NativeExecution(self.store)._insert(data,dedup=True))

    def test_native_install_rejects_unreviewed_cached_bytecode(self):
        folder=self.root/'source';folder.mkdir();(folder/'__pycache__').mkdir();(folder/'__pycache__/bad.pyc').write_bytes(b'MANUAL FIXTURE')
        (folder/'known.py').write_text('# fixture');data=(folder/'known.py').read_bytes()
        with self.assertRaises(AgentError):verify_tree(folder,{'known.py':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}})

    def test_direct_native_cli_without_kernel_namespace_fails_before_model_import(self):
        from redpad_pipeline.native_local_worker import main
        path=self.root/'request.json';path.write_text(json.dumps({'output_dir':str(self.root),'research_execution_authorized':True,'network_namespace_required':True,'parent_network_namespace':os.readlink('/proc/self/ns/net')}))
        with self.assertRaises(PermissionError):main(path)

    def test_video_container_metadata_checks_frames_fps_and_dimensions_without_media_generation(self):
        info={'streams':[{'codec_type':'video','width':512,'height':512,'avg_frame_rate':'24/1','nb_read_frames':'73'}],'format':{'duration':'3.0416667'}}
        expected={'width':512,'height':512,'fps':24,'frames':73}
        out=validate_video_metadata(info,expected);self.assertFalse(out['creative_quality_verified'])
        for key,value in [('avg_frame_rate','30/1'),('nb_read_frames','72'),('width',1024)]:
            bad=copy.deepcopy(info);bad['streams'][0][key]=value
            with self.assertRaises(AgentError):validate_video_metadata(bad,expected)

    def test_runtime_bridge_integrates_existing_service_without_new_route(self):
        from redpad_pipeline.shared_model_services import SharedServices
        service=SharedServices(self.store);runtime=service.native_research_workers()
        self.assertIsInstance(runtime,NativeExecution)
        self.assertIsNone(service.policy('video'))

    def test_isolated_child_environment_does_not_inherit_provider_tokens_or_proxies(self):
        import subprocess
        old=subprocess.Popen;envs=[]
        def capture(argv,**kw):envs.append(kw['env']);return old(argv,**kw)
        id=self.runtime.queue_fixture()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'UNIT_NOT_SECRET','HF_TOKEN':'UNIT_NOT_SECRET','HTTPS_PROXY':'http://fixture.invalid'}),patch('subprocess.Popen',side_effect=capture):
            self.assertEqual(self.runtime.run(id,authorized=True,timeout=2)['state'],'CPU MOCK COMPLETE')
        self.assertNotIn('HF_TOKEN',envs[0]);self.assertNotIn('OPENAI_API_KEY',envs[0]);self.assertNotIn('HTTPS_PROXY',envs[0])
        self.assertEqual(envs[0]['TORCH_FORCE_WEIGHTS_ONLY_LOAD'],'1')

    def test_task_staging_native_worker_queue_binding_is_idempotent_and_not_launch_permission(self):
        from tests.test_offline_six_preparation import OfflineSixTests
        helper=OfflineSixTests();helper.setUp();self.addCleanup(helper.doCleanups)
        stage,spec=helper.ltx();prepared=helper.services.prepare_offline_request(stage['id'],spec=spec)
        self.assertEqual(prepared['worker_module'],'redpad_pipeline.native_local_worker');self.assertFalse(prepared['contract_only'])
        runtime=NativeExecution(helper.store)
        # Installation transport stub only; no actual approval or bundle access.
        with patch.object(runtime.installs,'get',return_value={'profile':'ltx25'}):
            a=runtime.queue(prepared['prepared_id'],'UNIT INSTALL STUB');b=runtime.queue(prepared['prepared_id'],'UNIT INSTALL STUB')
        self.assertEqual(a,b);self.assertEqual(runtime.status(a)['state'],'QUEUED')
        with self.assertRaises(AgentError):runtime.run(a)

    def test_readiness_separates_engineering_from_gated_voice_source(self):
        from redpad_pipeline.no_gpu_staging import readiness
        rows=readiness();self.assertEqual(sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values()),18)
        for role in ('performance','motion','video','music'):
            self.assertFalse(rows[role]['runtime_verified']);self.assertFalse(rows[role]['production_ready'])
        self.assertEqual(rows['voice']['engineering_status'],'PARTIAL');self.assertEqual(rows['casting']['engineering_status'],'NO-GPU ENGINEERING COMPLETE')

    def test_cancellation_will_not_signal_an_unrelated_or_reused_pid(self):
        from redpad_pipeline.native_execution import cancel_owned_process
        with patch('redpad_pipeline.native_execution.process_identity',return_value='different-start'),patch('os.killpg') as signal_call:
            self.assertFalse(cancel_owned_process(os.getpid(),'old-start',self.root/'manual'))
            signal_call.assert_not_called()

    def test_controller_policy_change_marks_existing_queue_stale(self):
        id=self.runtime.queue_fixture()
        with patch('redpad_pipeline.native_execution.controller_fingerprint',return_value='changed-policy'):
            self.assertEqual(self.runtime.run(id,authorized=True)['state'],'STALE')

    def test_pinned_install_identity_precision_and_source_mismatch_rejected_without_weight_reads(self):
        from redpad_pipeline.no_gpu_staging import load,fingerprint
        from redpad_pipeline.native_local_bundle import REQUIRED
        root=Path(__file__).resolve().parents[1];reg,_=load();p=reg['profiles']['ace15']
        lock=json.loads((root/'assets/professional/phase3_native_source_lock.json').read_text())
        files={f['path']:{k:f[k] for k in ('bytes','sha256')} for f in p['selected_weight_files']}
        for n in REQUIRED['ace15']:files.setdefault(n,{'bytes':1,'sha256':'0'*64})
        record=dict(profile='ace15',repo=p['repo'],revision=p['revision'],profile_sha256=fingerprint(p),model_root=str(self.root),model_files=files,source_root=str(self.root),source_files={n:{'sha256':h,'bytes':1} for n,h in lock['files']['ace15'].items()},source_revision=lock['revisions']['ace15'],owner='UNIT METADATA ONLY, NOT OWNER APPROVAL',license_note='NO LICENSE ACCEPTANCE',component_origins={n:{'repo':p['repo'],'revision':p['revision']} for n in REQUIRED['ace15']},code_reviewed=True,approved_for_research=True)
        self.assertEqual(validate_install(record,verify=False)['profile'],'ace15')
        for key,value in [('profile_sha256','precision changed'),('revision','0'*40),('source_revision','0'*40),('approved_for_research',False)]:
            with self.assertRaises(AgentError):validate_install(dict(record,**{key:value}),verify=False)
        with self.assertRaises(AgentError):validate_install(record,verify=True)  # Metadata is never an installed bundle.

    def test_ace_main_loader_uses_explicit_reviewed_class_and_safetensors_only(self):
        calls=[]
        class Base:
            def _sync_alignment_config(self):pass
            def _apply_cuda_bool_argsort_workaround(self):pass
        class FixedModel:
            config=types.SimpleNamespace()
            @classmethod
            def from_pretrained(cls,*args,**kwargs):calls.append(kwargs);return cls()
            def to(self,*args):return self
            def eval(self):return self
        tensor,torch=self.tensor();h=make_ace_handler(Base,torch,FixedModel,FixedModel,FixedModel,FixedModel,FixedModel,self.root);h.dtype='BF16 SOFTWARE FIXTURE'
        with patch('redpad_pipeline.native_local_worker.safe_latent',return_value=tensor):
            h._load_main_model_from_checkpoint(model_checkpoint_path=str(self.root),device='cuda',use_flash_attention=False,compile_model=False,quantization=None)
        self.assertTrue(calls[0]['local_files_only']);self.assertTrue(calls[1]['local_files_only']);self.assertTrue(calls[1]['use_safetensors'])
        self.assertNotIn('trust_remote_code',calls[1]);self.assertIsInstance(h.model,FixedModel)

    def test_recovery_does_not_interrupt_active_controller_during_preflight_or_postprocess(self):
        id=self.runtime.queue_fixture()
        with self.store.tx() as db:db.execute("UPDATE native_research_runs SET state='RUNNING',controller_pid=?,controller_ticks=? WHERE id=?",(os.getpid(),process_identity(os.getpid()),id))
        self.assertEqual(NativeExecution(self.store).recover(id)['state'],'RUNNING')

    def test_cancel_after_controller_loss_is_terminal_without_automatic_restart(self):
        id=self.runtime.queue_fixture()
        with self.store.tx() as db:db.execute("UPDATE native_research_runs SET state='RUNNING',controller_pid=99999999,controller_ticks='old' WHERE id=?",(id,))
        self.assertEqual(self.runtime.cancel(id)['state'],'CANCELLED')
        with self.assertRaises(AgentError):self.runtime.run(id,authorized=True)
