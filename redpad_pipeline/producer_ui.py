"""Director-centric Producer control center. Specialist tools stay secondary."""
import json
from pathlib import Path
import streamlit as st
from .agents import AgentError
from .studio_program import StudioProgram,PROGRAM_ROOT
from .producer_control import Producer
from .producer_references import CATEGORIES,RIGHTS,EXTENSIONS

NAV=['Dashboard Home','Director Studio','Approval Desk','Channel Manager','Growth & Analytics']

def action(fn):
    try:
        result=fn()
        if result is not None:st.success(str(result))
        st.rerun()
    except (AgentError,ValueError,OSError) as exc:st.error(str(exc))

def project_picker():
    ids=sorted(p.name for p in PROGRAM_ROOT.iterdir() if p.is_dir() and (p/'agent_control.sqlite3').is_file()) if PROGRAM_ROOT.exists() else []
    if st.session_state.get('producer_pending_project') in ids:
        st.session_state['producer_project']=st.session_state.pop('producer_pending_project')
    selected=st.selectbox('Saved production', ['— Select project —']+ids,key='producer_project')
    with st.expander('Create a film or series'):
        with st.form('producer_create'):
            id=st.text_input('Project ID',placeholder='dhaka-film')
            title=st.text_input('Production title')
            brief=st.text_area('Original idea / creative brief')
            episodes=st.number_input('Episodes (1 for film)',1,100,1)
            seconds=st.number_input('Target seconds per film / episode',180,4200,300)
            submit=st.form_submit_button('Create production')
        if submit:
            def create():
                StudioProgram(id).create(title,brief,episodes,seconds);st.session_state['producer_pending_project']=id
            action(create)
    if selected=='— Select project —':return None
    return Producer(StudioProgram(selected))

def overview():
    st.header('Productions')
    rows=[]
    for folder in sorted(PROGRAM_ROOT.iterdir()) if PROGRAM_ROOT.exists() else []:
        if not folder.is_dir() or not (folder/'agent_control.sqlite3').is_file() or folder.is_symlink():continue
        try:
            p=StudioProgram(folder.name);s=p.summary();project=s['project']
            if not project:continue
            latest=json.loads(s['runs'][0]['inputs']) if s['runs'] else {}
            episode=latest.get('brief',{}).get('episode',latest.get('episode'))
            previews=0
            for output in p.store.outputs():
                try:
                    body=json.loads(json.loads(output['payload'])['summary'])
                    path=body.get('artifact',{}).get('path')
                    if path:
                        from .offline_media import media_path
                        previews+=int(media_path(p.store.path,path).is_file())
                except (AgentError,ValueError,TypeError):continue
            directors=[r for r in s['runs'] if next(t['agent'] for t in s['tasks'] if t['id']==r['task'])=='director']
            rows.append({'Project':project['title'],'ID':folder.name,'Format':'Film' if project['episodes']==1 else 'Series','Stage':next((t['agent']+' · '+t['state'] for t in s['tasks']),'Brief saved'),
                         'Current focus':('Episode '+str(episode)) if episode else ('Film' if project['episodes']==1 else 'Series development'),'Available media previews':previews,'Episodes':project['episodes'],'Director':directors[0]['state'] if directors else 'Not queued','Pending review':sum(t['state'] in ('Awaiting QC','QC recommended') for t in s['tasks']),
                         'Approved artifacts':sum(t['state']=='Approved' for t in s['tasks']),'Blockers':sum(r['state'] in ('Blocked','Failed') for r in s['runs'])})
        except (AgentError,ValueError):continue
    if rows:
        st.dataframe(rows,hide_index=True,width='stretch')
        for row in rows:
            st.button('Open '+row['Project'],key='producer_open_'+row['ID'],on_click=lambda id=row['ID']:st.session_state.update(producer_nav='Director Studio',producer_pending_project=id))
    else:st.info('Create or open a production in Director Studio.')
    st.caption('Persisted task counts only. Approval is not artistic acceptance; no estimated completion percentages.')

