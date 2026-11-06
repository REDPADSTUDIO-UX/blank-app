"""Owner Dashboard integration; install approval does not download models."""
import json
import hashlib
from pathlib import Path
import streamlit as st
from .agents import AGENTS, AgentError
from .screenwriter import WritingError
from .model_routing import ModelRoutes,inventory
from .model_benchmark import cases, run_case, report, blind_comparison, DIMENSIONS
from .staged_writing import StagedDraft
from .local_ollama_session import ROOT,local_cpu_session


def show_model_routes(store,prefix=""):
    routes=ModelRoutes(store)
    with st.expander('Model comparison and specialist routing'):
        st.caption('Different local models per agent. No downloads, paid providers or automatic artistic approval. Research routes do not establish production readiness.')
        managed=st.checkbox('Use existing development CPU runtime',key=prefix+'models_cpu') if (ROOT/'phase3_models/ollama-runtime/bin/ollama').is_file() else False
        if st.button('Inspect installed local models',key=prefix+'models_inventory'):
            try:
                if managed:
                    with local_cpu_session():available=inventory()
                else:available=inventory()
                st.json(available)
            except (OSError,ValueError) as exc:st.error('Local model inventory unavailable; no model downloaded.')
        st.dataframe(routes.models(),hide_index=True)
        with st.form(prefix+'models_approve'):
            name=st.text_input('Exact installed local tag',key=prefix+'models_tag')
            sha=st.text_input('Full installed sha256 digest',key=prefix+'models_digest')
            license_note=st.text_input('Checked license / permitted use',key=prefix+'models_license')
            owner=st.text_input('Owner name / ID',key=prefix+'models_owner')
            confirm=st.checkbox('Owner authorizes research use of this installed model and checked license',key=prefix+'models_confirm')
            save=st.form_submit_button('Approve installed model for research')
        if save:
            try:
                if managed:
                    with local_cpu_session():routes.approve_installed(name,sha,license_note,owner,confirm)
                else:routes.approve_installed(name,sha,license_note,owner,confirm)
                st.success('Research authorization recorded; no creative acceptance.');st.rerun()
            except (AgentError,ValueError,OSError) as exc:st.error(str(exc))
        names=[m['name'] for m in routes.models() if m['approved']]
        if not names:return
        revoke=st.selectbox('Approved model to revoke',names,key=prefix+'models_revoke_tag')
        if st.button('Revoke model use and role acceptance',key=prefix+'models_revoke'):
            routes.revoke(revoke);st.rerun()
        with st.form(prefix+'models_route'):
            role=st.selectbox('Agent model route',list(AGENTS),key=prefix+'models_role')
            primary=st.selectbox('Primary local model',names,key=prefix+'models_primary')
            fallbacks=st.multiselect('Ordered local fallbacks (maximum two)',[n for n in names if n!=primary],key=prefix+'models_fallbacks')
            mode=st.selectbox('Route scope',['research','production'],key=prefix+'models_mode')
            save_route=st.form_submit_button('Save specialist route')
        if save_route:
            try:
                if managed:
                    with local_cpu_session():policy=routes.configure(role,[primary]+fallbacks,mode)
                else:policy=routes.configure(role,[primary]+fallbacks,mode)
                st.json(policy)
            except (AgentError,ValueError,OSError) as exc:st.error(str(exc))
        st.json({k:routes.policy(k) for k in AGENTS if routes.policy(k)})
        folder=ROOT/'phase3_runs/model_comparison'
        with st.form(prefix+'models_benchmark'):
            candidate=st.selectbox('Approved candidate',names,key=prefix+'models_candidate')
            case_id=st.selectbox('Equivalent Bengali task',[c['id'] for c in cases()],key=prefix+'models_case')
            run=st.form_submit_button('Run one bounded benchmark case')
        if run:
            try:
                with st.spinner('One local inference call; same benchmark, no fallback'):
                    if managed:
                        with local_cpu_session():result=run_case(store,folder,candidate,case_id)
                    else:result=run_case(store,folder,candidate,case_id)
                st.json(result)
            except (AgentError,WritingError,OSError,ValueError) as exc:st.error(str(exc))
        folders=[p.parent for p in folder.glob('*/manifest.json')]
        if folders:
            chosen=Path(st.selectbox('Saved candidate evidence',[str(p) for p in folders],key=prefix+'models_report'))
            evidence=report(chosen,store);st.json(evidence)
            failed=[k for k,r in evidence['records'].items() if r['status']=='failed']
            if failed:
                retry_case=st.selectbox('Failed benchmark case',failed,key=prefix+'models_retry_case')
                if st.button('Reset failed case for one explicit retry',key=prefix+'models_retry'):
                    try:StagedDraft(chosen).retry(retry_case);st.rerun()
                    except WritingError as exc:st.error(str(exc))
            st.download_button('Download candidate comparison evidence',json.dumps(evidence,ensure_ascii=False,indent=2),'candidate-evidence.json',key=prefix+'models_export')
            # Stable blind IDs until the compared evidence changes.
            fingerprint=json.dumps([report(p) for p in folders],sort_keys=True)
            if st.session_state.get(prefix+'models_blind_input')!=fingerprint:
                key=hashlib.sha256(fingerprint.encode()).hexdigest()[:20]
                package_path=folder/('blind-'+key+'.json');admin_path=folder/('blind-'+key+'-admin.json')
                if package_path.exists() and admin_path.exists():
                    package=json.loads(package_path.read_text());mapping=json.loads(admin_path.read_text())
                else:
                    package,mapping=blind_comparison(folders)
                    package_path.write_text(json.dumps(package,ensure_ascii=False,indent=2));admin_path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
                st.session_state[prefix+'models_blind_input']=fingerprint;st.session_state[prefix+'models_blind']=package;st.session_state[prefix+'models_blind_admin']=mapping
            st.download_button('Export blind editorial package',json.dumps(st.session_state[prefix+'models_blind'],ensure_ascii=False,indent=2),'blind-model-comparison.json',key=prefix+'models_blind')
            st.download_button('Administrator identity key — withhold from blind reviewer',json.dumps(st.session_state[prefix+'models_blind_admin'],ensure_ascii=False,indent=2),'blind-admin-key.json',key=prefix+'models_blind_admin_export')
            with st.form(prefix+'models_human'):
                accepted_role=st.selectbox('Role acceptance',['story','script','director','qc'],key=prefix+'models_accepted_role')
                st.caption('Ratings fields: '+', '.join(DIMENSIONS)+'. Each requires score, evidence, finding; no scores prefilled.')
                raw=st.text_area('Independent human review JSON (reviewer, independent, accepted, ratings)','{}',key=prefix+'models_ratings')
                human_confirm=st.checkbox('Owner attests this is an actual independent human review with exact evidence',key=prefix+'models_human_confirm')
                accept=st.form_submit_button('Record role-specific human acceptance')
            if accept:
                try:routes.accept(accepted_role,evidence['model'],evidence,json.loads(raw),human_confirm);st.success('Role acceptance recorded. Select a production route separately.')
                except (AgentError,ValueError,TypeError) as exc:st.error(str(exc))
