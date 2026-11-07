"""Functional execution controls inside the existing owner workspace."""
import json
import streamlit as st
from .agents import AgentError
from .agent_engine import Engine
from .departments import contract
from .readiness import inspect_resources


def show_execution(store,key):
    engine=Engine(store)
    st.subheader('Department execution')
    st.caption('Software mode validates and prepares supplied department data. Local mode requires an installed model. Media requests remain blocked until required assets/backends are available.')
    st.caption('The prefilled Bengali example is supplied test data, not model output. Edit it or queue it to test this department.')
    with st.expander('Input contract / editable starting example'):
        st.json(contract(key))
    from .specialists import IMPLEMENTED,example
    specialist=key in IMPLEMENTED and st.checkbox('Specialist workflow v1',value=True,key='specialist_mode_'+key)
    initial=example(key) if specialist else contract(key)
    if specialist:
        st.caption('Versioned specialist metadata, findings and targeted revisions. Use approved artifact bindings for sources/base. No creative or media quality verification.')
    tasks=store.tasks()
    approved=[t for t in tasks if t['state']=='Approved']
    if key=='storyboard' and specialist:
        scripts=[t for t in approved if t['agent']=='script']
        with st.expander('Draft coverage from an approved screenplay'):
            st.caption('Creates bounded shot slots from source action and timing. Reference IDs need Bible mapping and Director composition review.')
            if scripts:
                source_id=st.selectbox('Approved screenplay for coverage',[t['id'] for t in scripts],key='coverage_source')
                if st.button('Prepare screenplay shot breakdown',key='coverage_prepare'):
                    try:
                        from .specialist_workflows import screenplay_breakdown
                        output=[o for o in store.outputs() if o['task']==source_id][-1]
                        screenplay=json.loads(json.loads(output['payload'])['summary'])['artifact']
                        source=screenplay.get('screenplay',screenplay)
                        initial['records']=screenplay_breakdown(source)
                        initial['sources']={'screenplay':{'$from':source_id,'path':['artifact']}}
                        st.session_state['department_input_'+key+'_specialist']=json.dumps(initial,ensure_ascii=False,indent=2)
                        st.session_state['department_dependencies_'+key]=[source_id]
                        st.success('Prepared source-linked shot draft. Review the intake below before queueing.')
                    except (AgentError,ValueError,KeyError,TypeError) as exc:st.error('Cannot prepare structured coverage: '+str(exc))
            else:st.caption('Approve a structured screenplay first.')
    input_key='department_input_'+key+('_specialist' if specialist else '')
    if input_key not in st.session_state:st.session_state[input_key]=json.dumps(initial,ensure_ascii=False,indent=2)
    with st.form('department_run_'+key):
        raw=st.text_area('Department input JSON',height=240,key=input_key)
        deps=st.multiselect('Upstream task dependencies',[t['id'] for t in tasks],key='department_dependencies_'+key)
        bindings=st.multiselect('Bind approved department artifacts',[t['id'] for t in approved],key='specialist_bindings_'+key) if specialist else []
        targets=st.text_input('Targeted revision record IDs (comma separated)',key='specialist_targets_'+key) if specialist else ''
        mode=st.selectbox('Execution mode',['software','local']+(['media'] if key in ('video','voice','music','editing') else []),key='department_mode_'+key)
        revision=st.selectbox('Revise existing task',['']+[t['id'] for t in tasks if t['agent']==key and t['state']=='Revision requested'],key='department_revision_'+key)
        enqueue=st.form_submit_button('Queue department task')
    if enqueue:
        try:
            inputs=json.loads(raw)
            if specialist:
                for tid in bindings:
                    source=next(t for t in approved if t['id']==tid)
                    alias='screenplay' if source['agent']=='script' else source['agent']
                    if alias in inputs['sources']:raise AgentError('One source per department alias; edit JSON for explicit source selection.')
                    inputs['sources'][alias]={'$from':tid,'path':['artifact']}
                    if tid not in deps:deps.append(tid)
                if revision:
                    revised=next(t for t in tasks if t['id']==revision)
                    for ref in json.loads(revised['refs']):
                        if ref['id'] not in deps:deps.append(ref['id'])
                    previous=[o for o in store.outputs() if o['task']==revision][-1]
                    inputs['base']=json.loads(json.loads(previous['payload'])['summary'])['artifact']
                    inputs['targets']=[x.strip() for x in targets.split(',') if x.strip()]
            rid=engine.enqueue(key,inputs,deps,mode,revision or None)
            st.success('Queued execution '+rid)
        except (AgentError,ValueError) as exc:st.error(str(exc))
    from .local_ollama_session import ROOT,local_cpu_session
    managed=st.checkbox('Use installed development CPU runtime',key='department_owned_runtime_'+key) if (ROOT/'phase3_models/ollama-runtime/bin/ollama').is_file() else False
    if st.button('Run ready tasks once',key='department_tick_'+key):
        with st.spinner('Executing queued tasks; no automatic media generation'):
            if managed:
                with local_cpu_session():st.json(engine.tick(local_options={'num_ctx':4096,'num_predict':2048,'timeout_seconds':420}))
            else:st.json(engine.tick())
    if st.button('Run independent software tasks',key='specialist_parallel_'+key):
        st.json(engine.tick_parallel())
    own={t['id'] for t in store.tasks() if t['agent']==key}
    runs=[r for r in engine.runs() if r['task'] in own]
    if runs:
        st.dataframe(runs,hide_index=True)
        rid=st.selectbox('Execution record',[r['id'] for r in runs],key='department_record_'+key)
        run=next(r for r in runs if r['id']==rid)
        st.json(run)
        versions=[o for o in store.outputs() if o['task']==run['task']]
        if versions:
            st.caption('Versioned department artifacts')
            for output in versions:
                envelope=json.loads(output['payload'])
                with st.expander('Output revision '+str(output['revision'])):
                    try:
                        body=json.loads(envelope['summary']);st.json(body)
                        if isinstance(body.get('artifact'),dict) and 'records' in body['artifact']:
                            st.dataframe(body['artifact']['records'],hide_index=True)
                        if body.get('findings'):st.write(body['findings'])
                    except ValueError: st.write(envelope['summary'])
            st.download_button('Download task artifacts',json.dumps(versions,ensure_ascii=False,indent=2),'department-artifacts.json',key='department_artifacts_'+rid)
        if key=='qc' and next(t for t in store.tasks() if t['id']==run['task'])['state']=='Approved':
            candidates=json.loads(next(t for t in store.tasks() if t['id']==run['task'])['refs'])
            if candidates:
                target=st.selectbox('Reviewed task requiring revision',[r['id'] for r in candidates],key='specialist_route_target_'+rid)
                confirm=st.checkbox('Record targeted revision as owner',key='specialist_route_confirm_'+rid)
                if st.button('Route approved QC revision',disabled=not confirm,key='specialist_route_'+rid):
                    from .specialist_review import route_revision
                    try:route_revision(store,run['task'],target);st.success('Revision requested for the reviewed task.');st.rerun()
                    except AgentError as exc:st.error(str(exc))
        if run['state'] in ('Failed','Blocked'):
            corrected=st.text_area('Retry input JSON',run['inputs'],key='department_retry_input_'+rid)
            if st.button('Retry selected execution',key='department_retry_'+rid):
                try:engine.retry(rid,inputs=json.loads(corrected));st.rerun()
                except (AgentError,ValueError) as exc:st.error(str(exc))
        if run['state']=='Running':
            confirm=st.checkbox('The previous worker is interrupted; discard any late result.',key='recover_confirm_'+rid)
            if st.button('Recover interrupted execution',disabled=not confirm,key='department_recover_'+rid):
                try:engine.recover(rid);st.rerun()
                except AgentError as exc:st.error(str(exc))
    if st.button('Check local runtime availability',key='department_probe_'+key):
        st.json(inspect_resources(probe=True))
    if key=='production_manager':
        st.subheader('Current execution queue and task states')
        st.dataframe(engine.runs(),hide_index=True)
        with st.expander('Queue a branched specialist production plan'):
            from .specialist_project import queue_project,DEPENDENCIES
            st.json(DEPENDENCIES)
            st.caption('Manual metadata plan. Every department waits for owner-approved dependencies; this does not generate a film.')
            with st.form('specialist_project'):
                project_inputs=st.text_area('Inputs for all 17 specialist departments',json.dumps({k:example(k) for k in DEPENDENCIES},ensure_ascii=False,indent=2),height=240)
                creative_refs=st.multiselect('Approved creative source tasks',[t['id'] for t in approved if t['agent'] in ('script','director','story')])
                queue=st.form_submit_button('Queue supplied production plan')
            if queue:
                try:st.json(queue_project(engine,json.loads(project_inputs),creative_refs))
                except (AgentError,ValueError) as exc:st.error(str(exc))
    st.caption('QC outputs are reviewed directly by the owner; other departments require independent QC recommendation before owner approval. This does not publish anything.')
