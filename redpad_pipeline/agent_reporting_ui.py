"""Shared registry/matrix/QC view for the owner dashboards."""
import json
import streamlit as st
from .agents import AgentError
from .agent_reporting import dashboard,load_matrix

def show_registry_status(store=None,*,key='registry_status'):
    try:data=dashboard(store)
    except (AgentError,OSError,ValueError) as exc:
        st.error('Current agent matrix requires synchronization: '+str(exc));return
    total=data['registered_agents']
    cols=st.columns(3)
    cols[0].metric('Registered agents',total)
    cols[1].metric('CPU workflow evidence',f"{data['engineering_verified']}/{total}")
    cols[2].metric('Production verified',f"{data['production_ready']}/{total}")
    st.progress(data['engineering_verified']/total,text='Recorded CPU fixture coverage; not model intelligence or artistic acceptance')
    with st.expander('Current agent implementation matrix'):
        st.dataframe(data['agents'],hide_index=True)
        st.download_button('Download current agent matrix',json.dumps(load_matrix(),ensure_ascii=False,indent=2),'agent-implementation-matrix-current.json',key=key+'_matrix')
    if data['qc'] is not None:
        report=data['qc']
        with st.expander('QC coverage and revision reporting'):
            st.caption('Every registered agent is shown. Zero findings is not a QC pass. Only owner-approved QC may request an exact-version revision; Casting retains Director inspection and Producer identity locks.')
            st.dataframe([{k:v for k,v in row.items() if k not in ('findings','handoffs')}|{'recorded_findings':len(row['findings']),'handoff_count':len(row['handoffs'])} for row in report['agents']],hide_index=True)
            st.download_button('Download registry-wide QC report',json.dumps(report,ensure_ascii=False,indent=2),'agent-qc-coverage.json',key=key+'_qc')
            if report['unassigned_findings'] or report['record_errors']:st.warning('Some historical records reference unregistered identities; see the report. They have not been silently discarded.')
