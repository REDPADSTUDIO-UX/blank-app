"""Run only new/affected no-inference tests; preserve every attempt separately."""
import importlib.util,json,sys,types,unittest
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'verification/voice_final'
CHANGED=[
 'tests.test_voice_casting_integration.VoiceCastingTests.'+name for name in (
 'test_public_source_and_exact_selected_gated_sources_are_separate',
 'test_unreviewed_selected_voice_fails_before_any_model_import',
 'test_missing_source_casting_draft_abstains_without_hidden_fallback',
 'test_director_inspection_contains_explicit_voice_blocker_without_approval',
 'test_readiness_casting_complete_with_explicit_voice_blocker_not_false_readiness',
 'test_reference_voice_actor_spoof_rejected_and_document_only_draft_cannot_clone')]
CHANGED += [
 'tests.test_offline_six_preparation.OfflineSixTests.test_indicf5_reference_transcript_consent_and_original_bengali_preserved',
 'tests.test_offline_six_preparation.OfflineSixTests.test_indic_speak_keeps_native_entry_unbound_until_exact_revision_verified',
 'tests.test_offline_11_preparation.OfflineElevenTests.test_scope_and_readiness_separate_engineering_from_inference',
 'tests.test_native_local_execution.NativeLocalTests.test_readiness_separates_engineering_from_gated_voice_source',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_all_19_roles_all_declared_supported_contracts_without_resources',
 'tests.test_no_gpu_staging.NoGPUStagingTests.test_ledger_reports_real_engineering_gaps_and_never_accepts_mock_art',
]

class ReceiptResult(unittest.TextTestResult):
    def startTest(self,test):self.attempted.append(test.id());super().startTest(test)
    def addSuccess(self,test):self.successful.append(test.id());super().addSuccess(test)
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.attempted=[];self.successful=[]

def main():
    OUT.mkdir(exist_ok=True)
    if importlib.util.find_spec('requests') is None:
        m=types.ModuleType('requests');m.RequestException=type('RequestException',(Exception,),{})
        def deny(*a,**kw):raise AssertionError('NO HTTP TRANSPORT')
        m.Session=deny;sys.modules['requests']=m
    names=sys.argv[1:] or ['tests.test_selected_voice_binding.SelectedVoiceTests','tests.test_selected_voice_binding.SelectedCastingTests']+CHANGED
    result=unittest.TextTestRunner(verbosity=2,resultclass=ReceiptResult).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    number=len(list(OUT.glob('cpu_attempt_*.json')))+1
    (OUT/f'cpu_attempt_{number:02}.json').write_text(json.dumps(dict(selected=names,attempted=result.attempted,successful=result.successful,
      errors=[t.id() for t,_ in result.errors],failures=[t.id() for t,_ in result.failures],gpu=False,inference=False,real_weights_read_loaded_downloaded=False,
      custom_upstream_executed=False,human_review=False,fixture_scope='Manual fixtures and injected classes only; no native model process launched.'),indent=2)+'\n')
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
