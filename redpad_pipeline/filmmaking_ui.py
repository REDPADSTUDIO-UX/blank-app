"""Small additions to the existing three-agent owner workspace."""
import json
import streamlit as st
from .filmmaking_knowledge import readiness,retrieve
from .series_ledger import SeriesLedger
from .agents import AgentError
from .screenwriter import WritingError
from .model_routing import ModelRoutes
from .local_ollama_session import local_cpu_session,ROOT

def show_knowledge():
    with st.expander('Filmmaking knowledge and evidence'):
        r=readiness();st.caption('Versioned guidance and original examples used by agent execution. This is contextual conditioning; no model weights have been trained and artistic quality remains unapproved.')
        st.dataframe(r['agents'],hide_index=True)
        role=st.selectbox('Department craft guidance',[a['agent'] for a in r['agents']],key='craft_department')
        st.json(retrieve(role))

def show_series(program):
    with st.expander('পর্ব ধরে series architecture — draft only'):
        ledger=SeriesLedger(program.root/'series_architecture')
        config_path=ledger.folder/'series.json'
        if not config_path.exists():
            with st.form('craft_series_create'):
                actors=st.text_area('চরিত্রের নাম — প্রতি লাইনে একজন',key='craft_series_actors')
                facts=st.data_editor([{'তথ্যের নাম':'','বর্তমান অবস্থা':''}],num_rows='dynamic',key='craft_series_facts')
                create=st.form_submit_button('পর্বের কাঠামো শুরু করুন')
            if create:
                try:
                    state={r['তথ্যের নাম']:r['বর্তমান অবস্থা'] for r in facts if r['তথ্যের নাম'].strip() and r['বর্তমান অবস্থা'].strip()}
                    if len(state)!=len([r for r in facts if r['তথ্যের নাম'].strip()]):raise AgentError('Distinct fact names and nonempty states required.')
                    p=program.summary()['project']
                    ledger.create(p['brief'],[n.strip() for n in actors.splitlines() if n.strip()],state,p['episodes']);st.rerun()
                except (AgentError,ValueError,TypeError) as exc:st.error(str(exc))
            return
        try:state=ledger.state()
        except (AgentError,ValueError,WritingError) as exc:st.error(str(exc));return
        st.write(f"Draft architecture: {state['completed']}/{state['config']['episodes']} episodes")
        st.caption('প্রতি action-এ একটি ছোট পর্ব। আগের state, causal link ও setup ID যাচাই হয়; গল্পের মান বা owner approval এতে প্রমাণিত হয় না। পুরোনো সফল পর্ব পুনরায় generate হবে না।')
        st.json(state['state'])
        for p in sorted(ledger.folder.glob('ep*.json')):st.json(json.loads(p.read_text()))
        names=[m['name'] for m in ModelRoutes(program.store).models() if m['approved']]
        if not names:st.info('একটি installed local model-এর research authorization প্রয়োজন; নতুন model download করা হবে না।');return
        model=st.selectbox('Series research model',names,key='craft_series_model')
        managed=st.checkbox('Use existing local CPU runtime',key='craft_series_cpu') if (ROOT/'phase3_models/ollama-runtime/bin/ollama').exists() else False
        if st.button('পরের একটি পর্বের draft তৈরি করুন',key='craft_series_run'):
            try:
                if managed:
                    with local_cpu_session():result=ledger.run_next(model=model,store=program.store)
                else:result=ledger.run_next(model=model,store=program.store)
                st.json(result)
            except (AgentError,WritingError,ValueError,OSError) as exc:st.error(str(exc))
        failed=ledger.folder/f"ep{state['completed']+1:03}.json"
        if failed.exists() and json.loads(failed.read_text()).get('status')=='failed':
            correction=st.text_area('ব্যর্থ draft-এর নির্দিষ্ট সংশোধন',key='craft_series_correction')
            if st.button('মূল ব্যর্থতা রেখে একবার সংশোধিত retry',key='craft_series_retry'):
                try:
                    if managed:
                        with local_cpu_session():result=ledger.retry_next(correction,model=model,store=program.store)
                    else:result=ledger.retry_next(correction,model=model,store=program.store)
                    st.json(result)
                except (AgentError,WritingError,ValueError,OSError) as exc:st.error(str(exc))
