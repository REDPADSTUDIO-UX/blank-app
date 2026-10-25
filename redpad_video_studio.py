"""REDPAD AI Studio: free experimental video, ambient audio and editing pipeline.

Produces MP4 storyboard previews, not generative AI video or commercial AI music.
All drafts await human review; nothing is published.
"""
from __future__ import annotations
from contextlib import closing
import hashlib
import math
import random
import re
import shutil
import sqlite3
import subprocess
import tempfile
import wave
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import streamlit as st

SEEDS = [
    ("শেষ ট্রেনের যাত্রী", "শেষ ট্রেনে এক অচেনা যাত্রী বারবার একই স্টেশনের নাম বলছিল।"),
    ("বন্ধ দরজার ওপারে", "পুরোনো বাড়ির তালাবদ্ধ ঘর থেকে প্রতিরাতে হাঁটার শব্দ শোনা যেত।"),
    ("অচেনা নম্বর", "রাত তিনটায় এমন একটি নম্বর থেকে ফোন এল যার মালিক বহু বছর আগে মারা গেছে।"),
    ("আয়নায় ছায়া", "আয়নায় নিজের পেছনে একটি ছায়া দেখা গেল, অথচ ঘরে কেউ ছিল না।"),
]
VOICES = {"Nabanita (test female)": "bn-BD-NabanitaNeural",
          "Pradeep (test male)": "bn-BD-PradeepNeural"}

def demo_idea(channel, previous):
    """Demo templates, NOT autonomous AI research or model-generated scripts."""
    niche = (channel.get("niche") or "").lower()
    if any(s in niche for s in ("horror", "ভৌতিক", "রহস্য", "ghost")):
        title, topic = next((x for x in SEEDS if x[1] not in previous), SEEDS[0])
        text = (f"গভীর রাত। বাইরে এক অদ্ভুত নীরবতা। {topic} "
                "প্রথমে সবাই ভাবল, এটি হয়তো ভুল বোঝা। কিন্তু কয়েক মিনিট পর আবার ঘটল একই ঘটনা। "
                "একটি পুরোনো ডায়েরিতে পাওয়া গেল এমন কিছু লেখা, যা কেউ পড়তে চায়নি। "
                "সকালে সবকিছু স্বাভাবিক হয়ে গেল, শুধু ঘড়িটা থেমে ছিল ঠিক তিনটায়।")
    else:
        title = f"{channel.get('niche') or 'Content'} — ডেমো"
        topic = "REDPAD Production Engine-এর পরীক্ষামূলক ভিডিও"
        text = ("এটি রেডপ্যাড এআই স্টুডিওর একটি পরীক্ষামূলক ভিডিও। "
                "এখানে ডেমো দৃশ্য, অডিও এবং স্বয়ংক্রিয় এডিটিং যাচাই করা হচ্ছে। "
                "বাস্তব তথ্যভিত্তিক গবেষণা বা প্রিমিয়াম ভিডিও জেনারেশন এখানে যুক্ত নয়।")
    return title, topic, text

def ffmpeg_binary():
    value = shutil.which("ffmpeg")
    if value:
        return value
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

def ffmpeg_call(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=160)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Video render timed out.") from exc
    if p.returncode:
        raise RuntimeError("FFmpeg failed: " + p.stderr[-750:])

def create_ambient_wav(path, seconds, mood):
    """Procedurally synthesized royalty-free-to-create drone, not sampled music."""
    rate = 12000
    horror = mood == "Suspense / Horror"
    f1, f2 = (55, 82.41) if horror else (130.81, 196.0)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        data = bytearray()
        for i in range(int(rate * seconds)):
            t = i / rate
            fade = max(0.0, min(1.0, t, (seconds - t) / 2.0))
            swell = 0.6 + 0.4 * math.sin(t * 0.30) ** 2
            tone = math.sin(2 * math.pi * f1 * t) + .25 * math.sin(2 * math.pi * f2 * t)
            sample = max(-32000, min(32000, int(tone * swell * fade * 3600)))
            data.extend(sample.to_bytes(2, "little", signed=True))
            if len(data) > 32000:
                stream.writeframesraw(data)
                data.clear()
        if data:
            stream.writeframesraw(data)