def references(c):
    st.subheader('Project references')
    with st.expander('Add multiple references'):
        files=st.file_uploader('Story, casting, location, audio or film references',type=sorted(e.lstrip('.') for e in EXTENSIONS),accept_multiple_files=True,key='producer_upload')
        category=st.selectbox('Category',CATEGORIES,key='producer_ref_category')
        notes=st.text_area('Reference notes (your observations)',key='producer_ref_notes')
        source=st.text_input('Source / ownership / authorization evidence',key='producer_ref_source')
        rights=st.selectbox('Identity rights',RIGHTS,key='producer_ref_rights')
        attest=st.checkbox('I confirm these rights; a reference is not permission to copy or clone',key='producer_ref_attest')
        if st.button('Save reference files',disabled=not files or not attest):
            def save():
                for f in files:c.refs.put(f.name,f.getvalue(),category,notes,source,rights)
            action(save)
    rows=c.refs.rows()
    if not rows:return
    selected=st.selectbox('Reference', [r['id'] for r in rows],format_func=lambda id:next(r['original_name']+' · v'+str(r['version']) for r in rows if r['id']==id),key='producer_ref_id')
    row=c.refs.get(selected)
    st.caption(f"{row['id']} · version {row['version']} · {row['status']} · {row['category']} · {row['rights']}")
    st.info(row['limitation'])
    try:
        file=c.refs.path(row)
        if row['extension'] in ('.png','.jpg','.jpeg','.webp'):st.image(str(file),width=360)
        elif row['extension'] in ('.wav','.mp3','.m4a'):st.audio(file.read_bytes())
        elif row['extension'] in ('.mp4','.mov','.webm'):st.video(file.read_bytes())
        if row['text']:st.text_area('Actual extracted text',row['text'],disabled=True,key='producer_ref_extract')
        st.download_button('Original reference',file.read_bytes(),file_name=row['original_name'])
    except AgentError as exc:st.error(str(exc))
    with st.expander('Reference history / replace / relabel / remove'):
        st.json([r for r in c.refs.rows(True) if r['id']==selected])
        newcategory=st.selectbox('New category',CATEGORIES,index=CATEGORIES.index(row['category']))
        newnotes=st.text_area('New notes',row['notes'])
        replacement=st.file_uploader('Replacement original',type=sorted(e.lstrip('.') for e in EXTENSIONS),key='producer_ref_replace')
        confirm=st.checkbox('Invalidate work that uses this reference version',key='producer_ref_invalidate')
        if st.button('Save reference metadata'):action(lambda:c.refs.update(selected,row['version'],confirm,category=newcategory,notes=newnotes))
        if st.button('Replace reference',disabled=replacement is None):action(lambda:c.refs.put(replacement.name,replacement.getvalue(),newcategory,newnotes,row['source'],row['rights'],id=selected,expected=row['version'],confirm_invalidation=confirm))
        if st.button('Archive reference'):action(lambda:c.refs.update(selected,row['version'],confirm,archived=True))

