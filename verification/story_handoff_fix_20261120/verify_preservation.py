"""Offline source/evidence preservation receipt. No runtime/model execution."""
import ast,hashlib,json,runpy,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE='7a737fc1af6bb62d61ca31dae11d23c6701f64cc'
path='verification/story_budget8_20261119/sections_only_resume_cell.py'
original=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode()
updated=(ROOT/path).read_text();old=ast.parse(original);new=ast.parse(updated)
def named(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.Assign)) and (getattr(n,'name',None)==name or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
def dump(n):return ast.dump(n,include_attributes=False)
for name in ('BUNDLE','BASELINE','AUTHORIZATION','SECTIONS','digest','validate','authorize','reserve','budget','section_eligibility'):
 assert dump(named(old,name))==dump(named(new,name)),name
# Preserve exact prompt/details generation and server launch configuration.
for target in ('details','system','prompt'):
 extract=lambda tree:[dump(n) for n in ast.walk(named(tree,'generate_section')) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==target for t in n.targets)]
 assert extract(old)==extract(new),target
launch=lambda tree:[dump(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen']
assert launch(old)==launch(new)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'verification/story_budget8_20261119','verification/story_budget8_20261120','verification/story_option_c_20261116'],cwd=ROOT,text=True).splitlines()
allowed={path,'verification/story_budget8_20261119/test_adapter_budget.py'}
protected=[]
for name in paths:
 if name in allowed:continue
 before=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
 assert before==(ROOT/name).read_bytes(),name
 protected.append({'path':name,'sha256':hashlib.sha256(before).hexdigest()})
scope=runpy.run_path(str(HERE/'test_handoff.py'));guard=scope['declarations']()
f=json.loads((ROOT/'verification/story_budget8_20261120/restored_foundation_actual.json').read_text())
a=json.loads((ROOT/'verification/story_budget8_20261120/restored_act1_actual.json').read_text())
try:guard['require_story_handoff']({'foundation':f['sections']['foundation']['parsed'],'act_1':a['section']['parsed']})
except guard['StoryHandoffError'] as e:findings=e.findings
else:raise AssertionError('Actual malformed outputs incorrectly accepted')
(HERE/'actual_output_replay.json').write_text(json.dumps({'scope':'CPU replay of saved genuine model output; not new inference','error_type':'StoryHandoffError','findings':findings,'no_runtime_launch':True,'no_output_repair':True,'consumed':5,'ceiling':8,'remaining':3,'new_model_calls':0,'human_review':'PENDING','benchmark_resume':'BLOCKED_INVALID_PRIOR_OUTPUT'},ensure_ascii=False,indent=2)+'\n')
(HERE/'preservation.json').write_text(json.dumps({'base_commit':BASE,'protected_files_count':len(protected),'protected_files':protected,'prompt_bundle_baseline_budget_limits_and_server_command_unchanged':True,'production_worker_changed':False,'new_inferences':0,'gpu_use':0,'downloads':0,'test_scope':'11 distinct new handoff tests + 2 affected adapter/budget regression tests; mocked transport is not inference evidence','new_test_fixture_repairs':'Mock process STDOUT and foundation schema fixture completed during initial test development; not new model calls or additional independent tests'},indent=2)+'\n')
print(json.dumps({'protected_files':len(protected),'actual_findings':len(findings),'source_preservation':'PASS','new_model_calls':0}))
