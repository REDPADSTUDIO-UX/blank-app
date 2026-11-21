"""Identical, original Bengali tasks and explicit human selection gates.
No model downloads and no automatic winner. Stored legacy runs are not relabeled
as equivalent-task comparisons. Critic ground truth is withheld from prompts.
"""
import hashlib
import json
from pathlib import Path
from .agents import AgentError, encode
from .staged_writing import StagedDraft, obj, text_schema, enum, compact_scene_schema, digest, blind_package
from .model_routing import ModelRoutes, inventory

DIMENSIONS=['originality_logic','bangladeshi_dialogue','emotion_psychology','humor_wit',
 'romance_tension','visual_first','hooks_cliffhangers','continuity','revision_following','criticism_accuracy']
CASES_BY_ROLE={'story':['story'],'script':['romance','humor','revision'],'director':['criticism'],'qc':['qc']}
OPTIONS={'num_ctx':4096,'num_predict':1024,'temperature':.35,'seed':42,'timeout_seconds':180,'stream':True}
SOURCE={'heading':'INT. বাসা — সকাল','lines':{
 'L1':'তানিয়া নিজের চাকরির সাক্ষাৎকারে যাবে; রাশেদ নিজের অফিসে যাবে।',
 'L2':'টেবিলে তাদের একমাত্র ছাতা। তানিয়া সেটি ব্যাগে রাখে।',
 'L3':'রাশেদ একই ছাতাটি টেবিল থেকে তুলে খুলে ফেলে; কেউ ফেরত দেয়নি।',
 'L4':'দুজনই বেরোনোর আগে বাসভাড়া গুনে রাখে।'}}


def cases():
    story=obj({k:text_schema(100) for k in ['want','costly_choice','consequence','emotional_change','opening_image','earned_cliffhanger']})
    criticism=obj({'findings':{'type':'array','maxItems':3,'items':obj({'line_id':enum(SOURCE['lines']),
             'category':enum(['continuity','logic','dialogue','visual','motivation']),
             'problem':text_schema(100),'suggestion':text_schema(100)})}})
    return [
      {'id':'story','role':'story','data':'কুষ্টিয়ার এক দর্জি মায়ের চিকিৎসার টাকার জন্য মেয়ের কলেজের শেষ কিস্তি খরচ করে ফেলে। মেয়ে জানে না; আজ ভর্তি নিশ্চিত করার শেষ দিন। মা নিজে সিদ্ধান্ত নিতে সক্ষম। কোনো আকস্মিক ধনী উদ্ধারকারী নয়।',
       'task':'মৌলিক সংক্ষিপ্ত পর্বের কাঠামো দিন: কার চাওয়া, তার দামি সিদ্ধান্ত, তার ফল, আচরণে আবেগের পরিবর্তন, প্রথম দৃশ্যের হুক ও সিদ্ধান্ত থেকে জন্মানো cliffhanger। প্রতি field-এ একটি ছোট বাংলা বাক্য।','schema':story},
      {'id':'romance','role':'script','data':'ঢাকার বাসায় নীলা ও সাব্বির, বিবাহের কথা চলছে। নীলা নিজের বদলির চাকরিটা নিতে চায়, সাব্বির শহর ছাড়তে ভয় পায়। কাউকে খলনায়ক বানাবেন না। বিদ্যুৎ নেই, দুজন মিলে পাখা ঠিক করছে।',
       'task':'একটি visual-first ক্ষুদ্র দৃশ্য। opening_action, সাব্বিরের first_reply, নীলার second_reply, closing_action ও INT. heading দিন। কথাগুলো সরাসরি speech, নাম বা বলে যোগ করবেন না। প্রতি কথায় ৬–১০টি শব্দ। রোমান্টিক টান, না-বলা ভয় ও একটি ছোট যত্নের কাজ।','schema':compact_scene_schema()},
      {'id':'humor','role':'script','data':'চট্টগ্রামের বাসায় মা রেহানা ছেলের অফিসের ব্যাগে অতিরিক্ত খাবার দেন; ছেলে ইমরান ওজন কমানোর চেষ্টা করছে। দুজনের স্নেহ আছে, কাউকে অপমান নয়।',
       'task':'একটি ছোট visual-first দৃশ্য। opening_action, ইমরানের first_reply, রেহানার responsive second_reply, closing_action, INT. heading। শুধু সরাসরি speech; নাম বা বলে নয়। অভ্যাসের সংঘাত থেকে মৃদু witty exchange, বক্তৃতা নয়। প্রতি কথায় ৬–১০টি শব্দ।','schema':compact_scene_schema()},
      {'id':'revision','role':'script','data':{'source':{'s1':'রুমি খামের ভেতর কলেজের বিল রাখে।','s2':'বাবা: আমি তোমার জন্য সব করেছি। রুমি: আমি সব বুঝি।'},'locked':['s1'],'target':'s2'},
       'task':'শুধু s2 বদলান। আগে ছোট দৃশ্যমান কাজ, তারপর বাবা ও রুমির দুইটি সংক্ষিপ্ত সরাসরি কথা। বিল/চরিত্র/সম্পর্ক বদলাবেন না। অভিযোগের বদলে না-বলা সংকোচ দেখান। s1 ফেরত দেবেন না।',
       'schema':obj({'scene_id':enum(['s2']),'action':text_schema(100),'father':text_schema(80),'rumi':text_schema(80)})},
      {'id':'criticism','role':'director','data':SOURCE,'task':'এই নির্দিষ্ট উৎসে বাস্তব ভুল থাকলে line_id ও category দিয়ে সংক্ষিপ্ত সমালোচনা করুন। উদ্ধৃতি বানাবেন না। নেই এমন আবেগ/ঘটনা/ভুল কল্পনা করবেন না। নিশ্চিত না হলে findings খালি রাখুন।','schema':criticism},
      {'id':'qc','role':'qc','data':SOURCE,'task':'একটি independent QC observation লিখুন। শুধু প্রমাণিত ভুল, বিদ্যমান line_id ও category। আংশিক বা সুন্দর লেখাকে অনুমোদন দেবেন না; নির্ভুল দৃশ্যপটকে খারাপ বলবেন না। উদ্ধৃতি লিখবেন না।','schema':criticism}]


