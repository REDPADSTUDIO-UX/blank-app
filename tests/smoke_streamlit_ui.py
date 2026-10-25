"""Headless smoke test for the REDPAD Streamlit UI and demo rendering.

Runs in a disposable GitHub Actions checkout; does not access user secrets,
production databases, social accounts, or the deployed Codespace.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
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
    channel_form = at.form(key="add_channel")
    inputs = channel_form.text_input
    assert len(inputs) >= 2, "Channel form inputs missing"
    inputs[0].set_value("REDPAD CI Horror")
    inputs[1].set_value("Horror")
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
    print("PASS: preview", str(path), "size", Path(path).stat().st_size)


if __name__ == "__main__":
    main()
