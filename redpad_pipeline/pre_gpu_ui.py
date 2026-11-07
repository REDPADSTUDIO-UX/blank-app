"""Small additions to the existing owner workspace; no automatic inference/approval."""
import json
from uuid import uuid4
import streamlit as st
from .agents import AgentError

def story_bridge(program):
    from .story_bridge import StoryBridge,FIELDS
    bridge=StoryBridge(program)
    with st.expander('Staged season → approved episode production'):
        st.caption('Bible → character arcs → one outline at a time → compiled season → Director review → sequences → screenplay. Every output keeps existing QC/owner gates. No giant 30-episode model call.')
        stage=st.selectbox('Story development stage',list(FIELDS),key='bridge_stage')
        ep=st.number_input('Staged episode',1,program.summary()['project']['episodes'],1,key='bridge_episode')
        revision_task=None;targets=[]
        label='bridge:'+stage+(':'+str(ep) if stage in ('outline','sequences') else '')
        with program.store.tx() as db:linked=db.execute('SELECT run FROM studio_links WHERE label=?',(label,)).fetchone()
        if linked:
            run=next((r for r in program.engine.runs() if r['id']==linked[0]),None)
            task=next((t for t in program.store.tasks() if run and t['id']==run['task']),None)
            if task and task['state']=='Revision requested':
                revision_task=task['id'];output=next(o for o in program.store.outputs() if o['task']==task['id'] and o['revision']==task['revision'])
                prior=json.loads(json.loads(output['payload'])['summary'])['artifact']['records']
                targets=st.multiselect('Only these requested record IDs may change',[r.get('id',str(r.get('number',0))) for r in prior],key='bridge_targets')
        if st.button('Queue one bounded story stage',key='bridge_queue'):
            try:st.success('Queued: '+bridge.queue(stage,ep,task=revision_task,targets=targets))
            except AgentError as exc:st.error(str(exc))
        if st.button('Compile approved episode outlines without rewriting',key='bridge_compile'):
            try:st.success('Queued season compilation: '+bridge.compile_season())
            except AgentError as exc:st.error(str(exc))
        critic=st.selectbox('Episode critic',['director','qc'],key='bridge_critic_role')
        if st.button('Queue source-grounded episode criticism',key='bridge_critic'):
            try:st.success('Queued: '+bridge.queue_critic(ep,critic))
            except AgentError as exc:st.error(str(exc))
        st.caption('Existing execution and approval controls run/review these stages. Raw model prose is never replaced by the acceptance fixture.')

