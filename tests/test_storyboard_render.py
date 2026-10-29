"""Real offline MP4 from an approved REDPAD storyboard, without providers."""
from pathlib import Path
from unittest.mock import patch
import json
import sqlite3
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from redpad_pipeline.storyboard import draft_board, save_board, approve_board
from redpad_pipeline.storyboard_render import AnimaticError, render_approved_board
from redpad_pipeline.media import ff, duration


class ApprovedAnimatic(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="redpad-animatic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db_path = self.root / "test.db"
        self.media = self.root / "media"
        self.media.mkdir()
        self.script = "নিশিকথার রাত। অন্ধকার দরজা খুলে যায়। অচেনা ছায়া এগিয়ে আসে।"
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE content (
                id INTEGER PRIMARY KEY, channel_id INTEGER, title TEXT,
                topic TEXT, script TEXT, status TEXT, created_at TEXT, updated_at TEXT
            )""")
            db.execute("""INSERT INTO content VALUES
                (1,1,'Nishikotha','Horror',?,'Draft','today','today')""", (self.script,))
        board = draft_board(1, "Nishikotha", self.script, "16:9")
        self.assertEqual(len(board["shots"]), 3)
        for shot in board["shots"]:
            shot["seconds"] = 4
        save_board(self.db_path, board)
        self.assertEqual(approve_board(self.db_path, 1, 1), 2)

    def test_unapproved_and_stale_scripts_block_generation(self):
        with sqlite3.connect(self.db_path) as db:
            db.execute("UPDATE content SET script='A modified script' WHERE id=1")
        with self.assertRaises(AnimaticError):
            render_approved_board(self.db_path, self.media, 1)
        with sqlite3.connect(self.db_path) as db:
            self.assertFalse(db.execute("SELECT name FROM sqlite_master WHERE name='content_video'").fetchone())

    def test_render_real_mp4_audio_captions_and_final_approval(self):
        with patch("requests.Session.request", side_effect=AssertionError("Network used during offline render")):
            result = render_approved_board(self.db_path, self.media, 1)
        final = Path(result["path"])
        self.assertTrue(final.is_file())
        self.assertGreater(final.stat().st_size, 5000)
        self.assertAlmostEqual(duration(final), 12, delta=.55)
        self.assertFalse(result["voice"])
        with sqlite3.connect(self.db_path) as db:
            status = db.execute("SELECT status FROM content WHERE id=1").fetchone()[0]
            export = db.execute("SELECT video_path,voice_included FROM content_video WHERE content_id=1").fetchone()
        self.assertEqual(status, "Awaiting review")
        self.assertEqual(export[0], str(final))
        self.assertEqual(export[1], 0)
        self.assertIn("অন্ধকার", Path(result["subtitle"]).read_text(encoding="utf-8"))
        self.assertEqual(len(list(final.parent.glob("scene_*.mp4"))), 3)
        ff(["-i", final, "-f", "null", "-"], timeout=60)
        ff(["-ss", "0.5", "-i", final, "-frames:v", "1", final.parent / "frameA.png"])
        ff(["-ss", "1.7", "-i", final, "-frames:v", "1", final.parent / "frameB.png"])
        self.assertNotEqual(
            (final.parent / "frameA.png").read_bytes(),
            (final.parent / "frameB.png").read_bytes(),
            "Motion animatic was rendered as a static freeze"
        )
        print("PASS: Approved storyboard -> real moving MP4, audio, Bangla SRT, final human review")

    def test_failed_or_draft_board_does_not_replace_existing_video(self):
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE content_video(
                content_id INTEGER PRIMARY KEY,video_path TEXT,seconds REAL,voice_included INTEGER,created_at TEXT
            )""")
            db.execute("""INSERT INTO content_video VALUES(1,'original.mp4',30,0,'before')""")
            db.execute("UPDATE storyboards SET review_status='Draft' WHERE content_id=1")
        with self.assertRaises(AnimaticError):
            render_approved_board(self.db_path, self.media, 1)
        with sqlite3.connect(self.db_path) as db:
            self.assertEqual(db.execute("SELECT video_path FROM content_video").fetchone()[0], "original.mp4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
