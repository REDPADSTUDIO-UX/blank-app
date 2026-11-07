"""Readiness and real-output review within the existing owner workspace."""
import json
import streamlit as st
from .agents import AgentError
from .professional_readiness import ProfessionalLab,audit,suite,models

def show_summary():
    with st.expander('Professional readiness — capability and real output'):
        data=audit()
        st.warning('০/২০ agent-এর professional capability যাচাইকৃত। Software tests, knowledge ও JSON pass শিল্পমানের প্রমাণ নয়।')
        st.dataframe([{'Agent':r['name'],'Software':'Foundation/partial adapters','Real capability':r['historical_real_model_attempts'],
                       'Production capable':r['production_capable'],'Needs':r['specialist_development_needed']} for r in data['agents']],hide_index=True)
        st.download_button('Download model / compute / specialist requirement matrix',json.dumps(data,ensure_ascii=False,indent=2),'professional-readiness.json',key='professional_matrix_download')

def show_trials(program):
    lab=ProfessionalLab(program.store)
    with st.expander('Real-output benchmark and independent expert review'):
        st.caption('Trials do not download models, contact reviewers, generate on opening, or grant production approval. Configure exact approved research models through existing model controls.')
        with st.form('professional_plan'):
            role=st.selectbox('Specialist under evaluation',list(suite()['agents']),key='professional_role')
            profiles=st.multiselect('Researched model / tool profiles',list(models()),key='professional_models')
            hypothesis=st.text_area('Why this candidate should address an observed capability gap',key='professional_hypothesis')
            expected=st.text_area('Observable improvement and expert evaluation target',key='professional_target')
            budget=st.number_input('Maximum generation attempts, including media',1,24,3,key='professional_budget')
            create=st.form_submit_button('Record a bounded evaluation plan')
        if create:
            try:st.json(lab.plan(role,profiles,hypothesis,expected,max_calls=budget))
            except (AgentError,ValueError) as exc:st.error(str(exc))
        with program.store.tx() as db:trials=[r[0] for r in db.execute('SELECT id FROM professional_trials ORDER BY rowid')]
        if not trials:return
        trial=st.selectbox('Evaluation trial',trials,key='professional_trial');st.json(lab.trial(trial))
        try:st.json(lab.status(trial))
        except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
        runs=program.engine.runs()
        if runs:
            rid=st.selectbox('Existing queued / executed Studio run',[r['id'] for r in runs],key='professional_run')
            sample=st.text_input('Unique sample label',key='professional_sample')
            if st.button('Bind queued run before generation',key='professional_bind'):
                try:st.json(lab.bind(trial,rid,sample))
                except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
            st.caption('Run through the existing Studio execution control. Only the bound installed/approved model may answer; existing source/QC/owner gates remain.')
            kind=st.selectbox('Evidence to capture',['text','media','execution trace'],key='professional_capture_kind')
            if st.button('Capture original executed evidence',key='professional_capture'):
                try:st.json((lab.capture_text if kind=='text' else lab.capture_media if kind=='media' else lab.capture_trace)(trial,rid))
                except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
        samples=lab.samples(trial)
        for item in samples:
            st.json(item)
            if item.get('path'):
                from .offline_media import media_path
                try:
                    path=media_path(program.store.path,item['path'])
                    if item['kind']=='image':st.image(str(path))
                    elif item['kind']=='audio':st.audio(str(path))
                    else:st.video(str(path))
                except (AgentError,OSError) as exc:st.error(str(exc))
        st.download_button('Export unchanged real-output review packet',json.dumps({'case':lab.trial(trial)['case'],'samples':samples,'human_review_completed':False},ensure_ascii=False,indent=2),'expert-review-packet.json',key='professional_packet_download')
        try:
            blind,key=lab.blind_packet(trial)
            st.download_button('Blind expert packet',json.dumps(blind,ensure_ascii=False,indent=2),'blind-expert-packet.json',key='professional_blind')
            st.download_button('Administrator mapping — withhold from reviewer',json.dumps(key,ensure_ascii=False,indent=2),'expert-admin-key.json',key='professional_blind_key')
        except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
        if not samples:st.info('প্রকৃত output ছাড়া expert evaluation শুরু হবে না।');return
        st.caption('Actual human evaluation only. No scores or acceptance are prefilled. Required expertise: '+lab.trial(trial)['case']['expertise_required'])
        reviewer=st.text_input('Actual reviewer name / ID',key='professional_reviewer')
        expertise=st.text_area('Reviewer’s relevant professional expertise',key='professional_expertise')
        independent=st.checkbox('Reviewer assessed independently of the generating model',key='professional_independent')
        qualified=st.checkbox('Reviewer is qualified for this department',key='professional_qualified')
        modes=st.multiselect('Actually performed evaluation',['text','visual','listening'],key='professional_review_modes')
        examined=st.checkbox('Reviewer actually examined every sample listed above',key='professional_examined')
        criteria={};complete=True;table={s['id']:s for s in samples}
        for criterion in lab.trial(trial)['case']['criteria']:
            with st.expander('Evaluate: '+criterion):
                decision=st.selectbox('Judgment',['Not evaluated','Pass','Fail'],key='professional_judgment_'+criterion)
                finding=st.text_area('Observed finding, in the reviewer’s own words',key='professional_finding_'+criterion)
                ids=st.multiselect('Original samples supporting this finding',list(table),key='professional_evidence_'+criterion)
                anchors=[]
                for sample_id in ids:
                    item=table[sample_id];prefix=criterion+'_'+sample_id
                    anchor={'sample':sample_id}
                    if item['kind'] in ('text','trace'):
                        anchor['quote']=st.text_input('Exact observed excerpt from '+sample_id,key='professional_quote_'+prefix)
                    elif item['kind']=='image':
                        seen=st.checkbox('I inspected this complete image: '+sample_id,key='professional_image_seen_'+prefix)
                        anchor['region']=[0,0,1,1] if seen else []
                    else:
                        duration=float(item['runtime_evidence']['inspection']['duration'])
                        anchor['start']=st.number_input('Observed start seconds: '+sample_id,0.,duration,value=None,key='professional_start_'+prefix)
                        anchor['end']=st.number_input('Observed end seconds: '+sample_id,0.,duration,value=None,key='professional_end_'+prefix)
                    anchors.append(anchor)
                complete=complete and decision!='Not evaluated'
                criteria[criterion]={'passed':decision=='Pass','finding':finding,'evidence':anchors}
        confirmed=st.checkbox('Owner attests this records a real named human evaluation, not a simulated or AI review',key='professional_review_confirm')
        if st.button('Record actual expert evaluation',key='professional_review_save'):
            try:
                if not complete:raise AgentError('Every criterion needs an actual Pass/Fail judgment; nothing is accepted by default.')
                review={'reviewer_type':'human','reviewer':reviewer,'expertise':expertise,'independent':independent,'qualified_for_role':qualified,
                        'modes':modes,'examined_samples':list(table) if examined else [],'criteria':criteria}
                st.json(lab.expert_review(trial,review,confirmed))
            except (AgentError,OSError,ValueError,TypeError) as exc:st.error(str(exc))
