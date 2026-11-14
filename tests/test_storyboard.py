"""Offline Storyboard Studio regression tests; no external API or paid calls."""
import io
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.storyboard import (
    StoryboardError, approve_board, draft_board, export_board, is_current,
    load_board, load_reference, save_board, save_reference, sketch_frame, split_script,
)


def rejected(fn):
    try:
        fn()
    except StoryboardError:
        return
    raise AssertionError("Unsafe storyboard operation unexpectedly succeeded")


def backend():
    with tempfile.TemporaryDirectory(prefix="redpad-storyboard-unit-") as directory:
        folder = Path(directory)
        db_file = folder / "test.db"
        with sqlite3.connect(db_file) as db:
            db.execute("CREATE TABLE content (id INTEGER PRIMARY KEY, script TEXT NOT NULL)")
            db.execute("INSERT INTO content VALUES (1, ?)",
                       ("রাতের ঢাকা। এক তরুণ দৌড়াচ্ছে। হঠাৎ সামনে ছায়া।",))
        script = "রাতের ঢাকা। এক তরুণ দৌড়াচ্ছে। হঠাৎ সামনে ছায়া।"
        assert len(split_script(script)) == 3
        board = draft_board(1, "Night in Dhaka", script)
        assert len(board["shots"]) == 3
        assert board["shots"][0]["shot_type"] == "Wide"
        assert board["shots"][1]["shot_type"] == "Medium"
        assert sketch_frame(board["shots"][0], "16:9").size == (480, 270)
        assert sketch_frame(board["shots"][0], "9:16").size == (270, 480)
        assert b"REDPAD-Storyboard-v1" in export_board(board)
        assert not board.get("review_status")
        assert save_board(db_file, board, 0) == 1
        assert load_board(db_file, 1)["review_status"] == "Draft"
        rejected(lambda: save_board(db_file, board, 0))  # stale second writer

        board = load_board(db_file, 1)
        board["shots"][0]["visual"] = "Wide railway platform in heavy fog"
        board["character_bible"] = "Same young Bangladeshi man in a grey shirt"
        assert save_board(db_file, board, 1) == 2
        assert approve_board(db_file, 1, 2) == 3
        assert load_board(db_file, 1)["review_status"] == "Approved"
        rejected(lambda: approve_board(db_file, 1, 2))

        board = load_board(db_file, 1)
        board["shots"][0]["camera"] = "Tracking"
        assert save_board(db_file, board, 3) == 4
        assert load_board(db_file, 1)["review_status"] == "Draft"

        # Real-reference upload, decoding, and secure directory containment.
        buffer = io.BytesIO()
        Image.new("RGB", (400, 200), "blue").save(buffer, format="PNG")
        path = save_reference(folder, 1, 1, buffer.getvalue(), "16:9")
        assert load_reference(folder, path).size == (400, 200)
        assert load_reference(folder, str(folder / "test.db")) is None
        rejected(lambda: save_reference(folder, 1, 1, b"not an image", "16:9"))

        with sqlite3.connect(db_file) as db:
            db.execute("UPDATE content SET script=? WHERE id=1",
                       ("পরিবর্তিত স্ক্রিপ্ট।",))
        stale = load_board(db_file, 1)
        assert not is_current(stale, "পরিবর্তিত স্ক্রিপ্ট।")
        rejected(lambda: approve_board(db_file, 1, 4))
        rejected(lambda: save_board(db_file, stale, 4))
        fresh = draft_board(1, "Night in Dhaka", "পরিবর্তিত স্ক্রিপ্ট।")
        assert save_board(db_file, fresh, 4) == 5
        assert load_board(db_file, 1)["review_status"] == "Draft"
        assert is_current(load_board(db_file, 1), "পরিবর্তিত স্ক্রিপ্ট।")
        rejected(lambda: draft_board(1, "Bad", ""))
        rejected(lambda: split_script("হাই। " * 100))
        print("PASS: offline sketch, JSON, version lock, human review, stale script and image safety")


def frontend():
    with tempfile.TemporaryDirectory(prefix="redpad-storyboard-ui-") as directory:
        destination = Path(directory)
        for name in ("streamlit_app.py", "redpad_video_studio.py"):
            shutil.copy2(ROOT / name, destination / name)
        for name in ("redpad_pipeline", "assets"):
            shutil.copytree(ROOT / name, destination / name)
        with patch("requests.Session.request", side_effect=AssertionError("Network must not be called")):
            at = AppTest.from_file(str(destination / "streamlit_app.py"), default_timeout=120).run()
            assert not at.exception, [str(x) for x in at.exception]
            assert any(x.label == "🎬 Storyboard Studio" for x in at.tabs)
            next(w for w in at.text_input if w.label == "Channel Name").set_value("Story Test")
            next(w for w in at.text_input if w.label == "Content Category / Niche").set_value("Horror")
            next(x for x in at.button if x.label == "➕ Save Channel").click().run()
            next(w for w in at.text_input if w.label == "Video Title").set_value("Storyboard Test")
            next(w for w in at.text_input if w.label == "Topic / Idea").set_value("Horror")
            next(w for w in at.text_area if w.label == "Script or Content Notes").set_value(
                "রাতের ঢাকায় অচেনা ছায়া। সে থেমে যায়।")
            next(x for x in at.button if x.label == "📥 Submit Draft for Approval").click().run()
            assert any(b.key == "sb_create" for b in at.button)
            at.button(key="sb_create").click().run()
            assert not at.exception, [str(x) for x in at.exception]
            assert len(at.get("image")) >= 2
            assert any(b.key == "sb_approve" for b in at.button)
            with sqlite3.connect(destination / "redpad_studio.db") as db:
                assert db.execute("SELECT count(*) FROM storyboards").fetchone()[0] == 1
            at.button(key="sb_approve").click().run()
            assert not at.exception, [str(x) for x in at.exception]
            with sqlite3.connect(destination / "redpad_studio.db") as db:
                assert db.execute("SELECT review_status FROM storyboards").fetchone()[0] == "Approved"
            next(w for w in at.text_area if w.label == "Visual direction / frame action").set_value(
                "A shadow crosses a narrow alley in rainy Dhaka")
            next(x for x in at.button if x.label == "Save Shot").click().run()
            assert not at.exception, [str(x) for x in at.exception]
            with sqlite3.connect(destination / "redpad_studio.db") as db:
                status, payload = db.execute("SELECT review_status,payload FROM storyboards").fetchone()
                assert status == "Draft"
                assert "narrow alley" in json.loads(payload)["shots"][0]["visual"]
            print("PASS: actual Streamlit shot cards, edit, approve, version reset and zero requests")


if __name__ == "__main__":
    backend()
    frontend()
