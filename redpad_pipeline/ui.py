"""Additive Streamlit production controls; all live calls require explicit spend approval."""
import json
import hashlib
import sqlite3
import threading
from contextlib import closing
from pathlib import Path
import streamlit as st
from .models import Config, ProductionError, estimate_usd, mock_plan, digest
from .providers import LiveGateway
from .media import MockGateway, shaped_font
from redpad_video_studio import ffmpeg_binary
from .engine import create_job, initialize, load_state, run_job


def launch(db_path, root, config):
    state = load_state(root)
    if state['mode'] == 'live':
        plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
        gateway = LiveGateway(config, plan['seconds'], state['approved_usd'])
    else:
        gateway = MockGateway()
    worker = threading.Thread(target=run_job, args=(db_path, root, gateway), daemon=True,
                              name='redpad-production-' + state['job_id'][:8])
    worker.start()


def show_production_studio(db_path, media_dir, get_secret):
    st.subheader('🎥 AI Film Production — pipeline beta')
    st.caption('Topic → Bangla script + English translation → moving scenes → narration → music/SFX → bilingual MP4 → human review')
    initialize(db_path)
    config = Config.load(get_secret)
    with closing(sqlite3.connect(db_path)) as db:
        channels = db.execute('SELECT id,name FROM channels ORDER BY id DESC').fetchall()
    if not channels:
        st.info('Add a channel above before creating a production job.')
        return
    mode = st.radio('Production mode', ['Offline mock test — free', 'Live AI — paid providers'], key='prod_mode')
    live = mode.startswith('Live')
    if live:
        st.warning('Live uses OpenAI, Azure Speech and Runway Gen-4.5. No free generation is promised. Existing consumer subscriptions do not supply API credits.')
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
    topic = st.text_area('Topic / story / existing Bangla script', max_chars=6000, key='prod_topic')
    seconds = st.selectbox('Finished video length (seconds)', [30, 60, 120, 300, 600], key='prod_seconds')
    ratio = st.selectbox('Production aspect ratio', ['720:1280', '1280:720'], key='prod_ratio')
    voice = st.selectbox('Production Bangla voice', ['bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural'], key='prod_voice')
    music = st.file_uploader('Optional licensed background music (MP3/WAV, max 20 MB)', type=['mp3', 'wav'], key='prod_music')
    oversized_music = bool(music and music.size > 20 * 1024 * 1024)
    if oversized_music:
        st.error('Music file exceeds the 20 MB limit.')
    quote = estimate_usd(seconds)
    agreed = False
    fingerprint = digest(json.dumps([topic, seconds, ratio, voice, channel_id,
                          hashlib.sha256(music.getbuffer()).hexdigest() if music and not oversized_music else '']))
    if st.session_state.get('prod_consent_fingerprint') != fingerprint or st.session_state.pop('prod_reset_consent', False):
        st.session_state['prod_consent'] = False
        st.session_state['prod_consent_fingerprint'] = fingerprint
    if live:
        st.write(f'Planning estimate: US${quote:.2f} per job; video alone US${seconds*.12:.2f}. Taxes, reruns and pricing changes can increase actual billing. Checked 25 Oct 2026.')
        if config.max_job_usd < quote:
            st.info(f'Owner job limit REDPAD_MAX_JOB_USD must be at least US${quote:.2f}.')
        st.caption('The displayed estimate is a local guard, not a provider invoice cap. Use provider-side billing controls too. No automatic billed retries.')
        agreed = st.checkbox(f'I authorize this {seconds}s job at the displayed US${quote:.2f} estimate.', key='prod_consent')
    enabled = bool(topic.strip()) and not oversized_music and (not live or (agreed and config.paid_enabled and config.max_job_usd >= quote
              and all((config.runway_key, config.azure_key, config.azure_region, config.openai_key))))
    if st.button('🎬 Create AI production job' if live else '🧪 Create offline production test', disabled=not enabled, key='prod_create'):
        try:
            if music and music.size > 20 * 1024 * 1024:
                raise ProductionError('Music file exceeds the 20 MB limit.')
            shaped_font(20)
            if not ffmpeg_binary():
                raise ProductionError('FFmpeg is unavailable.')
            if live:
                gateway = LiveGateway(config, seconds, quote)
                with st.spinner('Planning the film and translating subtitles…'):
                    plan = gateway.plan(topic, seconds, ratio, voice)
            else:
                plan = mock_plan(topic, seconds, ratio, voice)
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
