"""Offline, editable shot boards bound to existing content script revisions.

No network, paid model, YouTube write, or production API calls live here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import hashlib
import json
import re
import sqlite3

from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

MAX_SHOTS = 80
SHOT_TYPES = ("Wide", "Medium", "Close-up", "Insert", "POV", "Over-shoulder")
CAMERA_MOVES = ("Static", "Slow push-in", "Pan", "Tracking", "Tilt", "Handheld")
MAX_REFERENCE_BYTES = 5 * 1024 * 1024


class StoryboardError(ValueError):
    pass


def script_hash(script: str) -> str:
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def split_script(script: str) -> list[str]:
    if not isinstance(script, str) or not script.strip():
        raise StoryboardError("Write a script in Approval Dashboard first.")
    if len(script) > 25000:
        raise StoryboardError("Script exceeds 25,000 characters. Split it into episodes.")
    # Keep Bangla danda and English punctuation; do not send text to a provider.
    sections = re.split(r"(?<=[।!?])\s+|(?<=[.!?])\s+|\n+", script.strip())
    parts: list[str] = []
    for section in sections:
        section = " ".join(section.split())
        if not section:
            continue
        # Long, unpunctuated scripts still receive manageable shot cards.
        words = section.split()
        current: list[str] = []
        for word in words:
            if len(word) > 420:
                raise StoryboardError("A script token is too long for a storyboard card.")
            if current and len(" ".join(current + [word])) > 260:
                parts.append(" ".join(current))
                current = []
            current.append(word)
        if current:
            parts.append(" ".join(current))
    if not parts or len(parts) > MAX_SHOTS:
        raise StoryboardError(f"Storyboard requires 1–{MAX_SHOTS} shots; split a longer script.")
    return parts


def draft_board(content_id: int, title: str, script: str, ratio: str = "16:9") -> dict:
    if ratio not in ("16:9", "9:16"):
        raise StoryboardError("Choose portrait or landscape.")
    shots = []
    for index, narration in enumerate(split_script(script), 1):
        kind = ("Wide", "Medium", "Close-up", "Insert")[((index - 1) % 4)]
        seconds = max(4, min(10, round(len(narration.split()) / 2.5)))
        shots.append({
            "number": index, "narration": narration, "visual": narration,
            "shot_type": kind, "camera": "Slow push-in" if kind == "Close-up" else "Static",
            "seconds": seconds, "notes": "", "reference_path": "",
        })
    return {
        "content_id": int(content_id), "title": str(title)[:160],
        "script_hash": script_hash(script), "ratio": ratio,
        "character_bible": "", "location_bible": "", "look_bible": "Cinematic Bangladeshi realism",
        "shots": shots,
    }


def validate_board(board: dict) -> dict:
    if not isinstance(board, dict) or board.get("ratio") not in ("16:9", "9:16"):
        raise StoryboardError("Invalid storyboard aspect ratio.")
    if not isinstance(board.get("script_hash"), str) or not re.fullmatch(r"[a-f0-9]{64}", board["script_hash"]):
        raise StoryboardError("Storyboard must be linked to a script revision.")
    shots = board.get("shots")
    if not isinstance(shots, list) or not 1 <= len(shots) <= MAX_SHOTS:
        raise StoryboardError("Storyboard must have 1–80 shots.")
    for key in ("character_bible", "location_bible", "look_bible"):
        if not isinstance(board.get(key), str) or len(board[key]) > 1200:
            raise StoryboardError("A continuity note is invalid or too long.")
    for i, shot in enumerate(shots, 1):
        if not isinstance(shot, dict) or shot.get("number") != i:
            raise StoryboardError("Shot numbers must be continuous.")
        if shot.get("shot_type") not in SHOT_TYPES or shot.get("camera") not in CAMERA_MOVES:
            raise StoryboardError(f"Shot {i} has an unsupported camera setting.")
        if type(shot.get("seconds")) is not int or not 2 <= shot["seconds"] <= 20:
            raise StoryboardError(f"Shot {i} must last 2–20 seconds.")
        for name, cap in (("narration", 700), ("visual", 900), ("notes", 800), ("reference_path", 512)):
            value = shot.get(name)
            if not isinstance(value, str) or len(value) > cap:
                raise StoryboardError(f"Shot {i} has invalid {name}.")
            if name in ("narration", "visual") and not value.strip():
                raise StoryboardError(f"Shot {i} needs narration and visual direction.")
    return board


def initialize(db_path: str | Path):
    with sqlite3.connect(db_path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS storyboards (
            content_id INTEGER PRIMARY KEY,
            script_hash TEXT NOT NULL,
            payload TEXT NOT NULL,
            revision INTEGER NOT NULL,
            review_status TEXT NOT NULL DEFAULT 'Draft',
            updated_at TEXT NOT NULL,
            FOREIGN KEY(content_id) REFERENCES content(id)
        )""")


