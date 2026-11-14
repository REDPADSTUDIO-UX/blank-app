"""Offline reproducible evidence; all owner approvals below are test fixtures."""
import json
import tempfile
from pathlib import Path
from redpad_pipeline.agents import AgentStore,AGENTS
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.readiness import inspect_resources
from tests.test_agent_foundation import fixture


def main():
    root=Path(__file__).resolve().parents[1]/'verification'
    root.mkdir(exist_ok=True)
    readiness=inspect_resources(probe=True)
    matrix=[]
    with tempfile.TemporaryDirectory() as temp:
        store=AgentStore(Path(temp)/'agent_control.sqlite3');engine=Engine(store)
        previous=None
        order=['story','script','director','character','art','location','costume','storyboard','performance','cinematographer','motion','video','continuity','voice','music','editing','qc','production_manager','growth','youtube']
        ids={}
        for key in order:
            data=fixture(key);deps=[previous] if previous else []
            if key=='storyboard':
                deps.append(ids['script'])
                data['script']={'$from':ids['script'],'path':['artifact','formatted']}
            rid=engine.enqueue(key,data,deps);assert engine.execute(rid)=='Awaiting QC'
            run=next(r for r in engine.runs() if r['id']==rid);tid=run['task']
            if key!='qc':store.review(tid,1,'Recommend','Synthetic test review; not a real creative verdict','qc')
            store.review(tid,1,'Approve','Synthetic owner action performed only in test workspace','owner')
            ids[key]=tid;previous=tid
            matrix.append({'id':AGENTS[key]['id'],'name':AGENTS[key]['name'],'software':'Software Working',
                'workspace':True,'execution_test':'passed','task':tid,'input_contract':True,
                'output_contract':True,'review_revision_handoff':'tested','model_connected':False,
                'real_inference_verified':False,'production_quality_verified':False,
                'blockers':[{'category':'B','detail':'No available local model server on this host'},
                            {'category':'C','detail':'No compatible local model configured'},
                            {'category':'E','detail':'Creative/media quality not independently verified'}]})
        media=[]
        for key in ('video','voice','music','editing'):
            rid=engine.enqueue(key,fixture(key),mode='media');assert engine.execute(rid)=='Blocked'
            media.append(next(r for r in engine.runs() if r['id']==rid))
        evidence={'provenance':'software test with supplied Bengali fixture and simulated human approvals',
                  'real_inference_completed':0,'scene_media_generated':0,'department_count':len(matrix),
                  'tasks':store.tasks(),'runs':engine.runs(),'outputs':store.outputs(),'audit':store.history(),
                  'blocked_media_attempts':media,'readiness':readiness}
        (root/'agent_foundation_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    (root/'agent_implementation_matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    print('PASS: 20 software department outputs; 4 honest media blocks; zero real model inference; evidence exported')
    print(json.dumps(readiness))
if __name__=='__main__':main()
