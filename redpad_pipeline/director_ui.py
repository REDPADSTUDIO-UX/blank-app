import json
import streamlit as st
from .agents import AgentError
from .director import Director


def show_director(store):
    director=Director(store)
    st.subheader('Director — creative planning and department coordination')
    st.info('Local inference requires an installed, configured Ollama model. Manual plans and tests are not AI inference. Dispatch records tasks only.')
    with st.form('director_create'):
        brief=st.text_area('Owner creative brief',key='director_brief')
        seconds=st.number_input('Target duration (seconds)',min_value=15,max_value=4200,value=300,step=1)
        mode=st.selectbox('Planning mode',['Existing local model','Manual JSON plan'])
        raw=st.text_area('Manual plan JSON (manual mode only)',key='director_json')
        revisions=[p['id'] for p in director.plans() if p['state']=='Revision requested']
        revision=st.selectbox('Revise rejected/requested plan',['']+revisions)
        run=st.form_submit_button('Create Director plan')
    if run:
        try:
            manual=json.loads(raw) if mode=='Manual JSON plan' else None
            if mode=='Manual JSON plan' and not isinstance(manual,dict): raise AgentError('Manual plan must be a JSON object.')
            with st.spinner('Preparing and validating Director plan'):
                director.create(brief,int(seconds),manual=manual,revision_of=revision)
            st.success('Plan saved for independent QC; no department executed.')
        except (AgentError,ValueError) as exc: st.error(str(exc))
    plans=director.plans()
    if not plans: return
    pid=st.selectbox('Director plan',[p['id'] for p in plans],key='director_selected')
    plan=next(p for p in plans if p['id']==pid)
    st.write({'state':plan['state'],'provenance':plan['provenance'],'model':plan['model']})
    st.json(json.loads(plan['plan']))
    with st.form('director_review_'+pid):
        decision=st.selectbox('Director plan review',['Recommend','Reject','Approve','Request revision'])
        evidence=st.text_area('Director review evidence')
        confirmed=st.checkbox('I am the owner recording this review; QC recommendations are manual.')
        review=st.form_submit_button('Save Director review')
    if review:
        try:
            if not confirmed: raise AgentError('Owner confirmation required.')
            director.review(pid,decision,evidence,'qc' if decision in ('Recommend','Reject') else 'owner')
            st.rerun()
        except AgentError as exc: st.error(str(exc))
    if st.button('Dispatch approved department tasks',disabled=plan['state']!='Approved',key='director_dispatch'):
        try: st.success('Assigned task IDs: '+', '.join(director.dispatch(pid)))
        except AgentError as exc: st.error(str(exc))
    st.download_button('Download Director plan',json.dumps(plan,ensure_ascii=False,indent=2),'director-plan.json')
