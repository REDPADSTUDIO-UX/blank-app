"""Headless smoke test for the REDPAD Streamlit UI and demo rendering.

Runs in a disposable GitHub Actions checkout; does not access user secrets,
production databases, social accounts, or the deployed Codespace.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

from streamlit.testing.v1 import AppTest

SOURCE = Path(__file__).resolve().parents[1]
TEST_SPACE = tempfile.TemporaryDirectory(prefix="redpad-ui-test-")
ROOT = Path(TEST_SPACE.name)
for filename in ("streamlit_app.py", "redpad_video_studio.py"):
    shutil.copy2(SOURCE / filename, ROOT / filename)
DB = ROOT / "redpad_studio.db"


def verify_no_exceptions(at, stage):
    errors = [getattr(x, "message", str(x)) for x in at.exception]
    assert not errors, f"{stage}: Streamlit exceptions: {errors}"


def main():
    # A GitHub Actions checkout is temporary and should not have user state.
    assert not DB.exists(), "CI test needs a clean, disposable database"
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=240).run()
    verify_no_exceptions(at, "first app load")
    tabs = [t.label for t in at.tabs]
    assert "🎞️ Video Studio" in tabs, f"Video Studio tab missing: {tabs}"
    print("PASS: Streamlit app opens and Video Studio tab is present")

    # Exercise channel creation via the real Streamlit UI widgets.
    name_input = next((w for w in at.text_input if w.label == "Channel Name"), None)
    niche_input = next((w for w in at.text_input if w.label == "Content Category / Niche"), None)
    assert name_input is not None and niche_input is not None, "Channel form inputs missing"
    name_input.set_value("REDPAD CI Horror")
    niche_input.set_value("Horror")
    submit = next((b for b in at.button if b.label == "➕ Save Channel"), None)
    assert submit is not None, "Save Channel form button missing"
    submit.click().run()
    verify_no_exceptions(at, "channel creation")
    with sqlite3.connect(DB) as db:
        count = db.execute("SELECT count(*) FROM channels WHERE name=?", ("REDPAD CI Horror",)).fetchone()[0]
    assert count == 1, "Channel not saved in temporary test database"
    print("PASS: add-channel UI successfully saves a test channel")

    render_button = at.button(key="vs_render")
    assert not render_button.disabled, "Video rendering button should be enabled"
    render_button.click().run()
    verify_no_exceptions(at, "Video Studio render click")
    with sqlite3.connect(DB) as db:
        rows = db.execute(
            "SELECT video_path,seconds,voice_included FROM content_video"
        ).fetchall()
        drafts = db.execute("SELECT status FROM content").fetchall()
    assert len(rows) == 1, f"Expected one generated video, got {len(rows)}"
    path, seconds, voice = rows[0]
    assert Path(path).is_file() and Path(path).stat().st_size > 3000, "Video file missing"
    assert 29 <= seconds <= 31 and voice == 0, "Unexpected demo video metadata"
    assert drafts == [("Awaiting review",)], f"Approval gate was bypassed: {drafts}"
    print("PASS: UI button creates playable MP4; draft awaits human approval")
    artifact_dir = SOURCE / "ci_artifacts"
    artifact_dir.mkdir(exist_ok=True)
    shutil.copy2(path, artifact_dir / "redpad-ui-demo.mp4")
    print("PASS: preview", str(path), "size", Path(path).stat().st_size)
    # Decode the whole file, not just its container header.
    sys.path.insert(0, str(ROOT))
    from redpad_video_studio import ffmpeg_binary
    ff = ffmpeg_binary()
    decoded = subprocess.run([ff, "-v", "error", "-i", path, "-f", "null", "-"],
                             capture_output=True, timeout=60)
    assert decoded.returncode == 0 and not decoded.stderr, decoded.stderr
    assert len(at.get("video")) >= 2, "Video missing from review or saved previews"
    downloads = at.get("download_button")
    assert any(w.proto.label == "Download review MP4" for w in downloads)
    assert any(w.proto.label == "Download MP4" for w in downloads)
    for widget in downloads:
        if "MP4" in widget.proto.label:
            assert widget.proto.url.endswith(".mp4") and not widget.proto.disabled


    def decision(value):
        next(r for r in at.radio if r.label == "Review Decision").set_value(value)
        next(b for b in at.button if b.label == "💾 Save Review Decision").click().run()
        verify_no_exceptions(at, value)

    def status():
        with sqlite3.connect(DB) as db:
            return db.execute("SELECT status FROM content WHERE id=1").fetchone()[0]

    # Missing correction text must not change the review state.
    decision("Request Changes")
    assert status() == "Awaiting review"
    next(w for w in at.text_area if w.label.startswith("Correction Instructions")).set_value("Improve ending")
    decision("Request Changes")
    assert status() == "Changes requested"
    decision("Submit for Review")
    assert status() == "Awaiting review"
    decision("Approve")
    assert status() == "Approved"

    # Rendering another version must invalidate approval and use a fresh URL.
    at.radio(key="vs_source").set_value("Existing draft").run()
    at.selectbox(key="vs_ratio").set_value("16:9 landscape")
    at.selectbox(key="vs_mood").set_value("Calm / Documentary")
    at.button(key="vs_render").click().run()
    verify_no_exceptions(at, "rerender")
    assert status() == "Awaiting review", "New render retained old approval"
    with sqlite3.connect(DB) as db:
        new_path = db.execute("SELECT video_path FROM content_video WHERE content_id=1").fetchone()[0]
    assert new_path != path and Path(new_path).is_file()
    decision("Approve")
    next(w for w in at.text_area if w.label == "Edit Script / Notes").set_value("Updated script")
    decision("Approve")
    assert status() == "Awaiting review", "Changed script approved against stale video"
    with sqlite3.connect(DB) as db:
        assert db.execute("SELECT count(*) FROM content_video").fetchone()[0] == 0
    print("PASS: request changes, review, approve, rerender reset, stale video invalidation")
    print("PASS: vertical and landscape renders; video and download widgets in both review and studio")


if __name__ == "__main__":
    main()
