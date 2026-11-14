"""Only Voice/Casting ledger updates; other seventeen records remain byte-identical."""
import hashlib,json
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness,OPERATIONS
from redpad_pipeline.voice_source_policy import binding_status

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/voice_casting'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def export():
    b=json.loads((OUT/'preservation_baseline.json').read_text());rows=readiness()
    rp=ROOT/'assets/professional/phase3_candidates.json';lp=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json';reg=json.loads(rp.read_text());ledger=json.loads(lp.read_text())
    for row in ledger['roles']:
        k=row['agent']
        if k in ('voice','casting'):
            row['no_gpu_readiness']=rows[k];row['voice_casting_evidence']='verification/voice_casting/'
            reg['agents'][k]['no_gpu_staging'].update(engineering_status=rows[k]['engineering_status'],voice_casting_evidence='verification/voice_casting/')
        else:
            assert sha(row)==b['untouched_rows'][k],k
            assert row['no_gpu_readiness']==rows[k],k
    for k,h in b['untouched_agents'].items():assert sha(reg['agents'][k])==h,k
    assert sha(reg['profiles'])==b['profiles_sha256']
    assert hashlib.sha256((ROOT/'assets/professional/models.json').read_bytes()).hexdigest()==b['models_sha256']
    ledger['voice_casting_engineering_revision']='selected-voice-bindings-v2'
    reg['agents']['voice']['no_gpu_staging']['selected_source_bindings']={pid:binding_status(pid) for pid in ('indic_speak','indicf5','indic_parler')}
    lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
    matrix={k:{'engineering':rows[k]['engineering_status'],'runtime':'MODEL/GPU VALIDATION BLOCKED','creative':'HUMAN REVIEW PENDING','production_ready':False} for k in rows}
    complete=sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())
    result={'resumed_commit':'e7dc992f187d9bd545b88d3ee11dd174ac08566c','total_agents_in_matrix':19,'director_script':'separate unchanged workstreams','engineering_complete':complete,'partial':19-complete,'professionally_accepted_of_21':0,'other_seventeen_and_all_profiles_preserved':True,'gpu_inference_weights_hosted_paid_license_acceptance':0,'roles':matrix,'voice_candidates':{pid:binding_status(pid) for pid in ('indic_speak','indicf5','indic_parler')},'latest_evidence':'verification/voice_final/'}
    (OUT/'readiness_19.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('roles','voice_candidates')},indent=2))
if __name__=='__main__':export()
