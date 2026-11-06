"""Opt-in development pilot; existing production approvals are untouched."""
import json
import re
import streamlit as st
from .screenwriter import WritingError
from .staged_bengali import run_next, KEYS
from .staged_writing import StagedDraft
from .local_ollama_session import ROOT, local_cpu_session


def show_staged(managed=False):
    with st.expander('Staged Bengali writing pilot'):
        st.caption('Six short stages: character plan → three causal choices → one scene → grounded Director notes. Experimental drafts need independent editorial review.')
        name=st.text_input('Staged draft ID','bengali-staged',key='staged_id')
        if not re.fullmatch(r'[a-z0-9_-]{1,48}',name):
            st.error('Use 1–48 lowercase letters, digits, underscores or hyphens.');return
        folder=ROOT/'phase3_runs'/('staged-'+name)
        records=[]
        for key in KEYS:
            p=folder/(key+'.json')
            if p.exists():records.append(json.loads(p.read_text()))
        st.caption(f'{sum(r["status"]=="validated_stage" for r in records)} / 6 structurally validated stages. No creative acceptance or automatic revision.')
        if st.button('Generate next short stage',key='staged_next'):
            try:
                with st.spinner('Bounded local CPU generation'):
                    if managed:
                        with local_cpu_session():record=run_next(folder)
                    else:record=run_next(folder)
                st.json(record)
            except WritingError as exc:st.error(str(exc))
        failed=[k for k in KEYS if (folder/(k+'.json')).exists() and json.loads((folder/(k+'.json')).read_text())['status']=='failed']
        if failed and st.button('Reset failed stage for one explicit retry',key='staged_retry'):
            try:StagedDraft(folder).retry(failed[0]);st.rerun()
            except WritingError as exc:st.error(str(exc))
        for r in records:
            st.json({'stage':r['request']['role'],'status':r['status'],'result':r['result'],'error':r['error']})
        if records:
            st.download_button('Export staged raw evidence',json.dumps(records,ensure_ascii=False,indent=2),'staged-evidence.json',key='staged_export')
        archive=ROOT/'verification/phase3_staged'
        if (archive/'blind_review.json').is_file():
            st.download_button('Download unreviewed blind comparison',(archive/'blind_review.json').read_text(),'blind-review.json',key='staged_blind')
