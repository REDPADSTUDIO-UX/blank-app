"""Export actual saved candidates; never invokes inference or invents human ratings."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from redpad_pipeline.staged_writing import blind_package, plan_schema, scene_schema, state_check, ground_review, digest, expand_compact_scene
from redpad_pipeline.staged_bengali import NAMES, GOALS, INITIAL, BRIEF

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/phase3_staged'
def read(path):return json.loads(path.read_text())
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))

if __name__=='__main__':
    records=[]
    for folder in ('phase3_staged','phase3_grounded'):
        for p in sorted((ROOT/'verification'/folder).glob('*.json')):
            r=read(p)
            if isinstance(r,dict) and 'request_sha256' in r:
                if r['status']=='running':raise SystemExit('Do not export an active generation.')
                assert digest(r['request'])==r['request_sha256']
                raw_hash=hashlib.sha256(r['raw'].encode()).hexdigest()
                if r.get('evidence',{}).get('raw_sha256'):assert raw_hash==r['evidence']['raw_sha256']
                records.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'raw_sha256':raw_hash,'status_at_generation':r['status'],'role':r['request']['role'],
                    'completed':r.get('evidence',{}).get('inference_completed',False),
                    'finish_reason':r.get('evidence',{}).get('finish_reason'),
                    'tokens':r.get('evidence',{}).get('eval_count'),'seconds':r.get('evidence',{}).get('wall_seconds'),
                    'error':r['error']})
    plan=read(OUT/'plan.json')['result']
    post={'scope':'Revalidation of ORIGINAL replies using strengthened guards, no model rerun; semantic quality still unverified',
          'plan_goal_schema_pass':Draft202012Validator(plan_schema(NAMES,GOALS)).is_valid(plan),'beats':[]}
    before=INITIAL
    for i in range(1,4):
        r=read(OUT/f'beat{i}.json')['result'];error=''
        try:state_check(before,r['state_after'],NAMES)
        except ValueError as exc:error=str(exc)
        post['beats'].append({'id':f'beat{i}','state_check_pass':not error,'error':error});before=r['state_after']
    scene=read(OUT/'scene.json')['result']
    post['scene_schema_errors']=[e.message for e in Draft202012Validator(scene_schema(NAMES)).iter_errors(scene)]
    review=read(OUT/'director.json')['result']
    post['director_grounded']=ground_review(review,scene,digest(scene))
    old_story=read(ROOT/'verification/phase3_cpu/trial_story_nfc.json')['result']
    old_script=read(ROOT/'verification/phase3_cpu/trial_script_nfc.json')['result']['scenes'][0]
    candidates={'checkpoint_story':old_story,'staged_story':{'plan':plan,'beats':[read(OUT/f'beat{i}.json')['result'] for i in range(1,4)]},
                'checkpoint_home_scene':old_script,'staged_home_scene':scene}
    grounded=ROOT/'verification/phase3_grounded/scene.json'
    if grounded.exists():
        gr=read(grounded)
        if gr['result'] and 'opening_action' in gr['result']:
            try:expand_compact_scene(gr['result'],NAMES);post['compact_slot_check_pass']=True
            except ValueError as exc:post['compact_slot_check_pass']=False;post['compact_slot_error']=str(exc)
        if (grounded.parent/'expanded_scene.json').exists():
            expanded=read(grounded.parent/'expanded_scene.json')['scene']
            candidates['fixed_brief_home_scene']=expanded
            if (grounded.parent/'director.json').exists():
                post['fixed_brief_director_grounded']=ground_review(read(grounded.parent/'director.json')['result'],expanded,digest(expanded))
        elif gr['result']:candidates['fixed_brief_home_scene']=gr['result']
    save('postcheck.json',post)
    package,mapping=blind_package(candidates)
    package['brief']=BRIEF
    package['comparison_limit']='Different generation contracts, budgets and scene scopes; diagnostic comparison only, not a controlled quality win. Some drafts violate contracts. Do not infer artistic acceptance.'
    if not (OUT/'blind_review.json').exists():
        save('blind_review.json',package);save('blind_admin_mapping.json',mapping)
    summary={'checkpoint':'7a6b1ed1b82e3fd82500da05b739f098c147cb95',
         'actual_attempts':len(records),'complete_runtime_replies':sum(r['completed'] for r in records),
         'incomplete_runtime_attempts':sum(not r['completed'] for r in records),
         'validated_at_generation':sum(r['status_at_generation']=='validated_stage' for r in records),
         'total_measured_wall_seconds':round(sum(r['seconds'] or 0 for r in records),3),
         'records':records,'human_review_completed':False,'production_approved':False,
         'important':'Status at generation used the schema saved in each request. Postcheck records stricter guards added after observing real failures. Neither status constitutes creative acceptance.',
         'alternative_models_downloaded':0,'alternative_models_tested':0}
    save('summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},ensure_ascii=False,indent=2))
