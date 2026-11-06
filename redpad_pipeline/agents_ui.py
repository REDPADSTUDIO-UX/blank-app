"""Owner-only offline development workspace, behind the Studio login gate."""
import json
import streamlit as st
from .agents import CATALOG, AGENTS, AgentStore, AgentError


def render_agent_control(path):
    st.header('AI AGENTS CONTROL CENTER')
    st.warning('20 department software workflows. Model inference and media generation are separate capabilities; no automatic publishing.')
    with st.expander('Phase 3 — real-model experiments'):
        from .phase3_ui import show_phase3
        show_phase3()
    store = AgentStore(path)
    st.dataframe([{'ID':a['id'],'Agent':a['name'],'Department':a['department'],**store.status(a['key'])} for a in CATALOG],hide_index=True)
    key=st.selectbox('Individual agent workspace',list(AGENTS),format_func=lambda k:AGENTS[k]['name'],key='agent_workspace')
    a=AGENTS[key]
    st.subheader(a['name'])
    st.json(a)
    st.caption('Related modules are retained in their existing Studio tabs. Dependencies are planning requirements; manual routing fixtures may reference any approved task.')
    with st.form('agent_config'):
        model=st.text_input('Installed local model identifier (configuration only)',value=store.status(key)['model'],key='agent_model_'+key)
        save=st.form_submit_button('Save agent configuration')
    if save:
        try: store.configure(key,model); st.success('Configuration saved. Connection remains unverified.')
        except AgentError as e: st.error(str(e))
    if key in ('story','script','director'):
        from .creative_ui import show_creative
        show_creative(store,key)
    if key == 'director':
        from .director_ui import show_director
        show_director(store)
    from .agent_execution_ui import show_execution
    show_execution(store,key)
    tasks=store.tasks()
    with st.form('agent_assign'):
        brief=st.text_area('Task brief',key='agent_brief')
        refs=st.multiselect('Approved task references',[t['id'] for t in tasks if t['state']=='Approved'],key='agent_refs')
        assign=st.form_submit_button('Assign development task')
    if assign:
        try: store.assign(key,brief,refs); st.success('Task recorded. No model was called.'); tasks=store.tasks()
        except AgentError as e: st.error(str(e))
    own=[t for t in tasks if t['agent']==key]
    if own:
        tid=st.selectbox('Task',[t['id'] for t in own],key='agent_task_'+key)
        t=next(t for t in own if t['id']==tid)
        st.json(t)
        with st.form('agent_output_'+tid):
            summary=st.text_area('Output summary')
            provenance=st.selectbox('Provenance',['manual','simulation'])
            submit=st.form_submit_button('Save versioned output')
        if submit:
            try:
                store.submit(tid,{'schema_version':1,'kind':a['output_contract']['kind'],'summary':summary,'artifacts':[],'provenance':provenance},t['revision'])
                st.success('Output saved for independent QC.'); st.rerun()
            except AgentError as e: st.error(str(e))
        with st.form('agent_review_'+tid):
            decision=st.selectbox('Review action',['Recommend','Reject','Approve','Request revision'])
            evidence=st.text_area('Review evidence / targeted revision instructions')
            confirm=st.checkbox('I am recording this review as the owner; QC entries are manual recommendations, not AI inference.')
            review=st.form_submit_button('Record review',disabled=False)
        if review:
            try:
                if not confirm: raise AgentError('Owner confirmation required.')
                store.review(tid,t['revision'],decision,evidence,'qc' if decision in ('Recommend','Reject') else 'owner')
                st.success('Review recorded. No publishing action exists here.'); st.rerun()
            except AgentError as e: st.error(str(e))
    st.subheader('Versioned output records')
    st.dataframe(store.outputs(),hide_index=True)
    st.subheader('Assignment and audit history')
    st.dataframe(store.tasks(),hide_index=True)
    st.dataframe(store.history(),hide_index=True)
    st.download_button('Download development records',json.dumps({'agents':CATALOG,'tasks':store.tasks(),'history':store.history(),'outputs':store.outputs()},ensure_ascii=False,indent=2),'agent-development-records.json',key='agent_export')
