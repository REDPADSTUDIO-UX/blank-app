"""Validate captured research outputs offline; never infer, download or approve art."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile

from redpad_pipeline.agents import AgentStore, AgentError
from redpad_pipeline.director import Director, validate
from redpad_pipeline.screenwriter import model_json

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'verification/director_recovery_20261113'


def inspect(case):
    path=EVIDENCE/(case+'_raw.txt');raw=path.read_text()
    result={'case':case,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'strict_json':False,'derived_json':False,'professional_accepted':False,
            'independent_review':'pending','finish_reason':None,'truncation':'unknown'}
    try:model_json(raw);result['strict_json']=True
    except ValueError as e:result['strict_error']=str(e)
    text=raw.strip()
    if text.startswith('```json\n') and text.endswith('```'):
        text=text[7:-3].strip();result['derivation']='outer Markdown fence removed only'
    else:result['derivation']='none; no repair or partial extraction'
    try:data=model_json(text);result['derived_json']=True
    except ValueError as e:result['derived_error']=str(e);return result,None
    (EVIDENCE/(case+'_derived.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return result,data


def validate_all():
    rows=[]
    for case in ('director_plan','source_understanding','locked_camera_revision','source_questions'):
        row,data=inspect(case)
        if case=='director_plan':
            row['plan_contract_pass']=False
            if data is not None:
                try:validate(data,30);row['plan_contract_pass']=True
                except AgentError as e:row['plan_error']=str(e)
            row['visible_response_ends_mid_string']=True
        elif case=='source_understanding':
            row['excluded_from_factual_accuracy']=True
            row['reason']='Input supplied answer values and ambiguously assumed salma_has_job=false; interview does not establish her employment status. Preserve as a leading diagnostic, not comprehension evidence.'
        elif case=='source_questions' and data is not None:
            source=json.loads((ROOT/'assets/professional/kaggle_bengali_cases.json').read_text())['original_brief']
            answers=data.get('answers',[])
            row['four_distinct_ids']=len(answers)==4 and {a.get('id') for a in answers}=={1,2,3,4}
            row['quotes_grounded']=all(isinstance(a.get('quote'),str) and a['quote'].strip() and a['quote'] in source for a in answers)
            row['editorial_observation']='Four answers match source facts; no job-loss invention. Operator assessment only, not independent expertise or creative approval.'
        elif case=='locked_camera_revision' and data is not None:
            row['target_contract_pass']=set(data)=={'target','replacement'} and data['target']=='/scenes/0/camera' and isinstance(data['replacement'],str) and 0<len(data['replacement'].split())<=30
            row['editorial_observation']='Scope is correct. Replacement describes gesture and speculative memory weight; camera framing/movement is unspecified. Independent artistic review still required.'
            if row['target_contract_pass']:row['research_gate_check']=check_research_revision(data['replacement'])
        rows.append(row)
    out={'classification':'hosted research evidence; no production integration',
         'new_submissions':5,'preserved_responses':4,'excluded_leading_diagnostics':1,
         'delegation':'one submitted attempt displayed Error and no assistant response; stop requested, completion unknown; do not blind retry',
         'selected_model':None,'professionally_complete_agents':0,'cases':rows}
    (EVIDENCE/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    return out


def check_research_revision(replacement):
    # A manually authored benchmark fixture, not owner-approved production art.
    base={'vision':'সনদ দেখার মুহূর্ত','tone':'সংযত',
          'scenes':[{'id':'s1','seconds':15,'visual':'রুবা সনদ দেখে থামে।',
                     'performance':'সংযত দ্বিধা','camera':'স্থির মিডিয়াম শট',
                     'sound':'দূরের যানবাহন','continuity':'নীল ব্যাগ, একই সকাল, interview অজানা'}],
          'assignments':[{'agent':'script','brief':'সনদ দেখা পর্যন্ত লিখুন','scene_ids':['s1']}],
          'risks':['প্রকৃত footage ও স্বাধীন পর্যালোচনা বাকি']}
    with tempfile.TemporaryDirectory() as tmp:
        d=Director(AgentStore(Path(tmp)/'agent_control.sqlite3'))
        pid=d.create('Research fixture only',15,manual=base)
        d.review(pid,'Request revision','Synthetic test scope only','owner',allowed_changes=['/scenes/0/camera'])
        changed=copy.deepcopy(base);changed['scenes'][0]['camera']=replacement
        new=d.create('Research fixture only',15,manual=changed,revision_of=pid)
        rejected=False
        try:d.dispatch(new)
        except AgentError:rejected=True
        return {'scope_check_executed':True,'state':d.plans()[0]['state'],
                'provenance':d.plans()[0]['provenance'],'unapproved_dispatch_blocked':rejected,
                'research_fixture_only':True,'qc_recommendation':False,'owner_artistic_approval':False,
                'production_sidecar_accessed':False}


if __name__=='__main__':print(json.dumps(validate_all(),ensure_ascii=False,indent=2))
