"""Unified owner workspace with three creative roles; advanced agents retained."""
import hashlib,json,subprocess
from pathlib import Path
import streamlit as st
from .agents import AGENTS,AgentError
from .studio_program import StudioProgram,PROGRAM_ROOT,ROOT,WORKSTREAMS
from .screenwriter import WritingError
from .local_ollama_session import local_cpu_session


def show_studio_program():
    st.header('REDPAD • Film Studio')
    st.caption('Director • Story • Script সামনে; ১৭টি specialist একই project-এর versioned workflow-এ। Planning, AI inference ও artistic approval আলাদা।')
    from .filmmaking_ui import show_knowledge,show_series
    from .professional_ui import show_summary,show_trials
    show_summary()
    show_knowledge()
    project_id=st.text_input('Studio project ID','redpad-film',key='master_project_id')
    left,right=st.columns(2)
    with left:
        if st.button('Open saved Studio project',key='master_open'):
            try:
                program=StudioProgram(project_id)
                if program.summary()['project'] is None:raise AgentError('Project not created yet.')
                st.session_state['master_open_id']=project_id
            except AgentError as exc:st.error(str(exc))
    with st.expander('Create original project'):
        with st.form('master_create'):
            title=st.text_input('Film / series title',key='master_title')
            brief=st.text_area('Original creative brief',key='master_brief')
            episodes=st.number_input('Planned episode count',1,100,30,key='master_episodes')
            seconds=st.number_input('Target episode / film seconds',180,4200,300,key='master_seconds')
            create=st.form_submit_button('Create unified project')
        if create:
            try:StudioProgram(project_id).create(title,brief,episodes,seconds);st.session_state['master_open_id']=project_id;st.rerun()
            except AgentError as exc:st.error(str(exc))
    if 'master_open_id' not in st.session_state:
        st.info('একটি project খুলুন বা তৈরি করুন। Models/media নিজে থেকে download বা generate হবে না।');return
    program=StudioProgram(st.session_state['master_open_id']);summary=program.summary()
    if summary['project'] is None:st.error('Saved project missing.');return
    st.subheader(summary['project']['title'])
    area=st.radio('Filmmaking workspace',['Creative Studio','Production Studio','Post-Production Studio','Project Management','Admin / Advanced'],horizontal=True,key='master_nav')
    if area=='Creative Studio':
        role=st.radio('Creative partner',['director','story','script'],horizontal=True,key='master_creative_role')
        if role=='story':show_series(program)
        for note in summary['owner_notes']:
            if note['role']==role:st.markdown('**Owner note:** '+note['text'])
        with st.form('master_note'):
            note=st.text_area('Creative instruction / revision note',key='master_note_text')
            save=st.form_submit_button('Save owner instruction')
        if save:
            try:program.note(role,note);st.rerun()
            except AgentError as exc:st.error(str(exc))
        st.caption('Notes are owner instructions, not AI replies. Generated output appears only after real execution; accepted source stages remain locked.')
        stage_options={'story':['story'],'script':['script'],'director':['director_story','director_script']}[role]
        stage=st.selectbox('Creative workflow step',stage_options,key='master_stage')
        episode=st.number_input('Episode under development',1,summary['project']['episodes'],1,key='master_episode')
        if st.button('Queue next creative task',key='master_queue_creative'):
            try:st.success('Queued run: '+program.queue_creative(stage,episode));st.rerun()
            except AgentError as exc:st.error(str(exc))
        managed=st.checkbox('Use restored development CPU runtime',key='master_creative_cpu') if (ROOT/'phase3_models/ollama-runtime/bin/ollama').exists() else False
        if st.button('Run one queued creative/internal task',key='master_tick'):
            try:
                if managed:
                    with local_cpu_session():result=program.tick()
                else:result=program.tick()
                st.json(result)
            except (AgentError,WritingError) as exc:st.error(str(exc))
        st.caption('Long series: use the per-episode draft architecture under Story. One giant season call remains blocked. Validated draft state is separate from an approved complete season and production handoff; full creative acceptance is pending.')
        st.dataframe(summary['runs'],hide_index=True)
        for output in program.store.outputs():
            st.json(json.loads(json.loads(output['payload'])['summary']))
    elif area=='Production Studio':
        st.caption('Internal tasks bind the approved screenplay and Director review automatically; no copy-paste between departments.')
        episode=st.number_input('Production episode',1,summary['project']['episodes'],1,key='master_production_episode')
        if st.button('Coordinate all 17 internal specialists',key='master_queue_internal'):
            try:st.json(program.queue_specialists(episode));st.rerun()
            except AgentError as exc:st.error(str(exc))
        st.dataframe(summary['hierarchy'],hide_index=True)
        _media_panel(program)
    elif area=='Post-Production Studio':
        from .offline_speech import preflight,PRESETS,STYLES,synthesize
        if st.button('Inspect offline speech readiness',key='master_speech_status'):st.json(preflight())
        preset=st.selectbox('Synthetic Bengali voice preset',PRESETS,key='master_preset')
        style=st.selectbox('Speech style',list(STYLES),key='master_style')
        text=st.text_area('Short Bengali speech test',key='master_speech_text')
        if st.button('Run approved local speech test',key='master_speech'):
            try:st.json(synthesize({'preset':preset,'style':style,'text':text},program.store.path))
            except (AgentError,WritingError) as exc:st.error(str(exc))
        st.caption('Bangladeshi pronunciation, emotion and voice consistency require listening review. Music/SFX sketches are procedural unless an actual neural backend is identified. Editing still requires approved real assets in the existing Quality Studio.')
        media=program.root/'agent_media'
        for evidence in sorted(media.glob('offline*/*/evidence.json'))[-10:]:
            record=json.loads(evidence.read_text());st.json(record)
            if record.get('technical_output_validated') or record.get('state')=='technical_output_validated':
                clip=evidence.parent/('speech.wav' if 'offline_speech' in str(evidence) else 'clip.mp4')
                if clip.is_file():
                    if clip.suffix=='.wav':st.audio(str(clip))
                    else:st.video(str(clip))
                    st.caption('Technical output only; artistic/owner approval not inferred.')
    elif area=='Project Management':
        show_trials(program)
        st.dataframe(summary['runs'],hide_index=True);st.dataframe(summary['workstreams'],hide_index=True)
        tasks=program.store.tasks()
        if tasks:
            task_id=st.selectbox('Project approval / revision task',[t['id'] for t in tasks],key='master_review_task')
            task=next(t for t in tasks if t['id']==task_id);st.json(task)
            with st.form('master_review'):
                decision=st.selectbox('Explicit project review',['Recommend','Reject','Approve','Request revision'],key='master_decision')
                evidence=st.text_area('Exact review evidence / targeted correction',key='master_review_evidence')
                confirm=st.checkbox('Record this explicit owner action; QC recommendation is manual and is not model-certified',key='master_review_confirm')
                save=st.form_submit_button('Record current-version review')
            if save:
                try:
                    if not confirm:raise AgentError('Explicit review confirmation required.')
                    program.store.review(task_id,task['revision'],decision,evidence,'qc' if decision in ('Recommend','Reject') else 'owner');st.rerun()
                except AgentError as exc:st.error(str(exc))
        retryable=[r for r in summary['runs'] if r['state'] in ('Failed','Blocked')]
        if retryable:
            retry_id=st.selectbox('Failed / blocked project run',[r['id'] for r in retryable],key='master_retry_run')
            if st.button('Retry after resolving the reported blocker',key='master_retry'):
                try:program.engine.retry(retry_id);st.rerun()
                except AgentError as exc:st.error(str(exc))
        running=[r for r in summary['runs'] if r['state']=='Running']
        if running:
            rid=st.selectbox('Interrupted project run',[r['id'] for r in running],key='master_recover_run')
            stopped=st.checkbox('Previous worker is stopped',key='master_recover_stopped')
            if st.button('Recover stopped run',key='master_recover'):
                try:program.recover(rid,stopped);st.rerun()
                except AgentError as exc:st.error(str(exc))
        if st.button('Save resumable project checkpoint',key='master_checkpoint'):
            try:
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
                st.json(program.checkpoint(commit,{'human_review_completed':False,'note':'No cinematic acceptance inferred from software status.'}))
            except (AgentError,subprocess.SubprocessError,OSError) as exc:st.error('Checkpoint requires a valid source revision and readable development store.')
        st.download_button('Export project ledger',json.dumps(summary,ensure_ascii=False,indent=2),'studio-project-ledger.json',key='master_export')
    else:
        st.dataframe([{'agent':key,**program.store.status(key)} for key in AGENTS],hide_index=True)
        from .model_routing_ui import show_model_routes
        show_model_routes(program.store,prefix='master_'+program.project_id+'_')
        st.caption('Existing AI Agents tab retains all department workspaces. No GPU/cloud account is created by these controls.')


