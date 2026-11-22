"""Focused CPU fixture QA only; no inference, transport, model package or GPU."""
import importlib.util,json,sys,types,unittest
from pathlib import Path

COMPAT=[
 'tests.test_producer_control.ProducerTests.test_casting_cannot_bypass_director_qc_or_identity_rights',
 'tests.test_producer_control.ProducerTests.test_casting_lock_costume_consumption_and_reference_replacement_stales',
 'tests.test_producer_control.ProducerTests.test_wrong_actor_unexplained_hair_change_and_portrait_acting_rejected',
 'tests.test_offline_11_preparation.OfflineElevenTests.test_parler_and_stable_audio_prepare_only_their_existing_local_payloads',
 'tests.test_native_local_execution.NativeLocalTests.test_actual_running_dummy_is_cancelled_from_restarted_service',
 'tests.test_native_local_execution.NativeLocalTests.test_isolated_child_environment_does_not_inherit_provider_tokens_or_proxies',
]

def main():
    shim=importlib.util.find_spec('requests') is None
    if shim:
        module=types.ModuleType('requests');module.RequestException=type('RequestException',(Exception,),{})
        def no_http(*a,**kw):raise AssertionError('NO HTTP TRANSPORT IN QA')
        module.Session=no_http;sys.modules['requests']=module
    import redpad_pipeline.youtube
    names=sys.argv[1:] or ['tests.test_voice_casting_integration.VoiceCastingTests']+COMPAT
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    receipt={'selected':names,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'requests_import_only_shim':shim,
       'gpu':False,'model_inference':False,'weights_read_loaded_downloaded':False,'hosted_paid_calls':False,'license_acceptance':False,'actual_human_voice_or_artistic_review':False,
       'scope':'manual software fixtures and injected classes only; any process recheck is the existing fixed CPU dummy, not native model inference'}
    (Path(__file__).resolve().parents[1]/'verification/voice_casting/test_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
