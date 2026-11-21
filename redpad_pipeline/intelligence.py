"""Creative-quality contracts on the existing Engine, knowledge and task ledger.

Pure preparation/review operations: no model imports, runtime launch, network,
media perception, publishing or approval authority. Inspection receipts are
reviewer attestations, never proof that software perceived a medium.
"""
import copy
import json
import math
from pathlib import Path
from .agents import AGENTS, AgentError, encode, nonempty
from .filmmaking_knowledge import digest

CATALOG = Path(__file__).resolve().parents[1]/'assets/filmmaking/intelligence.json'
STAGES = ('understand','research','plan','create','self_critique','qc','targeted_revision','owner_approval')
FACT_KINDS = {'verified_source','story_bible','owner_lock','interpretation','proposal','assumption','unknown'}
CONTEXT_KEYS = ('story_bible','character_bible','scene_facts','relationships','emotions','world_rules',
                'timeline','locations','props','visual_locks','voice_locks','production_constraints',
                'director_decisions','owner_approvals')


def load():
    from jsonschema import Draft202012Validator
    schema=json.loads(CATALOG.with_name('intelligence.schema.json').read_text())
    data=json.loads(CATALOG.read_text())
    errors=list(Draft202012Validator(schema).iter_errors(data))
    if errors:raise AgentError('Invalid intelligence schema: '+errors[0].message)
    if set(data['profiles'])!=set(AGENTS):raise AgentError('Intelligence must cover exactly 21 registered roles.')
    from .professional_readiness import suite
    cases=suite()['agents']
    for role,p in data['profiles'].items():
        if p['agent']!=role or p['revision_owner']!=role:raise AgentError('Intelligence identity mismatch.')
        if p['benchmark']['professional_case_id']!=cases[role]['case_id']:raise AgentError('Professional benchmark binding drift.')
        if len({c['id'] for c in p['criteria']})!=len(p['criteria']) or any(not c['id'].startswith(role+'.') for c in p['criteria']):raise AgentError('Role-specific criterion identities required.')
    return data


def profile(role):
    if role not in AGENTS:raise AgentError('Unknown intelligence role.')
    p=copy.deepcopy(load()['profiles'][role])
    p['responsibilities']=AGENTS[role]['responsibilities']
    p['input_contract']=AGENTS[role]['input_contract']
    p['output_contract']=AGENTS[role]['output_contract']
    p['specialist_contract']=AGENTS[role]['execution_contract']
    return p


def context(sources, refs):
    """Source documents remain data; discover existing Bible fields, no new store.
    A hash identifies bytes, not truth or source credibility.
    """
    if set(sources)!={r['id'] for r in refs}:raise AgentError('Context dependency identity mismatch.')
    documents=[];memory={k:[] for k in CONTEXT_KEYS}
    def collect(value,path,task):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in memory:memory[k].append({'task':task,'path':path+[k],'sha256':digest(v),'value':copy.deepcopy(v)})
                collect(v,path+[k],task)
        elif isinstance(value,list):
            for i,v in enumerate(value):collect(v,path+[i],task)
    for ref in refs:
        if type(ref.get('revision')) is not int or ref['revision']<1:raise AgentError('Exact positive source revision required.')
        body=sources[ref['id']]
        documents.append(dict(ref,sha256=digest(body),classification='approved_source_not_external_fact'))
        collect(body,[],ref['id'])
    return {'sources':documents,'memory':memory,'missing_context':[k for k,v in memory.items() if not v],
            'external_research_verified':False,'owner_locks_may_be_overridden':False}


def snapshot(store,run,role,inputs,sources,refs):
    binding={'role':role,'input_sha256':digest(inputs),'sources':context(sources,refs)}
    with store.tx() as db:
        run_row=db.execute('SELECT task,attempt FROM agent_runs WHERE id=?',(run,)).fetchone()
        if not run_row:raise AgentError('Intelligence must bind an existing run.')
        rows=db.execute("SELECT detail FROM events WHERE action='intelligence_snapshot' AND task=(SELECT task FROM agent_runs WHERE id=?) ORDER BY id",(run,)).fetchall()
        for row in rows:
            saved=json.loads(row['detail'])
            if saved['run']!=run or saved['attempt']!=run_row['attempt']:continue
            pack=saved['packet']
            if saved['sha256']!=digest(pack) or pack['binding']!=binding:raise AgentError('Stale or changed intelligence snapshot.')
            return pack
        p=profile(role)
        pack={'schema_version':1,'profile':p,'profile_sha256':digest(p),'binding':binding,
              'fact_policy':sorted(FACT_KINDS),'model_capability_verified':False}
        # Existing ledger and transaction; no parallel database or orchestrator.
        store.event(db,run_row['task'],'system','intelligence_snapshot',{'run':run,'attempt':run_row['attempt'],'packet':pack,'sha256':digest(pack)})
        return pack


