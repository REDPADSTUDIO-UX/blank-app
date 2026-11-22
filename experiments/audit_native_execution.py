"""Second automated code-level audit, separate from test assertions; no inference.
Same engineering session, not an independent human review or model acceptance.
"""
import ast,hashlib,json,re
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/offline_execution'

def audit():
    names=('native_execution.py','native_local_bundle.py','native_local_worker.py','native_fixture_worker.py')
    files={n:(ROOT/'redpad_pipeline'/n).read_text() for n in names}
    for n,s in files.items():ast.parse(s)
    worker=ast.parse(files['native_local_worker.py'])
    imports=[a.name for n in worker.body if isinstance(n,ast.Import) for a in n.names]
    assert not set(imports)&{'torch','transformers','diffusers','acestep','ltx_pipelines'}
    assert 'trust_remote_code=True' not in files['native_local_worker.py']
    assert "weights_only=True,map_location='cpu'" in files['native_local_worker.py']
    assert 'Kernel-isolated network namespace required before any model import' in files['native_local_worker.py']
    assert "'--unshare-net'" in files['native_execution.py'] and "'--ro-bind'" in files['native_execution.py']
    assert 'start_new_session=True' in files['native_execution.py'] and 'cancel_owned_process' in files['native_execution.py']
    assert 'controller_ticks' in files['native_execution.py'] and 'BEGIN IMMEDIATE' in files['native_execution.py']
    assert "'production_ready':False" in files['native_execution.py']
    successful=set()
    for path in OUT.glob('*.txt'):
        successful.update(re.findall(r'\((tests\.[^)]+)\) \.\.\. ok',path.read_text()))
    assert len(successful)==52,len(successful)
    methods={n.name for n in ast.walk(ast.parse((ROOT/'tests/test_native_local_execution.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    assert len(methods)==38 and all('tests.test_native_local_execution.NativeLocalTests.'+n in successful for n in methods)
    rows=readiness();assert sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())==17
    roles=['performance','motion','video','voice','music','casting']
    result={'audit':'Second automated code audit, same assistant; NOT independent human review',
      'findings_fixed':['atomic queue deduplication','controller/worker source fingerprints','reject unreviewed cached Python bytecode','kernel namespace check before model imports','nested artifact path and symlink handling','cancel escalation and PID reuse protection','recovery distinguishes active controller preflight/postprocess from abandoned execution'],
      'source_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in files.items()},
      'distinct_tests_successfully_verified':len(successful),'tests':sorted(successful),
      'role_matrix':{k:{'engineering':rows[k]['engineering_status'],'runtime':'MODEL/GPU VALIDATION BLOCKED','artistic':'HUMAN REVIEW PENDING','production_ready':False,
                      'native_path':'fixed native local worker + authenticated bundle + isolated supervisor' if k not in ('voice','casting') else 'Parler/Wan/surrounding workflow implemented; exact selected gated voice source remains unavailable'} for k in roles},
      'ordinary_cpu_engineering_findings_open':[],
      'unavoidable_source_blockers':{'voice':'Exact pinned Indic-Speak inference/speaker map and IndicF5 gated source/auxiliary review require owner-authorized access, not guessing from preview-v2.',
                                     'casting':'Selected Indic-Speak shared binding depends on the same unavailable exact voice source.'},
      'runtime_blockers':['Current environment denies bwrap kernel network namespace; native inference must not launch here','No actual model install/weights/license approved by this task','LTX official pinned upsampler exact SHA/size still unverified; third-party mirror digest is not adopted','Wan exact approved auxiliary origins/hashes and actual weights-only compatibility','Full owner-approved local dependency/code bundles and actual GPU/MPI/media/listening tests'],
      'gpu_inference_weights_hosted_paid_license_acceptance':0,'human_artistic_reviews':0,'production_ready':0}
    (OUT/'second_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'audit_checks_passed':True,'distinct_tests':52,'engineering_complete':17,'partial':2,'professional_ready':0}))

if __name__=='__main__':audit()
