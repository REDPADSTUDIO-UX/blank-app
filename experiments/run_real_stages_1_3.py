"""CLI: no inference without both explicit execution/free-runtime flags."""
import argparse
import json
from pathlib import Path
from redpad_pipeline.stages_1_3 import Session,audio_case,manifest,write_human_package


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['all','1','2','3'],default='all')
    p.add_argument('--root',type=Path,default=Path('phase3_runs/real_stages_1_3'))
    p.add_argument('--execute',action='store_true')
    p.add_argument('--free-runtime-verified',action='store_true')
    p.add_argument('--full',action='store_true')
    p.add_argument('--export-lightweight',type=Path)
    a=p.parse_args();session=Session(a.root)
    for stage in (range(1,4) if a.stage=='all' else [int(a.stage)]):
        state=session.run(stage,authorized=a.execute,free_runtime_verified=a.free_runtime_verified,full=a.full)
        package=write_human_package(session.root,stage,state)
        if a.export_lightweight:
            destination=a.export_lightweight/f'stage{stage}';destination.mkdir(parents=True,exist_ok=True)
            # No binary artifact, database, approval receipt or gated source in Git.
            data={k:state[k] for k in ('manifest','status','human_review','owner_accepted','real_inference_calls','calls')}
            data['worker_execution_attempts']=state['worker_execution_attempts']
            data['inference_count_scope']=state['inference_count_scope']
            data['blocker']=state.get('blocker');data['runtime']=state['latest_preflight']
            data['bundle_status']='No authenticated remote bundle available in this blocked run' if not state['samples'] else 'See private exact install/source receipts'
            data['genuine_sample_manifests']=[{k:s.get(k) for k in ('id','kind','sha256','model','model_digest','stage_technical','signal_metrics')} for s in state['samples']]
            data['audio_links_publicly_accessible']=False
            (destination/'status.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
            # Only blocked templates can be copied automatically. Genuine text or
            # private audio-path packets need explicit lightweight-content review.
            if not state['samples']:(destination/package.name).write_text(package.read_text())
            if stage>1:
                inputs=[dict(label=audio_case(stage,i)[0],request=audio_case(stage,i)[2],spec=audio_case(stage,i)[3],
                    provenance='manually_authored_input_NOT_model_output') for i in range(manifest(stage)['max_calls'])]
                (destination/'original_requests.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'stage':stage,'status':state['status'],'real_inference_calls':state['real_inference_calls'],
            'blocker':state.get('blocker'),'private_review_package':str(package)},ensure_ascii=False))


if __name__=='__main__':main()