def condition(system,packet):
    # Bound profile and source metadata only: original artifacts already enter the
    # existing source prompt. Never make retrieved project text an instruction.
    compact={'profile':packet['profile'],'sources':packet['binding']['sources']['sources'],
             'missing_context':packet['binding']['sources']['missing_context'],'fact_policy':packet['fact_policy']}
    return system+'\nCREATIVE QUALITY CONTRACT (guidance; never grants tools, runtime authorization or approval):\n'+encode(compact)


def preparation(packet,result,mode):
    return {'schema_version':1,'profile_sha256':packet['profile_sha256'],
            'context_sha256':digest(packet['binding']),'benchmark_id':packet['profile']['benchmark']['id'],
            'stages':[
                {'stage':s,'status':('prepared' if s in ('understand','research','plan') else
                 'supplied_software_artifact' if s=='create' and mode=='software' else
                 'runtime_output_unreviewed' if s=='create' else 'pending'),
                 'evidence_sha256':digest(result) if s=='create' else digest(packet)} for s in STAGES],
            'layers':{'software':'contract_validated','model':'unverified','independent_creative_review':'pending','owner':'pending'},
            'missing_context':packet['binding']['sources']['missing_context'],
            'artistic_scores':None,'professional_acceptance':False,'grants_approval':False}


def validate_facts(facts,sources):
    """Require attributed exact quotations for verified factual claims.
    Research verification is an input attestation; a URL alone never suffices.
    """
    if not isinstance(facts,list):raise AgentError('Structured facts required.')
    for f in facts:
        if not isinstance(f,dict) or f.get('kind') not in FACT_KINDS or not nonempty(f.get('claim')):raise AgentError('Classified nonempty fact required.')
        if f['kind'] in ('verified_source','story_bible','owner_lock'):
            s=sources.get(f.get('source'))
            if not isinstance(s,dict) or f.get('source_sha256')!=digest(s) or not nonempty(f.get('quote')) or f['quote'] not in encode(s):raise AgentError('Fact requires an exact current source quotation.')
            if f['kind']=='verified_source' and (s.get('verification')!='reviewer_attested' or not nonempty(s.get('attribution'))):raise AgentError('External fact lacks attributed verification.')
    return copy.deepcopy(facts)