def scene_images(folder, seed, vertical):
    from PIL import Image, ImageDraw, ImageFilter
    w, h = (360, 640) if vertical else (640, 360)
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16))
    images = []
    for i in range(4):
        img = Image.new("RGB", (w, h), (5 + i * 4, 11 + i * 5, 28 + i * 5))
        draw = ImageDraw.Draw(img, "RGBA")
        for j in range(20):
            a = 12 + j // 2 + i
            y = j * h // 20
            draw.rectangle((0, y, w, y + h // 20 + 2), fill=(a, a + 5, a + 24, 16))
        gx, gy = int(w * (.2 + .2 * i)), int(h * (.28 + .05 * (i % 2)))
        for layer in range(12, 0, -1):
            r = int(min(w, h) * layer / 20)
            draw.ellipse((gx-r, gy-r, gx+r, gy+r), fill=(100, 125, 175, 7))
        for j in range(35):
            x,y=rng.randrange(w),rng.randrange(h)
            draw.ellipse((x,y,x+2,y+2),fill=(195,210,235,rng.randrange(30,110)))
        img = img.filter(ImageFilter.GaussianBlur(0.6))
        p = folder / f"scene_{i}.png"
        img.save(p)
        images.append(p)
    return images

def inspect_audio_seconds(path, ff):
    p = subprocess.run([ff, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True, timeout=20)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", p.stderr)
    if not match:
        raise ValueError("Unable to read MP3 duration.")
    a,b,c = match.groups()
    return int(a) * 3600 + int(b) * 60 + float(c)

def render_mp4(title, script, destination, portrait=True,
               mood="Suspense / Horror", narration=None):
    """Four-scene 30 second low-resolution preview with original ambient audio.
    narration: optionally user-provided MP3 bytes, not an API call.
    """
    ff = ffmpeg_binary()
    if not ff:
        raise RuntimeError("FFmpeg unavailable. Add imageio-ffmpeg dependency.")
    if not script.strip():
        raise ValueError("The script is empty.")
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="redpad_video_") as workdir:
        work = Path(workdir)
        narration_file = None
        if narration:
            if len(narration) > 20 * 1024 * 1024:
                raise ValueError("MP3 exceeds the 20 MB limit.")
            narration_file = work / "voice.mp3"
            narration_file.write_bytes(narration)
        duration = 30.0
        if narration_file:
            duration = inspect_audio_seconds(narration_file, ff) + 1.0
            if not 1.0 < duration <= 80.0:
                raise ValueError("Narration must be nonempty and at most 79 seconds; split longer audio first.")
            duration = max(12.0, duration)
        width,height = (360,640) if portrait else (640,360)
        stills = scene_images(work, title, portrait)
        clips=[]
        for index, image in enumerate(stills):
            clip = work / f"part_{index}.mp4"
            ffmpeg_call([ff, "-loglevel", "error", "-y",
                         "-loop", "1", "-framerate", "12", "-i", str(image),
                         "-t", f"{duration/4:.3f}", "-vf", f"scale={width}:{height},format=yuv420p",
                         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(clip)])
            clips.append(clip)
        concat = work / "concat.txt"
        concat.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips))
        bed = work / "ambient.wav"
        create_ambient_wav(bed, duration, mood)
        args=[ff,"-loglevel","error","-y",
              "-f","concat","-safe","0","-i",str(concat),"-i",str(bed)]
        if narration_file:
            args+=["-i",str(narration_file),"-filter_complex",
                   "[1:a]volume=0.25[bed];[2:a]volume=1.0[voice];"
                   "[bed][voice]amix=inputs=2:duration=longest:dropout_transition=0[a]",
                   "-map","0:v:0","-map","[a]"]
        else:
            args+=["-map","0:v:0","-map","1:a:0"]
        args+=["-t",f"{duration:.2f}","-c:v","copy","-c:a","aac",
               "-movflags","+faststart",str(destination)]
        ffmpeg_call(args)
        if destination.stat().st_size < 3000:
            raise RuntimeError("MP4 output failed integrity check.")
        return {"path":str(destination),"seconds":round(duration,1),
                "voice":bool(narration_file),"bytes":destination.stat().st_size}

def _query(db, sql, args=()):
    with closing(sqlite3.connect(db)) as connection:
        connection.row_factory=sqlite3.Row
        return [dict(row) for row in connection.execute(sql,args)]

