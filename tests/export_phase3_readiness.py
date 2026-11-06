"""Actual host preflight, with no injected provider, download, GPU session or paid API."""
import json
from pathlib import Path
from redpad_pipeline.phase3 import Lab,audit,cases
from redpad_pipeline.agents import AGENTS


def export():
    root=Path(__file__).resolve().parents[1]/'verification/phase3';root.mkdir(parents=True,exist_ok=True)
    ready=audit(True);(root/'hardware.json').write_text(json.dumps(ready,indent=2)+'\n')
    lab=Lab('phase3-readiness-checkpoint')
    # Only bounded localhost requests; they do not install/pull or contact external inference.
    for case in ('family_architecture','horror_architecture_30'):
        rid=lab.queue(case,'qwen3:4b-instruct-2507-q4_K_M')
        run=next(r for r in lab.engine.runs() if r['id']==rid)
        if run['state']=='Ready for Input':lab.run(rid)
    summary=lab.summary()
    summary['registered_agents']=len(AGENTS)
    summary['blocked_media_stages']=['D: reference images unavailable','E/F: no GPU/checkpoint, no generated performance/video','G: local Bengali TTS backend/weights absent','H/I: genuine audiovisual assets and independent reviewers absent','K: upstream prerequisites missing; no cinematic MP4 produced']
    summary['source_dependent_cases']=[dict(id=c['id'],state='Awaiting actual generated, owner-approved upstream source') for c in cases() if c['requires_source']]
    (root/'status.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    approval=dict(required=True,granted=False,action='Install local Ollama runtime and download qwen3:4b-instruct-2507-q4_K_M in this development environment only',model_download_bytes_approx=2500000000,paid=False,cloud_gpu=False,personal_computer_install=False,source='https://ollama.com/library/qwen3/tags',next='After explicit approval: verify runtime release, pull one exact model tag, record full digest, run bounded CPU text tests, measure RAM/latency, preserve raw replies and request independent Bengali review.')
    (root/'approval_request.json').write_text(json.dumps(approval,indent=2)+'\n')
    print('Real completed inference:',summary['real_inference_completed'])
    print('Blocked local preflights:',summary['blocked_preflight_or_dependency'])
    print('Genuine cinematic export:',summary['playable_cinematic_export'])

if __name__=='__main__':export()
