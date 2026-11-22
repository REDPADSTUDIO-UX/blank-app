"""Three-agent creative workspace inside the existing dashboard."""
import copy
import json
from pathlib import Path
import streamlit as st
from .agents import AgentError
from .agent_engine import Engine
from .creative import ROLES,WEIGHTS,evaluate


def samples():
    return json.loads((Path(__file__).resolve().parents[1]/'assets/writing/creative/scenarios.json').read_text())

def show_creative(store,key):
    st.subheader('Creative intelligence — Story / Director / Script')
    st.caption('Software Working · Human Review Pending. Supplied examples are manual fixtures; they are not model output or proof of premium writing quality.')
    seed=samples();engine=Engine(store)
    approved={t['id']:t for t in store.tasks() if t['state']=='Approved'}
    outputs={}
    for o in store.outputs():
        if o['task'] in approved and o['revision']==approved[o['task']]['revision']:
            try:
                body=json.loads(json.loads(o['payload'])['summary'])
                if body.get('artifact_type','').startswith('creative_'):outputs[o['task']]=body
            except (ValueError,AttributeError):pass
    kind=st.selectbox('Creative operation',sorted(ROLES[key]),key='creative_kind_'+key)
    with st.form('creative_brief_'+key):
        title=st.text_input('Creative project title',seed['brief']['title'])
        premise=st.text_area('Owner story brief',seed['brief']['premise'])
        genre=st.selectbox('Genre',['horror','family romance','drama','thriller'])
        tone=st.text_input('Tone','সংযত আবেগ, স্বাভাবিক উষ্ণতা; forced comedy নয়')
        c1,c2,c3=st.columns(3)
        count=c1.number_input('Season episodes',1,100,30)
        episode=c2.number_input('Current episode',1,100,1)
        seconds=c3.number_input('Estimated seconds',180,4200,300)
        source=st.selectbox('Approved creative source',['']+list(outputs),format_func=lambda x: 'None — initial Story task' if not x else approved[x]['agent']+' · '+x)
        deps=st.multiselect('Additional approved reviews / sources',list(outputs),format_func=lambda x:approved[x]['agent']+' · '+x)
        target_text=st.text_input('Rewrite scene IDs (comma-separated)','s2')
        mode=st.radio('Creative execution',['Validate supplied draft','Generate with configured local model'])
        default={'season':seed['season'],'screenplay':seed['screenplay'],'treatment':copy.deepcopy(seed['screenplay']),
                 'direction':seed['direction_story'],'rewrite':[seed['screenplay']['scenes'][1]]}[kind]
        if kind=='treatment':
            for scene in default['scenes']:scene['beats']=[b for b in scene['beats'] if b['type']=='action']
        raw=st.text_area('Structured draft / schema example',json.dumps(default,ensure_ascii=False,indent=2),height=200,key='creative_draft_'+key+'_'+kind)
        submit=st.form_submit_button('Queue creative task')
    if submit:
        try:
            data={'creative_v1':True,'kind':kind,'brief':{'title':title,'premise':premise,'genre':genre,'tone':tone,'episodes':int(count),'episode':int(episode),'seconds':int(seconds)},'artifact':json.loads(raw)}
            dependencies=list(dict.fromkeys(([source] if source else [])+deps))
            if source:data['source']={'$from':source,'path':['artifact']}
            if kind=='rewrite':data['targets']=[x.strip() for x in target_text.split(',') if x.strip()]
            rid=engine.enqueue(key,data,dependencies,'local' if mode.startswith('Generate') else 'software')
            st.success('Creative task queued: '+rid+'. Use Run ready tasks once below; source approval and local availability are enforced.')
        except (AgentError,ValueError) as exc:st.error(str(exc))
    # Review existing creative outputs independently of source handoff approval.
    versions=[]
    tasks={t['id']:t for t in store.tasks()}
    for o in store.outputs():
        if tasks[o['task']]['agent']!=key:continue
        try:
            body=json.loads(json.loads(o['payload'])['summary'])
            if body.get('artifact_type','').startswith('creative_'):versions.append((o,body))
        except (ValueError,AttributeError):pass
    if not versions:return
    choice=st.selectbox('Creative artifact version',range(len(versions)),format_func=lambda i:versions[i][0]['task']+' revision '+str(versions[i][0]['revision']),key='creative_version_'+key)
    o,body=versions[choice]
    st.write({'provenance':body['provenance'],'model_inference':body['model_inference'],'creative_quality_verified':False})
    st.json(body['findings'])
    if body.get('formatted'):st.markdown(body['formatted'])
    else:st.json(body['artifact'])
    previous=[b for row,b in versions if row['task']==o['task'] and row['revision']<o['revision']]
    if previous:
        import difflib
        st.code('\n'.join(difflib.unified_diff(json.dumps(previous[-1]['artifact'],ensure_ascii=False,indent=2).splitlines(),json.dumps(body['artifact'],ensure_ascii=False,indent=2).splitlines(),fromfile='previous',tofile='current')))
    st.download_button('Export creative artifact',json.dumps(body,ensure_ascii=False,indent=2),'creative-artifact.json',key='creative_export_'+key)
    with store.tx() as db:
        db.execute('CREATE TABLE IF NOT EXISTS creative_reviews(task TEXT,revision INTEGER,payload TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP)')
        records=[dict(r) for r in db.execute('SELECT * FROM creative_reviews WHERE task=? ORDER BY rowid',(o['task'],))]
    st.caption('Rubric scores are supplied by the named reviewer. No score is inferred from field presence, and no score grants approval.')
    with st.form('creative_eval_'+key):
        reviewer=st.text_input('Reviewer name / ID')
        provenance=st.selectbox('Review provenance',['human','model_review','simulation'])
        ratings={}
        for dim,weight in WEIGHTS.items():
            with st.expander(dim+' · '+str(weight)+'%'):
                ratings[dim]={'score':st.number_input('Score 0–10',0.0,10.0,5.0,key=key+dim+'score'),
                 'strength':st.text_input('Specific strength',key=key+dim+'strength'),
                 'weakness':st.text_input('Specific weakness',key=key+dim+'weakness'),
                 'evidence':st.text_input('Exact quote from this artifact',key=key+dim+'evidence'),
                 'revision':st.text_input('Targeted improvement',key=key+dim+'revision')}
        confirm=st.checkbox('I supplied and checked these scores and quotes; this is not owner approval.')
        save=st.form_submit_button('Save evidence-based evaluation')
    if save:
        try:
            if not confirm:raise AgentError('Reviewer confirmation required.')
            earlier=next((json.loads(r['payload']) for r in reversed(records) if r['revision']<o['revision']),None)
            report=evaluate(body['artifact'],ratings,reviewer,provenance,earlier)
            with store.tx() as db:
                db.execute('BEGIN IMMEDIATE')
                t=store._task(db,o['task']);store._current(db,t)
                if t['revision']!=o['revision']:raise AgentError('Only the current artifact can receive a new review.')
                db.execute('INSERT INTO creative_reviews(task,revision,payload) VALUES (?,?,?)',(o['task'],o['revision'],json.dumps(report,ensure_ascii=False)))
                store.event(db,o['task'],'owner','creative_evaluation',{'revision':o['revision'],'provenance':provenance})
            st.success('Creative Evaluation Completed — attributed review only; Human Review/approval remains separate.');st.rerun()
        except AgentError as exc:st.error(str(exc))
    for record in records:st.json(json.loads(record['payload']))
