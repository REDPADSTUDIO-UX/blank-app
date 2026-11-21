"""Independently reconcile existing kernel receipts and live Actions metadata."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
V=ROOT/'verification'
BASE=V/'runtime_phase2_20261121'
STABLE=V/'runtime_phase2_remaining_20261121'
EXACT=V/'runtime_phase2_exact_20261121'
KERNEL=V/'kernel_phase1_20261121'


def load(path):
    return json.loads(path.read_text())


def normalized_lock(path):
    return dict(line.split('==',1) for line in path.read_text().splitlines())


def verify_run(folder, run_id, job_name, expected_commit, expected_lines):
    historical=load(folder/f'github-{run_id}.json') if folder!=KERNEL else load(folder/f'github-final-{run_id}.json')
    live=json.loads(subprocess.check_output(['gh','run','view',str(run_id),'--json','headSha,status,conclusion,jobs'],cwd=ROOT,text=True))
    assert live['headSha']==historical['headSha']==expected_commit
    assert live['status']==historical['status']=='completed'
    assert live['conclusion']==historical['conclusion']=='success'
    for record in (historical,live):
        job=next(j for j in record['jobs'] if j['name']==job_name)
        assert job['conclusion']=='success'
    log=folder/(f'github-{run_id}.log.gz' if folder!=KERNEL else f'github-final-{run_id}.log.gz')
    with gzip.open(log,'rt') as stream:
        body=stream.read()
    assert all(line in body for line in expected_lines)
    return {'run':run_id,'commit':expected_commit,'job':job_name,
            'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'live_confirmed':True}


def probe_json(folder,run_id,job_name,step):
    with gzip.open(folder/f'github-{run_id}.log.gz','rt') as stream:
        prefix=f'{job_name}\t{step}\t'
        messages=[line.removeprefix(prefix).split(' ',1)[1].rstrip('\n')
                  for line in stream if line.startswith(prefix)]
    start=messages.index('{')
    end=messages.index('}',start+1)
    return json.loads('\n'.join(messages[start:end+1]))


def main():
    matrix=load(EXACT/'final-18-profile-matrix.json')['profiles']
    registry=load(ROOT/'assets/professional/phase3_candidates.json')['profiles']
    confirmed={}
    for name,r in load(BASE/'sandbox-results.json').items():
        lock=normalized_lock(BASE/f'{name}.lock.txt')
        assert r['binding']['identity']['dependency_lock']==lock
        assert hashlib.sha256(json.dumps(lock,sort_keys=True).encode()).hexdigest()==r['lock_sha256']
        assert r['isolated_imports_passed'] and r['import_count']>0
        from_log=probe_json(BASE,44922713868,f'runtime-phase2 ({name})',
                            'Verify real runtime startup inside the production sandbox')
        assert from_log['interpreter']==r['interpreter']
        assert from_log['dependency_lock']==lock and from_log['weights_loaded'] is False
        assert len(from_log['imports'])==r['import_count'] and all(v['ok'] for v in from_log['imports'].values())
        names=r['binding']['validated_profiles']
        evidence=verify_run(BASE,44922713868,f'runtime-phase2 ({name})',r['tested_commit'],
                            [r['interpreter'],*names])
        for profile in names:
            confirmed[profile]=evidence
    r=load(STABLE/'stable-sandbox-receipt.json')
    assert r['isolated_pass'] and r['exit_code']==0 and r['binding']['validated_profiles']==['stable_audio_small']
    assert all(v['passed'] for v in r['probe']['imports'].values())
    assert r['binding']['identity']['dependency_lock']==normalized_lock(STABLE/'stable.lock.txt')
    assert r['lock_file_sha256']==hashlib.sha256((STABLE/'stable.lock.txt').read_bytes()).hexdigest()
    assert probe_json(STABLE,44924150354,'runtime-phase2 (stable)',
                      'Verify real runtime startup inside the production sandbox')==r['probe']
    confirmed['stable_audio_small']=verify_run(STABLE,44924150354,'runtime-phase2 (stable)',r['tested_commit'],
                                              ['stable_audio_small',r['probe']['interpreter']])
    exact=load(EXACT/'sandbox-receipts.json')
    for key,run in [('ltx25',44932910851),('ace15',44933003941)]:
        r=exact[key]
        assert r['source_mount_and_cpu_imports_pass'] and r['workflow_conclusion']=='success'
        binding=r['binding']
        assert binding['revision']==registry[key]['revision']
        assert binding['identity']['dependency_lock']==normalized_lock(EXACT/f'{key}.lock.txt')
        source=EXACT/f'{key}-source-lock.json'
        assert len(load(source))==binding['source_files']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['source_lock_sha256']
        probe=r['isolated_probe']
        assert not probe['loaded_weights'] and not probe['inference']
        assert all(x['ok'] and x['file'].startswith('/redpad/source/') for x in probe['imports'].values())
        assert probe_json(EXACT,run,'runtime-phase2-ltx','Import pinned entrypoints in the production sandbox')==probe
        confirmed[key]=verify_run(EXACT,run,'runtime-phase2-ltx',r['tested_commit'],[key,probe['interpreter']])
    historical_kernel=load(KERNEL/'github-final-44921166025.json')
    kernel=verify_run(KERNEL,44921166025,'kernel-phase1',historical_kernel['headSha'],
                      ['PASS F synthetic launch boundary: native_local_worker',
                       'PASS F synthetic launch boundary: shared_model_worker',
                       'Phase 1 probe exit code: 0'])
    assert len(registry)==len(matrix)==18
    assert all(row['repo']==registry[key]['repo'] and row['revision']==registry[key]['revision'] for key,row in matrix.items())
    assert set(confirmed)=={k for k,row in matrix.items() if row['cpu_model_free_startup'].startswith('PASS')}
    assert len(confirmed)==13
    print(json.dumps({'verified_profiles':confirmed,'total':len(confirmed),'kernel':kernel,
                      'new_runtime_runs':0,'total_profiles':len(matrix)},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
