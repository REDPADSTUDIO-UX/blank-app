"""Separate second code-audit pass; same assistant, not human/artistic review."""
import ast,hashlib,json,re
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness
from redpad_pipeline.voice_source_policy import PUBLIC_SOURCE

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/voice_casting'
def audit():
    if all(x['selected_source_verified'] for x in PUBLIC_SOURCE.values()):
        # Keep the checkpoint-specific 18/19 receipt intact; current audit writes separately.
        from .audit_selected_voice import audit as current_audit
        return current_audit()
    files=['casting_voice.py','voice_consent.py','voice_source_policy.py','native_voice_worker.py','casting.py','native_execution.py','agent_engine.py']
    texts={n:(ROOT/'redpad_pipeline'/n).read_text() for n in files}
    for s in texts.values():ast.parse(s)
    tree=ast.parse(texts['native_voice_worker.py'])
    assert all(not any(a.name in ('torch','transformers','snac','bodhan_genai') for a in n.names) for n in tree.body if isinstance(n,ast.Import))
    assert 'weights_only=True' in texts['native_voice_worker.py'] and 'weights_only=False' not in texts['native_voice_worker.py']
    assert 'local_files_only=True' in texts['native_voice_worker.py'] and 'trust_remote_code=False' in texts['native_voice_worker.py']
    assert 'require_selected_source' in texts['native_voice_worker.py'] and all(x['selected_source_verified'] is False for x in PUBLIC_SOURCE.values())
    assert 'generic text/model execution is prohibited' in texts['agent_engine.py']
    assert 'packet_fingerprint' in texts['casting.py'] and 'voice_sha' in texts['casting.py']
    assert 'voice_consent_revocations' in texts['voice_consent.py'] and 'document upload is insufficient' in texts['voice_consent.py']
    success=set()
    for p in OUT.glob('*.txt'):success.update(re.findall(r'\((tests\.[^)]+)\) \.\.\. ok',p.read_text()))
    methods={x.name for x in ast.walk(ast.parse((ROOT/'tests/test_voice_casting_integration.py').read_text())) if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')}
    assert len(methods)==37 and len(success)==46,(len(methods),len(success))
    assert all('tests.test_voice_casting_integration.VoiceCastingTests.'+n in success for n in methods)
    sources=json.loads((OUT/'public_source_metadata.json').read_text());assert len(sources)==14 and all(x['git_blob_bytes_match'] for x in sources)
    correction=json.loads((OUT/'source_lock_correction.json').read_text());lock=json.loads((ROOT/'assets/professional/phase3_native_source_lock.json').read_text())
    for r in correction['files']:assert lock['files'][r['profile']][r['path']]==r['canonical_source_sha256']
    rows=readiness();assert sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())==18
    assert rows['voice']['engineering_status']=='PARTIAL' and rows['casting']['engineering_status']=='NO-GPU ENGINEERING COMPLETE'
    assert all(not r['production_ready'] and not r['runtime_verified'] for r in rows.values())
    result={'kind':'second automated code-audit pass, same assistant; no independent human review',
      'code_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in texts.items()},'distinct_successful_checks':46,'new_tests':37,'affected_existing_checks':9,'successful_test_ids':sorted(success),
      'findings_fixed':['Missing casting revision output now raises deterministic AgentError','Public source versus selected gated source kept separate','Exact source-lock newline corruption corrected against 16 authoritative Git blobs','Native voice audition cannot fall back to generic text/model execution','Character/casting/assessment/reference pins rechecked in staging and Director review','Attached native voice artifact must remain original, correctly bound and present','Voice/Casting raw upstream diagnostic logs suppressed; private inputs remain local provenance records'],
      'open_ordinary_cpu_findings':[],'remaining_source_access_requirement':PUBLIC_SOURCE,
      'engineering_complete':18,'partial':1,'runtime_status':'MODEL/GPU VALIDATION BLOCKED','creative_status':'HUMAN REVIEW PENDING','professionally_accepted_of_21':0,
      'gpu_inference_weights_hosted_paid_license_acceptance':0}
    (OUT/'second_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'audit_passed':True,'distinct_checks':46,'engineering_complete':18,'partial':1,'professional_ready':0}))
if __name__=='__main__':audit()