def suite_hash():return digest({'cases':cases(),'options':OPTIONS,'version':1})


def run_case(store,folder,name,case_id,*,think=None):
    """One explicit call, no fallback: a candidate must answer as itself."""
    model=next((m for m in ModelRoutes(store).models() if m['name']==name and m['approved']),None)
    if not model or inventory().get(name)!=model['digest']:raise AgentError('Candidate is not explicitly approved and installed with this digest.')
    case=next((c for c in cases() if c['id']==case_id),None)
    if case is None:raise AgentError('Unknown benchmark case.')
    if think is not None and type(think) is not bool:raise AgentError('Invalid thinking benchmark control.')
    identity=[name,model['digest'],suite_hash()]
    if think is not None:identity.append({'think':think})
    candidate=digest(identity)[:20]
    directory=Path(folder)/candidate
    lab=StagedDraft(directory)
    manifest={'model':name,'digest':model['digest'],'suite_sha256':suite_hash(),'options':OPTIONS,'candidate':candidate}
    if think is not None:manifest['think']=think
    p=directory/'manifest.json'
    if p.exists() and json.loads(p.read_text())!=manifest:raise AgentError('Benchmark manifest mismatch.')
    p.write_text(json.dumps(manifest,indent=2))
    result=lab.run(case_id,case['role'],case['data'],case['task'],case['schema'],model=name,tokens=1024,think=think)
    try:unchanged=inventory().get(name)==model['digest']
    except (OSError,ValueError):unchanged=False
    if not unchanged:
        result['status']='failed';result['error']='Candidate digest changed or post-inference identity unavailable.'
    result.setdefault('evidence',{})['model_digest']=model['digest']
    (directory/(case_id+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def critic_findings(result):
    return {(n['line_id'],'prop_continuity' if n['line_id']=='L3' and n['category'] in ('logic','continuity') else n['category']) for n in result['findings']}


def report(folder,store=None):
    folder=Path(folder);manifest=json.loads((folder/'manifest.json').read_text());records={};accuracy={}
    for case in cases():
        p=folder/(case['id']+'.json')
        if p.exists():
            r=json.loads(p.read_text());records[case['id']]=r
            if case['id'] in ('criticism','qc') and r['status']=='validated_stage':
                found=critic_findings(r['result']);expected={('L3','prop_continuity')}
                tp=len(found&expected);fp=len(found-expected);fn=len(expected-found)
                accuracy[case['id']]={'true_positive':tp,'false_positive':fp,'false_negative':fn,
                    'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn),
                    'scope':'one deterministic seeded prop-continuity defect, not general editorial intelligence'}
    accepted={};selected=[]
    if store is not None:
        routes=ModelRoutes(store)
        with store.tx() as db:
            for r in db.execute('SELECT role,human FROM model_acceptances WHERE name=? AND digest=?',(manifest['model'],manifest['digest'])):
                accepted[r['role']]=json.loads(r['human'])
        for role in CASES_BY_ROLE:
            policy=routes.policy(role)
            if policy and policy['mode']=='production' and any(m['name']==manifest['model'] and m['digest']==manifest['digest'] for m in policy['models']):selected.append(role)
    return dict(manifest,records=records,criticism_accuracy=accuracy,human_review_status='owner_attested_independent_review_recorded' if accepted else 'not_recorded',human_reviews=accepted,selected_roles=selected)


def check_selection(role,name,model_digest,benchmark,human,confirmed):
    if role not in CASES_BY_ROLE:raise AgentError('Role-specific acceptance currently covers Story, Script, Director and QC.')
    if confirmed is not True or human.get('independent') is not True or human.get('accepted') is not True or not str(human.get('reviewer','')).strip():raise AgentError('Independent human acceptance must be explicitly attested by the owner.')
    if benchmark.get('model')!=name or benchmark.get('digest')!=model_digest or benchmark.get('suite_sha256')!=suite_hash():raise AgentError('Benchmark identity, digest or suite differs.')
    records=benchmark.get('records',{});quoted=''
    from jsonschema import Draft202012Validator
    specs={c['id']:c for c in cases()}
    for key in CASES_BY_ROLE[role]:
        r=records.get(key,{})
        raw=r.get('raw','');e=r.get('evidence',{})
        if r.get('provenance')!='local_inference' or r.get('status')!='validated_stage' or not e.get('inference_completed') or e.get('model')!=name or e.get('model_digest')!=model_digest or e.get('raw_sha256')!=hashlib.sha256(raw.encode()).hexdigest():raise AgentError('Missing complete, integrity-checked actual inference for this role.')
        if r.get('request_sha256')!=digest(r.get('request')):raise AgentError('Benchmark request evidence modified.')
        req=r['request'];case=specs[key]
        if req.get('think')!=benchmark.get('think') or e.get('thinking_control',{}).get('requested')!=benchmark.get('think'):raise AgentError('Thinking mode evidence differs from benchmark manifest.')
        if req.get('data')!=case['data'] or req.get('task')!=case['task'] or req.get('schema')!=case['schema'] or req.get('model')!=name or req.get('tokens')!=1024:raise AgentError('Equivalent benchmark task not established.')
        from .staged_writing import SYSTEM
        if req.get('system')!=SYSTEM or e.get('options')!={k:OPTIONS[k] for k in ('num_ctx','num_predict','temperature','seed')}:raise AgentError('Benchmark system or sampling settings differ.')
        if json.loads(raw)!=r.get('result') or not Draft202012Validator(case['schema']).is_valid(r['result']):raise AgentError('Benchmark reply does not validate.')
        quoted+=encode(r['result'])
        if role in ('director','qc'):
            found=critic_findings(r['result'])
            if found!={('L3','prop_continuity')}:raise AgentError('Seeded criticism precision/recall gate failed.')
    ratings=human.get('ratings',{})
    if set(ratings)!=set(DIMENSIONS):raise AgentError('All ten creative dimensions require actual human findings.')
    for rating in ratings.values():
        if type(rating.get('score')) not in (int,float) or not 0<=rating['score']<=10 or not rating.get('evidence') or rating['evidence'] not in quoted or not str(rating.get('finding','')).strip():raise AgentError('Every human rating needs a bounded score, exact evidence and finding.')
    # No score-based auto-winner; owner's explicit acceptance remains necessary.


def blind_comparison(folders):
    candidates={};manifests={}
    for folder in folders:
        b=report(folder)
        if b['suite_sha256']!=suite_hash():raise AgentError('Cannot mix different benchmark suites.')
        for key,r in b['records'].items():
            label=b['candidate']+':'+key;candidates[label]={'case':key,'output':r['result'],'status':r['status']};manifests[label]={'model':b['model'],'digest':b['digest'],'raw_sha256':hashlib.sha256(r['raw'].encode()).hexdigest()}
    package,mapping=blind_package(candidates)
    package['tasks']=[{k:c[k] for k in ('id','data','task')} for c in cases()]
    package['limitations']='Metadata-blind comparison only; model self-identification inside raw creative prose may reveal identity. Seeded criticism accuracy is a narrow mechanical check, not human editorial approval.'
    return package,{code:manifests[label] for code,label in mapping.items()}
