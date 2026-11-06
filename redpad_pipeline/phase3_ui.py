"""Isolated Phase 3 controls within the existing authenticated Studio."""
import json
import streamlit as st
from .agents import AgentError
from .phase3 import Lab,audit,cases


def show_phase3():
    st.caption('Bounded local experiments. Models/GPU are not installed or enabled here; no remote inference or automatic approval.')
    from .local_ollama_session import ROOT,local_cpu_session
    managed=st.checkbox('Use installed development CPU runtime for experiments',key='phase3_owned_runtime') if (ROOT/'phase3_models/ollama-runtime/bin/ollama').is_file() else False
    from .staged_writing_ui import show_staged
    show_staged(managed)
    if st.button('Audit available model runtime',key='phase3_audit'):
        if managed:
            with local_cpu_session():st.json(audit(True))
        else:st.json(audit(True))
    lab_id=st.text_input('Isolated experiment ID','bengali-phase3',key='phase3_lab_id')
    if st.button('Open isolated experiment',key='phase3_open'):
        try:Lab(lab_id);st.session_state['phase3_open_id']=lab_id
        except AgentError as exc:st.error(str(exc))
    if 'phase3_open_id' not in st.session_state:return
    lab=Lab(st.session_state['phase3_open_id']);summary=lab.summary()
    st.caption('Open experiment: '+st.session_state['phase3_open_id'])
    st.json({k:v for k,v in summary.items() if k not in ('runs','runtime_records')})
    approved=[t for t in lab.store.tasks() if t['state']=='Approved']
    options={c['id']:c for c in cases()}
    with st.form('phase3_queue'):
        case=st.selectbox('Bengali benchmark',list(options),key='phase3_case')
        model=st.text_input('Installed local model identifier','qwen3:4b-instruct-2507-q4_K_M',key='phase3_model')
        source=st.selectbox('Approved experiment source',['']+[t['id'] for t in approved],key='phase3_source')
        deps=st.multiselect('Additional approved experiment reviews',[t['id'] for t in approved],key='phase3_deps')
        queue=st.form_submit_button('Queue bounded local experiment')
    if queue:
        try:lab.queue(case,model,deps,source or None);st.success('Experiment queued. No model download or inference yet.');st.rerun()
        except AgentError as exc:st.error(str(exc))
    runs=lab.engine.runs()
    if runs:
        st.dataframe(runs,hide_index=True)
        rid=st.selectbox('Experiment execution',[r['id'] for r in runs],key='phase3_run')
        run=next(r for r in runs if r['id']==rid)
        if st.button('Run selected local experiment',key='phase3_execute',disabled=run['state']!='Ready for Input'):
            try:
                with st.spinner('Local inference preflight / bounded generation'):
                    if managed:
                        with local_cpu_session():state=lab.run(rid)
                    else:state=lab.run(rid)
                st.info(state);st.rerun()
            except AgentError as exc:st.error(str(exc))
        if run['state'] in ('Blocked','Failed') and st.button('Retry after resolving blocker',key='phase3_retry'):
            try:lab.engine.retry(rid);st.rerun()
            except AgentError as exc:st.error(str(exc))
        if run['state']=='Running':
            abandoned=st.checkbox('Previous worker is stopped; discard late replies',key='phase3_recover_confirm')
            if st.button('Recover interrupted experiment',disabled=not abandoned,key='phase3_recover'):
                try:lab.recover(rid);st.rerun()
                except AgentError as exc:st.error(str(exc))
        task=next(t for t in lab.store.tasks() if t['id']==run['task'])
        outputs=[o for o in lab.store.outputs() if o['task']==task['id']]
        for output in outputs:
            st.json(json.loads(json.loads(output['payload'])['summary']))
        if outputs:
            version=outputs[-1]['revision']
            st.download_button('Export blind editorial package',json.dumps(lab.blind_review_package(task['id'],version),ensure_ascii=False,indent=2),'blind-editorial.json',key='phase3_blind')
            with st.form('phase3_human_review'):
                reviewer=st.text_input('Human reviewer name / ID',key='phase3_reviewer')
                st.caption('Provide all eight rubric dimensions: score, strength, weakness, exact evidence quote and revision. No scores are prefilled.')
                raw=st.text_area('Editorial ratings JSON','{}',key='phase3_ratings')
                confirm=st.checkbox('I personally supplied and checked this human editorial assessment',key='phase3_human_confirm')
                save=st.form_submit_button('Record attributed editorial review')
            if save:
                try:st.json(lab.review(task['id'],version,json.loads(raw),reviewer,confirm))
                except (AgentError,ValueError) as exc:st.error(str(exc))
            with st.form('phase3_owner_gate'):
                action=st.selectbox('Experiment review action',['Recommend','Reject','Approve','Request revision'])
                evidence=st.text_area('Specific review evidence / revision request')
                confirm=st.checkbox('Record this explicit QC/owner action; no model performs approval')
                review=st.form_submit_button('Record experiment gate')
            if review:
                try:
                    if not confirm:raise AgentError('Explicit reviewer confirmation required.')
                    lab.store.review(task['id'],version,action,evidence,'qc' if action in ('Recommend','Reject') else 'owner');st.rerun()
                except AgentError as exc:st.error(str(exc))
    st.download_button('Export experiment evidence',json.dumps(lab.summary(),ensure_ascii=False,indent=2),'phase3-evidence.json',key='phase3_export')

    archive=ROOT/'verification/phase3_cpu'
    files=sorted(archive.glob('trial_*.json')) if archive.is_dir() else []
    if files:
        st.subheader('Actual CPU creative research archive')
        st.caption('Unapproved experimental candidates and model criticism; no independent human quality approval.')
        chosen=st.selectbox('Saved CPU experiment',[p.name for p in files],key='phase3_cpu_archive')
        content=(archive/chosen).read_text();st.json(json.loads(content))
        st.download_button('Download actual CPU experiment',content,chosen,key='phase3_cpu_download')
