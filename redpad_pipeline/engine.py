"""Durable scene checkpoints, one worker per job, and the existing human review gate.

No secret, raw error, authorization header, or signed media URL is serialized.
"""
import fcntl
import json
import os
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .models import ProductionError, validate_plan, canonical, digest, narration
from .media import edit_scene, assemble, duration


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.chmod(0o600)
    temporary.replace(path)


def initialize(db_path):
    with closing(sqlite3.connect(db_path)) as db, db:
        db.execute('''CREATE TABLE IF NOT EXISTS production_jobs(
            job_id TEXT PRIMARY KEY, content_id INTEGER NOT NULL, mode TEXT NOT NULL,
            job_dir TEXT NOT NULL, created_at TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS production_exports(
            content_id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, video_path TEXT NOT NULL,
            script_hash TEXT NOT NULL, mode TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS content_video(
            content_id INTEGER PRIMARY KEY, video_path TEXT NOT NULL, seconds REAL NOT NULL,
            voice_included INTEGER NOT NULL, created_at TEXT NOT NULL)''')


def create_job(db_path, media_dir, channel_id, plan, mode, approved_usd=0):
    validate_plan(plan)
    if plan.get('source_storyboard'):
        from .storyboard_live import verify_source
        verify_source(db_path, media_dir, plan)
    if mode not in ('mock', 'live'):
        raise ProductionError('Unknown production mode.')
    initialize(db_path)
    job_id = uuid4().hex
    root = Path(media_dir).resolve() / 'production' / job_id
    root.mkdir(parents=True, mode=0o700)
    write_json(root / 'plan.json', plan)
    state = dict(job_id=job_id, mode=mode, phase='queued', error='', plan_hash=digest(canonical(plan)),
                 approved_usd=approved_usd, scenes=[{} for _ in plan['scenes']], created_at=now())
    with closing(sqlite3.connect(db_path)) as db, db:
        if not db.execute('SELECT id FROM channels WHERE id=?', (channel_id,)).fetchone():
            raise ProductionError('Channel no longer exists.')
        content_id = db.execute('''INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at)
             VALUES (?,?,?,?,'Awaiting review',?,?)''',
             (channel_id, plan['title'], 'AI production' if mode == 'live' else 'OFFLINE MOCK TEST',
              narration(plan), now(), now())).lastrowid
        db.execute('INSERT INTO production_jobs VALUES (?,?,?,?,?)', (job_id, content_id, mode, str(root), now()))
    state['content_id'] = content_id
    write_json(root / 'state.json', state)
    return root


def load_state(root):
    return json.loads((Path(root) / 'state.json').read_text(encoding='utf-8'))


def publish_to_review(db_path, root, plan, state, final):
    if plan.get('source_storyboard'):
        from .storyboard_live import verify_source
        verify_source(db_path, Path(root).parent.parent, plan)
    with closing(sqlite3.connect(db_path)) as db, db:
        row = db.execute('SELECT script FROM content WHERE id=?', (state['content_id'],)).fetchone()
        if not row or digest(row[0]) != digest(narration(plan)):
            raise ProductionError('Draft changed while rendering. Create a new production job for the updated script.')
        db.execute('''INSERT INTO content_video VALUES (?,?,?,?,?) ON CONFLICT(content_id) DO UPDATE SET
            video_path=excluded.video_path, seconds=excluded.seconds,
            voice_included=excluded.voice_included, created_at=excluded.created_at''',
            (state['content_id'], str(final), plan['seconds'], int(state['mode'] == 'live'), now()))
        db.execute('''INSERT INTO production_exports VALUES (?,?,?,?,?) ON CONFLICT(content_id) DO UPDATE SET
            job_id=excluded.job_id, video_path=excluded.video_path, script_hash=excluded.script_hash,mode=excluded.mode''',
            (state['content_id'], state['job_id'], str(final), digest(narration(plan)), state['mode']))
        db.execute("UPDATE content SET status='Awaiting review',updated_at=? WHERE id=?", (now(), state['content_id']))


