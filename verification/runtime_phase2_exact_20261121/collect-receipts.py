"""Attach kernel-run evidence to the seven open rows; keep the earlier 11 untouched."""
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLDER=HERE.parent/'runtime_phase2_targeted_20261121'
RUNS={'ltx25':44932910851,'ace15':44933003941,'wan_animate2':44933044564}


def read_run(profile,number):
    run=json.loads((HERE/f'github-{number}.json').read_text())
    raw=gzip.decompress((HERE/f'github-{number}.log.gz').read_bytes()).decode()
    lines=[line.split('\t',2)[-1].partition(' ')[2] for line in raw.splitlines()
           if line.startswith('runtime-phase2-ltx\tImport pinned entrypoints')]
    identity=next((json.loads(line) for line in lines if line.startswith('{') and '"publisher_source_revision"' in line),None)
    output=None
    if '{' in lines:
        start=lines.index('{')
        end=lines.index('}',start+1)
        output=json.loads('\n'.join(lines[start:end+1]))
        assert output['profile']==profile and output['loaded_weights'] is False and output['inference'] is False
        assert output['interpreter']=='/redpad/runtime/bin/python3.11'
        assert all(v['file'].startswith('/redpad/source/') for v in output['imports'].values() if v['ok'])
    if identity:
        assert identity['profile']==profile
    all_imports=bool(output and all(row['ok'] for row in output['imports'].values()))
    return {'run_url':run['url'],'tested_commit':run['headSha'],'workflow_conclusion':run['conclusion'],
            'profile':profile,'binding':identity,'isolated_probe':output,
            'source_mount_and_cpu_imports_pass':bool(run['conclusion']=='success' and identity and all_imports)}


def main():
    previous=json.loads((OLDER/'final-18-profile-matrix.json').read_text())
    rows=previous['profiles']
    receipts={name:read_run(name,number) for name,number in RUNS.items()}
    for key in ('ltx25','ace15'):
        profile=rows[key]
        if receipts[key]['source_mount_and_cpu_imports_pass']:
            profile.update(runtime_contract='IMPLEMENTED — exact publisher Python source and isolated CPU diagnostic lock',
                           cpu_model_free_startup='PASS — exact pinned source entrypoints imported in production sandbox',
                           secure_runtime_binding='PASS — exact revision, interpreter, packages, file and ABI manifests; isolated CPU child',
                           observed=('Locked Torch 2.10 CPU diagnostic environment and bound publisher entrypoints. '
                                     'No models were instantiated.'))
        profile.update(evidence='sandbox-receipts.json#'+key)
    rows['ltx25']['remaining']=('Exact spatial-upscaler official SHA-256 and approved model/auxiliary manifest; '
                               'separate CUDA and full model tests. OpenImageIO shutdown reference-count warning '
                               'was localized to the import combination, with process exit zero.')
    rows['ace15']['remaining']=('Approved model install and publisher CUDA 12.8 runtime, GPU execution '
                               'and actual generated audio validation. Optional training modules excluded.')
    wan=rows['wan_animate2']
    wan.update(cpu_model_free_startup='BLOCKED — exact source initializes CUDA in a module-level default argument',
               secure_runtime_binding=('PASS — diagnostic interpreter, receipt and kernel startup'
                   if receipts['wan_animate2']['isolated_probe'] else 'PARTIAL — host lock available; isolated child receipt pending'),
               observed='Pinned source and CPU dependency lock recovered. Exact import fails at T5Encoder device default.',
               evidence='wan-import-trace.txt',
               remaining='Publisher-reviewed deferred device initialization or authorized CUDA import on the pinned recipe.')
    rows['qwen35_moe'].update(observed='CPU/meta synthetic FP8 E4M3FN conversion and routed reference passed on 128x128 tile geometry.',
        evidence='moe-candidate-recipe.json',
        remaining='Owner approval for exact FP8 backend and checkpoint; actual CUDA kernel and model tests.')
    rows['wan_animate2_distilled']['evidence']='publisher-options.json'
    rows['indicf5'].update(evidence='publisher-options.json',
        remaining='Authorized exact source, owner-approved commercial vocoder and compatibility verification. Upstream BigVGAN is a candidate, with no IndicF5 substitution authorized.')
    rows['indic_speak']['evidence']='publisher-options.json'
    new_count=sum(row['source_mount_and_cpu_imports_pass'] for row in receipts.values())
    assert len(rows)==18
    (HERE/'sandbox-receipts.json').write_text(json.dumps(receipts,indent=2,ensure_ascii=False)+'\n')
    final={'previous_verified':11,'new_cpu_verified':new_count,'total_verified':11+new_count,'total_profiles':18,'profiles':rows}
    (HERE/'final-18-profile-matrix.json').write_text(json.dumps(final,indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':
    main()
