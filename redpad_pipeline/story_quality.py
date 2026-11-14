"""Story-only extension of Engine contracts and existing intelligence/review services.
No model loading, download, resource allocation or second story/task database.
"""
import copy,json,os,shutil,subprocess
from pathlib import Path
from .agents import AgentError,encode,nonempty
from .filmmaking_knowledge import digest
from .intelligence import targeted_revision,validate_facts,review_packet

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/'assets/filmmaking/story_benchmark.json'

def spec():
    data=json.loads(SPEC.read_text())
    from .shared_model_services import profile,catalog
    p=profile('qwen35_27')
    if data['schema_version']!=1 or data['benchmark_id']!='intelligence.story.v1' or (p['repo'],p['revision'],p['adapter'])!=(data['model_repo'],data['model_revision'],data['adapter']) or catalog()['agents']['story']['primary_candidate']!='qwen35_27':raise AgentError('Pinned Story candidate or benchmark changed.')
    from .professional_readiness import suite
    if suite()['agents']['story']['case_id']!=data['professional_case_id']:raise AgentError('Story professional case drift.')
    if len(data['rubric'])!=15 or len({r['id'] for r in data['rubric']})!=15:raise AgentError('Fifteen distinct creative criteria required.')
    return data

def output_contract():return json.loads(SPEC.with_name('story_benchmark.schema.json').read_text())

REFLECTION={'treatment','ending_consequence','filmability','self_critique'}

def section_contract(section):
    full=output_contract();props=full['properties']
    if section in ('foundation','reflection'):
        keys=REFLECTION if section=='reflection' else set(props)-REFLECTION-{'beats'}
        return {'type':'object','additionalProperties':False,'required':sorted(keys),'properties':{k:props[k] for k in sorted(keys)}}
    if section in ('act_1','act_2','act_3'):
        beat=copy.deepcopy(props['beats']['items']);beat['properties']['act']={'const':int(section[-1])}
        return {'type':'array','minItems':4,'maxItems':6,'items':beat}
    raise AgentError('Unknown bounded Story section.')

def instructions():
    return '\n'.join(spec()['instructions'])+'\nDeliverables use the supplied versioned JSON schema. Do not emit a model self-score or claim a human accepted the story.'

def request(artifact=None,*,sources=None,research=None,locks=None,base=None,targets=None):
    from .professional_readiness import suite
    return {'story_benchmark_v1':True,'benchmark_id':spec()['benchmark_id'],'brief':suite()['shared_original_brief'],
            'artifact':artifact,'sources':sources or {},'research':research or [],'locks':locks or [],'base':base,'targets':targets or []}

def canary_request():
    """Small native worker request specification, not a dispatched job."""
    data={'system':'Return a JSON object only with cause, choice, consequence, knowledge. Each value is a short original Bengali sentence. No approval or quality score.',
          'prompt':'মানব-প্রণীত canary brief: নীরা এখনও টিকিটের কথা জানে না। হাসান টিকিট বাক্সে রেখেছেন। একটি ছোট বিশ্বাসযোগ্য সিদ্ধান্ত ও তার ফল লিখুন; আগে না জেনে নীরা টিকিটের প্রতিক্রিয়া দেখাবে না।',
          'max_new_tokens':384,'seed':117,'temperature':0.2,'context_tokens':4096,'thinking':False}
    from .shared_model_services import validate_request,profile
    validate_request(profile('qwen35_27'),data)
    return data

def pointer(value,path):
    if not isinstance(path,list):raise AgentError('Explicit source/output path list required.')
    try:
        for part in path:
            if type(part) not in (str,int):raise KeyError()
            value=value[part]
    except (KeyError,IndexError,TypeError):raise AgentError('Locked path missing.') from None
    return value

