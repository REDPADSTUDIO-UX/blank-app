"""Offline cross-check of actual receipts; does not run models or repeat suites."""
import hashlib
import json
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.worker_isolation import source_digest


def load(name):
    return json.loads((BASE / name).read_text())


def main():
    matrix = load('18-profile-readiness.json')
    assert len(matrix['profiles']) == 18
    assert matrix['previous_model_free_secure_pass'] == 13
    assert matrix['new_model_free_secure_pass'] == 2
    assert matrix['total_model_free_secure_pass'] == 15
    assert matrix['phase2'] == 'BLOCKED' and matrix['gpu_purchase'] == 'NOT APPROVED'
    job = load('ci-verification.json')
    assert job['conclusion'] == 'success' and job['commit'] == 'd8fbed1f9593934b170be404e5af72ab5209f64d'
    log = (BASE / 'ci-public-runtime-job.log').read_bytes()
    assert hashlib.sha256(log).hexdigest() == job['log_sha256']
    binding = load('ci-public-runtime/binding.json')
    assert source_digest() == binding['studio_sha256']
    manifest = load('ci-public-runtime/source-receipt.json')
    raw = (BASE / 'ci-public-runtime/source-receipt.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == binding['source_manifest_sha256']
    assert manifest['model_weights'] is False and manifest['source_execution'] is False
    assert len(manifest['source_files']) == binding['source_files'] == 1033
    wheels = load('ci-public-runtime/wheel-acquisition.json')
    assert wheels['verified_files'] == 79
    assert sum(f['bytes'] for f in wheels['files']) == 4200362442
    lock = binding['identity']['dependency_lock']
    for row in wheels['files']:
        assert lock[row['name']] == row['version']
    for worker in job['worker_boundaries']:
        receipt = load('ci-public-runtime/' + worker + '.json')
        assert receipt['status'] == 'PASS' and receipt['kernel_files'] == 12
        assert receipt['kernel_revision'] == '3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8'
        for field in ('cuda_initialized', 'weights_loaded', 'model_inference',
                      'registry_routes_promoted', 'production_ready'):
            assert receipt[field] is False
    identity = load('wan-component-identity-comparison.json')
    assert identity['all_component_file_identities_match'] and identity['weight_shards'] == 4
    assert identity['weights_downloaded'] is False and identity['tensor_values_read'] is False
    for folder in ('transformer', 'scheduler'):
        a=load('wan-59e4141-' + folder + '-metadata.json')
        b=load('wan-ff28d41-' + folder + '-metadata.json')
        assert a['pagination'] is None and b['pagination'] is None
        before={f['path']:(f['oid'],f['size'],f.get('lfs')) for f in a['files']}
        after={f['path']:(f['oid'],f['size'],f.get('lfs')) for f in b['files']}
        assert before == after
    assert load('f5-mel-comparison.json')['frontends_interchangeable'] is False
    assert len(load('voice-source-access.json')['exact_matching_files']) == 18
    tests=set()
    for name in ('affected-cpu-tests.log','new-tests-final.log','changed-contract-tests.log'):
        tests.update(re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. ok$',(BASE/name).read_text(),re.M))
    assert len(tests) == load('cpu-test-summary.json')['distinct_passed_cpu_tests'] == 95
    assert load('render-safety.json')['safe_to_push'] is True
    print('PASS: 18-profile ledger, 15 model-free secure profiles, 95 distinct CPU tests, exact source/binding/wheel identities and closed GPU/production gates')


if __name__ == '__main__':
    main()