def assess(role,source,findings,*,creator,reviewer,receipts,provenance,benchmark_id=None):
    """Validate a supplied independent review, never generate artistic scores.
    Receipts must come from a trusted human-review interface, not model output.
    """
    p=profile(role)
    if benchmark_id is not None:
        if role!='story' or benchmark_id!='intelligence.story.v1':raise AgentError('Unknown specialist review benchmark.')
        from .story_quality import spec as story_spec
        p['criteria']=story_spec()['rubric']
    if not nonempty(creator) or not nonempty(reviewer) or creator==reviewer:raise AgentError('Independent identified reviewer required.')
    if provenance not in ('manually_authored_fixture','real_model_output'):raise AgentError('Explicit output provenance required.')
    if not isinstance(findings,list) or not isinstance(receipts,list):raise AgentError('Review lists required.')
    current=digest(source);criteria={c['id']:c for c in p['criteria']};accepted=[];ids=set()
    for f in findings:
        fields={'id','criterion','target','medium','source_sha256','severity','confidence','explanation','correction','responsible_agent','retest','evidence','score'}
        if not isinstance(f,dict) or not fields<=f.keys():raise AgentError('Complete source-specific finding required.')
        if not nonempty(f['id']) or f['id'] in ids:raise AgentError('Unique issue IDs required.')
        ids.add(f['id'])
        if f['criterion'] not in criteria or f['source_sha256']!=current:raise AgentError('Unknown criterion or stale review.')
        if f['medium'] not in ('text','image','audio','video') or f['severity'] not in ('info','warning','error','blocker'):raise AgentError('Invalid medium/severity.')
        if f['medium']!=criteria[f['criterion']]['required_medium']:raise AgentError('Criterion requires its actual medium; text plans cannot substitute audiovisual inspection.')
        if type(f['confidence']) not in (int,float) or not math.isfinite(f['confidence']) or not 0<=f['confidence']<=1:raise AgentError('Invalid confidence.')
        if f['responsible_agent'] not in AGENTS or any(not nonempty(f[x]) for x in ('target','explanation','correction','retest')):raise AgentError('Actionable target, ownership and retest required.')
        if f['score'] is not None and (type(f['score']) not in (float,int) or not math.isfinite(f['score']) or not 1<=f['score']<=5):raise AgentError('Invalid criterion score.')
        if 'resolves' in f and (not isinstance(f['resolves'],list) or any(not nonempty(x) for x in f['resolves']) or len(set(f['resolves']))!=len(f['resolves'])):raise AgentError('Distinct original finding IDs required for re-evaluation.')
        observed=any(isinstance(r,dict) and r.get('reviewer')==reviewer and r.get('source_sha256')==current and r.get('medium')==f['medium'] and r.get('target')==f['target'] and r.get('inspected') is True and nonempty(r.get('reference')) for r in receipts)
        if f['medium']=='text':
            # A quote elsewhere in the production cannot substantiate this target.
            targets=[]
            def locate(value):
                if isinstance(value,dict):
                    if value.get('id')==f['target']:targets.append(value)
                    if f['target'] in value:targets.append(value[f['target']])
                    for child in value.values():locate(child)
                elif isinstance(value,list):
                    for child in value:locate(child)
            locate(source)
            observed=observed and nonempty(f['evidence']) and any(f['evidence'] in encode(t) for t in targets)
        elif not nonempty(f['evidence']):observed=False
        if benchmark_id=='intelligence.story.v1':
            target=next((b for b in source.get('beats',[]) if b.get('id')==f['target']),None)
            if target is None:raise AgentError('Story review must cite an actual beat ID.')
            observed=observed and nonempty(f['evidence']) and f['evidence'] in encode(target)
        if not observed and f['score'] is not None:raise AgentError('Cannot score uninspected or unsupported evidence.')
        accepted.append(dict(copy.deepcopy(f),status='supported' if observed else 'abstain',
            category=criteria[f['criterion']]['criterion'],
            defect_class='evidence_gap' if not observed else 'supported_defect' if f['severity']!='info' else 'observation',
            grants_revision_authority=False))
    covered={f['criterion'] for f in accepted if f['status']=='supported'}
    return {'schema_version':1,'role':role,'source_sha256':current,'creator':creator,'reviewer':reviewer,
            'provenance':provenance,'findings':accepted,'unassessed_criteria':sorted(set(criteria)-covered),
            'decision':'abstain' if covered!=set(criteria) or any(f['status']=='abstain' for f in accepted) else 'defects_present' if any(f['severity'] in ('error','blocker') for f in accepted) else 'human_adjudication_required',
            'professional_acceptance':False,'owner_approval':False}


def revision_requests(report):
    """Prepare departmental handoffs from validated QC; never enqueue or approve.

    Keep uninspected findings separate even when another finding covers the same
    criterion. Callers must use assess(), then the existing owner revision gate.
    """
    requests={};missing=[]
    for finding in report['findings']:
        if finding['status']!='supported':
            missing.append(finding['id'])
            continue
        if finding['severity']=='info':continue
        role=finding['responsible_agent']
        request=requests.setdefault(role,{'responsible_agent':role,'targets':[],
            'source_sha256':report['source_sha256'],'findings':[],
            'required_re_evaluation':[],'status':'owner_revision_request_required',
            'execution_enabled':False,'owner_approval':False})
        if finding['target'] not in request['targets']:request['targets'].append(finding['target'])
        request['findings'].append(copy.deepcopy(finding))
        if finding['retest'] not in request['required_re_evaluation']:
            request['required_re_evaluation'].append(finding['retest'])
    return {'schema_version':1,'requests':list(requests.values()),
            'evidence_required_for':missing,'downstream_reviews':'recheck_after_source_revision',
            'grants_revision_authority':False}