def intake(role,data,sources,prior=None):
    expected=set(request())
    if role!='story' or set(data)!=expected or data['story_benchmark_v1'] is not True or data['benchmark_id']!=spec()['benchmark_id']:raise AgentError('Exact Story-only benchmark envelope required.')
    from .professional_readiness import suite
    if data['brief']!=suite()['shared_original_brief']:raise AgentError('Use the existing original professional brief unchanged.')
    if data['sources']!={k:v.get('artifact') for k,v in sources.items()}:raise AgentError('Story context must bind exact approved source artifacts.')
    validate_facts(data['research'],data['sources'])
    if not isinstance(data['locks'],list):raise AgentError('Source-bound owner locks required.')
    for lock in data['locks']:
        if not isinstance(lock,dict) or set(lock)!={'source_task','source_path','target_path'} or lock['source_task'] not in data['sources']:raise AgentError('Lock must cite an approved dependency.')
        pointer(data['sources'][lock['source_task']],lock['source_path'])
    if prior is not None and data['base']!=prior:raise AgentError('Story revision base is not the immutable previous artifact.')
    if data['base'] is not None and prior is None:raise AgentError('Revision requires this task’s actual previous artifact.')
    if not isinstance(data['targets'],list) or len(set(data['targets']))!=len(data['targets']):raise AgentError('Distinct revision beat targets required.')
    if prior is None and data['targets']:raise AgentError('Targets require a prior story.')

def validate(artifact):
    from jsonschema import Draft202012Validator
    errors=list(Draft202012Validator(output_contract()).iter_errors(artifact))
    if errors:raise AgentError('Story output contract: '+errors[0].message)
    chars={c['id'] for c in artifact['characters']}
    if len(chars)!=len(artifact['characters']) or set(artifact['initial_knowledge'])!=chars:raise AgentError('Distinct character IDs and complete initial knowledge required.')
    beats=artifact['beats'];ids=[b['id'] for b in beats]
    if len(set(ids))!=len(ids) or sorted({b['act'] for b in beats})!=[1,2,3] or [b['act'] for b in beats]!=sorted(b['act'] for b in beats):raise AgentError('Stable beat IDs and ordered three-act progression required.')
    seen=set();plants={};paid=set();known={k:set(v) for k,v in artifact['initial_knowledge'].items()};last=None;findings=[]
    choices=set();subtle=0;humor=0
    def issue(beat,code,note):findings.append({'target':beat,'code':code,'severity':'warning','confidence':None,'evidence_kind':'deterministic_authored_structure','explanation':note,'responsible_agent':'story','retest':'Revalidate affected beats and obtain independent creative review.','grants_revision_authority':False})
    for n,b in enumerate(beats):
        if b['actor'] not in chars or (b['cause']!='brief' if n==0 else b['cause'] not in seen):raise AgentError('Each beat needs a known actor and earlier causal reference.')
        if last is not None and b['before']!=last:raise AgentError('Beat state contradicts its predecessor.')
        if set(b['before'])!=set(b['after']) or b['before']==b['after']:raise AgentError('Every beat must change tracked state without silently dropping facts.')
        if set(b['requires'])-chars or set(b['learns'])-chars:raise AgentError('Unknown character in knowledge transition.')
        for char,facts in b['requires'].items():
            if not set(facts)<=known[char]:raise AgentError('Secret knowledge used before a disclosure event.')
        for payoff in b['payoffs']:
            if payoff not in plants or payoff in paid:raise AgentError('Payoff lacks an earlier unresolved plant.')
            paid.add(payoff)
        for plant in b['plants']:
            if plant in plants:raise AgentError('Setup ID reused.')
            plants[plant]=b['id']
        if not set(b['emotion_setups'])<=seen:raise AgentError('Emotional payoff must reference earlier investment.')
        if b['subtle_emotion']:
            subtle+=1
            if not b['emotion_setups']:issue(b['id'],'unprepared_emotion','Claimed subtle emotion has no earlier setup reference; emotional authenticity is unverified.')
        if b['humor']:
            humor+=1
            if not b['humor_motivation']:issue(b['id'],'unsupported_humor','Humor lacks a character/situation motivation; an expert must assess whether it is organic.')
        if b['choice'] in choices:issue(b['id'],'repeated_choice','Repeated choice text; examine whether scene purpose progresses.')
        choices.add(b['choice'])
        for char,facts in b['learns'].items():known[char].update(facts)
        seen.add(b['id']);last=b['after']
    if subtle<2:raise AgentError('At least two explicitly identified subtle emotional moments required.')
    if humor<1:raise AgentError('At least one motivated humor opportunity required.')
    if not paid:raise AgentError('At least one earned reveal/setup payoff required.')
    for setup in set(plants)-paid:issue(plants[setup],'unresolved_setup','Setup remains unresolved; distinguish deliberate uncertainty from a broken promise in human review.')
    if any(c['beat'] not in seen for c in artifact['self_critique']):raise AgentError('Self-critique must cite actual beat IDs.')
    return {'technical_compliance':True,'findings':findings,'known_after':{k:sorted(v) for k,v in known.items()},
            'setup_payoff_map':{'plants':plants,'paid':sorted(paid)},'semantic_causality_verified':False,'creative_quality':'not_automatically_scored','human_review':'pending','owner_acceptance':'pending'}

