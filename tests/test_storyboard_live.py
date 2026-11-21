"""Approval-bound storyboard -> live model plan, without any paid network calls."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3
import tempfile
import unittest
import requests

from redpad_pipeline.engine import create_job, run_job
from redpad_pipeline.models import Config, ProductionError, estimate_usd
from redpad_pipeline.providers import LiveGateway
from redpad_pipeline.storyboard import approve_board, draft_board, save_board, save_reference
from redpad_pipeline.storyboard_live import approved_to_plan, verify_source


def response(body):
    r = requests.Response()
    r.status_code = 201
    import json
    r._content = json.dumps(body).encode("utf-8")
    return r


class StoryboardAI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="redpad-live-board-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "script.db"
        self.media = self.root / "media"
        self.media.mkdir()
        self.script = "একজন ছেলেকে দেখা গেল। সে একটি দরজার দিকে এগিয়ে গেল। আলো নিভে গেল। আবার আলো জ্বলে উঠল। একটি ছায়া নড়ল।"
        with sqlite3.connect(self.db) as con:
            con.execute("CREATE TABLE channels(id INTEGER PRIMARY KEY,name TEXT)")
            con.execute("INSERT INTO channels VALUES(1,'Nishikotha')")
            con.execute("""CREATE TABLE content(id INTEGER PRIMARY KEY, channel_id INTEGER,
                title TEXT,topic TEXT,script TEXT,status TEXT,created_at TEXT,updated_at TEXT)""")
            con.execute("INSERT INTO content VALUES(1,1,'Test','Horror',?,'Draft','now','now')",
                        (self.script,))
        self.board = draft_board(1, "Test", self.script)
        self.assertEqual(len(self.board["shots"]), 5)
        for i, shot in enumerate(self.board["shots"]):
            shot["seconds"] = 6
            shot["english"] = f"The narrator describes frightening moment {i+1}."
        save_board(self.db, self.board)
        approve_board(self.db, 1, 1)

    def test_needs_human_english_and_shot_bounds(self):
        self.board["shots"][0]["english"] = ""
        save_board(self.db, self.board, expected_revision=2)
        approve_board(self.db, 1, 3)
        with self.assertRaisesRegex(ProductionError, "English subtitle"):
            approved_to_plan(self.db, self.media, 1, 'bn-BD-PradeepNeural', 'gen4.5')
        self.board["shots"][0]["english"] = "A man appears."
        self.board["shots"][0]["seconds"] = 15
        save_board(self.db, self.board, expected_revision=4)
        approve_board(self.db, 1, 5)
        with self.assertRaisesRegex(ProductionError, "4–10 seconds"):
            approved_to_plan(self.db, self.media, 1, 'bn-BD-PradeepNeural', 'gen4.5')

    def test_bound_plan_source_and_stale_script_blocked(self):
        plan = approved_to_plan(self.db, self.media, 1, 'bn-BD-PradeepNeural', 'gen4.5')
        self.assertEqual(plan["seconds"], 30)
        self.assertEqual(plan["ratio"], "1280:720")
        self.assertEqual(len(plan["scenes"]), 5)
        self.assertIn("Cinematic", plan["scenes"][0]["prompt"])
        verify_source(self.db, self.media, plan)
        job = create_job(self.db, self.media, 1, plan, "live",
                         approved_usd=estimate_usd(30))
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE content SET script='new version' WHERE id=1")
        with self.assertRaises(ProductionError):
            verify_source(self.db, self.media, plan)
        class FakePaid:
            mode = "live"
            approved_seconds = 30
            video_model = "gen4.5"
            def voice(self, *args):
                raise AssertionError("A stale storyboard must never invoke a paid voice request")
            def submit_video(self, *args):
                raise AssertionError("A stale storyboard must never invoke a paid video request")
        result = run_job(self.db, job, FakePaid())
        self.assertEqual(result['phase'], 'blocked')
        self.assertTrue(result['error'])
        self.assertEqual(result['scenes'], [{}] * 5)

    def test_image_to_video_first_frame_contract_and_checksum(self):
        from PIL import Image
        from io import BytesIO
        picture = Image.new("RGB", (160, 90), "gray")
        stream = BytesIO()
        picture.save(stream, "PNG")
        ref = save_reference(self.media, 1, 1, stream.getvalue(), '16:9')
        self.board["shots"][0]["reference_path"] = ref
        save_board(self.db, self.board, 2)
        approve_board(self.db, 1, 3)
        with self.assertRaisesRegex(ProductionError, "Gen-4.5"):
            approved_to_plan(self.db, self.media, 1, 'bn-BD-PradeepNeural', 'grok_imagine_1_5_lite')
        plan = approved_to_plan(self.db, self.media, 1, 'bn-BD-PradeepNeural', 'gen4.5')
        scene = plan['scenes'][0]
        self.assertEqual(len(scene['image_sha256']), 64)
        session = Mock()
        session.request.return_value = response({"id": "paid-mock-response-1"})
        conf = Config('test-runway', 'test-azure', 'eastus', 'test-openai', True, 100)
        gateway = LiveGateway(conf, 30, estimate_usd(30), session, video_model='gen4.5')
        directory = self.media / "production" / "job123"
        directory.mkdir(parents=True)
        gateway.bind_job(directory)
        self.assertEqual(gateway.submit_video(scene, '1280:720'), 'paid-mock-response-1')
        args = session.request.call_args
        self.assertTrue(args.args[1].endswith('/image_to_video'))
        self.assertTrue(args.kwargs["json"]["promptImage"].startswith('data:image/jpeg;base64,'))
        self.assertNotIn('test-runway', str(args.kwargs["json"]))
        self.assertEqual(args.kwargs["json"]["duration"], 6)
        # Altering reference bytes after approval must block before network POST.
        Path(ref).write_bytes(Path(ref).read_bytes() + b'fake-corruption')
        with self.assertRaisesRegex(ProductionError, "differs"):
            gateway.submit_video(scene, '1280:720')
        self.assertEqual(session.request.call_count, 1)
        with self.assertRaises(ProductionError):
            verify_source(self.db, self.media, plan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
