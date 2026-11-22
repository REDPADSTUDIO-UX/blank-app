"""Focused current CPU checks, forbidden resource attempts counted and blocked."""
import json,sys,unittest,types,importlib.util
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

OLD=[
 'tests.test_offline_11_preparation.OfflineElevenTests.test_scope_and_readiness_separate_engineering_from_inference',
 'tests.test_offline_11_preparation.OfflineElevenTests.test_native_wan_and_svd_keep_supported_worker_controls',
 'tests.test_offline_11_preparation.OfflineElevenTests.test_parler_and_stable_audio_prepare_only_their_existing_local_payloads',
 'tests.test_producer_control.ProducerTests.test_casting_cannot_bypass_director_qc_or_identity_rights',
 'tests.test_producer_control.ProducerTests.test_wrong_actor_unexplained_hair_change_and_portrait_acting_rejected',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_all_19_roles_all_declared_supported_contracts_without_resources',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_staging_is_restart_safe_idempotent_and_never_changes_routes_or_task_state',
]

def run():
    shim=importlib.util.find_spec('requests') is None
    if shim:
        # This environment lost the optional HTTP package between sessions. Do not
        # fetch dependencies: these tests use only channel validators, no HTTP.
        module=types.ModuleType('requests')
        class RequestException(Exception):pass
        def no_http(*args,**kwargs):raise AssertionError('HTTP dependency shim has no transport')
        module.RequestException=RequestException;module.Session=no_http
        sys.modules['requests']=module
    import redpad_pipeline.youtube  # Only existing validator import, no account access.
    names=sys.argv[1:] or ['tests.test_offline_six_preparation.OfflineSixTests']+OLD
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    attempts={}
    def deny(name):
        def blocked(*args,**kwargs):
            attempts[name]=attempts.get(name,0)+1
            raise AssertionError('NO RESOURCE AUTHORIZED: '+name)
        return blocked
    guards=['socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open','redpad_pipeline.kaggle_runtime.probe',
            'redpad_pipeline.shared_model_services.SharedServices.execute','redpad_pipeline.screenwriter.LocalWriter.__call__']
    out=Path(__file__).resolve().parents[1]/'verification/offline_6'
    with ExitStack() as stack:
        for target in guards:stack.enter_context(patch(target,side_effect=deny(target)))
        stack.enter_context(patch.dict('sys.modules',{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bitsandbytes':None,'acestep':None,'ltx_pipelines':None}))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'selected':names,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),
             'forbidden_resource_attempts':{k:attempts.get(k,0) for k in guards},'gpu':False,'model_inference':False,'weights_opened_or_downloaded':False,
             'requests_import_only_shim':shim,'http_transport_tested':False,
             'scope':'software-only manual fixtures; no artistic/model evidence'}
    (out/'test_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not result.wasSuccessful() or attempts:raise SystemExit(1)

if __name__=='__main__':run()