def prepare(role,data,sources,prior=None):
    intake(role,data,sources,prior);artifact=copy.deepcopy(data['artifact']);checks=validate(artifact)
    for lock in data['locks']:
        if pointer(artifact,lock['target_path'])!=pointer(data['sources'][lock['source_task']],lock['source_path']):raise AgentError('Owner/source lock conflict; escalate to owner.')
    comparison=None
    if prior is not None:
        if any(artifact[k]!=prior[k] for k in prior if k!='beats'):raise AgentError('Beat-only revision cannot rewrite untargeted treatment or character metadata; request a separately scoped revision.')
        replacement=[b for b in artifact['beats'] if b['id'] in data['targets']]
        comparison=targeted_revision(prior['beats'],replacement,data['targets'])
        if comparison['records']!=artifact['beats']:raise AgentError('Revision changed untargeted beats or beat order.')
    evidence={'brief':digest(data['brief']),'research_context':digest(data['research']),
              'premise':digest([artifact['logline'],artifact['dramatic_question'],artifact['theme']]),
              'character_motivations':digest(artifact['characters']),'causal_beats':digest(artifact['beats']),
              'emotional_arc':digest([{'beat':b['id'],'emotion':b['emotion'],'setup':b['emotion_setups']} for b in artifact['beats']]),
              'story_treatment':digest(artifact['treatment']),'self_critique':digest(artifact['self_critique'])}
    workflow=[{'stage':stage,'status':'supplied_deliverable_validated' if stage in evidence else 'pending',
               'evidence_sha256':evidence.get(stage)} for stage in spec()['workflow']]
    return {'agent':'story','artifact_type':'story_benchmark','artifact':artifact,'findings':checks['findings'],'story_workflow':workflow,
            'story_quality':checks,'comparison':comparison,'benchmark_id':spec()['benchmark_id'],
            'model_inference':False,'media_generated':False,'human_review_required':True,'creative_quality_verified':False}

def packet(artifact,provenance):
    result=review_packet('story',artifact,provenance=provenance)
    result.update(benchmark_id=spec()['benchmark_id'],rubric=spec()['rubric'],technical_result=validate(artifact),automated_critique='Structural checks only; semantic and artistic findings require beat-specific review.',independent_human_review='pending',owner_acceptance='pending')
    return result

def comparison(before,after):
    a=validate(before);b=validate(after)
    return {'before_sha256':digest(before),'after_sha256':digest(after),'rubric_sha256':digest(spec()['rubric']),
            'before_technical':a,'after_technical':b,'changed_beats':sorted(k for k in {x['id'] for x in before['beats']}|{x['id'] for x in after['beats']} if next((x for x in before['beats'] if x['id']==k),None)!=next((x for x in after['beats'] if x['id']==k),None)),
            'measured_creative_improvement':None,'regressions':'Independent review required','owner_acceptance':False}

