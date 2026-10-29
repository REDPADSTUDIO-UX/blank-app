"""Approved storyboard -> validated, checkpoint-compatible Live AI video scene plan.

This module prepares provider instructions but does NOT call paid providers.
English subtitle text is human-supplied; missing translations must be fixed
before starting any billable generation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sqlite3

from .models import ProductionError, validate_plan
from .storyboard import load_board, validate_board, script_hash, is_current


def _payload(board):
    return {key: value for key, value in board.items()
            if key not in ("revision", "review_status")}


def board_checksum(board):
    return sha256(
        json.dumps(_payload(board), ensure_ascii=False,
                   sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _shot_reference(media_dir, content_id, shot):
    ref = shot.get("reference_path", "")
    if not ref:
        return "", ""
    directory = (Path(media_dir) / "storyboards").resolve()
    path = Path(ref).resolve()
    if not path.is_relative_to(directory) or not path.is_file():
        raise ProductionError("Storyboard reference is not in the approved local media folder.")
    expected = f"{int(content_id)}/shot_{shot['number']:03d}.jpg"
    if path.relative_to(directory).as_posix() != expected:
        raise ProductionError("Storyboard reference path does not match its approved shot.")
    raw = path.read_bytes()
    if len(raw) > 3 * 1024 * 1024:
        raise ProductionError("Storyboard image exceeds the data-URI budget; compress it before AI production.")
    return expected, sha256(raw).hexdigest()


def approved_to_plan(db_path, media_dir, content_id, voice, model):
    """Build a shot-exact AI plan; never silently modify approved dialogue."""
    board = load_board(db_path, content_id)
    if not board or board.get("review_status") != "Approved":
        raise ProductionError("Approve the storyboard before preparing Live AI production.")
    validate_board(board)
    with sqlite3.connect(db_path) as db:
        row = db.execute(
            "SELECT title, script FROM content WHERE id=?", (int(content_id),)
        ).fetchone()
    if row is None or not is_current(board, row[1]):
        raise ProductionError("Script changed after storyboard approval.")
    ratio = {"16:9": "1280:720", "9:16": "720:1280"}[board["ratio"]]
    scenes = []
    for shot in board["shots"]:
        seconds = shot["seconds"]
        if not 4 <= seconds <= 10:
            raise ProductionError(
                f"Shot {shot['number']} is {seconds}s. Live text/image-to-video requires 4–10 seconds per shot."
            )
        english = shot.get("english", "").strip()
        if not english:
            raise ProductionError(
                f"Shot {shot['number']} needs an English subtitle translation. "
                "Enter one in Storyboard Studio and approve the updated storyboard."
            )
        if len(shot["narration"].encode("utf-16-le")) // 2 > 220:
            raise ProductionError(
                f"Shot {shot['number']} narration is too long for one generated scene."
            )
        prompt = (
            f"Cinematic original {board['ratio']} shot {shot['number']}. "
            f"Shot: {shot['shot_type']}. Camera: {shot['camera']}. "
            f"Visual story action: {shot['visual']}. "
            f"Same character appearance: {board['character_bible'][:280] or 'as described in story'}. "
            f"Location continuity: {board['location_bible'][:180] or 'as described in story'}. "
            f"Lighting/look: {board['look_bible'][:200]}. "
            "Natural physical motion, realistic cinematic texture, no text or logos."
        )
        if len(prompt.encode("utf-16-le")) // 2 > 1000:
            raise ProductionError(
                f"Shot {shot['number']} visual description is too long; shorten it before approval."
            )
        ref_key, ref_hash = _shot_reference(media_dir, content_id, shot)
        if ref_key and model != "gen4.5":
            raise ProductionError(
                "Reference-image animation is currently verified only for Runway Gen-4.5. "
                "Choose Gen-4.5 or remove the approved reference images."
            )
        scene = {
            "seconds": seconds,
            "bn": shot["narration"],
            "en": english,
            "prompt": prompt,
            "sfx": shot.get("sfx", "none"),
        }
        if ref_key:
            scene["image_key"] = ref_key
            scene["image_sha256"] = ref_hash
        scenes.append(scene)
    total = sum(x["seconds"] for x in scenes)
    if not 30 <= total <= 600 or not 3 <= len(scenes) <= 120:
        raise ProductionError("Live storyboard production requires 3–120 shots totalling 30–600 seconds.")
    result = {
        "title": f"{row[0]} — Approved Storyboard",
        "ratio": ratio, "voice": voice, "seconds": total, "video_model": model,
        "scenes": scenes,
        "source_storyboard": {
            "content_id": int(content_id),
            "revision": int(board["revision"]),
            "script_hash": board["script_hash"],
            "board_checksum": board_checksum(board),
        },
    }
    return validate_plan(result)


def verify_source(db_path, media_dir, plan):
    """Fail closed when a previous consent/shot plan becomes stale."""
    source = plan.get("source_storyboard")
    if source is None:
        return
    if not isinstance(source, dict):
        raise ProductionError("Invalid storyboard source binding.")
    if (type(source.get("content_id")) is not int
            or type(source.get("revision")) is not int
            or source["content_id"] <= 0 or source["revision"] <= 0
            or not isinstance(source.get("script_hash"), str)
            or not isinstance(source.get("board_checksum"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", source["board_checksum"])):
        raise ProductionError("Invalid storyboard source binding.")
    board = load_board(db_path, source["content_id"])
    if board is None or board.get("review_status") != "Approved":
        raise ProductionError("Source storyboard is no longer approved. Paid generation stopped.")
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT script FROM content WHERE id=?",
                         (source["content_id"],)).fetchone()
    if (row is None or not is_current(board, row[0])
            or board["revision"] != source["revision"]
            or board["script_hash"] != source["script_hash"]
            or board_checksum(board) != source["board_checksum"]):
        raise ProductionError("Approved storyboard or script changed. Paid generation stopped.")
    for shot, scene in zip(board["shots"], plan["scenes"]):
        key, checksum = _shot_reference(media_dir, source["content_id"], shot)
        if key != scene.get("image_key", "") or checksum != scene.get("image_sha256", ""):
            raise ProductionError("A storyboard reference image changed; paid generation stopped.")
    if len(board["shots"]) != len(plan["scenes"]):
        raise ProductionError("Storyboard shot count changed; paid generation stopped.")
