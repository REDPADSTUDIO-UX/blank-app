"""CPU fixture supervision QA; native inference process launch is never permitted."""
import importlib.util,json,sys,types,unittest
from pathlib import Path

COMPAT=[
 'tests.test_offline_11_preparation.OfflineElevenTests.test_native_wan_and_svd_keep_supported_worker_controls',
 'tests.test_offline_11_preparation.OfflineElevenTests.test_parler_and_stable_audio_prepare_only_their_existing_local_payloads',
 'tests.test_offline_six_preparation.OfflineSixTests.test_casting_assessment_task_handoff_persists_but_never_creates_approval',
 'tests.test_offline_six_preparation.OfflineSixTests.test_extra_consent_evidence_change_stales_existing_preparation',
 'tests.test_offline_six_preparation.OfflineSixTests.test_real_portrait_cannot_be_declared_fictional_for_wan_or_casting',
 'tests.test_producer_control.ProducerTests.test_casting_cannot_bypass_director_qc_or_identity_rights',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_all_19_roles_all_declared_supported_contracts_without_resources',
]

def main():
    shim=importlib.util.find_spec('requests') is None
    if shim:
        module=types.ModuleType('requests');module.RequestException=type('RequestException',(Exception,),{})
        def forbidden(*a,**k):raise AssertionError('HTTP TRANSPORT NOT AVAILABLE IN CPU QA')
        module.Session=forbidden;sys.modules['requests']=module
    import redpad_pipeline.youtube
    names=sys.argv[1:] or ['tests.test_native_local_execution.NativeLocalTests']+COMPAT
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'selected':names,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),
      'gpu_used':False,'model_inference':False,'real_weights_read_loaded_downloaded':False,'hosted_paid_calls':False,'license_acceptance':False,
      'authorized_processes':'fixed CPU fixture only; source-pinned native process launch blocked by test filter',
      'requests_import_only_shim':shim,'http_transport_verified':False,'model_class_calls':'injected fake classes only, no model libraries imported',
      'scope':'software engineering only; no model intelligence/artistic acceptance'}
    out=Path(__file__).resolve().parents[1]/'verification/offline_execution/test_receipt.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
