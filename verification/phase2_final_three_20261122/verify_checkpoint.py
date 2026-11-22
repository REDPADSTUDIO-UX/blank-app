"""Check this continuation without rerunning accepted profiles or model code."""
import ast
import hashlib
import json
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT))
from redpad_pipeline.worker_isolation import source_digest


def read(path):
    return json.loads(path.read_text())


def main():
    previous=ROOT/'verification/phase2_resume_20261122/18-profile-readiness.json'
    old=read(previous);new=read(BASE/'18-profile-readiness.json')
    assert hashlib.sha256(previous.read_bytes()).hexdigest()==new['continuation']['previous_matrix_sha256']
    assert new['total_model_free_secure_pass']==old['total_model_free_secure_pass']==15
    assert len(new['profiles'])==18 and new['phase2']=='BLOCKED'
    remaining={'wan_animate2','indic_speak','indicf5'}
    unchanged=[name for name in old['profiles'] if name not in remaining]
    assert len(unchanged)==15
    for name in unchanged:assert old['profiles'][name]==new['profiles'][name]
    binding=read(ROOT/'verification/phase2_resume_20261122/ci-public-runtime/binding.json')
    assert source_digest()==binding['studio_sha256']
    kaggle=read(BASE/'kaggle-host-receipt.json')
    assert kaggle['exit_code']==1 and kaggle['namespace_primitive_pass'] is False
    assert kaggle['session_stopped'] and not kaggle['private_voice_source_transferred']
    for field in ('model_inference','weights_downloaded','cuda_initialized'):
        assert kaggle[field] is False
    for filename in ('speak-selected-source-check.json','f5-selected-source-check.json'):
        source=read(BASE/filename)
        assert source['sha256']==source['expected_sha256']
        assert not source['source_executed'] and not source['gated_source_committed_or_uploaded']
    codec=read(BASE/'vocos-mel-candidate.json')
    candidate=(BASE/'vocos_mel_candidate.py.txt').read_bytes()
    assert hashlib.sha256(candidate).hexdigest()==codec['candidate_sha256']
    ast.parse(candidate)
    for field in ('source_executed','secure_binding_verified','full_commercial_stack_verified',
                  'decoder_waveform_verified','launch_authorized'):
        assert codec[field] is False
    assert new['separate_ltx_auxiliary_gate']['authoritative_sha256'] is None
    assert read(BASE/'render-safety.json')['safe_to_push']
    print('PASS continuation evidence: prior 15 profiles/source fingerprint unchanged; no false kernel/model/codec/LTX acceptance')


if __name__=='__main__':main()