def assemble_sections(foundation,acts,reflection):
    """Lossless CPU compilation of five supplied bounded sections, no prose repair.
    This helper does not authenticate inference; only the existing runtime ledger
    can establish provenance, and no real runtime is enabled in this phase.
    """
    from jsonschema import Draft202012Validator
    if not isinstance(acts,list) or len(acts)!=3:raise AgentError('Foundation, three ordered acts and final reflection required.')
    parts=[foundation,*acts,reflection]
    for name,part in zip(spec()['budget']['primary_sections'],parts):
        if list(Draft202012Validator(section_contract(name)).iter_errors(part)):raise AgentError('Invalid bounded Story section: '+name)
    if any(not isinstance(rows,list) or not rows or any(b.get('act')!=n for b in rows) for n,rows in enumerate(acts,1)):raise AgentError('Each bounded section must contain its own act only.')
    artifact=dict(copy.deepcopy(foundation),**copy.deepcopy(reflection),beats=copy.deepcopy([b for rows in acts for b in rows]))
    checks=validate(artifact)
    return {'artifact':artifact,'technical_result':checks,'section_sha256':[digest(p) for p in parts],
            'compilation':'exact authored/supplied section preservation; not new inference','owner_acceptance':False}

def queue_bible_handoff(engine,task,*,seconds=660):
    """Approved Story output -> existing StoryBridge Bible contract, no new prose.
    This preserves the existing path toward Script/Director, never runs them.
    """
    if type(seconds) is not int or not 180<=seconds<=4200:raise AgentError('Bounded handoff duration required.')
    with engine.store.tx() as db:
        t=engine.store._task(db,task);engine.store._current(db,t)
        if t['agent']!='story' or t['state']!='Approved':raise AgentError('Current owner-approved Story source required.')
        out=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,t['revision'])).fetchone()
        body=json.loads(json.loads(out[0])['summary'])
        if body.get('artifact_type')!='story_benchmark':raise AgentError('Exact benchmark artifact required.')
        a=body['artifact'];validate(a)
        row={'id':'story_benchmark_bible','title':'ফিরতি টিকিট','logline':a['logline'],'premise':a['treatment'],
             'conflict':a['conflict_stakes'],'season_arc':a['relationship_dynamics'],'ending_strategy':a['ending_consequence'],
             'feasibility':a['filmability'],'characters':[dict(id=c['id'],name=c['name'],biography=c['biography'],want=c['want'],need=c['need'],internal_conflict=c['internal_conflict'],relationship_arc=c['emotional_change']) for c in a['characters']],
             'rules':['Preserve the exact approved source state and knowledge; this transformation grants no approval.'],
             'initial_state':a['beats'][0]['before']}
    data={'story_stage_v1':True,'stage':'bible','episode':1,'seconds':seconds,'brief':request()['brief'],'records':[row],
          'sources':{task:{'$from':task,'path':['artifact']}},'targets':[]}
    return engine.enqueue('story',data,[task],mode='software',idempotency_key='story-bible:'+digest([task,t['revision'],data]))

