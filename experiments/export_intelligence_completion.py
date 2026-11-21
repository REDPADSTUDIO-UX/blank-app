"""Export preparation and source-preservation evidence, with zero inference.

No historical benchmark is executed or relabeled. Empty review templates are
prepared in a temporary existing AgentStore, never in a production database.
"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from redpad_pipeline.agents import AgentStore
from redpad_pipeline.intelligence import benchmark_audit,sequential_evaluation_plan
from redpad_pipeline.professional_readiness import ProfessionalLab

ROOT=Path(__file__).resolve().parents[1]
BASE='9122eca96881550826d3aa7f2d2e0e895bece471'
OUT=ROOT/'verification/intelligence/completion_20261115'


def export():
    OUT.mkdir(parents=True,exist_ok=True)
    def save(name,data):
        (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    audit=benchmark_audit();plan=sequential_evaluation_plan()
    assert not audit['missing'] and len(audit['agents'])==21
    save('benchmark_coverage.json',audit);save('sequential_evaluation_plan.json',plan)
    packets={}
    with tempfile.TemporaryDirectory() as d:
        lab=ProfessionalLab(AgentStore(Path(d)/'agent_control.sqlite3'))
        for batch in plan['batches']:
            for recipe in batch['agents']:
                trial=lab.plan(recipe['agent'],recipe['professional_trial_profiles'],
                    'Preparation only: evaluate existing pinned candidates against the unchanged role-specific benchmark.',
                    'Independent experts must cite original evidence; software controls do not establish creative capability.',max_calls=24)
                packet,key=lab.blind_packet(trial['id'])
                assert packet['samples']==[] and key=={} and not packet['human_review_completed']
                packets[recipe['agent']]=dict(packet,template_only=True,
                    instructions='After future authorized inference, export the actual bound trial packet. Preserve original bytes and hashes; rename copied assets to their anonymous IDs using the separate administrator mapping. No output or review exists in this template.')
    save('human_review_templates.json',packets)
    protected=['assets/professional','assets/filmmaking','verification/voice_final',
               'verification/offline_execution','verification/intelligence',
               'PHASE3_FINAL_VOICE_INTEGRATION_REPORT_BN.md','PHASE3_NATIVE_OFFLINE_COMPLETION_REPORT_BN.md',
               'PHASE3_VOICE_CASTING_COMPLETION_REPORT_BN.md','PHASE3_DIRECTOR_FIRST_REPORT_BN.md',
               'PHASE3_STORY_INTELLIGENCE_REPORT_BN.md']
    paths=subprocess.run(['git','ls-tree','-r','--name-only',BASE,'--',*protected],cwd=ROOT,
                         check=True,capture_output=True,text=True).stdout.splitlines()
    rows=[]
    for name in paths:
        if Path(name).suffix not in ('.json','.md','.txt'):continue
        before=subprocess.run(['git','show',BASE+':'+name],cwd=ROOT,check=True,capture_output=True).stdout
        current=(ROOT/name).read_bytes()
        rows.append({'path':name,'base_sha256':hashlib.sha256(before).hexdigest(),
                     'current_sha256':hashlib.sha256(current).hexdigest(),'unchanged':before==current})
    assert rows and all(r['unchanged'] for r in rows)
    save('preservation.json',{'base':BASE,'files':rows,'all_unchanged':True,
                            'production_data_opened':False,'new_inference_calls':0})
    print('Prepared',len(packets),'empty review templates;',len(plan['batches']),
          'primary model batches;',len(plan['required_support_batches']),'required support batches;',
          len(rows),'unchanged protected evidence files.')


if __name__=='__main__':export()
