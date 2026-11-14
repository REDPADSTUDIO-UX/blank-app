"""Offline storyboard-to-MP4 production with script/revision-bound human review.

Produces an animated *animatic* from user-supplied images or schematic sketches.
No AI image/video generation, neural narration or network access occurs here.
"""
from __future__ import annotations

from array import array
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import json
import math
import shutil
import sqlite3
import wave

from PIL import Image, ImageDraw, ImageOps

from redpad_video_studio import create_ambient_wav
from .media import duration, ff, shaped_font, wrap
from .storyboard import (
    StoryboardError, is_current, load_board, load_reference, sketch_frame,
    validate_board,
)

MAX_UPLOAD = 20 * 1024 * 1024


class AnimaticError(StoryboardError):
    pass


def _source(db_path, content_id):
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT script FROM content WHERE id=?", (content_id,)).fetchone()
    if row is None:
        raise AnimaticError("The selected script no longer exists.")
    return row[0]


def approved_board(db_path, content_id):
    board = load_board(db_path, content_id)
    if board is None or board.get("review_status") != "Approved":
        raise AnimaticError("Approve this storyboard before creating an animatic.")
    validate_board(board)
    if not is_current(board, _source(db_path, content_id)):
        raise AnimaticError("The script changed after storyboard approval.")
    if sum(s["seconds"] for s in board["shots"]) > 600:
        raise AnimaticError("Offline animatic is limited to 10 minutes; split this story.")
    return board


def _safe_reference(media_dir, reference):
    if not reference:
        return None, ""
    image = load_reference(media_dir, reference)
    if image is None:
        raise AnimaticError("A storyboard reference image is missing or outside the media folder.")
    # Digest content rather than trusting paths: overwrite of an approved ref is detectable.
    candidate = Path(reference)
    data = candidate.read_bytes()
    if len(data) > MAX_UPLOAD:
        raise AnimaticError("Reference file is too large.")
    return image, sha256(data).hexdigest()


def _shot_frame(shot, ratio, reference):
    width, height = (640, 360) if ratio == "16:9" else (360, 640)
    image = reference if reference is not None else sketch_frame(shot, ratio)
    image = ImageOps.fit(image.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image, "RGBA")
    # Burn readable Bangla narration into safe lower third; no fake translation.
    text = shot["narration"]
    font_size = 24 if ratio == "16:9" else 24
    for size in range(font_size, 11, -1):
        font = shaped_font(size)
        lines = wrap(draw, text, font, width - 36)
        line_height = int(size * 1.48)
        block_height = len(lines) * line_height + 30
        if block_height <= int(height * 0.43):
            break
    else:
        raise AnimaticError(f"Shot {shot['number']}: narration too long for safe subtitles.")
    top = height - block_height - 14
    draw.rounded_rectangle((8, top, width - 8, height - 8),
                           radius=10, fill=(0, 0, 0, 195))
    y = top + 12
    for line in lines:
        x = (width - draw.textlength(line, font=font)) / 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height
    # Clearly identify generated sketches; user images never get called AI output.
    if reference is None:
        draw.rectangle((0, 0, width, 32), fill=(12, 18, 27, 205))
        draw.text((12, 8), "STORYBOARD SKETCH (NOT AI FOOTAGE)", fill=(241, 230, 205))
    return image


