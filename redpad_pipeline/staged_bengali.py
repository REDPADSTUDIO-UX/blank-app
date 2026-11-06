"""Resumable six-call Bengali CPU pilot; one explicitly requested stage per call."""
import json
from jsonschema import Draft202012Validator
from .staged_writing import (StagedDraft, plan_schema, beat_schema, scene_schema,
                             director_schema, state_check, ground_review, digest, compact_scene_schema, expand_compact_scene)
from .screenwriter import WritingError

MODEL='qwen3:4b-instruct-2507-q4_K_M'
NAMES=['রাশেদ','তানিয়া']
BRIEF='ঢাকার বৃষ্টির সকাল। রাশেদ (৩২) ও তানিয়া (২৯) বিবাহিত। তানিয়ার চাকরির সাক্ষাৎকার, রাশেদের অফিসে জরুরি উপস্থিতি; একটি ছাতা আর সীমিত বাসভাড়া। তাদের অভ্যাসের তফাতে স্বাভাবিক রসিকতা ও মমতা আছে। বাস্তব সিদ্ধান্তে সমস্যা সামলাবে; জোর করা কাকতাল বা নীতিকথা নয়।'
GOALS={NAMES[0]:'নিজের অফিসে পৌঁছানো',NAMES[1]:'নিজের চাকরির সাক্ষাৎকারে পৌঁছানো'}
INITIAL={NAMES[0]:'home',NAMES[1]:'home','umbrella':'table'}
DOMAINS={NAMES[0]:['home','door','bus_stop','office'],NAMES[1]:['home','door','bus_stop','interview'],
         'umbrella':['table']+NAMES}
KEYS=['plan','beat1','beat2','beat3','scene','director']


def run_next(folder, *, complete=None):
    lab=StagedDraft(folder);records={}
    for k in KEYS:
        p=lab.folder/(k+'.json')
        if not p.exists():break
        r=json.loads(p.read_text())
        if r['status']!='validated_stage':raise WritingError('Stopped at '+k+'; inspect the saved failure before an explicit retry.')
        # Check immutable parent hashes even when re-opening an existing pipeline.
        for dep, h in r['request']['dependencies'].items():
            if digest(records.get(dep))!=h:raise WritingError('Stale staged dependency: '+dep)
        if k=='plan' and not Draft202012Validator(plan_schema(NAMES,GOALS)).is_valid(r['result']):
            raise WritingError('Saved plan contradicts fixed character goals; do not propagate it. Preserve evidence and start a separate corrected draft.')
        records[k]=r
    if len(records)==len(KEYS):return {'status':'needs_human_editorial_review','stages':len(records),'production_approved':False}
    key=KEYS[len(records)];deps=list(records)
    base={'brief':BRIEF,'names':NAMES,'initial_state':INITIAL,'fixed_goals':GOALS}
    check=None
    if key=='plan':
        role='story';schema=plan_schema(NAMES,GOALS);data=base
        task='Design distinct wants, fears and habits for EACH named person, then an opening image, emotional payoff and earned unresolved decision. No dialogue. Do not resolve the entire interview/job outcome. প্রতি উত্তরে সর্বোচ্চ ছয়টি বাংলা শব্দ; ছোট সরাসরি বাক্য।'
        def check(result):
            if sorted(c['name'] for c in result['characters'])!=sorted(NAMES):raise WritingError('Each known character must occur exactly once.')
    elif key.startswith('beat'):
        role='story';index=int(key[-1]);before=INITIAL if index==1 else records['beat'+str(index-1)]['result']['state_after']
        schema=beat_schema(NAMES,DOMAINS,'brief' if index==1 else 'beat'+str(index-1))
        data=dict(base,plan=records['plan']['result'],state_before=before,
                  previous_beats=[records[k]['result'] for k in records if k.startswith('beat')])
        task=f'Write ONLY beat {index} of 3. The actor chooses because of a stated want; name a concrete cost and visible consequence. '+('Open on the material conflict.' if index==1 else 'Previous consequence must force this choice. ')+('Pay off a caring action, then leave a practical consequential decision unresolved.' if index==3 else '')+' No teleporting; table is at home. Umbrella transfer only when holders are together and do not travel in this beat. State_after must agree with visible action; no offscreen purchase, extra umbrella or unexplained return. One short sentence per field.'
        check=lambda result:state_check(before,result['state_after'],NAMES)
    elif key=='scene':
        role='script';schema=compact_scene_schema()
        data=dict(base,plan=records['plan']['result'],story=[records[k]['result'] for k in ('beat1','beat2','beat3')])
        check=lambda result:expand_compact_scene(result,NAMES)
        task='Dramatize ONLY the first home moment from the story, NOT all three beats. Use the five fixed fields: heading (INT.), opening_action, first_reply (রাশেদ), second_reply (তানিয়া), closing_action. Two short responsive dialogue turns only. Preserve actual prop position; finish before later travel. Bangladeshi spoken Bengali: natural তুমি/তোমার, not literary declarations. Let her answer his words; gentle marital teasing comes from their differing habits and the real umbrella problem. Care through behavior, not a moral speech. No narration of inner thoughts, no random mystery.'
    else:
        role='director';scene=expand_compact_scene(records['scene']['result'],NAMES);schema=director_schema(scene)
        data={'source_sha256':digest(scene),'lines':{f'L{i+1}':b for i,b in enumerate(scene['beats'])}}
        task='Return at most TWO concrete editorial problems actually supported by the indexed source. Empty findings is allowed if unsure. Cite line_id only; NEVER generate a quotation. Do not praise without evidence. Check if each reply answers the previous line and whether actions are filmable and prop states plausible. Suggestions are hypotheses for a human, never an automatic rewrite. Preserve the source facts; invent no missing events or people.'
        check=lambda result:ground_review(result,scene,digest(scene))
    return lab.run(key,role,data,task,schema,dependencies=deps,model=MODEL,tokens=1024 if key in ('plan','scene') else 768,complete=complete,check=check)
