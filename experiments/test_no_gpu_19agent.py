"""Run only affected existing CPU checks under explicit resource prohibitions.
New staging tests have their own barrier and a separately preserved log.
"""
import json
from pathlib import Path
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
NAMES=[
 'tests.test_kaggle_model_services.KaggleServices.'+name for name in (
 'test_exact_21_agents_18_pinned_candidates_no_winners',
 'test_distinct_candidate_versions_are_never_silently_aliased',
 'test_download_recipes_exclude_mutually_exclusive_weight_variants',
 'test_resources_do_not_pool_two_t4_cards_or_claim_verified_fit',
 'test_cgroup_ram_and_disk_headroom_block_before_download',
 'test_install_approval_is_explicit_exact_and_change_invalidates',
 'test_tokenizer_config_hash_tamper_is_rejected_before_approval',
 'test_origin_and_official_weight_hash_mismatch_rejected',
 'test_production_route_cannot_be_replaced_by_research_preference',
 'test_service_snapshot_is_pinned_not_changed_by_later_preference',
 'test_engine_shared_route_blocks_without_weights_and_never_falls_back',
 'test_writing_limits_and_unsupported_media_controls_rejected',
 'test_retry_cannot_switch_from_legacy_to_new_shared_preference',
 'test_shared_retry_stays_bound_when_production_policy_changes',
 'test_old_ollama_run_snapshot_wins_over_later_shared_configuration',
 'test_engine_retry_uses_same_shared_backend_after_policy_change',
 )]+[
 'tests.test_agent_foundation.FoundationTests.'+name for name in (
 'test_dependency_scheduler_and_revision_scope',
 'test_quality_checks_and_owner_qc_review',
 'test_continuity_and_edit_checks','test_restart_preserves_runs',
 )]+['tests.test_specialist_integration.Integration.test_each_specialist_revisions_approval_sources_and_recovery']


def run():
    with ExitStack() as stack:
        guards={name:stack.enter_context(patch(name,side_effect=AssertionError('FORBIDDEN RESOURCE during no-GPU tests'))) for name in
                ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open','redpad_pipeline.kaggle_runtime.probe')}
        stack.enter_context(patch.dict('sys.modules',{'torch':None,'diffusers':None,'transformers':None,'huggingface_hub':None,'bitsandbytes':None}))
        suite=unittest.defaultTestLoader.loadTestsFromNames(NAMES)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        counts={k:v.call_count for k,v in guards.items()}
    receipt={'scope':'CPU software checks only; no inference/artistic acceptance',
             'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'forbidden_resource_attempts':counts,'new_model_generations':0,'gpu_used':False,
             'model_weights_downloaded':False,'selected_tests':NAMES}
    (ROOT/'verification/no_gpu_19agent/affected_regression_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not result.wasSuccessful() or any(counts.values()):raise SystemExit(1)


if __name__=='__main__':run()
