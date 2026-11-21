"""Current 19-agent engineering audit. Reuses verified evidence; no test reruns.
Same assistant's code audit, never an independent human/artistic evaluation.
"""
import ast,hashlib,json
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness
from redpad_pipeline.voice_source_policy import binding_status
from redpad_pipeline.voice_native_contracts import source_lock

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/voice_final'
def sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def audit():
    attempts=[json.loads(p.read_text()) for p in sorted(OUT.glob('cpu_attempt_*.json'))]
    successful={t for r in attempts for t in r['successful']}
    # A test-selection typo is retained as an actual error, not relabeled as a code failure.
    errors={t for r in attempts for t in r['errors']+r['failures']}
    expected=[]
    tree=ast.parse((ROOT/'tests/test_selected_voice_binding.py').read_text())
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name in ('SelectedVoiceTests','SelectedCastingTests'):
            expected += ['tests.test_selected_voice_binding.'+n.name+'.'+m.name for m in n.body if isinstance(m,ast.FunctionDef) and m.name.startswith('test_')]
    assert len(expected)==24 and set(expected)<=successful,(len(expected),set(expected)-successful)
    from .test_selected_voice import CHANGED
    assert set(CHANGED)<=successful and len(successful)==36,(set(CHANGED)-successful,len(successful))
    assert errors=={'unittest.loader._FailedTest.test_readiness_preserves_complete_vs_runtime_blocked_and_partial'}
    assert all(not r[k] for r in attempts for k in ('gpu','inference','real_weights_read_loaded_downloaded','custom_upstream_executed','human_review'))
    b=json.loads((ROOT/'verification/voice_casting/preservation_baseline.json').read_text())
    registry=json.loads((ROOT/'assets/professional/phase3_candidates.json').read_text())
    ledger=json.loads((ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json').read_text())
    for k,v in b['untouched_agents'].items():assert sha(registry['agents'][k])==v,k
    for r in ledger['roles']:
        if r['agent'] in b['untouched_rows']:assert sha(r)==b['untouched_rows'][r['agent']],r['agent']
    assert sha(registry['profiles'])==b['profiles_sha256']
    assert hashlib.sha256((ROOT/'assets/professional/models.json').read_bytes()).hexdigest()==b['models_sha256']
    rows=readiness();assert len(rows)==19 and all(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())
    assert all(not r['runtime_verified'] and not r['production_ready'] for r in rows.values())
    assert all(ledger_row['no_gpu_readiness']==rows[ledger_row['agent']] for ledger_row in ledger['roles'])
    assert all(not binding_status(pid)['source_blocked'] and not binding_status(pid)['runtime_verified'] for pid in ('indic_speak','indicf5','indic_parler'))
    files=('voice_source_policy.py','voice_native_contracts.py','native_voice_worker.py','native_execution.py','native_local_bundle.py','native_local_worker.py','offline_preparation.py','offline_specialist_preparation.py')
    texts={n:(ROOT/'redpad_pipeline'/n).read_text() for n in files}
    for n,s in texts.items():ast.parse(s)
    for n in ('voice_native_contracts.py','native_voice_worker.py'):
        for node in ast.parse(texts[n]).body:
            if isinstance(node,ast.Import):assert not any(a.name.split('.')[0] in ('torch','transformers','snac','f5_tts','vocos') for a in node.names)
    assert 'weights_only=False' not in texts['native_voice_worker.py'] and 'trust_remote_code=True' not in texts['native_voice_worker.py']
    assert 'require_voice_job(job)' in texts['native_voice_worker.py'] and 'local_files_only=True' in texts['native_voice_worker.py']
    assert "'indic_speak':voice,'indicf5':voice" in texts['native_local_worker.py']
    assert 'Kernel-isolated network namespace required before any model import' in texts['native_local_worker.py']
    assert 'if authorized is not True' in texts['native_execution.py'] and 'cancel_owned_process' in texts['native_execution.py']
    assert "'raw_audio.npy'),audio,allow_pickle=False" in texts['native_voice_worker.py']
    lock=source_lock();assert sum(len(m['files']) for m in lock['models'].values())==19
    result={'resumed_commit':'e7dc992f187d9bd545b88d3ee11dd174ac08566c','audit_kind':'Current automated code/evidence audit by same assistant; not independent human review',
      'new_distinct_checks':24,'affected_existing_distinct_checks':12,'distinct_successful_checks':len(successful),'successful_test_ids':sorted(successful),
      'test_invocations':sum(len(r['attempted']) for r in attempts),'unique_error_retained':sorted(errors),'error_resolution':'Test selector name corrected; actual intended readiness test passed. No code assertion failures observed.',
      'recheck_reasons':['After adding zero-energy/wrong-rate/truncated-reference guard, only four affected F5 positives rerun alongside one new guard test.','After requiring source-review manifest at binding resolution, only two affected source gates rerun alongside two first-time checks.'],
      'engineering_complete':19,'partial':0,'runtime':'MODEL/GPU VALIDATION BLOCKED','artistic':'HUMAN REVIEW PENDING','professionally_accepted_of_21':0,
      'source_files_reviewed':19,'source_byte_attestation':'Exact revision Raw page text hashes; not an independent Git-blob byte attestation. Future approved local source must match or fail closed.',
      'models_profiles_other_seventeen_director_script_preserved':True,'source_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in texts.items()},
      'real_generation_or_listening_results':None,'gpu_cpu_inference_real_weights_hosted_paid_new_licenses':0,
      'historical_supervisor_evidence_reused':'verification/offline_execution/second_audit.json: fixed CPU dummy timeout/cancellation/recovery; not repeated because lifecycle implementation unchanged.',
      'remaining_runtime_dependencies':{
       'indic_speak':['Approved exact 7,068,852,569-byte selected weight recipe; no download approved by this task','Exact approved SNAC 24kHz auxiliary revision/files + dependencies','Matching selected v9 EMA weights-only codec state and BF16 package/device compatibility','Bounded source prompt/token-contract and ckpt-8937/8944 documentation discrepancy test','Independent Bengali listening/speaker/pronunciation/emotion review and owner acceptance'],
       'indicf5':['Approved exact 1,402,789,408-byte selected safetensors recipe; no download approved by this task','Actual selected INF5 wrapper key/shape and fixed FP32 DiT/CFM/Vocos compatibility','Approved installed f5_tts/dependencies + complete owner source/code/license receipt','Actual authorized voice reference/transcript, scoped non-revoked human consent and independent listening'],
       'shared':['Owner hardware kernel isolation preflight (prior bwrap failure remains unresolved)','Separate explicit model installation/download and runtime/GPU authorization','Raw output + provenance + independent QC/Director/Producer approval gates']}}
    (OUT/'final_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('distinct_successful_checks','new_distinct_checks','affected_existing_distinct_checks','engineering_complete','partial','professionally_accepted_of_21')}))
    return result

if __name__=='__main__':audit()