def _media_panel(program):
    from .offline_media import CATALOG,preflight,generate,approve_reference
    engine=st.selectbox('Offline generation engine',list(CATALOG),key='master_video_engine')
    st.json(CATALOG[engine])
    if st.button('Inspect selected offline engine',key='master_video_status'):st.json(preflight(engine))
    uploaded=st.file_uploader('Fictional character / scene reference',['png','jpg','jpeg'],key='master_reference_upload')
    if uploaded is not None and st.button('Save unreviewed reference',key='master_reference_save'):
        from io import BytesIO
        from PIL import Image
        raw=uploaded.getvalue()
        try:
            if len(raw)>10*1024*1024:raise AgentError('Reference exceeds 10 MB.')
            with Image.open(BytesIO(raw)) as im:
                if im.width*im.height>20_000_000:raise AgentError('Reference image exceeds pixel bound.')
                suffix='.png' if im.format=='PNG' else '.jpg';im.verify()
            folder=program.root/'agent_media/references'
            if any(p.is_symlink() for p in (folder,*folder.parents)):raise AgentError('Unsafe reference path.')
            folder.mkdir(parents=True,exist_ok=True)
            path=folder/(hashlib.sha256(raw).hexdigest()+suffix);path.write_bytes(raw);st.success('Unreviewed local reference: references/'+path.name)
        except (AgentError,OSError,ValueError,Image.DecompressionBombError) as exc:st.error('Reference is invalid or exceeds supported limits.')
    reference=st.text_input('Local reference path (relative to this project media)','references/reference.png',key='master_reference')
    with st.form('master_reference_review'):
        reviewer=st.text_input('Reference reviewer',key='master_reference_reviewer')
        rights=st.text_input('Fictional/reference usage rights note',key='master_reference_rights')
        confirm=st.checkbox('I reviewed and approve this exact reference for production testing',key='master_reference_confirm')
        save=st.form_submit_button('Approve current reference hash')
    if save:
        try:st.json(approve_reference(program.store.path,reference,reviewer,rights,confirm))
        except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
    mode=st.selectbox('Supported generation mode',CATALOG[engine]['modes'],key='master_video_mode')
    prompt=st.text_area('Shot prompt (SVD stores this as editorial guidance only)',key='master_video_prompt')
    if st.button('Generate one approved offline micro-clip',key='master_video_generate'):
        width,height,frames={'wan-local':(1280,704,81),'ltx-local':(704,480,49),'local-svd':(1024,576,25)}[engine]
        request=dict(mode=mode,prompt=prompt,reference=reference,width=width,height=height,frames=frames,fps=CATALOG[engine]['fps'],steps=CATALOG[engine]['steps'],seed=42)
        try:st.json(generate(engine,request,program.store.path))
        except (AgentError,WritingError) as exc:st.error(str(exc))