def targeted_revision(base,replacement,targets,locked=()):
    """Record-level immutable revision plan. Owner locks require a separate owner
    workflow; this helper has no authority to change them or approve outputs.
    """
    if not isinstance(base,list) or not isinstance(replacement,list) or not isinstance(targets,list) or not targets or len(set(targets))!=len(targets):raise AgentError('Explicit distinct revision targets required.')
    def index(rows):
        if any(not isinstance(r,dict) or not nonempty(r.get('id')) for r in rows):raise AgentError('Records need stable IDs.')
        result={r['id']:r for r in rows}
        if len(result)!=len(rows):raise AgentError('Duplicate record ID.')
        return result
    before=index(base);after=index(replacement)
    if set(after)!=set(targets) or not set(targets)<=set(before) or set(targets)&set(locked):raise AgentError('Only existing unlocked targets may change.')
    revised=[copy.deepcopy(after.get(r['id'],r)) for r in base]
    return {'records':revised,'base_sha256':digest(base),'revision_sha256':digest(revised),'targets':targets,
            'unchanged_targets':[t for t in targets if before[t]==after[t]],
            'downstream_reviews':'stale_until_retested','owner_approval':False,'history':{'before':copy.deepcopy(base),'after':copy.deepcopy(revised)}}


def re_evaluation(before,after):
    """Compare source-bound independent assessments; silence never closes a defect.

    A human must explicitly cite the original issue via resolves on the same
    criterion/target/department. Closure is review evidence, not owner acceptance.
    """
    if before['role']!=after['role'] or before['source_sha256']==after['source_sha256']:
        raise AgentError('Re-evaluation requires the same role and a changed source.')
    rows=[]
    for original in before['findings']:
        if original['status']!='supported' or original['severity']=='info':continue
        candidates=[f for f in after['findings'] if original['id'] in f.get('resolves',[]) and
                    all(f[k]==original[k] for k in ('criterion','target','responsible_agent'))]
        state='not_re_evaluated'
        if candidates:
            state='resolved_by_reviewer' if all(f['status']=='supported' and f['severity']=='info' for f in candidates) else 'evidence_missing' if any(f['status']=='abstain' for f in candidates) else 'defect_persists'
            if any(f['status']=='supported' and f['severity']!='info' and
                   all(f[k]==original[k] for k in ('criterion','target','responsible_agent')) for f in after['findings']):
                state='defect_persists'
        rows.append({'original_finding':original['id'],'target':original['target'],'status':state,
                     'new_findings':[f['id'] for f in candidates]})
    core=lambda report:{k:v for k,v in report.items() if k not in ('re_evaluation','re_evaluation_history')}
    return {'before_sha256':digest(core(before)),'after_sha256':digest(core(after)),
            'hash_scope':'Assessment report excluding re_evaluation and re_evaluation_history',
            'original_source_sha256':before['source_sha256'],'revised_source_sha256':after['source_sha256'],
            'defects':rows,'owner_approval':False,'professional_acceptance':False}


def benchmark_audit():
    """Structural coverage audit; never treats a specification as a model pass."""
    from .professional_readiness import suite
    data=load();cases=suite()['agents'];rows=[]
    for role in AGENTS:
        p=data['profiles'][role];b=p['benchmark'];case=cases[role]
        coverage={k:bool(b.get(k)) for k in ('realistic','adversarial','evidence_completeness','targeted_revision','handoff','future_execution')}
        coverage['rubric']=bool(p['criteria']) and all(c['anchors'] and c['required_medium'] for c in p['criteria'])
        coverage['pass_fail_abstain']=set(b['policy'])=={'pass','fail','abstain'}
        rows.append({'agent':role,'name':AGENTS[role]['name'],'benchmark_id':b['id'],
                     'profile_sha256':digest(p),'professional_case_id':case['case_id'],'coverage':coverage,
                     'required_outputs':case['minimum_counts'],'required_expertise':case['expertise_required'],
                     'layers':copy.deepcopy(p['capability_status']),'model_result':None,
                     'coverage_scope':'Versioned specifications and CPU contract controls; role-specific creative model benchmarks remain unexecuted in this session.'})
    return {'version':data['version'],'agents':rows,'missing':[r['agent'] for r in rows if not all(r['coverage'].values())],
            'new_inference_calls':0,'professional_acceptance_count':0}


