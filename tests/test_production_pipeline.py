"""Offline production contracts, provider HTTP mocks, real codecs and review integration."""
import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.models import Config, ProductionError, estimate_usd, mock_plan, validate_plan, narration
from redpad_pipeline.providers import LiveGateway, safe_download
from redpad_pipeline.engine import create_job, load_state, run_job
from redpad_pipeline.media import MockGateway, duration, ff, subtitles


def database(path):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE channels(id INTEGER PRIMARY KEY,name TEXT)')
        db.execute("INSERT INTO channels VALUES(1,'REDPAD test')")
        db.execute('''CREATE TABLE content(id INTEGER PRIMARY KEY,channel_id INTEGER,title TEXT,topic TEXT,
                    script TEXT,status TEXT,created_at TEXT,updated_at TEXT)''')


def response(data=None, status=200, content=None):
    result = requests.Response()
    result.status_code = status
    result._content = content if content is not None else json.dumps(data).encode()
    return result


def config():
    return Config('runway-secret', 'azure-secret', 'eastus', 'openai-secret', True, 100)


class Contracts(unittest.TestCase):
    def test_spend_and_credentials_gate(self):
        self.assertEqual(estimate_usd(30), 3.85)
        with self.assertRaises(ProductionError):
            LiveGateway(Config(), 30, 100)
        with self.assertRaises(ProductionError):
            LiveGateway(config(), 30, 0)
        self.assertNotIn('secret', repr(config()))
        invalid_cap = config()
        invalid_cap.max_job_usd = float('nan')
        with self.assertRaises(ProductionError):
            LiveGateway(invalid_cap, 30, 4)
        with self.assertRaises(ProductionError):
            LiveGateway(config(), -30, 4)
        for setting in ('runway_key', 'azure_key', 'openai_key', 'azure_region'):
            value = config()
            setattr(value, setting, '')
            with self.assertRaises(ProductionError):
                LiveGateway(value, 30, 4)

    def test_plans_and_long_timeline(self):
        for seconds in (30, 60, 120, 300, 600):
            plan = mock_plan('Test', seconds)
            self.assertEqual(sum(s['seconds'] for s in plan['scenes']), seconds)
        plan = mock_plan('Test')
        for field, value in [('seconds', 0), ('ratio', '1:1'), ('voice', 'unknown')]:
            invalid = copy.deepcopy(plan)
            invalid[field] = value
            with self.assertRaises(ProductionError):
                validate_plan(invalid)
        invalid = copy.deepcopy(plan)
        invalid['scenes'][0]['sfx'] = 'shell command'
        with self.assertRaises(ProductionError):
            validate_plan(invalid)
        with tempfile.TemporaryDirectory() as directory:
            for p in subtitles(mock_plan('Long', 600), Path(directory)):
                text = p.read_text()
                self.assertIn('00:09:54,000 --> 00:10:00,000', text)
                self.assertEqual(text.count('-->'), 100)

    def test_runway_payload_and_status(self):
        session = Mock()
        gateway = LiveGateway(config(), 30, 4, session)
        session.request.return_value = response({'id': 'task-123'})
        task = gateway.submit_video(mock_plan('Test')['scenes'][0], '720:1280')
        self.assertEqual(task, 'task-123')
        kwargs = session.request.call_args.kwargs
        self.assertEqual(kwargs['json']['model'], 'gen4.5')
        self.assertEqual(kwargs['json']['duration'], 6)
        self.assertEqual(kwargs['headers']['X-Runway-Version'], '2024-11-06')
        self.assertFalse(kwargs['allow_redirects'])
        session.request.return_value = response({'status': 'RUNNING'})
        self.assertFalse(gateway.video_status(task, Path('unused.mp4')))
        session.request.return_value = response({'status': 'SUCCEEDED', 'output': ['https://test.cloudfront.net/result.mp4']})
        with patch('redpad_pipeline.providers.safe_download') as download:
            self.assertTrue(gateway.video_status(task, Path('unused.mp4')))
            download.assert_called_once()
        session.request.return_value = response({'status': 'FAILED', 'failure': 'secret=https://signed.url'})
        with self.assertRaises(ProductionError) as error:
            gateway.video_status(task, Path('unused.mp4'))
        self.assertNotIn('signed', str(error.exception))

    def test_safe_errors_no_billed_http_retry(self):
        session = Mock()
        gateway = LiveGateway(config(), 30, 4, session)
        session.request.side_effect = requests.Timeout('Authorization: secret')
        with self.assertRaises(ProductionError) as error:
            gateway.submit_video(mock_plan('Test')['scenes'][0], '720:1280')
        self.assertEqual(session.request.call_count, 1)
        self.assertNotIn('secret', str(error.exception))
        session.request.side_effect = None
        session.request.return_value = response({'key': 'supersecret'}, status=429)
        with self.assertRaises(ProductionError) as error:
            gateway.submit_video(mock_plan('Test')['scenes'][0], '720:1280')
        self.assertNotIn('supersecret', str(error.exception))

    def test_planner_contract_and_azure_xml(self):
        session = Mock()
        gateway = LiveGateway(config(), 30, 4, session)
        plan = mock_plan('Test')
        session.request.return_value = response({'output': [{'content': [{'type': 'output_text',
            'text': json.dumps({'title': plan['title'], 'scenes': plan['scenes']})}]}]})
        actual = gateway.plan('A train story', 30, '720:1280', 'bn-BD-PradeepNeural')
        self.assertEqual(actual['seconds'], 30)
        self.assertTrue(session.request.call_args.kwargs['json']['text']['format']['strict'])
        with tempfile.TemporaryDirectory() as directory:
            session.request.return_value = response(content=b'RIFF' + b'x' * 200)
            gateway.voice('বাংলা & <test>', 'bn-BD-PradeepNeural', Path(directory) / 'voice.wav')
            ssml = session.request.call_args.kwargs['data'].decode()
            self.assertIn('&amp;', ssml)
            self.assertIn('&lt;test&gt;', ssml)
            self.assertNotIn('azure-secret', ssml)

    def test_sound_effects_are_real_audio(self):
        from redpad_pipeline.media import effect
        import wave
        with tempfile.TemporaryDirectory() as directory:
            values = []
            for kind in ('none', 'whoosh', 'impact', 'chime'):
                path = Path(directory) / f'{kind}.wav'
                effect(path, 1, kind)
                with wave.open(str(path)) as audio:
                    data = audio.readframes(audio.getnframes())
                    self.assertEqual(audio.getnframes(), 24000)
                values.append(data)
            self.assertEqual(set(values[0]), {0})
            self.assertEqual(len(set(values)), 4)

    def test_download_rejects_network_pivots(self):
        for url in ('http://test.cloudfront.net/x', 'https://evil.example/x',
                    'https://user:pass@test.cloudfront.net/x', 'https://test.cloudfront.net:8080/x'):
            with self.assertRaises(ProductionError):
                safe_download(url, Path('/tmp/never-created.mp4'))
        with patch('socket.getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 443))]):
            with self.assertRaises(ProductionError):
                safe_download('https://test.cloudfront.net/x', Path('/tmp/never-created.mp4'))


class Jobs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / 'test.db'
        database(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_uncertain_submission_not_rebilled(self):
        job = create_job(self.db, self.root, 1, mock_plan('Test'), 'mock')
        gateway = MockGateway()
        gateway.submit_video = Mock(side_effect=ProductionError('Uncertain video connection.'))
        state = run_job(self.db, job, gateway)
        self.assertEqual(state['phase'], 'blocked')
        self.assertEqual(state['scenes'][0]['video'], 'submitting')
        run_job(self.db, job, gateway)
        self.assertEqual(gateway.submit_video.call_count, 1)
        serialized = (job / 'state.json').read_text()
        self.assertNotIn('secret', serialized)

    def test_saved_task_resumes_without_new_post(self):
        job = create_job(self.db, self.root, 1, mock_plan('Test'), 'mock')
        gateway = MockGateway()
        gateway.submit_video = Mock(return_value='task-saved')
        gateway.video_status = Mock(return_value=False)
        state = run_job(self.db, job, gateway, max_polls=1, sleep=lambda _: None)
        self.assertEqual(state['phase'], 'waiting')
        run_job(self.db, job, gateway, max_polls=1, sleep=lambda _: None)
        self.assertEqual(gateway.submit_video.call_count, 1)
        self.assertEqual(load_state(job)['scenes'][0]['task_id'], 'task-saved')

    def test_complete_real_codec_mock_and_review(self):
        plan = mock_plan('শেষ ট্রেন')
        job = create_job(self.db, self.root, 1, plan, 'mock')
        # Test user-supplied licensed music too; the UI test covers the default soundtrack.
        from redpad_video_studio import create_ambient_wav
        create_ambient_wav(job / 'music.upload', 3, 'Calm / Documentary')
        with patch('requests.Session.request', side_effect=AssertionError('Offline test attempted network')):
            state = run_job(self.db, job, MockGateway())
        self.assertEqual(state['phase'], 'complete', state['error'])
        final = job / 'final.mp4'
        self.assertAlmostEqual(duration(final), 30, delta=.5)
        ff(['-i', final, '-f', 'null', '-'])
        self.assertEqual(len(list(job.glob('scene_*/edited.mp4'))), 5)
        # Check that the actual encoded frames change over time.
        ff(['-ss', '0.5', '-i', final, '-frames:v', '1', job / 'frame-a.png'])
        ff(['-ss', '1.5', '-i', final, '-frames:v', '1', job / 'frame-b.png'])
        self.assertNotEqual((job / 'frame-a.png').read_bytes(), (job / 'frame-b.png').read_bytes())
        for track, word in [('0:s:0', 'রাতের ঢাকা'), ('0:s:1', 'Night in Dhaka')]:
            extracted = job / 'extracted.srt'
            ff(['-i', final, '-map', track, '-c:s', 'srt', extracted])
            self.assertIn(word, extracted.read_text())
        self.assertIn('রাতের ঢাকা', (job / 'subtitles.bn.srt').read_text())
        self.assertIn('Night in Dhaka', (job / 'subtitles.en.srt').read_text())
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT status FROM content').fetchone()[0], 'Awaiting review')
            self.assertEqual(db.execute('SELECT voice_included FROM content_video').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT mode FROM production_exports').fetchone()[0], 'mock')
        again = MockGateway()
        again.submit_video = Mock(side_effect=AssertionError('Completed job regenerated video'))
        self.assertEqual(run_job(self.db, job, again)['phase'], 'complete')
        import subprocess
        worker = subprocess.run([sys.executable, '-m', 'redpad_pipeline.worker', '--db', str(self.db),
                                 '--job', state['job_id']], cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(worker.returncode, 0, worker.stderr)
        self.assertIn('complete', worker.stdout)
        target = ROOT / 'ci_artifacts'
        target.mkdir(exist_ok=True)
        import shutil
        shutil.copy2(final, target / 'redpad-production-MOCK-30s.mp4')
        for lang in ('bn', 'en'):
            shutil.copy2(job / f'subtitles.{lang}.srt', target / f'redpad-production-MOCK.{lang}.srt')
        print('PASS: 30s offline moving scenes, tone, music/SFX, bilingual captions, MP4, review gate')

    def test_worker_lock_blocks_duplicate_runner(self):
        import fcntl
        job = create_job(self.db, self.root, 1, mock_plan('Lock'), 'mock')
        gateway = MockGateway()
        gateway.voice = Mock(side_effect=AssertionError('Duplicate worker started'))
        with (job / 'worker.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(run_job(self.db, job, gateway)['phase'], 'queued')
        gateway.voice.assert_not_called()

    def test_changed_script_cannot_publish(self):
        from redpad_pipeline.engine import publish_to_review
        plan = mock_plan('Test')
        job = create_job(self.db, self.root, 1, plan, 'mock')
        state = load_state(job)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE content SET script='changed'")
        with self.assertRaises(ProductionError):
            publish_to_review(self.db, job, plan, state, job / 'final.mp4')


if __name__ == '__main__':
    unittest.main(verbosity=2)
