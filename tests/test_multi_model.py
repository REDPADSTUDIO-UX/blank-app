"""Offline contract and budget tests for Runway-hosted multi-model selection.

NO actual paid provider POSTs. Input prices are planning estimates only.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from redpad_pipeline.models import Config, ProductionError, mock_plan, estimate_usd, validate_plan
from redpad_pipeline.video_models import (
    VIDEO_MODELS, AUTO, resolve_model, scene_payload, video_cost_usd, estimate_job_usd
)
from redpad_pipeline.providers import LiveGateway
from redpad_pipeline.engine import create_job, run_job, load_state


def config():
    return Config(runway_key='unit-test-placeholder', azure_key='unit-test-placeholder',
                  azure_region='eastus', openai_key='unit-test-placeholder',
                  paid_enabled=True, max_job_usd=500.0)


class MultiModelContract(unittest.TestCase):
    def test_catalog_includes_seedance_and_competitors(self):
        self.assertGreaterEqual(len(VIDEO_MODELS), 5)
        for required in ('gen4.5', 'wan3', 'seedance2_mini',
                         'kling3.0_standard', 'grok_imagine_1_5_lite'):
            self.assertIn(required, VIDEO_MODELS)
        lowest = min(VIDEO_MODELS, key=lambda m: VIDEO_MODELS[m]['usd_per_second'])
        self.assertEqual(resolve_model(AUTO), lowest)
        self.assertEqual(video_cost_usd(30, AUTO),
                         round(VIDEO_MODELS[lowest]['usd_per_second'] * 30, 2))

    def test_estimates_are_model_specific(self):
        self.assertAlmostEqual(estimate_usd(30, 'gen4.5'), 3.85)
        self.assertAlmostEqual(estimate_usd(30, 'seedance2_mini'), 5.05)
        self.assertAlmostEqual(estimate_usd(30, AUTO), 1.15)
        self.assertGreater(estimate_job_usd(60, 'gen4.5'), estimate_job_usd(30, 'gen4.5'))
        with self.assertRaises(ProductionError):
            resolve_model('undefined-or-expensive-model')

    def test_paid_gate_uses_selected_price_not_default(self):
        cheap = resolve_model(AUTO)
        allowed = config()
        self.assertTrue(estimate_usd(30, cheap) < estimate_usd(30, 'gen4.5'))
        allowed.require(30, estimate_usd(30, cheap), cheap)
        denied = config()
        denied.max_job_usd = estimate_usd(30, cheap) - 0.01
        with self.assertRaises(ProductionError):
            denied.require(30, estimate_usd(30, cheap), cheap)
        denied = config()
        denied.paid_enabled = False
        with self.assertRaises(ProductionError):
            denied.require(30, estimate_usd(30, cheap), cheap)
        with self.assertRaises(ProductionError):
            config().require(30, 0, cheap)

    def test_one_payload_per_selected_model(self):
        scene = mock_plan('test')['scenes'][0]
        for model in VIDEO_MODELS:
            with self.subTest(model=model):
                payload = scene_payload(model, scene, '720:1280')
                self.assertEqual(payload['model'], model)
                self.assertEqual(payload['duration'], 6)
                self.assertEqual(payload['ratio'], '720:1280')
                self.assertTrue(payload['promptText'])
                self.assertLessEqual(len(payload['promptText']), 1000)
                if model == 'kling3.0_standard':
                    self.assertFalse(payload['audio'])
                # Mock HTTPS contract; no real network or charge.
                session = Mock()
                response = Mock(status_code=201)
                response.json.return_value = {'id': 'task_abc'}
                session.request.return_value = response
                gateway = LiveGateway(config(), 30, estimate_usd(30, model),
                                      session=session, video_model=model)
                task = gateway.submit_video(scene, '720:1280')
                self.assertEqual(task, 'task_abc')
                self.assertEqual(session.request.call_count, 1)
                request_kwargs = session.request.call_args.kwargs
                self.assertEqual(request_kwargs['json'], payload)
                self.assertFalse(request_kwargs['allow_redirects'])
                self.assertEqual(gateway.video_model, model)

    def test_utf16_prompt_limit(self):
        scene = mock_plan('Test')['scenes'][0]
        scene['prompt'] = '🎬' * 501
        with self.assertRaises(ProductionError):
            scene_payload('gen4.5', scene, '720:1280')

    def test_saved_jobs_lock_model_before_billing(self):
        with tempfile.TemporaryDirectory(prefix='redpad-model-test-') as tmp:
            base = Path(tmp)
            db = base / 'state.db'
            with sqlite3.connect(db) as conn:
                conn.execute('CREATE TABLE channels(id INTEGER PRIMARY KEY, name TEXT)')
                conn.execute('INSERT INTO channels VALUES (1, "Test")')
                conn.execute("""CREATE TABLE content(
                    id INTEGER PRIMARY KEY, channel_id INTEGER, title TEXT, topic TEXT,
                    script TEXT, status TEXT, created_at TEXT, updated_at TEXT)""")
            plan = mock_plan('Test')
            plan['video_model'] = 'seedance2_mini'
            self.assertEqual(validate_plan(plan)['video_model'], 'seedance2_mini')
            root = create_job(db, base, 1, plan, 'live', 5.05)
            state = load_state(root)
            self.assertEqual(state['phase'], 'queued')
            fake = Mock(mode='live', approved_seconds=30, video_model='gen4.5')
            with self.assertRaises(ProductionError):
                run_job(db, root, fake, sleep=lambda _: None)
            fake.submit_video.assert_not_called()
            self.assertEqual(load_state(root)['phase'], 'queued')
            altered = dict(plan, video_model=AUTO)
            with self.assertRaises(ProductionError):
                validate_plan(altered)

    def test_no_auto_retry_after_a_provider_failure(self):
        # API response itself may fail; changing models would risk a second bill.
        model = resolve_model(AUTO)
        session = Mock()
        session.request.side_effect = RuntimeError('unexpected network problem')
        gateway = LiveGateway(config(), 30, estimate_usd(30, model), session=session,
                              video_model=model)
        # LiveGateway never invokes a second model on its own.
        with self.assertRaises(RuntimeError):
            gateway.submit_video(mock_plan('Test')['scenes'][0], '720:1280')
        self.assertEqual(session.request.call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
