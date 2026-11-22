"""Update only the eleven partial roles; preserve the eight earlier rows verbatim."""
import hashlib,json
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness,load,OPERATIONS
from redpad_pipeline.offline_department_contracts import PARTIAL_ROLES
from redpad_pipeline.offline_preparation import INTERFACES,NATIVE

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/offline_11'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def export():
    baseline=json.loads((OUT/'preservation_baseline.json').read_text());registry,_=load();rows=readiness()
    path=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json';doc=json.loads(path.read_text())
    for r in doc['roles']:
        k=r['agent']
        if k in PARTIAL_ROLES:
            r['required_operations']=OPERATIONS[k];r['no_gpu_readiness']=rows[k]
            r['offline_preparation_evidence']='verification/offline_11/'
            registry['agents'][k]['no_gpu_staging'].update(engineering_status=rows[k]['engineering_status'],offline_preparation_evidence='verification/offline_11/')
        else:assert sha(r)==baseline['untouched_role_rows'][k]
    for k,h in baseline['untouched_agent_records'].items():assert sha(registry['agents'][k])==h
    assert sha(registry['profiles'])==baseline['profiles_sha256']
    assert hashlib.sha256((ROOT/'assets/professional/models.json').read_bytes()).hexdigest()==baseline['models_file_sha256']
    doc['offline_11_engineering_revision']='offline-first-preparation-v1'
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'assets/professional/phase3_candidates.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    result={'resumed_checkpoint':baseline['checkpoint'],'target_roles':sorted(PARTIAL_ROLES),
            'newly_engineering_complete':[k for k in sorted(PARTIAL_ROLES) if rows[k]['engineering_status']=='NO-GPU ENGINEERING COMPLETE'],
            'no_gpu_complete_total':sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values()),
            'gpu_inference_weights_paid_api':0,'production_ready':0,'eight_and_director_script_preserved':True,
            'roles':{k:rows[k] for k in sorted(PARTIAL_ROLES)},'contract_only_interfaces':INTERFACES,
            'existing_native_bindings':NATIVE,'status_scope':'No-GPU engineering only, actual runtime/outputs/human review unverified'}
    (OUT/'readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('roles','contract_only_interfaces','existing_native_bindings')},indent=2))

if __name__=='__main__':export()
