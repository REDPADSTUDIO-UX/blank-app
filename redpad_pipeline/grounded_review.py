"""Grounded Director/QC observations and calibration, never an approval engine."""
import copy,math
from .agents import AgentError,encode
from .creative import digest

def prepare_stage(role,data,sources):
    if role not in ('director','qc') or not any(s.get('artifact')==data.get('source') for s in sources.values()):raise AgentError('Grounded critic requires exact current approved source.')
    source=data['source']
    if source.get('stage')=='outline':source={'episodes':source['records']}
    report=review(source,data.get('findings'),role)
    return {'agent':role,'artifact_type':'grounded_criticism','artifact':report,'findings':[{'code':'unsupported_criticism','severity':'warning','evidence':f} for f in report['unsupported']],
            'model_inference':False,'media_generated':False,'human_review_required':True,'creative_quality_verified':False}

def compile_season_review(role,data,sources):
    if role!='director' or data['season_task'] not in sources:raise AgentError('Approved season and Director critic sources required.')
    season=sources[data['season_task']]['artifact'];tasks=data['critic_tasks']
    if len(tasks)!=len(season['episodes']) or len(set(tasks))!=len(tasks):raise AgentError('One independent bounded Director report per episode required.')
    reports=[]
    for task,ep in zip(tasks,season['episodes']):
        report=sources.get(task,{}).get('artifact',{})
        if report.get('source_sha256')!=digest({'episodes':[ep]}) or report.get('role')!='director' or report.get('unassessed_targets'):raise AgentError('An episode is stale, unassessed or covered by the wrong critic source.')
        reports.append({'task':task,'report_sha256':digest(report),'episode':ep['number'],'unsupported':report['unsupported'],'revision_proposals':report['revision_proposals']})
    return {'agent':'director','artifact_type':'grounded_season_review','artifact':{'season_sha256':digest(season),'episode_reports':reports,'specialist_visual_direction_pending':True,'professional_judgment_verified':False},
            'findings':[],'human_review_required':True,'model_inference':False,'media_generated':False,'creative_quality_verified':False}

def review(source,findings,reviewer_role):
    if reviewer_role not in ('director','qc') or not isinstance(findings,list) or len(findings)>100:raise AgentError('Bounded Director/QC findings required.')
    items={str(s['id']):s for s in source.get('scenes',[])}
    items.update({'episode_'+str(e['number']):e for e in source.get('episodes',[])})
    accepted=[];unsupported=[]
    for supplied in findings:
        f=copy.deepcopy(supplied)
        fields={'id','target','quote','observation','interpretation','category','severity','confidence','decision','target_agent','instruction'}
        if not isinstance(f,dict) or not fields<=f.keys() or f['target'] not in items:raise AgentError('Source-specific review fields required.')
        if f['category'] not in ('contract','narrative','subjective','missing_evidence') or f['severity'] not in ('info','warning','error','blocker') or f['decision'] not in ('revise','abstain','clear'):raise AgentError('Review classification invalid.')
        if type(f['confidence']) not in (float,int) or not math.isfinite(f['confidence']) or not 0<=f['confidence']<=1:raise AgentError('Bounded explicit reviewer confidence required.')
        if f['target_agent'] not in ('story','script','character','art','location','costume','storyboard','performance','cinematographer','motion','video','voice','music','editing','continuity','production_manager','growth','youtube','director'):raise AgentError('Invalid revision recipient; QC cannot review itself.')
        if f['decision']=='revise' and (not f['quote'] or f['quote'] not in encode(items[f['target']]) or not f['instruction']):
            unsupported.append(dict(f,reason='Quotation absent from this target or missing precise instruction'));continue
        if f['category']=='subjective':f['artistic_adjudication_required']=True
        f['grants_revision_authority']=False;accepted.append(f)
    if len({f['id'] for f in accepted+unsupported})!=len(findings):raise AgentError('Distinct review finding IDs required.')
    return {'source_sha256':digest(source),'role':reviewer_role,'findings':accepted,'unsupported':unsupported,
            'unassessed_targets':sorted(set(items)-{f['target'] for f in accepted}),
            'revision_proposals':[f for f in accepted if f['decision']=='revise'],'human_adjudication_required':True,'owner_approval':False}

def calibrate(report,annotations):
    """Exact annotated defect matching only; semantic/artistic accuracy not inferred.
    Annotation definitions must come from a separately identified evaluator.
    """
    if not isinstance(annotations,dict) or not {'annotator','provenance','source_sha256','defects'}<=annotations.keys() or annotations['source_sha256']!=report['source_sha256']:raise AgentError('Attributed version-specific control annotations required.')
    if annotations['provenance'] not in ('human','manually_authored_fixture') or not annotations['annotator']:raise AgentError('Unknown control annotation provenance.')
    truth={(f['target'],f['category'],f['quote']) for f in annotations['defects']}
    observed={(f['target'],f['category'],f['quote']) for f in report['findings'] if f['decision']=='revise'}
    tp=len(truth&observed);fp=len(observed-truth)+len(report['unsupported']);fn=len(truth-observed)
    return {'tp':tp,'fp':fp,'fn':fn,'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None,
            'clean_control':not truth,'semantic_partial_credit':'Requires independent adjudication; exact matches alone are not dramatic intelligence.',
            'professional_judgment_verified':False,'annotations':annotations}