def load_board(db_path: str | Path, content_id: int) -> dict | None:
    initialize(db_path)
    with sqlite3.connect(db_path) as db:
        row = db.execute(
            "SELECT payload,revision,review_status FROM storyboards WHERE content_id=?",
            (int(content_id),),
        ).fetchone()
    if row is None:
        return None
    board = json.loads(row[0])
    board["revision"] = row[1]
    board["review_status"] = row[2]
    return board


def is_current(board: dict, script: str) -> bool:
    return board["script_hash"] == script_hash(script)


def save_board(db_path: str | Path, board: dict, expected_revision: int = 0) -> int:
    validate_board(board)
    initialize(db_path)
    content_id = int(board["content_id"])
    payload = {k: v for k, v in board.items() if k not in ("revision", "review_status")}
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with sqlite3.connect(db_path, isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        source = db.execute("SELECT script FROM content WHERE id=?", (content_id,)).fetchone()
        if source is None or script_hash(source[0]) != board["script_hash"]:
            raise StoryboardError("Script changed. Regenerate the storyboard before saving.")
        row = db.execute("SELECT revision FROM storyboards WHERE content_id=?", (content_id,)).fetchone()
        actual = row[0] if row else 0
        if actual != expected_revision:
            raise StoryboardError("Storyboard was updated elsewhere. Refresh before editing.")
        revision = actual + 1
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        db.execute("""INSERT INTO storyboards(content_id,script_hash,payload,revision,review_status,updated_at)
            VALUES (?,?,?,?,'Draft',?)
            ON CONFLICT(content_id) DO UPDATE SET
                script_hash=excluded.script_hash, payload=excluded.payload,
                revision=excluded.revision, review_status='Draft', updated_at=excluded.updated_at
        """, (content_id, board["script_hash"], data, revision, timestamp))
    return revision


def approve_board(db_path: str | Path, content_id: int, expected_revision: int) -> int:
    board = load_board(db_path, content_id)
    if board is None:
        raise StoryboardError("Create a storyboard first.")
    validate_board(board)
    with sqlite3.connect(db_path, isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        source = db.execute("SELECT script FROM content WHERE id=?", (content_id,)).fetchone()
        if not source or not is_current(board, source[0]):
            raise StoryboardError("Script changed. Previous storyboard cannot be approved.")
        cursor = db.execute("""UPDATE storyboards SET review_status='Approved', revision=revision+1,
            updated_at=? WHERE content_id=? AND revision=?""",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), content_id, expected_revision))
        if cursor.rowcount != 1:
            raise StoryboardError("Storyboard changed. Refresh and review again.")
    return expected_revision + 1


def shot_prompt(board: dict, shot: dict) -> str:
    return (
        f"Shot {shot['number']}, {board['ratio']}, {shot['shot_type']} framing, "
        f"{shot['camera']} camera, {shot['seconds']} seconds. "
        f"Visual: {shot['visual']}. "
        f"Characters: {board['character_bible'] or 'not specified'}. "
        f"Location: {board['location_bible'] or 'not specified'}. "
        f"Look: {board['look_bible']}. "
        f"Narration: {shot['narration']}."
    )


