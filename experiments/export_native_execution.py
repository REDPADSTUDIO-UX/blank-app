"""Update only six agent readiness entries, preserving previous verified evidence."""
import hashlib,json
from pathlib import Path
from redpad_pipeline.no_gpu_staging import readiness,OPERATIONS
from redpad_pipeline.native_local_bundle import REQUIRED,SOURCE_FILES
from redpad_pipeline.offline_specialist_preparation import PINS,LTX_AUXILIARY

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/offline_execution'
SCOPE={'performance','motion','video','voice','music','casting'}
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def export():
    b=json.loads((OUT/'preservation_baseline.json').read_text());rows=readiness()
    rp=ROOT/'assets/professional/phase3_candidates.json';lp=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json';reg=json.loads(rp.read_text());ledger=json.loads(lp.read_text())
    for row in ledger['roles']:
        k=row['agent']
        if k in SCOPE:
            row['no_gpu_readiness']=rows[k];row['required_operations']=OPERATIONS[k]
            row['native_execution_evidence']='verification/offline_execution/'
            reg['agents'][k]['no_gpu_staging'].update(engineering_status=rows[k]['engineering_status'],native_execution_evidence='verification/offline_execution/')
        else:
            assert sha(row)==b['untouched_rows'][k],k
            assert row['no_gpu_readiness']==rows[k],k
    assert sha(reg['profiles'])==b['profiles_sha256']
    for k,h in b['untouched_agents'].items():assert sha(reg['agents'][k])==h,k
    assert hashlib.sha256((ROOT/'assets/professional/models.json').read_bytes()).hexdigest()==b['models_sha256']
    ledger['native_local_execution_revision']='source-pinned-offline-workers-v1'
    lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
    (OUT/'component_inventory.json').write_text(json.dumps({'kind':'requirements only; NOT installed, downloaded or approved','required_paths':REQUIRED,'required_source_paths':SOURCE_FILES,'source_revisions':PINS,
      'ltx_missing_auxiliary':LTX_AUXILIARY,'ltx_packed_text_assets':'tokenizer_json + gemma_config + embedded HF assets per pinned gemma_assets.py; actual weight metadata validation pending',
      'wan_auxiliary_origins':'Must be exact owner-approved compatible repository/revisions; no filename-based origin claim',
      'ace_auxiliary_policy':'Authenticated bounded .pt file, weights_only=True/map_location=cpu, tensor type/shape/size/finite checks; fixed reviewed local model class, no model-side Python execution',
      'runtime_packages':'No package/model installation in this task. Wan official requirements.txt pinned with source; LTX package 1.6.2 plus its source dependencies; ACE pinned native package/local model classes. Full installed dependency/code receipt required before launch.'},ensure_ascii=False,indent=2)+'\n')
    (OUT/'readiness.json').write_text(json.dumps({'resumed_commit':b['checkpoint'],'engineering_complete':17,'partial':2,'production_ready':0,'professionally_validated_of_21':0,'other_thirteen_director_script_profiles_preserved':True,'roles':{k:rows[k] for k in sorted(SCOPE)}},ensure_ascii=False,indent=2)+'\n')
    print('Preserved 13 prepared agents, Director/Script, all pinned profiles and models.json; updated six readiness records only.')

if __name__=='__main__':export()
