"""Export CPU-validated preparation state; never runs a model or approves one."""
import argparse
import hashlib
import json
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import patch
from redpad_pipeline.no_gpu_staging import load,readiness,candidate_ids,resolve_profile,capabilities,OPERATIONS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/no_gpu_19agent'
SEQUENCE=['story','character','art','costume','storyboard','growth','production_manager','youtube',
          'video','voice','music','location','cinematographer','continuity','qc','performance','motion','editing','casting']


def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def export(update=False):
    OUT.mkdir(exist_ok=True)
    with ExitStack() as stack:
        guards={name:stack.enter_context(patch(name,side_effect=AssertionError('Resource forbidden in no-GPU export'))) for name in ('socket.socket','subprocess.run','subprocess.Popen','urllib.request.OpenerDirector.open')}
        stack.enter_context(patch.dict('sys.modules',{'torch':None,'transformers':None,'diffusers':None,'huggingface_hub':None,'bitsandbytes':None}))
        registry,roles=load();rows=readiness();baseline=json.loads((OUT/'preservation_baseline.json').read_text())
        assert sha(registry['profiles'])==baseline['profiles_sha256']
        for role in ('director','script'):assert sha(registry['agents'][role])==baseline[role+'_sha256']
        assert set(SEQUENCE)==set(rows) and len(SEQUENCE)==19
        profiles={pid:resolve_profile(pid,registry) for role,r in roles.items() for pid in candidate_ids(role,r)}
        contracts={k:{'repo':p['repo'],'revision':p['revision'],'profile_sha256':sha(p),
                      'adapter':p['adapter'],'supported_draft_operations':sorted(capabilities(p)),
                      'precision':p['precision'],'weight_bytes':p['selected_weight_bytes'],
                      'planning_gpu_gib':p['planning_gpu_gib'],'planning_ram_gib':p['planning_ram_gib'],
                      'license_metadata':p.get('license_metadata',p.get('license')),
                      'license_conditions':p['license_conditions'],'gated':p.get('gated','not recorded; approval still required'),
                      'exact_download_approval_required':not p['download_approved'],
                      'runtime_api_verified':False} for k,p in profiles.items()}
        (OUT/'runtime_dependencies.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2)+'\n')
        if update:
            path=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json';doc=json.loads(path.read_text())
            doc['no_gpu_engineering_ledger_version']='cpu-contract-validation-v1'
            doc['validation_evidence']='verification/no_gpu_19agent/'
            doc['status_scope']='NO-GPU ENGINEERING COMPLETE means safe preparation code/config only; not runtime, model quality, human acceptance or production integration.'
            for r in doc['roles']:
                role=r['agent'];r['required_operations']=OPERATIONS[role];r['no_gpu_readiness']=rows[role]
                r['supplemental_research_candidates']=[p for p in candidate_ids(role,r) if p not in [r['primary_research_candidate']]+r['alternative_research_candidates']]
                r['supplemental_binding_scope']='Existing professional suite/models.json only; explicit separate image critic, not a primary/secondary replacement.'
                r['integration_stage']='cpu_contracts_validated_runtime_blocked'
                registry['agents'][role]['no_gpu_staging']={'ledger':'assets/professional/phase3_19agent_no_gpu_staging.json',
                                                           'engineering_status':rows[role]['engineering_status'],
                                                           'runtime_verified':False,'production_ready':False}
            doc['future_gpu_execution_sequence']=SEQUENCE
            path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
            (ROOT/'assets/professional/phase3_candidates.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
        complete=sum(r['engineering_status']=='NO-GPU ENGINEERING COMPLETE' for r in rows.values())
        result={'baseline_checkpoint':baseline['checkpoint'],'scope':19,'engineering_complete':complete,
                'partial':19-complete,'production_ready':0,'gpu_used':False,'model_inferences':0,'weight_downloads':0,
                'forbidden_resource_attempts':{k:v.call_count for k,v in guards.items()},
                'director_script_and_profiles_preserved':True,'gpu_sequence':SEQUENCE,'roles':rows}
        (OUT/'readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--update-ledger',action='store_true');args=parser.parse_args()
    result=export(args.update_ledger)
    print(json.dumps({k:v for k,v in result.items() if k!='roles'},ensure_ascii=False,indent=2))