def export_board(board: dict) -> bytes:
    validate_board(board)
    payload = {
        "format": "REDPAD-Storyboard-v1", "title": board["title"],
        "content_id": board["content_id"], "script_hash": board["script_hash"],
        "ratio": board["ratio"], "character_bible": board["character_bible"],
        "location_bible": board["location_bible"], "look_bible": board["look_bible"],
        "shots": [{**shot, "motion_prompt": shot_prompt(board, shot)} for shot in board["shots"]],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def sketch_frame(shot: dict, ratio: str) -> Image.Image:
    """Deterministic FREE composition sketch, NOT an AI-generated image."""
    width, height = (480, 270) if ratio == "16:9" else (270, 480)
    image = Image.new("RGB", (width, height), (31, 38, 48))
    draw = ImageDraw.Draw(image)
    horizon = int(height * .63)
    draw.rectangle((0, horizon, width, height), fill=(47, 50, 54))
    vanishing = (width // 2, horizon)
    for x in range(0, width + 1, max(1, width // 6)):
        draw.line((x, height, *vanishing), fill=(80, 85, 89), width=1)
    for y in range(horizon + 24, height, 26):
        draw.line((0, y, width, y), fill=(76, 80, 84), width=1)
    # Vary subject scale with the planned composition.
    scale = {"Wide": .18, "Medium": .32, "Close-up": .61, "Insert": .40,
             "POV": .12, "Over-shoulder": .39}[shot["shot_type"]]
    radius = max(7, int(min(width, height) * scale * .25))
    cx = int(width * (.57 if shot["number"] % 2 else .42))
    cy = horizon - radius * 3
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(158, 170, 175))
    draw.rounded_rectangle((cx-radius*1.5, cy+radius, cx+radius*1.5,
                            cy+radius*5), radius=radius//2, fill=(106, 121, 132))
    if shot["shot_type"] == "Over-shoulder":
        draw.ellipse((0, int(height*.43), int(width*.32), int(height*.90)),
                     fill=(71, 82, 93))
    if shot["shot_type"] == "Insert":
        draw.rounded_rectangle((int(width*.21), int(height*.35),
                                int(width*.81), int(height*.80)),
                               radius=8, outline=(218, 193, 128), width=4)
    draw.rectangle((6, 6, width-7, height-7), outline=(143, 152, 158), width=2)
    draw.rectangle((9, 9, width-10, 35), fill=(18, 24, 33))
    draw.text((16, 16), f"SHOT {shot['number']:02d}  |  {shot['shot_type'].upper()}",
              fill=(238, 235, 221))
    return image


def save_reference(media_dir: Path, content_id: int, shot_number: int,
                   data: bytes, ratio: str) -> str:
    """Normalize a user-provided image to a bounded local asset."""
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_REFERENCE_BYTES:
        raise StoryboardError("Reference image must be 5 MB or smaller.")
    try:
        with Image.open(BytesIO(data)) as source:
            if source.format not in ("JPEG", "PNG", "WEBP"):
                raise StoryboardError("Use a JPEG, PNG or WEBP reference image.")
            if source.width * source.height > 15_000_000:
                raise StoryboardError("Reference image resolution is too large.")
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise StoryboardError("The uploaded reference image could not be opened.") from error
    image.thumbnail((1280, 720) if ratio == "16:9" else (720, 1280))
    directory = Path(media_dir) / "storyboards" / str(int(content_id))
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"shot_{int(shot_number):03d}.jpg"
    image.save(path, format="JPEG", quality=84)
    return str(path)


def load_reference(media_dir: Path, path: str) -> Image.Image | None:
    if not path:
        return None
    try:
        root = (Path(media_dir) / "storyboards").resolve()
        candidate = Path(path).resolve()
        if not candidate.is_relative_to(root):
            return None
        with Image.open(candidate) as source:
            return source.copy()
    except (OSError, ValueError):
        return None
