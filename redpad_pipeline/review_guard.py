"""Final MP4 review guards for storyboard-derived productions (no network)."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import sqlite3

from .models import ProductionError
from .storyboard import is_current, load_board


def ensure_current_source(db_path, media_dir, content_id):
    """Reject reviewing an MP4 if its approved storyboard source has changed.

    Legacy demo/videos with no storyboard provenance retain the existing
    dashboard review behavior.
    """
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT video_path FROM content_video WHERE content_id=?",
                         (content_id,)).fetchone()
        if row is None:
            return
        video = Path(row[0]).resolve()
        root = (Path(media_dir) / "storyboard_renders").resolve()
        if video.is_relative_to(root):
            if not video.is_file():
                raise ProductionError("Storyboard animatic video is missing.")
            try:
                manifest = json.loads((video.parent / "manifest.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise ProductionError("Storyboard render manifest is missing or invalid.") from None
            board = load_board(db_path, content_id)
            script_row = db.execute("SELECT script FROM content WHERE id=?",
                                    (content_id,)).fetchone()
            if (board is None or script_row is None
                    or board.get("review_status") != "Approved"
                    or not is_current(board, script_row[0])
                    or manifest.get("source_content_id") != content_id
                    or manifest.get("storyboard_revision") != board["revision"]
                    or manifest.get("source_script_hash") != board["script_hash"]):
                raise ProductionError(
                    "Source storyboard changed since rendering. Render a new MP4 before approval."
                )
            hashes = manifest.get("reference_sha256")
            if not isinstance(hashes, list) or len(hashes) != len(board["shots"]):
                raise ProductionError("Storyboard render reference manifest is invalid.")
            from .storyboard_render import _safe_reference
            for i, shot in enumerate(board["shots"]):
                _, actual = _safe_reference(media_dir, shot.get("reference_path", ""))
                if actual != hashes[i]:
                    raise ProductionError("Storyboard image changed after render; review is blocked.")
            return
        # AI Studio production jobs store an authoritative job plan, not an
        # arbitrary user-chosen path. Check only storyboard-origin live jobs.
        found = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='production_exports'"
        ).fetchone()
        if not found:
            return
        export = db.execute(
            "SELECT job_id FROM production_exports WHERE content_id=? AND video_path=?",
            (content_id, row[0]),
        ).fetchone()
        if export is None:
            return
        found = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='production_jobs'"
        ).fetchone()
        if not found:
            return
        job = db.execute("SELECT job_dir FROM production_jobs WHERE job_id=?",
                         (export[0],)).fetchone()
    if job is None:
        return
    try:
        plan = json.loads((Path(job[0]) / "plan.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ProductionError("Original production manifest is missing; review is blocked.") from None
    if plan.get("source_storyboard"):
        from .storyboard_live import verify_source
        verify_source(db_path, media_dir, plan)