def preparation(program):
    from .production_execution import ProductionOps
    from .offline_audio import ENGINES,preflight
    ops=ProductionOps(program)
    with st.expander('Shared shot execution, dialogue handoff and audio readiness'):
        with program.store.tx() as db:packets=[dict(r) for r in db.execute('SELECT id,kind FROM production_packets ORDER BY rowid')]
        ep=st.number_input('Shared-shot episode',1,program.summary()['project']['episodes'],1,key='ops_episode')
        def tasks(roles):
            out={};runs={r['id']:r for r in program.engine.runs()}
            with program.store.tx() as db:links={r['label']:r['run'] for r in db.execute('SELECT * FROM studio_links')}
            for role in roles:
                key=('script:episode' if role=='script' else 'internal:'+role+':episode')+str(ep)
                if key not in links:raise AgentError('Approved internal source is missing: '+role)
                out[role]=runs[links[key]]['task']
            return out
        shot=st.text_input('Existing approved shot ID',key='ops_shot')
        if st.button('Compile shared shot from all approved departments',key='ops_compile'):
            try:st.json(ops.shot(tasks(['script','character','art','location','costume','storyboard','performance','cinematographer','motion']),shot))
            except AgentError as exc:st.error(str(exc))
        for p in packets:
            try:st.json(ops.packet(p['id']))
            except AgentError as exc:st.warning(str(exc))
        try:
            voice_tasks=tasks(['script','voice','character']);characters=program.current_output(voice_tasks['character'])['artifact']['records']
        except AgentError:voice_tasks=None;characters=[]
        if voice_tasks:
            from .offline_speech import PRESETS,STYLES
            presets={};styles={}
            for character in characters:
                presets[character['id']]=st.selectbox('Synthetic preset: '+character['name'],PRESETS,key='ops_preset_'+character['id'])
                styles[character['id']]=st.selectbox('Supported delivery style: '+character['name'],list(STYLES),key='ops_style_'+character['id'])
            version=st.text_input('Pronunciation rule version','bn-v1',key='ops_lexicon_version')
            raw_rules=st.text_area('Optional pronunciation rules, one word = spoken form per line',key='ops_lexicon_rules')
            if st.button('Bind screenplay dialogue to voice production automatically',key='ops_voice_compile'):
                try:
                    rules={}
                    for line in raw_rules.splitlines():
                        if not line.strip():continue
                        word,sep,spoken=line.partition('=')
                        if not sep or not word.strip() or not spoken.strip():raise AgentError('Each rule needs word = spoken form.')
                        rules[word.strip()]=spoken.strip()
                    st.json(ops.voice(voice_tasks,presets,rules,version,styles));st.rerun()
                except AgentError as exc:st.error(str(exc))
        voice_packets=[p['id'] for p in packets if p['kind']=='voice_execution']
        if voice_packets:
            chosen=st.selectbox('Approved-source dialogue packet',voice_packets,key='ops_voice_packet')
            if st.button('Queue its dialogue segments without copying text',key='ops_queue_voice'):
                try:st.json([ops.queue_speech(chosen,line['id']) for line in ops.packet(chosen)['lines']])
                except AgentError as exc:st.error(str(exc))
        audio=st.selectbox('Prospective offline music/SFX backend',list(ENGINES),key='ops_audio')
        if st.button('Inspect offline audio blockers',key='ops_audio_preflight'):st.json(preflight(audio))
        from .offline_vision import preflight as vision_preflight
        if st.button('Inspect local visual-critic blockers',key='ops_vision_preflight'):st.json(vision_preflight())
        images=[str(p.relative_to(program.root/'agent_media')) for pattern in ('*.png','*.jpg','*.jpeg') for p in (program.root/'agent_media').rglob(pattern) if p.is_file() and not p.is_symlink()]
        if images:
            selected=st.multiselect('Local images/decoded frames for bounded visual criticism',images,key='ops_vision_images')
            question=st.text_area('Specific visible question; findings remain unverified',key='ops_vision_question')
            role=st.selectbox('Visual critic',['director','qc','continuity'],key='ops_vision_role')
            sources=st.multiselect('Approved source tasks for this inspection',[t['id'] for t in program.store.tasks() if t['state']=='Approved'],key='ops_vision_sources')
            if st.button('Queue source-bound local visual inspection',key='ops_vision_queue'):
                try:
                    if not sources or not 1<=len(selected)<=3 or not question.strip():raise AgentError('Approved sources, 1–3 actual local images and a specific question required.')
                    st.success('Queued: '+program.engine.enqueue(role,{'operation':'offline_vision','request':{'images':selected,'question':question,'seed':42}},sources,mode='media'))
                except AgentError as exc:st.error(str(exc))
        st.caption('Model-specific image/voice/video controls remain in existing Studio panels. Music/SFX adapters are prospective until actual checkpoint/API/GPU inference succeeds; no licenses or weights are acquired here.')

