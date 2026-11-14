"""Real Streamlit widgets and real free MP4, isolated from deployed records."""
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from redpad_video_studio import render_mp4
from redpad_pipeline.youtube import NISHIKOTHA_ID, Store


def main():
    with tempfile.TemporaryDirectory(prefix="redpad-youtube-ui-") as directory:
        root = Path(directory)
        for name in ("streamlit_app.py", "redpad_video_studio.py"):
            shutil.copy2(ROOT/name, root/name)
        for name in ("redpad_pipeline", "assets"):
            shutil.copytree(ROOT/name, root/name)
        # Explicitly prohibit all requests during UI execution.
        with patch("requests.Session.request", side_effect=AssertionError("Network forbidden")):
            at = AppTest.from_file(str(root/"streamlit_app.py"), default_timeout=120).run()
            assert not at.exception, at.exception
            assert not any(b.key == "yt_connect" for b in at.button)
            assert any(w.value == "Not connected" and w.label == "Nishikotha Google connection" for w in at.metric)
            at.button(key="yt_register").click().run()
            assert not at.exception, at.exception
            assert at.button(key="yt_connect").disabled
            with sqlite3.connect(root/"redpad_studio.db") as db:
                cid = db.execute("SELECT id FROM channels WHERE name='নিশিকথা'").fetchone()[0]
            at.button(key="yt_mock_connect").click().run()
            assert not at.exception, at.exception
            assert at.button(key="yt_live_write").disabled
            assert any(w.value == "Not connected" and w.label == "Nishikotha Google connection" for w in at.metric), "Mock falsely claims Google connection"
        # Real FFmpeg output, synthetic test audio only. Never reaches Google.
        video = root/"redpad_media"/"video"/"youtube-test.mp4"
        video.parent.mkdir(parents=True, exist_ok=True)
        render_mp4("YouTube mock workflow", "Fictional horror test", video)
        with sqlite3.connect(root/"redpad_studio.db") as db:
            did = db.execute("""INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at)
                VALUES (?,'YouTube offline test','MOCK','test','Approved','now','now')""", (cid,)).lastrowid
            db.execute("INSERT INTO content_video VALUES(?,?,30,0,'now')", (did, str(video)))
        with patch("requests.Session.request", side_effect=AssertionError("Network forbidden")):
            at.run()
            next(b for b in at.button if b.label == "Prepare dry-run publishing request").click().run()
            assert not at.exception, at.exception
            store = Store(root/"redpad_youtube_mock.db")
            request = store.list("request:")[0]
            at.checkbox(key="yt_upload_"+request["id"]).check().run()
            at.button(key="yt_approve").click().run()
            assert not at.exception, at.exception
            at.button(key="yt_run").click().run()
            assert not at.exception, at.exception
            assert any("0 network calls" in w.value for w in at.success)
            saved = store.list("request:")[0]
            assert saved["state"] == "dry_run_private"
            assert saved["plan"]["channel_id"] == NISHIKOTHA_ID
            assert at.button(key="yt_live_write").disabled
            assert at.button(key="yt_connect").disabled
        print("PASS: Nishikotha local registration, clearly separate mock connection, real MP4 plan, owner approval, zero-network dry run; live buttons locked")


if __name__ == "__main__":
    main()
