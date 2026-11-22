"""Six new equivalent-task CPU control cases; no new model download or fallback.
Uses only the exact restored, previously authorized Qwen model. Real output is
copied to the feature-branch evidence directory after each completed attempt.
"""
import json
from pathlib import Path
from redpad_pipeline.local_ollama_session import local_cpu_session,ROOT
from redpad_pipeline.agents import AgentStore
from redpad_pipeline.model_routing import ModelRoutes,inventory
from redpad_pipeline.model_benchmark import run_case,cases

MODEL='qwen3:4b-instruct-2507-q4_K_M'
DIGEST='sha256:0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0'
if __name__=='__main__':
    root=ROOT/'phase3_runs/master_baseline';store=AgentStore(root/'agent_control.sqlite3')
    with local_cpu_session():
        assert inventory().get(MODEL)==DIGEST
        ModelRoutes(store).approve_installed(MODEL,DIGEST,'Previously approved Apache-2.0 control; exact pinned model restored','existing owner authorization',True)
        for case in cases():
            result=run_case(store,root/'cases',MODEL,case['id'])
            print(case['id'],result['status'],result.get('error'),flush=True)
            for manifest in (root/'cases').glob('*/manifest.json'):
                out=ROOT/'verification/master_studio/qwen_control';out.mkdir(parents=True,exist_ok=True)
                for p in manifest.parent.glob('*.json'):(out/p.name).write_bytes(p.read_bytes())