def director(c):
    st.header('Director Studio')
    p=c.p.summary()['project'];st.subheader(p['title'])
    c.collect()
    for message in c.conversation():
        with st.chat_message('user' if message['speaker']=='producer' else 'assistant'):
            st.caption(message['speaker']+' · '+message['created']);st.write(message['text'])
    text=st.chat_input('ডিরেক্টরকে আইডিয়া, প্রশ্ন বা সংশোধনের নির্দেশ দিন',key='producer_message')
    if text:action(lambda:c.say(text))
    st.caption('ডিভাইসের বাংলা dictation দিয়ে লিখতে পারেন। Media upload নিজে থেকে transcription বা পূর্ণ movie analysis করে না।')
    if st.button('Continue Director’s queued work',key='producer_tick'):action(lambda:c.p.tick(1))
    references(c)
    with st.expander('Director delegation / production progress'):
        approved=[]
        for row in c.desk():
            try:body=json.loads(row['output']['summary'])
            except ValueError:continue
            if row['agent']=='director' and row['state']=='Approved' and body.get('artifact_type')=='producer_director':approved.append(row)
        if approved:
            chosen=st.selectbox('Reviewed Director plan',[r['id'] for r in approved],key='producer_dispatch_task')
            invalidate=st.checkbox('Authorize this plan’s targeted changes to approved work',key='producer_dispatch_invalidate')
            if st.button('Continue approved Director plan'):action(lambda:c.dispatch(chosen,invalidate))
        else:st.info('A generated Director plan must pass independent QC and Producer review before delegation.')
        runs=c.p.engine.runs()
        if runs:st.dataframe([{k:r[k] for k in ('id','state','task_state','error')} for r in runs],hide_index=True)
        if runs:
            selected_run=st.selectbox('Interrupted / blocked run',[r['id'] for r in runs],key='producer_recovery_run')
            if st.button('Retry existing blocked / failed run'):action(lambda:c.p.engine.retry(selected_run))
            stopped=st.checkbox('Previous worker has stopped',key='producer_worker_stopped')
            if st.button('Recover stopped worker',disabled=not stopped):action(lambda:c.p.recover(selected_run,worker_stopped=stopped))
        st.caption('Missing local models/media resources appear as blockers; no hosted fallback or automatic downloads.')
    with st.expander('Recent production activity'):
        st.dataframe(c.store.history()[:30],hide_index=True)

def casting_desk(c,row):
    st.subheader('Casting identity lock')
    body=json.loads(row['output']['summary']);candidates=body['artifact'].get('records',[])
    st.caption('Identity approval does not certify acting, voice or chemistry. Actual media and independent review remain necessary.')
    if st.button('Ask Director to inspect this casting proposal'):action(lambda:c.casting.queue_review(row['id']))
    selected=st.multiselect('Selected candidates',[r['id'] for r in candidates],key='producer_cast_selected')
    with c.store.tx() as db:
        inspections=[dict(r) for r in db.execute('SELECT i.task,t.state FROM casting_inspections i JOIN tasks t ON t.id=i.task WHERE i.source=? AND i.revision=?',(row['id'],row['revision']))]
    if inspections:
        review=st.selectbox('Exact Director inspection',[r['task'] for r in inspections])
        reason=st.text_area('Producer casting approval reason',key='producer_cast_reason')
        recast=st.checkbox('Confirm recast and invalidate dependent shots',key='producer_recast')
        if st.button('Approve and lock actor identities'):action(lambda:c.casting.lock(row['id'],review,selected,reason,recast))
    with st.expander('Record independent visual / listening / performance observation'):
        criterion=st.selectbox('Evaluation criterion',['appearance','performance','voice','chemistry'])
        assets=[r for r in c.refs.rows() if not r['archived']]
        media=st.multiselect('Actual observed media',[r['id'] for r in assets])
        reviewer=st.text_input('Human reviewer name / expertise')
        observation=st.text_area('What was actually seen or heard; limitations')
        if st.button('Record human media observation'):action(lambda:c.casting.evaluate(row['id'],criterion,[{'id':r['id'],'version':r['version']} for r in assets if r['id'] in media],observation,reviewer))
    with c.store.tx() as db:st.json([dict(r) for r in db.execute('SELECT * FROM casting_evaluations WHERE task=?',(row['id'],))])

