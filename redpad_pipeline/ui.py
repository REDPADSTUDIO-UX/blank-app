"""Additive Streamlit production controls; all live calls require explicit spend approval."""
import json
import hashlib
import sqlite3
import threading
from contextlib import closing
from pathlib import Path
import streamlit as st
from .models import Config, ProductionError, estimate_usd, mock_plan, digest
from .video_models import VIDEO_MODELS, AUTO, resolve_model, video_cost_usd, catalog_rows, OFFICIAL_PRICING, OFFICIAL_INPUTS
from .providers import LiveGateway
from .media import MockGateway, shaped_font
from redpad_video_studio import ffmpeg_binary
from .engine import create_job, initialize, load_state, run_job


def launch(db_path, root, config):
    state = load_state(root)
    if state['mode'] == 'live':
        plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
        gateway = LiveGateway(config, plan['seconds'], state['approved_usd'],
                              video_model=plan.get('video_model', 'gen4.5'))
    else:
        gateway = MockGateway()
    worker = threading.Thread(target=run_job, args=(db_path, root, gateway), daemon=True,
                              name='redpad-production-' + state['job_id'][:8])
    worker.start()


def show_production_studio(db_path, media_dir, get_secret):
    st.subheader('🎥 Multi-Model AI Video Production — beta')
    st.caption('Topic → Bangla script + English translation → moving scenes → narration → music/SFX → bilingual MP4 → human review')
    initialize(db_path)
    config = Config.load(get_secret)
    with closing(sqlite3.connect(db_path)) as db:
        channels = db.execute('SELECT id,name FROM channels ORDER BY id DESC').fetchall()
    st.write('Secure configuration status — presence only; no provider request')
    badges = st.columns(3)
    badges[0].metric('Runway secret', 'Present' if config.runway_key else 'Not available here')
    badges[1].metric('Script secret', 'Present' if config.openai_key else 'Not available here')
    badges[2].metric('Bangla voice credentials', 'Present' if config.azure_key and config.azure_region else 'Not available here')
    st.caption('Presence does not prove validity, credit balance or model access. Codespaces secrets can be checked only inside that Codespace.')
    with st.expander('Verified multi-model catalog and estimated costs', expanded=False):
        st.dataframe(catalog_rows(), hide_index=True, width='stretch')
        st.markdown(f'[Official API pricing]({OFFICIAL_PRICING}) · [Official input formats]({OFFICIAL_INPUTS})')
        st.caption('All listed models use the Runway Developer API. Cheapest means the lowest listed 720p text-to-video price; no paid fallback retries.')
    if not channels:
        st.info('No channel yet. Start a clearly labelled demo channel below or add your own channel in Channel Manager.')
        if st.button('🧪 Start free demo workspace', key='prod_demo_workspace'):
            with closing(sqlite3.connect(db_path)) as db, db:
                db.execute("INSERT INTO channels(name,platform,niche,videos_per_day,publish_time) VALUES (?,?,?,?,?)",
                           ('REDPAD Demo (Mock)', 'YouTube', 'Horror demo — no publishing', 0, '18:00'))
            st.rerun()
        return
    mode = st.radio('Production mode', ['Offline mock test — free', 'Live AI — paid providers'], key='prod_mode')
    live = mode.startswith('Live')
    if live:
        st.warning('Live requires OpenAI, Azure Speech and Runway Developer API credits. Available model options include Seedance, WAN, Kling, Grok and Runway; they are accessed via the Runway API, not separate vendor accounts. No free generation is promised.')
        required = [('RUNWAY_API_KEY', config.runway_key), ('OPENAI_API_KEY', config.openai_key),
                    ('AZURE_SPEECH_KEY', config.azure_key), ('AZURE_SPEECH_REGION', config.azure_region)]
        missing = [name for name, value in required if not value]
        if missing:
            st.info('Missing secure configuration: ' + ', '.join(missing))
        if not config.paid_enabled:
            st.info('Owner switch REDPAD_ENABLE_PAID_GENERATION is off. Paid calls cannot run.')
    else:
        st.info('MOCK ONLY: moving test patterns + synthetic tone. No real AI footage or spoken Bangla. Tests editing, captions, downloads and approval without API calls. The sample story is a fixed fixture, not a generated response to your topic.')
    channel_id = st.selectbox('Production channel', [row[0] for row in channels],
                               format_func=lambda cid: next(row[1] for row in channels if row[0] == cid), key='prod_channel')
    source_type = (st.radio('Production script source',
                            ['Topic or script', 'Approved Storyboard'],
                            key='prod_source') if live else 'Topic or script')
    storyboard_id = None
    storyboard_preview = None
    if source_type == 'Approved Storyboard':
        from .storyboard import initialize as initialize_storyboard, load_board
        initialize_storyboard(db_path)
        with closing(sqlite3.connect(db_path)) as db:
            approved = db.execute("""SELECT c.id,c.title FROM content c
                JOIN storyboards s ON s.content_id=c.id
                WHERE c.channel_id=? AND s.review_status='Approved'
                ORDER BY c.id DESC""", (channel_id,)).fetchall()
        if approved:
            storyboard_id = st.selectbox(
                'Approved storyboard to produce',
                [row[0] for row in approved],
                format_func=lambda cid: next(f'#{row[0]} · {row[1]}' for row in approved if row[0] == cid),
                key='prod_board_id')
            storyboard_preview = load_board(db_path, storyboard_id)
        else:
            st.warning('No approved storyboard exists for this channel. Approve one in Storyboard Studio first.')
    topic = st.text_area('Topic / story / existing Bangla script', max_chars=6000,
                         disabled=source_type == 'Approved Storyboard', key='prod_topic')
    duration_options = [30, 60, 120, 300, 600]
    if storyboard_preview:
        storyboard_total = sum(s['seconds'] for s in storyboard_preview['shots'])
        if 30 <= storyboard_total <= 600:
            duration_options = [storyboard_total]
    seconds = st.selectbox('Finished video length (seconds)', duration_options, key='prod_seconds')
    ratio_options = ['720:1280', '1280:720']
    selected_ratio = (0 if storyboard_preview and storyboard_preview['ratio'] == '9:16' else 1)
    ratio = st.selectbox('Production aspect ratio', ratio_options,
                         index=selected_ratio if storyboard_preview else 0,
                         disabled=source_type == 'Approved Storyboard', key='prod_ratio')
    voice = st.selectbox('Production Bangla voice', ['bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural'], key='prod_voice')
    model_choice = st.selectbox('Video generation model',
        [AUTO] + list(VIDEO_MODELS),
        format_func=lambda value: ('Automatic — lowest estimated cost' if value == AUTO
                        else VIDEO_MODELS[value]['label']), key='prod_video_model')
    video_model = resolve_model(model_choice)
    storyboard_plan = None
    storyboard_error = ''
    if source_type == 'Approved Storyboard':
        if storyboard_id is None:
            storyboard_error = 'First approve a storyboard in Storyboard Studio.'
        else:
            try:
                from .storyboard_live import approved_to_plan
                storyboard_plan = approved_to_plan(db_path, media_dir, storyboard_id,
                                                    voice, video_model)
                refs = sum(bool(s.get('image_key')) for s in storyboard_plan['scenes'])
                st.success(f"Approved storyboard ready: {len(storyboard_plan['scenes'])} exact shots, "
                           f"{storyboard_plan['seconds']} seconds, {refs} first-frame reference images.")
                st.caption('Only approved reference images are sent to image-to-video, '
                           'and only with Gen-4.5. Other shots use text-to-video. '
                           'No image or generation is submitted until explicit paid approval.')
            except ProductionError as error:
                storyboard_error = str(error)
        if storyboard_error:
            st.warning('Storyboard not ready for Live Production: ' + storyboard_error)
    st.caption(f"Selected model: {VIDEO_MODELS[video_model]['label']} · "
               f"Estimated 720p video only: US${video_cost_usd(seconds, video_model):.2f} for {seconds}s. "
               "No provider call has been made. Model pricing checked 26 Oct 2026.")
    music = st.file_uploader('Optional licensed background music (MP3/WAV, max 20 MB)', type=['mp3', 'wav'], key='prod_music')
    oversized_music = bool(music and music.size > 20 * 1024 * 1024)
    if oversized_music:
        st.error('Music file exceeds the 20 MB limit.')
    quote = estimate_usd(seconds, video_model)
    agreed = False
    fingerprint = digest(json.dumps([
        topic if source_type == 'Topic or script' else 'approved storyboard',
        source_type, storyboard_id, storyboard_plan.get('source_storyboard') if storyboard_plan else None,
        seconds, ratio, voice, channel_id, model_choice, video_model,
        hashlib.sha256(music.getbuffer()).hexdigest() if music and not oversized_music else ''
    ]))
    if st.session_state.get('prod_consent_fingerprint') != fingerprint or st.session_state.pop('prod_reset_consent', False):
        st.session_state['prod_consent'] = False
        st.session_state['prod_consent_fingerprint'] = fingerprint
    if live:
        st.write(f'Planning estimate: US${quote:.2f} per job; video alone US${video_cost_usd(seconds, video_model):.2f}. Taxes, reruns and pricing changes can increase actual billing. Checked 26 Oct 2026.')
        if config.max_job_usd < quote:
            st.info(f'Owner job limit REDPAD_MAX_JOB_USD must be at least US${quote:.2f}.')
        st.caption('Automatic selection resolves ONCE before approval; it is not an automatic paid retry or provider-failure fallback. Quote is a local guard, not a provider invoice cap. Use provider billing controls.')
        agreed = st.checkbox(f'I authorize this {seconds}s job at the displayed US${quote:.2f} estimate.', key='prod_consent')
    ready_content = bool(storyboard_plan) if source_type == 'Approved Storyboard' else bool(topic.strip())
    enabled = ready_content and not oversized_music and (not live or (agreed and config.paid_enabled and config.max_job_usd >= quote
              and all((config.runway_key, config.azure_key, config.azure_region, config.openai_key))))
    if st.button('🎬 Create AI production job' if live else '🧪 Create offline production test', disabled=not enabled, key='prod_create'):
        try:
            if music and music.size > 20 * 1024 * 1024:
                raise ProductionError('Music file exceeds the 20 MB limit.')
            shaped_font(20)
            if not ffmpeg_binary():
                raise ProductionError('FFmpeg is unavailable.')
            if live:
                gateway = LiveGateway(config, seconds, quote, video_model=video_model)
                if source_type == 'Approved Storyboard':
                    from .storyboard_live import approved_to_plan
                    plan = approved_to_plan(db_path, media_dir, storyboard_id, voice, video_model)
                else:
                    with st.spinner('Planning the film and translating subtitles…'):
                        plan = gateway.plan(topic, seconds, ratio, voice)
                        plan['video_model'] = video_model
            else:
                plan = mock_plan(topic, seconds, ratio, voice)
                plan['video_model'] = video_model
            root = create_job(db_path, media_dir, channel_id, plan, 'live' if live else 'mock', quote if live else 0)
            if music:
                (root / 'music.upload').write_bytes(music.getvalue())
            launch(db_path, root, config)
            st.session_state['prod_selected'] = root.name
            st.session_state['prod_reset_consent'] = True
            st.rerun()
        except ProductionError as error:
            st.error(str(error))
        except Exception:
            st.error('Could not start production. Check local storage and provider configuration.')
    st.subheader('Production jobs')
    with closing(sqlite3.connect(db_path)) as db:
        jobs = db.execute('SELECT job_id,content_id,mode,job_dir FROM production_jobs ORDER BY created_at DESC, rowid DESC LIMIT 50').fetchall()
    if not jobs:
        return
    names = [row[0] for row in jobs]
    selected = st.selectbox('Saved production job', names,
        format_func=lambda job_id: next(f'#{r[1]} · {r[2]} · {r[0][:8]}' for r in jobs if r[0] == job_id), key='prod_selected')
    root = Path(next(row[3] for row in jobs if row[0] == selected))

    @st.fragment(run_every=4)
    def job_panel():
        try:
            state = load_state(root)
        except (OSError, ValueError):
            st.error('Production checkpoint is missing or invalid.')
            return
        done = sum(bool(scene.get('edited')) for scene in state['scenes'])
        st.write(f"Status: {state['phase']} · {done}/{len(state['scenes'])} scenes edited · {state['mode'].upper()}")
        st.progress(done / max(1, len(state['scenes'])))
        if state['error']:
            st.warning(state['error'])
        plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
        with st.expander('Scene plan and narration'):
            st.json(plan)
        if state['phase'] != 'complete':
            st.caption('Resume reuses existing audio, clips and saved task IDs. Uncertain billed submissions require reconciliation, not blind regeneration.')
            if st.button('▶ Resume / recover worker', key='prod_resume_' + selected):
                try:
                    launch(db_path, root, Config.load(get_secret))
                    st.success('Worker started; an existing worker keeps its exclusive job lock.')
                except ProductionError as error:
                    st.error(str(error))
        if state['phase'] == 'complete':
            output = root / 'final.mp4'
            with closing(sqlite3.connect(db_path)) as db:
                current = db.execute('SELECT script,status FROM content WHERE id=?', (state['content_id'],)).fetchone()
            from .models import narration
            if not current or current[0] != narration(plan):
                st.warning('This is an older script version. Create a new production job for the current draft.')
            if output.is_file():
                if state['mode'] == 'mock':
                    st.warning('OFFLINE MOCK OUTPUT — not generative AI footage or a Bangla voice test.')
                st.video(output.read_bytes())
                st.download_button('Download production MP4', output.read_bytes(), file_name=f'redpad-{selected[:8]}.mp4', mime='video/mp4', key='prod_mp4_' + selected)
                for lang in ('bn', 'en'):
                    path = root / f'subtitles.{lang}.srt'
                    st.download_button(f'Download {lang.upper()} subtitles', path.read_bytes(), file_name=path.name,
                                       mime='application/x-subrip', key='prod_srt_' + lang + selected)
                st.info(f"Draft status: {current[1] if current else 'missing'}. Open Approval Dashboard. This pipeline never uploads to social media.")
            else:
                st.error('Final MP4 is missing from local storage.')
    job_panel()
