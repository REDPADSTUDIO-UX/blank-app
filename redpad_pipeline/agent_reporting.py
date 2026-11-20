"""Registry-derived matrix and current QC reporting. Read-only; no approval authority.
Historical fixture evidence, current project state and selected-model acceptance
remain distinct. No inference, resource probes, publishing or production DB use.
"""
import hashlib,json
from pathlib import Path
from .agents import CATALOG,AGENTS,AgentError,validate_catalog

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/'verification/agent_implementation_matrix_current.json'
RECEIPT=ROOT/'verification/agent_registry_sync_20261120/cpu_tests.json'

def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def validate_matrix(matrix,catalog=None):
    catalog=CATALOG if catalog is None else catalog;validate_catalog(catalog)
    if not isinstance(matrix,dict) or matrix.get('schema_version')!=1 or not isinstance(matrix.get('agents'),list):raise AgentError('Versioned current agent matrix required; historical arrays are not current coverage.')
    rows=matrix['agents'];ids=[r.get('id') for r in rows if isinstance(r,dict)];keys=[r.get('key') for r in rows if isinstance(r,dict)]
    expected={r['id']:r for r in catalog}
    if len(ids)!=len(rows) or any(not isinstance(x,str) or not x for x in ids+keys) or len(set(ids))!=len(ids) or len(set(keys))!=len(keys):raise AgentError('Duplicate or malformed matrix agent identity.')
    if set(ids)!=set(expected):raise AgentError('Matrix registry mismatch: missing='+str(sorted(set(expected)-set(ids)))+' extra='+str(sorted(set(ids)-set(expected))))
    if type(matrix.get('registered_agents')) is not int or matrix['registered_agents']!=len(catalog) or len(rows)!=len(catalog):raise AgentError('Outdated matrix agent count.')
    if matrix.get('registry_sha256')!=sha(catalog):raise AgentError('Matrix registry snapshot is stale.')
    for row in rows:
        actual=expected[row['id']]
        if row['key']!=actual['key'] or row.get('name')!=actual['name']:raise AgentError('Matrix agent name/key differs from registry.')
        if not {'engineering','model','inference','qc','production'}<=row.keys():raise AgentError('Separate readiness layers required.')
    return matrix

def build_matrix(receipt=None):
    from .shared_model_services import catalog as candidates
    data=candidates();receipt=receipt or {};verified=receipt.get('all_registry_cpu_workflows') is True and receipt.get('registry_sha256')==sha(CATALOG) and receipt.get('failures')==0 and receipt.get('errors')==0
    rows=[]
    for a in CATALOG:
        key=a['key'];candidate=data['agents'][key];p=data['profiles'][candidate['primary_candidate']]
        rows.append({'id':a['id'],'key':key,'name':a['name'],'department':a['department'],
          'engineering':{'status':'cpu_fixture_workflow_verified' if verified else 'implemented_references_not_retested','existing_modules':a['existing_modules'],'input_contract':a['input_contract'],'output_contract':a['output_contract'],'verification':'verification/agent_registry_sync_20261120/cpu_tests.json' if verified else None},
          'model':{'profile':candidate['primary_candidate'],'repo':p['repo'],'revision':p['revision'],'registry_status':candidate['status'],'validated_selection':candidate.get('validated_selection'),'installation_and_connection':'not_probed_by_this_export'},
          'inference':{'selected_model_validation':'not_verified_by_this_audit','historical_evidence':candidate.get('latest_evidence',[]),'scope':'Historical research and fallback experiments do not verify the current selected model or current project route.'},
          'qc':{'workflow':'cpu_fixture_coverage_verified' if verified else 'implemented_not_retested','independent_creative_review':'not_attested_by_this_audit','owner_gate':'QC recommendation then owner approval; Casting additionally requires Director inspection and Producer identity lock; QC itself is owner-reviewed'},
          'production':{'status':'not_verified','ready':False,'reason':'Neither registry presence nor software tests establish artistic acceptance or production readiness.'}})
    return validate_matrix({'schema_version':1,'registered_agents':len(CATALOG),'registry_sha256':sha(CATALOG),'registry_source':'redpad_pipeline/agent_catalog.json','historical_matrix':'verification/agent_implementation_matrix.json','scope':'Current engineering/evidence index, not real-model or artistic acceptance; project runtime state is computed separately.','agents':rows})

def load_matrix():return validate_matrix(json.loads(CURRENT.read_text()))