def show_video_studio(db_path, media_dir):
    st.subheader("🎞️ Video · Background Sound · Editing")
    st.info("Free MVP: demo idea → procedural storyboard → original ambient soundtrack "
            "→ edited MP4 → approval. Real generative AI video/music are NOT included yet.")
    st.caption("Publishing is disabled. No paid APIs are called.")
    st.write("Video renderer:", "✅ Ready" if ffmpeg_binary() else "❌ FFmpeg missing")
    channels=_query(db_path,"SELECT * FROM channels ORDER BY id DESC")
    if not channels:
        st.warning("Add a channel in Channel Manager first.")
        return
    with closing(sqlite3.connect(db_path)) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS content_video(
           content_id INTEGER PRIMARY KEY,
           video_path TEXT NOT NULL,
           seconds REAL NOT NULL,
           voice_included INTEGER NOT NULL,
           created_at TEXT NOT NULL,
           FOREIGN KEY(content_id) REFERENCES content(id))""")
    drafts=_query(db_path,"SELECT * FROM content ORDER BY id DESC")
    cmap={f"{ch['name']} ({ch['platform']}) #{ch['id']}":ch for ch in channels}
    channel=cmap[st.selectbox("Channel",list(cmap),key="vs_channel")]
    source=st.radio("Starting point",["AI-free demo idea","Existing draft"],key="vs_source")
    chosen=None
    if source=="Existing draft":
        valid={f"#{d['id']} {d['title']}":d for d in drafts if d["channel_id"]==channel["id"]}
        if not valid:
            st.warning("No drafts on this channel.")
            return
        chosen=valid[st.selectbox("Draft",list(valid),key="vs_draft")]
        st.text_area("Current script",chosen["script"],height=130,disabled=True)
    portrait=st.selectbox("Video ratio",["9:16 vertical","16:9 landscape"],key="vs_ratio").startswith("9:16")
    mood=st.selectbox("Background soundtrack",["Suspense / Horror","Calm / Documentary"],key="vs_mood")
    voice=st.file_uploader("Optional narration MP3 (e.g. Nabanita test)",type=["mp3"],key="vs_audio")
    if st.button("🎬 Generate demo MP4",disabled=not ffmpeg_binary(),key="vs_render"):
        if chosen and not chosen["script"].strip():
            st.error("Selected draft needs a script first.")
            return
        try:
            if chosen:
                cid,title,script=chosen["id"],chosen["title"],chosen["script"]
            else:
                seen={d["topic"] for d in drafts if d["channel_id"]==channel["id"]}
                title,topic,script=demo_idea(channel,seen)
                now=datetime.now().strftime("%Y-%m-%d %H:%M")
                with closing(sqlite3.connect(db_path)) as db, db:
                    cid=db.execute(
                        """INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at)
                           VALUES (?,?,?,?,'Awaiting review',?,?)""",
                        (channel["id"],title,topic,script,now,now)).lastrowid
            out=Path(media_dir)/"video"/f"draft_{cid}_{uuid4().hex[:12]}.mp4"
            with st.spinner("Rendering video, audio and edits…"):
                result=render_mp4(title,script,out,portrait,mood,voice.getvalue() if voice else None)
                with closing(sqlite3.connect(db_path)) as db, db:
                    db.execute(
                        """INSERT INTO content_video(content_id,video_path,seconds,voice_included,created_at)
                           VALUES (?,?,?,?,?)
                           ON CONFLICT(content_id) DO UPDATE SET
                           video_path=excluded.video_path,seconds=excluded.seconds,
                           voice_included=excluded.voice_included,created_at=excluded.created_at""",
                        (cid,result["path"],result["seconds"],int(result["voice"]),datetime.now().isoformat(timespec="minutes")))
                    db.execute("UPDATE content SET status='Awaiting review', updated_at=? WHERE id=?",
                               (datetime.now().isoformat(timespec="minutes"), cid))
            st.session_state["vs_notice"] = f"Draft #{cid} rendered. Review the video in Approval Dashboard."
            st.rerun()
        except Exception as exc:
            st.error(f"Preview error: {type(exc).__name__}: {exc}")
    if "vs_notice" in st.session_state:
        st.success(st.session_state.pop("vs_notice"))
    st.subheader("Saved previews")
    old=_query(db_path,"""SELECT v.*,c.title,c.status FROM content_video v
                       JOIN content c ON c.id=v.content_id ORDER BY v.created_at DESC LIMIT 12""")
    for item in old:
        with st.expander(f"#{item['content_id']} · {item['title']} · {item['status']}"):
            path=Path(item["video_path"])
            if path.is_file():
                st.video(path.read_bytes())
                st.download_button("Download MP4",path.read_bytes(),file_name=path.name,
                                   mime="video/mp4",key=f"vs_download_{item['content_id']}")
            else:
                st.warning("Preview missing from ephemeral local storage.")
    st.caption("Existing Approval Dashboard remains the final human review gate.")