def scene_drafting(program):
    from .episode_scenes import EpisodeScenes
    from .story_bridge import StoryBridge
    from .model_routing import ModelRoutes
    from .screenwriter import WritingError
    with st.expander('Bounded screenplay scenes — preserve raw output and assemble later'):
        ep=st.number_input('Scene-draft episode',1,program.summary()['project']['episodes'],1,key='draft_episode')
        version=st.text_input('Immutable scene-draft version','v1',key='draft_version')
        try:draft=EpisodeScenes(program,ep,version)
        except AgentError as exc:st.error(str(exc));return
        bridge=StoryBridge(program)
        try:
            story=bridge._linked('story');director=bridge._linked('director_story');seq=bridge._linked('bridge:sequences:'+str(ep))
            season=program.current_output(story)['artifact'];sequences=program.current_output(seq)['artifact']['records']
        except AgentError as exc:st.info(str(exc));return
        if not (draft.folder/'plan.json').exists():
            chars=[];specs=[]
            with st.form('scene_spec_plan'):
                for c in season['characters']:
                    chars.append({**c,'voice':st.text_input('Distinct speaking habit: '+c['name'],key='draft_voice_'+c['id'])})
                i=0
                for sequence in sequences:
                    for id in sequence['scene_ids']:
                        i+=1;st.caption('Approved sequence '+sequence['id']+' / scene '+id)
                        heading=st.text_input('INT./EXT. scene heading',key='draft_heading_'+id);location=st.text_input('Scene location',key='draft_location_'+id)
                        seconds=st.number_input('Scene budget in seconds',1,600,int(sequence['seconds']//len(sequence['scene_ids'])),key='draft_seconds_'+id)
                        specs.append({'id':id,'number':i,'heading':heading,'location':location,'time':'approved episode chronology','seconds':seconds,
                            'objective':sequence['objective'],'obstacle':sequence['obstacle'],'turn':sequence['turn'],'consequence':sequence['consequence'],
                            'subtext':st.text_input('Playable subtext',key='draft_subtext_'+id),'performance':st.text_input('Performance instruction',key='draft_performance_'+id),
                            'transition':'cut','action_seconds':seconds/2,'pause_seconds':min(2,seconds/4),'continuity':[str(season['episodes'][ep-1].get('state_before',{}))],
                            'sound':{'music':st.text_input('Music intention / intentional silence',key='draft_music_'+id),'sfx':st.text_input('SFX intention / intentional absence',key='draft_sfx_'+id)}})
                setup=st.multiselect('Scenes that set up the episode ending',[s['id'] for s in specs],key='draft_ending_setups')
                create=st.form_submit_button('Save this immutable structural plan')
            if create:
                try:st.json(draft.create({'story':story,'director':director},specs,chars,setup));st.rerun()
                except (AgentError,ValueError) as exc:st.error(str(exc))
            return
        try:plan=draft.plan()
        except AgentError as exc:st.error(str(exc));return
        st.json(plan);scene=st.selectbox('One scene to generate',[s['id'] for s in plan['scene_specs']],key='draft_scene')
        path=draft.folder/('scene_'+scene+'.json')
        if path.exists() and json.loads(path.read_text()).get('status')=='failed':
            if st.button('Archive failed stopped attempt for one explicit retry',key='draft_retry'):
                try:
                    from .staged_writing import StagedDraft
                    StagedDraft(draft.folder).retry('scene_'+scene);st.success('Failed raw response retained; retry is not automatically executed.')
                except WritingError as exc:st.error(str(exc))
        names=[m['name'] for m in ModelRoutes(program.store).models() if m['approved']]
        if names:
            model=st.selectbox('Already approved local writing candidate',names,key='draft_model')
            if st.button('Generate only this scene; retain original response',key='draft_run'):
                try:st.json(draft.run_scene(scene,model=model))
                except (AgentError,WritingError,OSError,ValueError) as exc:st.error(str(exc))
        else:st.info('No approved installed writing candidate here. Planning remains available; no weights are downloaded.')
        if st.button('Assemble unchanged completed scenes for QC/owner review',key='draft_compile'):
            try:st.success('Queued: '+draft.compile())
            except (AgentError,OSError,ValueError) as exc:st.error(str(exc))
        for path in sorted(draft.folder.glob('scene_*.json')):
            st.json(json.loads(path.read_text()))
        st.caption('Token limits, raw failures and model-quality weaknesses remain visible. Assembly is software, not a new inference or artistic pass.')

def deliveries(program):
    from .delivery import Delivery
    delivery=Delivery(program)
    with st.expander('Genuine assets → approved EDL → review delivery'):
        upload=st.file_uploader('Import an owned MP4/MOV or PCM WAV into this isolated project',['mp4','mov','wav'],key='delivery_upload')
        owner=st.text_input('Asset owner / authorized reviewer',key='delivery_owner');rights=st.text_area('Rights and source attestation',key='delivery_rights')
        confirm=st.checkbox('I authorize this asset import and attest usage rights',key='delivery_rights_confirm')
        if st.button('Save and inspect genuine imported asset',key='delivery_import'):
            try:
                if upload is None or upload.size>100*1024*1024 or not confirm or not owner.strip() or not rights.strip():raise AgentError('Bounded actual asset and explicit owner/rights confirmation required.')
                root=program.root/'agent_media/imports'
                if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe import folder.')
                root.mkdir(parents=True,exist_ok=True);name=uuid4().hex+('.wav' if upload.name.lower().endswith('.wav') else '.mp4')
                (root/name).write_bytes(upload.getvalue());st.success('Receipt: '+delivery.register('imports/'+name,owner,rights,True))
            except (AgentError,OSError) as exc:st.error(str(exc))
        with program.store.tx() as db:ids=[r[0] for r in db.execute('SELECT id FROM delivery_assets')]
        valid={}
        for id in ids:
            try:valid[id]=delivery.asset(id)
            except AgentError as exc:st.warning(str(exc))
        approved=[t for t in program.store.tasks() if t['agent']=='editing' and t['state']=='Approved']
        if not approved:return
        task=st.selectbox('Approved edit plan / bound EDL',[t['id'] for t in approved],key='delivery_plan')
        try:rows=program.current_output(task,'editing')['artifact']['records']
        except AgentError as exc:st.error(str(exc));return
        videos=[i for i,a in valid.items() if any(s['codec_type']=='video' for s in a['inspection']['streams'])]
        audios=[i for i,a in valid.items() if any(s['codec_type']=='audio' for s in a['inspection']['streams'])]
        if videos and audios:
            bindings={};durations={}
            for row in rows:
                st.caption('Shot '+row['shot'])
                bindings[row['shot']]={'video':st.selectbox('Video receipt',videos,key='delivery_v_'+row['id']),
                    'audio':st.selectbox('Audio receipt',audios,key='delivery_a_'+row['id'])}
                durations[row['shot']]=st.number_input('Explicit cut duration',.01,300.,float(row['seconds']),key='delivery_t_'+row['id'])
            if st.button('Queue bound EDL for fresh QC and owner approval',key='delivery_bind'):
                try:st.success('Queued: '+delivery.queue_edl(task,bindings,durations))
                except AgentError as exc:st.error(str(exc))
        if rows and all('asset_receipts' in r for r in rows):
            mapping={r[field]:r['asset_receipts'][field] for r in rows for field in ('video','audio')}
            if st.button('Queue approved receipt-bound review render',key='delivery_render'):
                try:st.success('Queued: '+program.engine.enqueue('editing',{'operation':'assemble_delivery','editing_task':task,'receipts':mapping},[task],mode='media',idempotency_key='delivery-render:'+task))
                except AgentError as exc:st.error(str(exc))
        st.caption('Hard cuts and source color only. Unsupported grading/VFX/fades block explicitly. Imported provenance is owner-attested; actual neural origin and artistic approval are never inferred.')

def feedback(program):
    from .production_execution import ProductionOps
    ops=ProductionOps(program)
    with st.expander('Versioned expert feedback — future training requires separate approval'):
        outputs=program.store.outputs()
        if outputs:
            ids=list(dict.fromkeys(o['task'] for o in outputs));tid=st.selectbox('Exact reviewed output',ids,key='feedback_task')
            task=next(t for t in program.store.tasks() if t['id']==tid)
            owner=st.text_input('Actual reviewer name',key='feedback_reviewer');expertise=st.text_input('Relevant professional expertise',key='feedback_expertise')
            category=st.selectbox('Review department',['creative','visual','listening','editing','technical'],key='feedback_category')
            quote=st.text_area('Exact source quotation (text feedback)',key='feedback_quote');observation=st.text_area('Observed issue / preferred correction',key='feedback_observation')
            output=next(o for o in outputs if o['task']==tid and o['revision']==task['revision'])
            body=json.loads(json.loads(output['payload'])['summary']);anchor={'quote':quote}
            media=body.get('artifact',{}).get('path')
            if media and category in ('visual','listening','editing'):
                from .offline_media import media_path,sha
                try:
                    path=media_path(program.store.path,media);anchor={'asset':media,'sha256':sha(path)}
                    if path.suffix.lower() in ('.png','.jpg','.jpeg'):
                        st.image(str(path));anchor['region']=[st.number_input('Region '+label,0.,1.,default,key='feedback_region_'+label) for label,default in [('left',0.),('top',0.),('right',1.),('bottom',1.)]]
                    else:
                        from .specialist_inspection import inspect_clip
                        duration=inspect_clip(media,program.store.path)['duration']
                        if path.suffix.lower()=='.wav':st.audio(str(path))
                        else:st.video(str(path))
                        anchor['seconds']=st.number_input('Observed media timestamp (seconds)',0.,float(duration),0.,key='feedback_timestamp')
                except AgentError as exc:st.error(str(exc))
            decision=st.selectbox('Reviewer finding',['uncertain','correct','reject','prefer'],key='feedback_decision')
            consent=st.checkbox('May retain this feedback for a future separately approved training dataset',key='feedback_consent')
            actual=st.checkbox('This feedback was actually supplied by the named reviewer',key='feedback_actual')
            if st.button('Record attributed feedback without granting approval',key='feedback_save'):
                try:
                    if not actual:raise AgentError('Actual reviewer confirmation required; no fabricated feedback.')
                    st.json(ops.feedback(tid,task['revision'],owner,expertise,category,anchor,observation,decision,dataset_consent=consent))
                except AgentError as exc:st.error(str(exc))
        st.download_button('Export versioned feedback and consent ledger',json.dumps(ops.feedback_export(),ensure_ascii=False,indent=2),'studio-feedback.json',key='feedback_export')
