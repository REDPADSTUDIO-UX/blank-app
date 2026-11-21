"""Selected affected CPU compatibility checks, not a replay of the prior 42 tests."""
import json,sys,unittest
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import patch

NAMES=[
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_all_19_roles_all_declared_supported_contracts_without_resources',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_staging_is_restart_safe_idempotent_and_never_changes_routes_or_task_state',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_ledger_reports_real_engineering_gaps_and_never_accepts_mock_art',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_task_bound_tools_keep_same_approval_and_no_publishing_boundary',
 'tests.test_producer_control.ProducerTests.test_casting_cannot_bypass_director_qc_or_identity_rights',
 'tests.test_producer_control.ProducerTests.test_wrong_actor_unexplained_hair_change_and_portrait_acting_rejected',
 'tests.test_kaggle_model_services.KaggleServices.test_production_route_cannot_be_replaced_by_research_preference',
 'tests.test_kaggle_model_services.KaggleServices.test_service_snapshot_is_pinned_not_changed_by_later_preference',
]

def run():
    # Import test modules before guarding execution, so optional library import-time
    # local IPv6 capability detection is not confused with a model/network request.
    import redpad_pipeline.youtube  # Existing channel validator, no authenticated operation.
    names=sys.argv[1:] or NAMES
    if any(n not in NAMES for n in names):raise SystemExit('Choose only an existing affected CPU test.')
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    with ExitStack() as stack:
        guards={name:stack.enter_context(patch(name,side_effect=AssertionError('NO GPU / NETWORK / PROCESS'))) for name in ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open','redpad_pipeline.kaggle_runtime.probe')}
        stack.enter_context(patch.dict('sys.modules',{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bitsandbytes':None}))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        counts={k:v.call_count for k,v in guards.items()}
    out={'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'forbidden_execution_attempts':counts,'model_inference':False,'gpu_usage':False,'scope':'software fixtures only; import-time stdlib/library capability detection is outside the execution guard'}
    (Path(__file__).resolve().parents[1]/'verification/offline_11/compatibility_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    if not result.wasSuccessful() or any(counts.values()):raise SystemExit(1)

if __name__=='__main__':run()