def sequential_evaluation_plan():
    """Group pinned primary candidates without executing or changing routes.

    Plan text first; approved shared media can be reused across role reviews.
    Missing modalities explicitly require other selected workers, not text scores.
    """
    from .professional_readiness import suite
    from .no_gpu_staging import load as candidates
    registry,_=candidates()
    cases=suite()['agents'];groups={}
    for row in future_queue():
        key=(row['model'],row['revision']);group=groups.setdefault(key,{'model':row['model'],
            'repo':row['repo'],'revision':row['revision'],'adapter':row['adapter'],
            'compute_estimate_gib':row['compute_estimate'],'estimate_not_measurement':True,'agents':[]})
        role=row['agent'];case=cases[role];link=registry['agents'][role]
        trial_profiles=['pinned/'+row['model']]
        if role=='video':trial_profiles+=['pinned/'+mid for mid in link['secondary_candidates']]
        group['agents'].append({'agent':role,'benchmark':row['benchmark'],'professional_trial_profiles':trial_profiles,
            'minimum_unique_outputs':case['minimum_counts'],'review_modes':case['review_modes'],
            'required_expertise':case['expertise_required'],
            'selected_support_workers':[{'model':mid,'repo':registry['profiles'][mid]['repo'],
                'revision':registry['profiles'][mid]['revision'],'adapter':registry['profiles'][mid]['adapter']}
                for mid in link['secondary_candidates']],
            'previous_evidence_policy':'Preserve existing verification artifacts. Reuse only exact-case, exact-source, exact-model evidence; never relabel historical outputs as a new trial.',
            'initial_canary_calls':1,'retry_policy':'Stop on failure; record a specific defect and code/conditioning change before reserving a bounded retry.',
            'full_evaluation':'Reserve the existing professional minimum counts after canary review; include supporting modalities and failed attempts in the trial budget.',
            'all_modalities_verified':False})
    # Story canary is the first economical text check; retain original role IDs.
    for group in groups.values():group['agents'].sort(key=lambda r:({'story':0,'character':1,'script':2,'director':3}.get(r['agent'],4)))
    support=[]
    for mid in registry['agents']['video']['secondary_candidates']:
        p=registry['profiles'][mid]
        if (mid,p['revision']) not in groups:
            support.append({'order':len(groups)+len(support)+1,'model':mid,'repo':p['repo'],
                'revision':p['revision'],'adapter':p['adapter'],'purpose':'Required three-engine video benchmark coverage',
                'minimum_video_outputs':cases['video']['per_model_video_minimum'],'execution_enabled':False})
    return {'schema_version':1,'batches':[dict(g,order=i+1) for i,g in enumerate(groups.values())],
        'required_support_batches':support,
        'max_concurrent_models':1,'max_concurrent_agents':1,'execution_enabled':False,
        'phases':['Inspect existing evidence and source/model locks without inference',
                  'One text canary, then independent review; stop if unsuitable',
                  'Prepare approved reference assets and consent before media batches',
                  'Unload current worker before loading the next pinned model; retain shared approved evidence',
                  'Run required shortlisted video engines sequentially; do not call a single-engine canary a complete video benchmark',
                  'Complete modality-dependent reviews after supporting workers finish; QC remains independent',
                  'If model critique needs a reload, reserve one final shared critic pass after media batches; generator self-review is not independent expert acceptance',
                  'Targeted revision and source-bound re-evaluation; owner acceptance remains separate'],
        'hard_gates':['explicit future runtime authorization','complete local pinned bundle and source lock',
                      'rights and consent','available measured compute','exact approved source revisions'],
        'cost_policy':'No paid APIs or resources; do not repeat successful benchmarks. No cost, throughput or VRAM measurement is invented.'}


def review_packet(role,source,*,provenance):
    if provenance not in ('real_model_output','manually_authored_fixture'):raise AgentError('Declared sample provenance required.')
    p=profile(role);sid=digest({'role':role,'source':source,'provenance':provenance})
    return {'schema_version':1,'anonymous_sample_id':sid,'role':role,'source':copy.deepcopy(source),
            'source_sha256':digest(source),'provenance':provenance,'rubric':p['criteria'],
            'reviewer_expertise_required':p['required_reviews'],'notes':[],
            'disagreements':[],'technical_result':None,'artistic_result':None,'owner_approval':False}


def future_queue():
    """Pinned planning metadata only. No cache probe, GPU estimate invention or launch."""
    from .no_gpu_staging import load as candidates
    registry,_=candidates();rows=[]
    for role in AGENTS:
        link=registry['agents'][role];mid=link['primary_candidate'];model=registry['profiles'][mid]
        rows.append({'agent':role,'model':mid,'repo':model['repo'],'revision':model['revision'],
                     'capabilities_publisher_claimed':model['modalities'],'capabilities_runtime_verified':False,
                     'cache_status':'not_probed','compute_estimate':model.get('planning_gpu_gib','not_available'),
                     'compute_is_estimate':True,'adapter':model['adapter'],'benchmark':profile(role)['benchmark'],
                     'required_components':'Existing exact source lock, bundle manifest, rights and owner runtime authorization',
                     'max_concurrent_models':1,'max_concurrent_agents':1,'execution_enabled':False})
    return rows
