"""Central readiness update restricted to the six previously partial specialists."""
import hashlib,json
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness,OPERATIONS
from redpad_pipeline.offline_specialist_preparation import ROLES,LTX_AUXILIARY,PINS

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/offline_6'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def export():
    baseline=json.loads((OUT/'preservation_baseline.json').read_text())
    rp=ROOT/'assets/professional/phase3_candidates.json';lp=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json'
    reg=json.loads(rp.read_text());ledger=json.loads(lp.read_text());rows=readiness()
    for row in ledger['roles']:
        k=row['agent']
        if k in ROLES:
            row['no_gpu_readiness']=rows[k];row['required_operations']=OPERATIONS[k]
            row['offline_preparation_evidence']='verification/offline_6/'
            reg['agents'][k]['no_gpu_staging'].update(engineering_status=rows[k]['engineering_status'],offline_preparation_evidence='verification/offline_6/')
        else:
            assert sha(row)==baseline['untouched_rows'][k],k
            assert row['no_gpu_readiness']==rows[k],('computed unchanged readiness',k)
    assert sha(reg['profiles'])==baseline['profiles_sha256']
    for k,h in baseline['untouched_agents'].items():assert sha(reg['agents'][k])==h,k
    assert hashlib.sha256((ROOT/'assets/professional/models.json').read_bytes()).hexdigest()==baseline['models_sha256']
    count=sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())
    assert count==13
    ledger['offline_6_engineering_revision']='native-source-preparation-v1'
    lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
    manifest={'kind':'STATIC REQUIREMENTS ONLY, NOT INSTALLED/APPROVED','code_source_revisions':PINS,
      'candidates':{k:{f:reg['profiles'][k][f] for f in ('repo','revision','precision','selected_weight_files','license_conditions','gated','download_approved')} for k in ('wan_animate2','ltx25','indic_speak','indicf5','ace15')},
      'proposed_missing_ltx_component':LTX_AUXILIARY,'weights_downloaded':False,'components_loaded':False,
      'runtime_dependency_locks':'Native source revisions pinned. Complete transitive package locks are NOT validated or installed; see report and source_review.json.'}
    (OUT/'component_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    summary={'checkpoint':baseline['checkpoint'],'target_roles':sorted(ROLES),'engineering_complete':count,
             'partial':6,'production_ready':0,'professionally_verified_of_21':0,
             'roles':{k:rows[k] for k in sorted(ROLES)},'other_thirteen_and_director_script_preserved':True,
             'all_pinned_model_profiles_preserved':True,'gpu_inference_model_weights_hosted_paid_license_acceptance':0}
    (OUT/'readiness.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='roles'},indent=2))

if __name__=='__main__':export()
