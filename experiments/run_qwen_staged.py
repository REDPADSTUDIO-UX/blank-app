"""Authorized bounded CPU retest: six stages, at most one explicit retry per stage.
No installation, model pull, production task, automatic rewrite or approval.
"""
import json
from pathlib import Path
from redpad_pipeline.staged_bengali import run_next, KEYS
from redpad_pipeline.local_ollama_session import local_cpu_session

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'verification/phase3_staged'
if __name__=='__main__':
    with local_cpu_session():
        for _ in KEYS:
            r=run_next(FOLDER)
            print(json.dumps({k:r.get(k) for k in ('status','error')},ensure_ascii=False),flush=True)
            if r['status']!='validated_stage':break