def _srt_clock(seconds):
    total = round(seconds * 1000)
    hours, rem = divmod(total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    sec, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{millis:03d}"


def _write_srt(shots, destination):
    cursor = 0
    lines = []
    for index, shot in enumerate(shots, 1):
        end = cursor + shot["seconds"]
        lines.append(f"{index}\n{_srt_clock(cursor)} --> {_srt_clock(end)}\n{shot['narration']}\n")
        cursor = end
    destination.write_text("\n".join(lines), encoding="utf-8")


def _write_cue_audio(shots, destination):
    """Low-level royalty-free edit cue at each shot change, not a licensed sample."""
    rate = 24000
    length = sum(shot["seconds"] for shot in shots)
    samples = array("h", [0]) * (rate * length)
    cursor = 0
    for index, shot in enumerate(shots):
        if index:
            offset = cursor * rate
            for n in range(int(.30 * rate)):
                t = n / rate
                envelope = math.exp(-t * 15)
                value = int(math.sin(2 * math.pi * (110 + 800 * t) * t) * envelope * 2800)
                samples[offset + n] = value
        cursor += shot["seconds"]
    with wave.open(str(destination), "wb") as out:
        out.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        out.writeframes(samples.tobytes())


def _save_media_upload(path, data):
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_UPLOAD:
        raise AnimaticError("Uploaded audio must be 1–20 MB or smaller.")
    path.write_bytes(data)
    # FFmpeg must be able to decode a real audio stream; do not trust extensions.
    length = duration(path)
    if length <= .1:
        raise AnimaticError("Audio has no playable duration.")
    return length


def _encode_clip(image, destination, seconds, ratio):
    size = "640x360" if ratio == "16:9" else "360x640"
    width, height = (640, 360) if ratio == "16:9" else (360, 640)
    # Work on a double-size still, then smoothly move the window over real frames.
    video_filter = (
        f"scale={width*2}:{height*2}:flags=bicubic,"
        f"zoompan=z='min(zoom+0.0008,1.16)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={size}:fps=24,"
        "format=yuv420p"
    )
    ff(["-loop", "1", "-framerate", "24", "-i", image,
        "-frames:v", seconds * 24, "-vf", video_filter,
        "-an", "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", destination], timeout=240)


def _assemble(root, clips, shots, voice_path, music_path, mood):
    total = sum(shot["seconds"] for shot in shots)
    playlist = root / "concat.txt"
    playlist.write_text("".join(f"file '{p.name}'\n" for p in clips), encoding="utf-8")
    subs = root / "subtitles.bn.srt"
    _write_srt(shots, subs)
    cues = root / "edit_cues.wav"
    _write_cue_audio(shots, cues)
    bed = root / "soundtrack.wav"
    if music_path is None:
        create_ambient_wav(bed, total, mood)
        music_path = bed
    final = root / "final.partial.mp4"

    args = ["-f", "concat", "-safe", "0", "-i", playlist,
            "-stream_loop", "-1", "-i", music_path,
            "-i", cues]
    if voice_path is not None:
        args += ["-i", voice_path]
    args += ["-i", subs]
    # Duck music under the real user narration; never claim synthetic tones are voice.
    if voice_path is not None:
        filters = (
            f"[1:a]aresample=48000,volume=0.32,atrim=duration={total}[bed];"
            f"[3:a]aresample=48000,volume=1,apad,atrim=duration={total},"
            "asplit=2[voice][side];"
            "[bed][side]sidechaincompress=threshold=0.03:ratio=7:attack=15:release=270[duck];"
            "[2:a]aresample=48000,volume=0.3[fx];"
            "[duck][voice][fx]amix=inputs=3:duration=first:normalize=0,"
            "alimiter=limit=0.95[a]"
        )
        subtitle_input = "4:0"
    else:
        filters = (
            f"[1:a]aresample=48000,volume=0.35,atrim=duration={total}[bed];"
            "[2:a]aresample=48000,volume=0.30[fx];"
            "[bed][fx]amix=inputs=2:duration=first:normalize=0,"
            "alimiter=limit=0.95[a]"
        )
        subtitle_input = "3:0"
    args += ["-filter_complex", filters, "-map", "0:v:0",
             "-map", "[a]", "-map", subtitle_input,
             "-t", total, "-c:v", "copy", "-c:a", "aac",
             "-ar", "48000", "-ac", "2", "-c:s", "mov_text",
             "-metadata:s:s:0", "language=ben",
             "-movflags", "+faststart", final]
    ff(args, timeout=300)
    if abs(duration(final) - total) > .55:
        raise AnimaticError("Animatic duration validation failed.")
    finished = root / "final.mp4"
    final.replace(finished)
    return finished


def render_approved_board(db_path, media_dir, content_id, *,
                          narration_audio=None, music_audio=None,
                          mood="Suspense / Horror"):
    """Render and register a reviewed MP4 for an *existing* content draft.

    The final DB transaction checks that approved storyboard and source script
    have not changed during rendering. Reference image bytes are hash-bound.
    """
    if mood not in ("Suspense / Horror", "Calm / Documentary"):
        raise AnimaticError("Unknown soundtrack preset.")
    db_path, media_dir = Path(db_path), Path(media_dir)
    board = approved_board(db_path, content_id)
    total = sum(s["seconds"] for s in board["shots"])
    # Read approved media hashes before touching review records.
    images = []
    references = []
    for shot in board["shots"]:
        picture, checksum = _safe_reference(media_dir, shot["reference_path"])
        images.append(picture)
        references.append(checksum)
    root = media_dir.resolve() / "storyboard_renders" / uuid4().hex
    root.mkdir(parents=True, mode=0o700)
    try:
        voice_path = None
        if narration_audio is not None:
            voice_path = root / "uploaded_narration.mp3"
            voice_length = _save_media_upload(voice_path, narration_audio)
            if voice_length > total + .1:
                raise AnimaticError("Narration is longer than the animatic; extend shot durations first.")
        music_path = None
        if music_audio is not None:
            music_path = root / "uploaded_music.mp3"
            _save_media_upload(music_path, music_audio)
        root.joinpath("manifest.json").write_text(
            json.dumps({
                "source_content_id": content_id,
                "storyboard_revision": board["revision"],
                "source_script_hash": board["script_hash"],
                "reference_sha256": references,
                "ratio": board["ratio"], "seconds": total,
                "voice_is_real": voice_path is not None,
                "mode": "storyboard-animatic-offline",
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        clips = []
        for index, shot in enumerate(board["shots"]):
            picture = root / f"frame_{index:03d}.png"
            _shot_frame(shot, board["ratio"], images[index]).save(picture)
            clip = root / f"scene_{index:03d}.mp4"
            _encode_clip(picture, clip, shot["seconds"], board["ratio"])
            clips.append(clip)
        final = _assemble(root, clips, board["shots"], voice_path, music_path, mood)

        # Fail closed on changes while FFmpeg was running, including source refs.
        with sqlite3.connect(db_path, isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            source = db.execute(
                "SELECT script FROM content WHERE id=?", (content_id,)).fetchone()
            saved = db.execute(
                "SELECT revision,review_status,script_hash FROM storyboards WHERE content_id=?",
                (content_id,)).fetchone()
            if (source is None or saved is None
                    or saved != (board["revision"], "Approved", board["script_hash"])
                    or not is_current(board, source[0])):
                raise AnimaticError("Script or approved storyboard changed during rendering. Output was not registered.")
            for i, shot in enumerate(board["shots"]):
                _, current_hash = _safe_reference(media_dir, shot["reference_path"])
                if current_hash != references[i]:
                    raise AnimaticError("A reference image changed during rendering. Output was not registered.")
            db.execute("""CREATE TABLE IF NOT EXISTS content_video (
                content_id INTEGER PRIMARY KEY, video_path TEXT NOT NULL,
                seconds REAL NOT NULL, voice_included INTEGER NOT NULL, created_at TEXT NOT NULL
            )""")
            db.execute("""INSERT INTO content_video(content_id,video_path,seconds,voice_included,created_at)
                VALUES(?,?,?,?,?) ON CONFLICT(content_id) DO UPDATE SET
                    video_path=excluded.video_path,seconds=excluded.seconds,
                    voice_included=excluded.voice_included,created_at=excluded.created_at
            """, (content_id, str(final), total, int(voice_path is not None),
                  datetime.now(timezone.utc).isoformat(timespec="seconds")))
            # Separate fresh human review is compulsory even for approved storyboard.
            db.execute("UPDATE content SET status='Awaiting review' WHERE id=?", (content_id,))
        return {"path": str(final), "seconds": total, "shots": len(clips),
                "voice": voice_path is not None, "content_id": content_id,
                "storyboard_revision": board["revision"],
                "subtitle": str(root / "subtitles.bn.srt")}
    except Exception:
        # Keep an unregistered failed job from being mistaken for a finished render.
        shutil.rmtree(root, ignore_errors=True)
        raise