def desk(c):
    st.header('Approval Desk')
    rows=c.desk()
    if not rows:st.info('No generated deliverables yet.');return
    groups=c.policy();milestone=st.selectbox('Milestone',['All']+sorted(set(groups.values())),key='producer_milestone')
    visible=[r for r in rows if milestone=='All' or groups[r['agent']]==milestone]
    if not visible:st.info('No deliverables at this milestone.');return
    st.dataframe([{k:r[k] for k in ('id','agent','revision','state','stale')} for r in visible],hide_index=True)
    selected=st.selectbox('Review deliverable',[r['id'] for r in visible],format_func=lambda id:next(r['agent']+' · '+id[:10]+' · v'+str(r['revision']) for r in visible if r['id']==id),key='producer_review_task')
    row=next(r for r in visible if r['id']==selected)
    if row['stale']:st.error('Upstream source changed. Approval blocked; use targeted recovery.')
    with st.expander('View evidence / actual output',expanded=True):
        st.json(row['output'])
        try:
            body=json.loads(row['output']['summary']);artifact=body.get('artifact',{})
            if isinstance(body.get('formatted'),str):st.text(body['formatted'])
            if artifact.get('path'):
                from .offline_media import media_path
                media=media_path(c.store.path,artifact['path'])
                if media.is_file() and media.stat().st_size<=64*1024*1024:
                    if media.suffix.lower() in ('.mp4','.webm','.mov'):st.video(media.read_bytes())
                    elif media.suffix.lower() in ('.wav','.mp3','.m4a'):st.audio(media.read_bytes())
                    elif media.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):st.image(str(media))
                else:st.info('Media unavailable or exceeds bounded preview size.')
        except (AgentError,ValueError,OSError):st.info('Preview unavailable; inspect the recorded output and source status.')
    with st.expander('View previous versions'):
        st.json([json.loads(o['payload']) for o in c.store.outputs() if o['task']==selected and o['revision']<row['revision']])
    st.button('Open associated Director conversation',on_click=lambda:st.session_state.update(producer_nav='Director Studio'))
    reason=st.text_area('Review evidence / specific requested correction',key='producer_review_reason')
    human=st.checkbox('I am recording an actual independent QC assessment',key='producer_qc_attest')
    if st.button('Record independent QC recommendation',disabled=not human or row['agent']=='qc' or row['stale']):action(lambda:c.store.review(selected,row['revision'],'Recommend',reason,'qc'))
    reject_invalidation=st.checkbox('Confirm rejecting approved work will invalidate dependent assets',key='producer_reject_invalidate')
    a,b,d=st.columns(3)
    if a.button('Approve',disabled=row['stale'] or row['agent']=='casting'):action(lambda:c.approve_batch([(selected,row['revision'])],reason))
    if b.button('Request Changes',disabled=row['stale']):action(lambda:c.feedback(selected,row['revision'],'Request Changes',reason))
    if d.button('Reject',disabled=row['stale']):action(lambda:c.feedback(selected,row['revision'],'Reject',reason,reject_invalidation))
    if row['agent']=='casting':casting_desk(c,row)
    with st.expander('Milestone batch approval / gate grouping'):
        ready=[r for r in visible if not r['stale'] and r['agent']!='casting' and (r['state']=='QC recommended' or (r['agent']=='qc' and r['state']=='Awaiting QC'))]
        batch=st.multiselect('Inspected exact-version deliverables',[r['id'] for r in ready])
        if st.button('Approve selected milestone batch'):action(lambda:c.approve_batch([(r['id'],r['revision']) for r in ready if r['id'] in batch],reason))
        policy=st.text_area('Milestone group configuration (JSON)',json.dumps(groups,ensure_ascii=False,indent=2),key='producer_gate_policy')
        if st.button('Save milestone groups'):action(lambda:c.policy(json.loads(policy)))
        st.caption('Grouping never removes independent QC, source freshness or Producer authority.')

def show_producer_control(legacy):
    st.caption('Producer Control Center · Director-led production · 21 registered departments')
    nav=st.radio('Workspace',NAV,horizontal=True,key='producer_nav')
    if nav=='Dashboard Home':overview()
    elif nav in ('Director Studio','Approval Desk'):
        c=project_picker()
        if c:
            if nav=='Director Studio':director(c)
            else:desk(c)
        if nav=='Approval Desk':
            with st.expander('Existing channel draft approval and previews'):legacy('content')
    elif nav=='Channel Manager':
        legacy('channels')
        with st.expander('YouTube connection — read-only'):legacy('youtube')
    elif nav=='Growth & Analytics':legacy('marketing')
    if st.checkbox('Open advanced internal production tools',key='producer_advanced'):
        st.caption('Specialist operations and earlier workflows; production and artistic approval remain separate.')
        tool=st.selectbox('Internal workspace',['studio','agents','storyboard','video','ai','dashboard'],key='producer_advanced_tool')
        legacy(tool)