def run_job(db_path, root, gateway, max_polls=90, sleep=time.sleep):
    root = Path(root).resolve()
    with (root / 'worker.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return load_state(root)
        state = load_state(root)
        if state['phase'] == 'complete':
            return state
        plan = validate_plan(json.loads((root / 'plan.json').read_text(encoding='utf-8')))
        if (state['plan_hash'] != digest(canonical(plan)) or gateway.mode != state['mode']
                or (gateway.mode == 'live' and (
                    gateway.approved_seconds != plan['seconds'] or
                    gateway.video_model != plan.get('video_model', 'gen4.5')))):
            raise ProductionError('Saved job plan or provider mode changed; create a fresh job.')
        state.update(phase='running', error='')
        write_json(root / 'state.json', state)
        try:
            if hasattr(gateway, 'bind_job'):
                gateway.bind_job(root)
            if plan.get('source_storyboard'):
                from .storyboard_live import verify_source
                verify_source(db_path, root.parent.parent, plan)
            clips = []
            for i, scene in enumerate(plan['scenes']):
                # Reject stale changes before any additional billed provider submission.
                if plan.get('source_storyboard'):
                    from .storyboard_live import verify_source
                    verify_source(db_path, root.parent.parent, plan)
                checkpoint = state['scenes'][i]
                directory = root / f'scene_{i:03d}'
                directory.mkdir(exist_ok=True)
                voice, source, edited = directory / 'voice.wav', directory / 'source.mp4', directory / 'edited.mp4'
                if not voice.exists():
                    if checkpoint.get('voice') == 'requested':
                        raise ProductionError('Uncertain speech submission. Reconcile it with Azure; automatic paid resubmission is blocked.')
                    checkpoint['voice'] = 'requested'
                    write_json(root / 'state.json', state)
                    gateway.voice(scene['bn'], plan['voice'], voice)
                    checkpoint['voice'] = 'done'
                    write_json(root / 'state.json', state)
                if duration(voice) > scene['seconds'] * 1.5:
                    raise ProductionError('Voice is too long for the scene; shorten the script before paying for video.')
                if not source.exists():
                    if checkpoint.get('video') == 'submitting':
                        raise ProductionError('Uncertain video submission. Reconcile the task ID in Runway; automatic paid resubmission is blocked.')
                    if not checkpoint.get('task_id'):
                        checkpoint['video'] = 'submitting'
                        write_json(root / 'state.json', state)
                        checkpoint['task_id'] = gateway.submit_video(scene, plan['ratio'])
                        checkpoint['video'] = 'submitted'
                        write_json(root / 'state.json', state)
                    ready = False
                    for poll in range(max_polls):
                        if gateway.video_status(checkpoint['task_id'], source):
                            ready = True
                            break
                        # Safe GET polling only, never a second generation POST.
                        sleep(5)
                    if not ready:
                        state.update(phase='waiting', error='Provider still running. Resume to continue polling the saved task.')
                        write_json(root / 'state.json', state)
                        return state
                    checkpoint['video'] = 'done'
                    write_json(root / 'state.json', state)
                if duration(source) < scene['seconds'] - .1:
                    raise ProductionError('Provider clip is shorter than the planned scene; do not approve this output.')
                if not edited.exists():
                    # Use a temporary name so an interrupted codec write is never reused.
                    partial = directory / 'edited.partial.mp4'
                    edit_scene(scene, source, voice, partial, plan['ratio'], state['mode'] == 'mock',
                               root / 'music.upload' if (root / 'music.upload').is_file() else None)
                    partial.replace(edited)
                checkpoint['edited'] = True
                write_json(root / 'state.json', state)
                clips.append(edited)
            final = assemble(plan, clips, root)
            publish_to_review(db_path, root, plan, state, final)
            state.update(phase='complete', error='', completed_at=now())
        except ProductionError as error:
            state.update(phase='blocked', error=str(error))
        except Exception:
            state.update(phase='blocked', error='Unexpected production failure. Check local runtime and resume; credentials are never logged here.')
        write_json(root / 'state.json', state)
        return state
