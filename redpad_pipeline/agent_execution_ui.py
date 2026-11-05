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
    tasks=store.tasks()
    with st.form('department_run_'+key):
        raw=st.text_area('Department input JSON',json.dumps(contract(key),ensure_ascii=False,indent=2),height=240,key='department_input_'+key)
        deps=st.multiselect('Upstream task dependencies',[t['id'] for t in tasks],key='department_dependencies_'+key)
        mode=st.selectbox('Execution mode',['software','local']+(['media'] if key in ('video','voice','music','editing') else []),key='department_mode_'+key)
        revision=st.selectbox('Revise existing task',['']+[t['id'] for t in tasks if t['agent']==key and t['state']=='Revision requested'],key='department_revision_'+key)
        enqueue=st.form_submit_button('Queue department task')
    if enqueue:
        try:
            rid=engine.enqueue(key,json.loads(raw),deps,mode,revision or None)
            st.success('Queued execution '+rid)
        except (AgentError,ValueError) as exc:st.error(str(exc))
    if st.button('Run ready tasks once',key='department_tick_'+key):
        with st.spinner('Executing queued tasks; no automatic media generation'):
            st.json(engine.tick())
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
                    try: st.json(json.loads(envelope['summary']))
                    except ValueError: st.write(envelope['summary'])
            st.download_button('Download task artifacts',json.dumps(versions,ensure_ascii=False,indent=2),'department-artifacts.json',key='department_artifacts_'+rid)
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
    st.caption('QC outputs are reviewed directly by the owner; other departments require independent QC recommendation before owner approval. This does not publish anything.')