def preflight(store=None):
    """Read-only inventory. Never imports torch or activates/allocates a GPU."""
    gpus=[];error=None;tool=shutil.which('nvidia-smi')
    if tool:
        try:
            out=subprocess.run([tool,'--query-gpu=uuid,name,memory.total,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=10,check=True)
            for line in out.stdout.splitlines():
                uuid,name,total,free=[s.strip() for s in line.split(',')];gpus.append({'uuid':uuid,'name':name,'total_mib':int(total),'free_mib':int(free)})
        except (OSError,ValueError,subprocess.SubprocessError) as exc:error=type(exc).__name__
    cache_roots=[ROOT/'phase3_models',Path('/workspace/.cache/huggingface'),Path('/workspace/shared/downloads')]
    caches=[{'path':str(p),'exists':p.is_dir(),'qwen35_27_snapshot_present':(p/'hub/models--Qwen--Qwen3.5-27B/snapshots'/spec()['model_revision']).is_dir()} for p in cache_roots]
    approved=None if store is None else False
    if store is not None:
        with store.tx() as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='shared_model_installs'").fetchone():approved=db.execute("SELECT 1 FROM shared_model_installs WHERE profile='qwen35_27'").fetchone() is not None
    limit=Path('/sys/fs/cgroup/memory.max');memory=limit.read_text().strip() if limit.exists() else 'unknown'
    current=Path('/sys/fs/cgroup/memory.current')
    current_bytes=int(current.read_text()) if current.exists() else None
    from importlib.metadata import version,PackageNotFoundError
    dependencies={}
    for package in ('torch','transformers','bitsandbytes','accelerate','safetensors'):
        try:dependencies[package]=version(package)
        except PackageNotFoundError:dependencies[package]=None
    blockers=[]
    if not gpus:blockers.append('No exposed queryable NVIDIA GPU; no GPU resource was activated.')
    if memory.isdigit() and int(memory)<32*2**30:blockers.append('Container RAM below existing unmeasured 32 GiB planning gate.')
    if not approved:blockers.append('No approved exact installed bundle/rights receipt demonstrated in the supplied isolated agent store.')
    blockers+=['Exact owner approval of resource, selected model and bounded scope is required before inference.','Kernel network isolation and adapter/dependency/precision compatibility must be verified before launch.','Primary story uses five bounded sections: foundation, three acts, final reflection. Exact tokenizer feasibility for each 1536-output/4096-context request is unmeasured. Proposed seven-call ceiling is not owner authorization; stop on truncation.']
    return {'schema_version':1,'model':spec()['model_repo'],'revision':spec()['model_revision'],'gpus':gpus,'gpu_query_error':error,'cgroup_memory_limit_bytes':int(memory) if memory.isdigit() else memory,'cgroup_memory_current_bytes':current_bytes,'dependency_metadata_only':dependencies,'cache_inventory':caches,'approved_install_receipt_present':approved,'approval_scope':'Supplied isolated agent store only' if store is not None else 'No agent store supplied; install/rights receipt not inspected','cache_scope':'Known workspace paths only; no global/private-account search or weight reads. Presence is not manifest/license approval.','session_quota':'not exposed','network_namespace':os.readlink('/proc/self/ns/net'),'kernel_isolation_verified':False,'adapter_compatibility_verified':False,'gpu_allocated':False,'inference_authorized':False,'blockers':blockers}

def require_runtime(store,run):
    # This phase deliberately supplies preparation, not an unverified GPU launcher.
    # The older general shared worker has no Story-specific scoped owner receipt
    # or verified kernel-isolation integration. It must not be used as a bypass.
    from .screenwriter import LocalUnavailable
    raise LocalUnavailable('Story real benchmark blocked: exact GPU/scope owner authorization and kernel-isolated selected-model worker binding are not verified. Resume from the Story preflight checkpoint; no Ollama, CPU, hosted or alternate-model fallback.')

def main():
    import argparse
    p=argparse.ArgumentParser(description='CPU-safe Story checkpoint preparation; never launches inference.')
    p.add_argument('--output',required=True);args=p.parse_args();folder=Path(args.output)
    if any(p.is_symlink() for p in (folder,*folder.parents)):raise AgentError('No symlink output folder or parent.')
    folder.mkdir(parents=True,exist_ok=True)
    items=[('preflight.json',preflight()),('request.json',request()),('output_contract.json',output_contract()),('benchmark.json',spec()),('canary_request.json',canary_request()),('section_contracts.json',{n:section_contract(n) for n in spec()['budget']['primary_sections']})]
    if any((folder/name).exists() for name,_ in items):raise AgentError('Resume folder already contains evidence; choose a fresh folder instead of overwriting.')
    for name,value in items:
        target=folder/name
        with target.open('x') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print('Story checkpoint prepared; inference disabled.')

if __name__=='__main__':main()
