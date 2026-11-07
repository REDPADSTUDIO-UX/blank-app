"""Reproduce Phase 2 specialist evidence in disposable sidecars, never live data."""
import copy,hashlib,json,tempfile
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError,AGENTS,encode
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.specialists import STAGES,example,prepare
from redpad_pipeline.readiness import inspect_resources


def invalid(key,data):
    r=data['records'][0]
    if key=='qc':r['subject_agent']='qc'
    elif key=='character':r['age']=-1
    elif key=='art':r['props']=[]
    elif key=='location':data['records'][2]['openings'][0]['id']='d1'
    elif key=='costume':data['records'][2]['outfit']='white'
    elif key=='storyboard':r['order']=9
    elif key=='performance':r['intensity']=11
    elif key=='cinematographer':data['records'][1]['axis_side']='B'
    elif key=='motion':data['records'][1]['contact']='none'
    elif key=='video':r['mode']='text_to_video'
    elif key=='voice':data['records'][1]['speaker']='voice-rafi'
    elif key=='continuity':data['records'][2]['value']='white'
    elif key=='music':r['asset']='../outside.wav'
    elif key=='editing':r['subtitle_end']=999
    elif key=='production_manager':r['dependencies']=['job-video']
    elif key=='growth':r['title_bn']='a'*101
    elif key=='youtube':r['action']='publish'
    return data


def approve(store,tid):
    t=next(t for t in store.tasks() if t['id']==tid)
    if t['agent']!='qc':store.review(tid,t['revision'],'Recommend','Test-only independent review','qc')
    store.review(tid,t['revision'],'Approve','Test-only owner action','owner')


def export(destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    matrix=[]
    with tempfile.TemporaryDirectory() as d,patch('socket.socket',side_effect=AssertionError('Phase 2 network prohibited')):
        store=AgentStore(Path(d)/'agent_control.sqlite3');engine=Engine(store)
        for stage,keys in STAGES.items():
            for key in keys:
                data=example(key);result=prepare(key,data)
                bad=invalid(key,copy.deepcopy(data))
                try:
                    negative=prepare(key,bad)
                    assert negative['findings'],key+' defect was not detected'
                    outcome='rule finding';details=[f['code'] for f in negative['findings']]
                except AgentError as exc:outcome='rejected';details=[str(exc)]
                rid=engine.enqueue(key,data);assert engine.execute(rid)=='Awaiting QC'
                task=next(r['task'] for r in engine.runs() if r['id']==rid)
                try:store.review(task,1,'Approve','Forbidden self approval',key)
                except AgentError:pass
                else:raise AssertionError('Owner boundary bypass')
                approve(store,task)
                missing=engine.enqueue(key,data,mode='local');assert engine.execute(missing)=='Blocked'
                matrix.append(dict(agent=key,stage=stage,software_developed=True,software_tested=True,
                   input_sha256=hashlib.sha256(encode(data).encode()).hexdigest(),positive='Awaiting QC → independent review → owner Approved',
                   negative=dict(result=outcome,evidence=details),local_model='Blocked — no model configured',
                   provenance=result['provenance'],model_inference=False,media_generated=False,creative_media_quality_verified=False,
                   tests=['tests.test_specialists','tests.test_specialist_integration','tests.test_specialist_ui'],
                   artifact_record_count=len(result['artifact']['records']),approval_boundary='self/model approval rejected'))
        report=dict(phase=2,registered_agents=len(AGENTS),specialists=len(matrix),stages=list(STAGES),
                    inference_runs=0,creative_media_quality_verified=False,fixture_provenance='Original manually authored fictional Bengali metadata; temporary test sidecars',
                    resources=inspect_resources(False),matrix=matrix)
        assert len(AGENTS)==20 and len(matrix)==17
        (destination/'matrix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        # Keep auditable events, omit random UUIDs and mutable production paths.
        events=[dict(actor=e['actor'],action=e['action']) for e in store.history()]
        (destination/'audit_summary.json').write_text(json.dumps(dict(event_count=len(events),events=events),indent=2)+'\n')
    return report

if __name__=='__main__':
    report=export(Path(__file__).resolve().parents[1]/'verification/specialists')
    print('PASS: 17 specialist positive/negative cases; 20 registered; 0 model inference')