def qc_report(store):
    """Coverage includes every registry role, even with zero tasks/findings.
    Current findings are kept separate from stale observations; this function
    cannot recommend, revise, approve, lock identities or publish anything.
    """
    rows={a['key']:{'id':a['id'],'agent':a['key'],'name':a['name'],'tasks':0,'awaiting_qc':0,'qc_recommendations':0,'owner_approved':0,'stale_tasks':0,'findings':[],'handoffs':[],
                    'revision_recipient':a['key']!='qc','review_gate':'owner_reviews_qc' if a['key']=='qc' else 'independent_qc_then_owner'} for a in CATALOG}
    tasks={t['id']:t for t in store.tasks()};events=store.history();unassigned=[];errors=[]
    with store.tx() as db:
        for task in tasks.values():
            role=task['agent']
            if role not in rows:
                errors.append({'task':task['id'],'reason':'Unregistered historical task agent: '+role});continue
            r=rows[role];r['tasks']+=1;current=True
            try:store._current(db,task)
            except AgentError:current=False;r['stale_tasks']+=1
            if current:
                r['awaiting_qc']+=int(task['state']=='Awaiting QC')
                r['owner_approved']+=int(task['state']=='Approved')
                r['qc_recommendations']+=int(role!='qc' and any(e['task']==task['id'] and e['action']=='Recommend' and e['actor']=='qc' and json.loads(e['detail']).get('revision')==task['revision'] for e in events))
            for ref in json.loads(task['refs']):
                source=tasks.get(ref['id'])
                if source and source['agent'] in rows:rows[source['agent']]['handoffs'].append({'consumer_task':task['id'],'consumer_agent':role,'source_task':source['id'],'source_revision':ref['revision'],'current':current})
            out=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task['id'],task['revision'])).fetchone()
            if not out:continue
            try:body=json.loads(json.loads(out[0])['summary'])
            except (ValueError,KeyError,TypeError):continue # Plain manual summaries are valid, not structured QC reports.
            if not isinstance(body,dict):continue
            artifact=body.get('artifact',{});supplied=body.get('findings',[])
            default_recipient=artifact.get('subject_agent') if isinstance(artifact,dict) else None
            if role=='qc' and default_recipient is None and db.execute("SELECT 1 FROM sqlite_master WHERE name='agent_runs'").fetchone():
                legacy=db.execute('SELECT inputs FROM agent_runs WHERE task=? AND expected_revision=? ORDER BY rowid DESC LIMIT 1',(task['id'],task['revision']-1)).fetchone()
                if legacy:default_recipient=json.loads(legacy[0]).get('subject_agent')
            if default_recipient is None and role!='qc':default_recipient=role
            observations=list(supplied) if isinstance(supplied,list) else []
            if not isinstance(supplied,list):errors.append({'task':task['id'],'reason':'Malformed findings list'})
            if body.get('artifact_type') in ('grounded_criticism','grounded_season_review') and isinstance(artifact,dict):observations+=artifact.get('findings',[])
            for event in events:
                if event['task']!=task['id'] or event['action']!='intelligence_review':continue
                detail=json.loads(event['detail'])
                if detail.get('revision')==task['revision']:
                    observations += [dict(f,recorded_reviewer=event['actor']) for f in detail.get('report',{}).get('findings',[]) if isinstance(f,dict)]
            for f in observations:
                if not isinstance(f,dict):continue
                recipient=f.get('target_agent',f.get('responsible_agent',default_recipient))
                item={'source_task':task['id'],'source_revision':task['revision'],'source_agent':role,'current':current,'finding':f,'grants_revision_authority':False}
                if recipient in rows:rows[recipient]['findings'].append(item)
                else:unassigned.append(dict(item,unregistered_recipient=recipient))
    agents=list(rows.values())
    return {'schema_version':1,'registered_agents':len(CATALOG),'agents':agents,'revision_recipients':[a['key'] for a in CATALOG if a['key']!='qc'],'unassigned_findings':unassigned,'record_errors':errors,'professional_acceptance_inferred':False,'owner_approval_granted':False,'scope':'Current project ledger only. Zero findings means no observations recorded, not a QC pass. Stale evidence cannot authorize revision.'}

def dashboard(store=None):
    matrix=load_matrix();report=qc_report(store) if store is not None else None;rows=[]
    for a in matrix['agents']:
        row={'id':a['id'],'agent':a['key'],'name':a['name'],'engineering':a['engineering']['status'],'selected_model':a['model']['profile'],'selected_model_validation':a['inference']['selected_model_validation'],'production_ready':a['production']['ready']}
        if store is not None:
            status=store.status(a['key']);row.update(project_model=status['model'],project_inference_recorded=status['real_inference_verified'])
        rows.append(row)
    return {'registered_agents':len(CATALOG),'matrix_agents':len(rows),'engineering_verified':sum(a['engineering']['status']=='cpu_fixture_workflow_verified' for a in matrix['agents']),'production_ready':sum(a['production']['ready'] is True for a in matrix['agents']),'agents':rows,'qc':report}
