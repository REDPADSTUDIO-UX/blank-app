"""Reproducible isolated engineering exercise. No model or human-review claims.
CLI is for engineering recovery; owner operates the existing Dashboard.
"""
import argparse,json,platform,time
from pathlib import Path
from .agents import AgentError
from .creative import digest
from .pre_gpu_project import run_fixture,screenplay
from .studio_program import StudioProgram,ROOT
from .production_execution import ProductionOps
from .readiness import inspect_resources

def run(project_id,evidence_dir):
    if not project_id.startswith('pre-gpu-fixture-'):raise AgentError('Only a clearly isolated acceptance-fixture project ID is allowed.')
    out=Path(evidence_dir)
    if not out.resolve().is_relative_to((ROOT/'verification/pre_gpu').resolve()) or any(p.is_symlink() for p in (out,*out.parents)):raise AgentError('Use this repository’s verification/pre_gpu evidence directory.')
    out.mkdir(parents=True,exist_ok=True);p=StudioProgram(project_id);start=time.monotonic()
    if p.summary()['project'] is not None:
        receipt=out/'acceptance.json'
        if not receipt.is_file():raise AgentError('Interrupted fixture retained; inspect existing run IDs and recover before any new exercise.')
        previous=json.loads(receipt.read_text())
        if previous['project_id']!=project_id:raise AgentError('Existing evidence belongs to a different fixture.')
        for entry in previous['log']:
            if digest(p.current_output(entry['task'])['artifact'])!=entry['artifact_sha256']:raise AgentError('Saved acceptance sources changed.')
        return previous
    result=run_fixture(p);result.update(project_id=project_id,seconds=round(time.monotonic()-start,3),scope='Executable engineering fixture, not real creative intelligence or artistic approval.')
    ops=ProductionOps(p);tasks={'script':result['script_task'],**{r:result['tasks'][r] for r in ('character','art','location','costume','storyboard','performance','cinematographer','motion')}}
    boards=p.current_output(result['tasks']['storyboard'])['artifact']['records'];packets=[ops.shot(tasks,s['id']) for s in boards]
    artifacts=[]
    for record in result['log']:
        body=p.current_output(record['task']);artifacts.append({'role':record['role'],'task':record['task'],'source':'manually_authored_fixture','approval':'simulated_software_exercise_only',
             'artifact':body['artifact'],'artifact_sha256':digest(body['artifact']),'findings':body.get('findings',[]),'formatted':body.get('formatted')})
    (out/'acceptance_artifacts.json').write_text(json.dumps({'real_model_calls':0,'human_artistic_reviews':0,'artifacts':artifacts},ensure_ascii=False,indent=2))
    (out/'shot_execution_packets.json').write_text(json.dumps(packets,ensure_ascii=False,indent=2))
    (out/'episode1_screenplay.md').write_text('# ফিরতি টিকিট — manually authored acceptance fixture\n\nNot model output; not artistically approved.\n\n'+next(a['formatted'] for a in artifacts if a['role']=='script'))
    (out/'project_overview.json').write_text(json.dumps(p.production_overview(),ensure_ascii=False,indent=2))
    (out/'environment.json').write_text(json.dumps({'resources':inspect_resources(False),'python':platform.python_version(),'platform':platform.platform(),'new_model_downloads':0,'new_inference_calls':0,'new_human_reviews':0},ensure_ascii=False,indent=2))
    (out/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project-id',required=True);parser.add_argument('--evidence-dir',default=str(ROOT/'verification/pre_gpu'));args=parser.parse_args()
    r=run(args.project_id,args.evidence_dir);print(json.dumps({'project':r['project_id'],'agents':len(r['agents_exercised']),'executed_stages':len(r['log']),'new_model_calls':0,'human_reviews':0}))
