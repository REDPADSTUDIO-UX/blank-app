import hashlib
import html
import os
import re
import sqlite3
from contextlib import closing
from datetime import datetime, time
from pathlib import Path

import requests

import streamlit as st

st.set_page_config(page_title="REDPAD AI Studio", page_icon="🎬", layout="wide")

# Optional single-owner gate for externally hosted demos. Disabled by default
# in local Codespaces and CI. No credentials are logged or committed to Git.
if os.environ.get("REDPAD_REQUIRE_PREVIEW_LOGIN", "").lower() == "true":
    import hmac as _redpad_hmac

    _expected = os.environ.get("REDPAD_DASHBOARD_PASSWORD", "")
    if not _expected:
        st.error("Private preview is locked until its hosting password is configured.")
        st.stop()
    if not st.session_state.get("redpad_preview_authenticated", False):
        st.title("🔐 REDPAD AI Studio — Private Preview")
        st.caption("Access is restricted. Paid AI generation is disabled on this preview.")
        with st.form("redpad_preview_signin"):
            _entered = st.text_input("Preview password", type="password")
            _submit = st.form_submit_button("Open dashboard")
        if _submit:
            if _redpad_hmac.compare_digest(_entered, _expected):
                st.session_state["redpad_preview_authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect preview password.")
        st.stop()


DB_PATH = Path(__file__).with_name("redpad_studio.db")
MEDIA_DIR = Path(__file__).with_name("redpad_media")
SCRIPT_MODEL = "gpt-4.1-mini"
VOICE_CHOICES = {
    "Bangladeshi male — Pradeep": "bn-BD-PradeepNeural",
    "Bangladeshi female — Nabanita": "bn-BD-NabanitaNeural",
}


def get_secret(name):
    """Read environment variables or Streamlit secrets; never show credentials."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def openai_client():
    from openai import OpenAI
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=api_key, timeout=90.0)


def create_narration(item, channel, duration_seconds=90):
    """AI Script Agent: draft Bangla spoken narration, following corrections."""
    instructions = (
        "You are an original Bengali-language YouTube narrator and script editor for "
        "Bangladesh. Write ONLY the finished spoken narration in natural "
        "Bangladeshi Bangla (বাংলাদেশের প্রমিত বাংলা), no title, headings, stage "
            "directions, markdown or production notes. Open with a compelling hook, "
        "establish characters and stakes, maintain momentum and finish naturally. "
        "Avoid clichés, padding, reused copyrighted writing, and invented facts "
        "in nonfiction. If the channel is horror or fiction, make it clearly "
        "fictional. Keep violence non-graphic. Follow the requested revisions. "
        "Write content that is suitable for a narrated social video."
    )
    input_text = (
        f"Channel: {channel['name']}\n"
        f"Platform: {channel['platform']}\n"
        f"Niche: {channel['niche']}\n"
        f"Working title: {item['title']}\n"
        f"Topic: {item['topic']}\n"
        f"Existing notes or script: {item['script'] or '(none)'}\n"
        f"Required corrections: {item['correction'] or '(none)'}\n"
        f"Target spoken duration: approximately {duration_seconds} seconds.\n"
        "Output the final voiceover text only."
    )
    response = openai_client().responses.create(
        model=SCRIPT_MODEL,
        instructions=instructions,
        input=input_text,
        max_output_tokens=2000,
    )
    narration = (response.output_text or "").strip()
    if not narration:
        raise RuntimeError("The script model returned an empty narration.")
    return narration


def script_digest(script):
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def create_bangla_voice(script, content_id, voice_name):
    """Bangla Voice Agent: Azure Speech synthesis for Bangladesh locale."""
    speech_key = get_secret("AZURE_SPEECH_KEY")
    speech_region = get_secret("AZURE_SPEECH_REGION")
    if not speech_key or not speech_region:
        raise RuntimeError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION are required.")
    if not re.fullmatch(r"[a-z0-9-]+", speech_region):
        raise RuntimeError("AZURE_SPEECH_REGION contains invalid characters.")
    if voice_name not in VOICE_CHOICES.values():
        raise ValueError("Unsupported voice selection.")
    if not script.strip():
        raise ValueError("Generate or write the script before producing audio.")
    if len(script) > 6000:
        raise ValueError("Narration is longer than 6000 characters; split it first.")

    safe_script = html.escape(script, quote=False)
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xml:lang="bn-BD">'
        f'<voice name="{voice_name}">{safe_script}</voice>'
        '</speak>'
    )
    endpoint = (
        f"https://{speech_region}.tts.speech.microsoft.com/"
        "cognitiveservices/v1"
    )
    response = requests.post(
        endpoint,
        headers={
            "Ocp-Apim-Subscription-Key": speech_key,
            "Content-Type": "application/ssml+xml; charset=utf-8",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            "User-Agent": "REDPAD-AI-Studio",
        },
        data=ssml.encode("utf-8"),
        timeout=90,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Azure Speech failed (HTTP {response.status_code}). "
            "Check region, key, subscription and quota."
        )
    if not response.content:
        raise RuntimeError("Speech API returned empty audio.")
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    audio_name = f"draft_{int(content_id)}_{script_digest(script)[:12]}.mp3"
    destination = MEDIA_DIR / audio_name
    destination.write_bytes(response.content)
    return str(destination)



def db_execute(sql, params=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def db_query(sql, params=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def initialize_database():
    db_execute(
        """CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            niche TEXT NOT NULL,
            videos_per_day INTEGER NOT NULL DEFAULT 1,
            publish_time TEXT NOT NULL DEFAULT '18:00',
            active INTEGER NOT NULL DEFAULT 1
        )"""
    )
    db_execute(
        """CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            script TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Awaiting review',
            correction TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(channel_id) REFERENCES channels(id)
        )"""
    )


initialize_database()
# Additive migration: existing channels and drafts are preserved.
db_execute(
    """CREATE TABLE IF NOT EXISTS content_audio (
        content_id INTEGER PRIMARY KEY,
        audio_path TEXT NOT NULL,
        narration_hash TEXT NOT NULL,
        voice_name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(content_id) REFERENCES content(id)
    )"""
)

st.title("🎬 REDPAD AI Studio")
st.caption("Content Automation Control Center • Version 2.1 (AI agents)")
st.info(
    "AI Script Agent ও Bangla Voice Agent যুক্ত হয়েছে। API credentials যোগ করলে "
    "স্ক্রিপ্ট ও MP3 ভয়েস তৈরি করা যাবে। Video Studio-তে ডেমো MP4 তৈরি করা যায়। অটো-পাবলিশ এখনো নেই।"
)

channels = db_query("SELECT * FROM channels ORDER BY id DESC")
items = db_query(
    """SELECT c.*, ch.name AS channel_name, ch.platform AS platform
       FROM content AS c JOIN channels AS ch ON ch.id = c.channel_id
       ORDER BY c.id DESC"""
)

tab_dashboard, tab_channels, tab_content, tab_ai, tab_video = st.tabs(
    ["📊 Dashboard", "📺 Channel Manager", "✅ Approval Dashboard", "🤖 AI Production", "🎞️ Video Studio"]
)

with tab_dashboard:
    st.subheader("Central Dashboard")
    a, b, c, d = st.columns(4)
    a.metric("Total Channels", len(channels))
    b.metric("Active Channels", sum(ch["active"] for ch in channels))
    c.metric("Waiting for Review", sum(item["status"] == "Awaiting review" for item in items))
    d.metric("Approved", sum(item["status"] == "Approved" for item in items))

    st.subheader("Production Workflow")
    st.write("Content Draft → Human Review → Correction (if needed) → Approval")
    st.warning("No video will be published automatically in this version.")
    if items:
        st.dataframe(
            [
                {
                    "Title": item["title"],
                    "Channel": item["channel_name"],
                    "Status": item["status"],
                    "Updated": item["updated_at"],
                }
                for item in items
            ],
            hide_index=True,
            width="stretch",
        )
    else:
        st.info("No content yet. Add a channel, then create a draft for review.")

with tab_channels:
    st.subheader("Add a Channel")
    with st.form("add_channel", clear_on_submit=True):
        name = st.text_input("Channel Name")
        platform = st.selectbox("Platform", ["YouTube", "Facebook", "Instagram"])
        niche = st.text_input("Content Category / Niche", placeholder="Horror stories, documentaries, etc.")
        daily = st.number_input("Videos per Day", min_value=0, max_value=50, value=1)
        schedule = st.time_input("Preferred Publishing Time", value=time(18, 0))
        add = st.form_submit_button("➕ Save Channel")
        if add:
            if not name.strip() or not niche.strip():
                st.error("Please enter a channel name and content category.")
            else:
                db_execute(
                    """INSERT INTO channels
                       (name, platform, niche, videos_per_day, publish_time)
                       VALUES (?, ?, ?, ?, ?)""",
                    (name.strip(), platform, niche.strip(), int(daily), schedule.strftime("%H:%M")),
                )
                st.success("Channel saved.")
                st.rerun()

    st.divider()
    st.subheader("Manage Existing Channels")
    if not channels:
        st.info("Add your first channel above.")
    else:
        channel_map = {f"{ch['name']} ({ch['platform']}) — #{ch['id']}": ch for ch in channels}
        chosen_name = st.selectbox("Choose Channel to Edit", list(channel_map))
        chosen = channel_map[chosen_name]
        with st.form(f"edit_channel_{chosen['id']}"):
            new_name = st.text_input("Channel Name", value=chosen["name"])
            new_niche = st.text_input("Category / Niche", value=chosen["niche"])
            new_daily = st.number_input(
                "Videos per Day", min_value=0, max_value=50,
                value=int(chosen["videos_per_day"]),
            )
            hour, minute = map(int, chosen["publish_time"].split(":"))
            new_time = st.time_input("Publishing Time", value=time(hour, minute))
            active = st.checkbox("Channel Active", value=bool(chosen["active"]))
            if st.form_submit_button("💾 Update Channel Settings"):
                if not new_name.strip() or not new_niche.strip():
                    st.error("Channel name and category cannot be empty.")
                else:
                    db_execute(
                        """UPDATE channels SET name=?, niche=?, videos_per_day=?,
                           publish_time=?, active=? WHERE id=?""",
                        (
                            new_name.strip(), new_niche.strip(), int(new_daily),
                            new_time.strftime("%H:%M"), int(active), chosen["id"],
                        ),
                    )
                    st.success("Settings updated.")
                    st.rerun()

with tab_content:
    st.subheader("Create a Draft for Review")
    if not channels:
        st.warning("First add a channel in Channel Manager.")
    else:
        options = {f"{ch['name']} — {ch['platform']} (#{ch['id']})": ch["id"] for ch in channels}
        with st.form("create_draft", clear_on_submit=True):
            selected_channel = st.selectbox("Channel", list(options))
            title = st.text_input("Video Title")
            topic = st.text_input("Topic / Idea")
            script = st.text_area("Script or Content Notes", height=150)
            if st.form_submit_button("📥 Submit Draft for Approval"):
                if not title.strip() or not topic.strip():
                    st.error("Video title and topic are required.")
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    db_execute(
                        """INSERT INTO content
                           (channel_id, title, topic, script, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (options[selected_channel], title.strip(), topic.strip(), script, now, now),
                    )
                    st.success("Draft added to review queue.")
                    st.rerun()

    st.divider()
    st.subheader("Review and Correct Content")
    if not items:
        st.info("No drafts in the queue yet.")
    else:
        content_map = {
            f"#{item['id']} | {item['title']} | {item['status']}": item for item in items
        }
        chosen_item = st.selectbox("Select a Draft", list(content_map))
        item = content_map[chosen_item]
        st.write(f"**Channel:** {item['channel_name']} ({item['platform']})")
        st.write(f"**Current Status:** {item['status']}")
        st.write(f"**Topic:** {item['topic']}")
        if item["correction"]:
            st.warning(f"Last Correction Request: {item['correction']}")

        # Review the actual saved render before making an approval decision.
        has_video_table = db_query("SELECT name FROM sqlite_master WHERE type='table' AND name='content_video'")
        if has_video_table:
            previews = db_query("SELECT * FROM content_video WHERE content_id=?", (item["id"],))
            if previews:
                preview_path = Path(previews[0]["video_path"])
                if preview_path.is_file():
                    st.video(preview_path.read_bytes())
                    st.download_button("Download review MP4", preview_path.read_bytes(),
                                       file_name=preview_path.name, mime="video/mp4", key="review_video_download")
                else:
                    st.warning("Saved video is missing. Render it again before video approval.")

        # Production subtitles are tied to the same rendered file and script version.
        if has_video_table and previews:
            has_exports = db_query("SELECT name FROM sqlite_master WHERE type='table' AND name='production_exports'")
            if has_exports:
                exports = db_query("SELECT * FROM production_exports WHERE content_id=? AND video_path=?",
                                   (item["id"], previews[0]["video_path"]))
                if exports:
                    export = exports[0]
                    st.caption("Production type: " + export["mode"].upper() + " · scene-timed bilingual captions")
                    if export["mode"] == "mock":
                        st.warning("MOCK TEST: synthetic motion and test tone; no real AI footage or spoken Bangla.")
                    for language in ("bn", "en"):
                        subtitle = Path(export["video_path"]).with_name(f"subtitles.{language}.srt")
                        if subtitle.is_file():
                            st.download_button(f"Review {language.upper()} subtitles", subtitle.read_bytes(),
                                               file_name=subtitle.name, mime="application/x-subrip",
                                               key=f"review_srt_{language}_{item['id']}")

        with st.form(f"review_{item['id']}"):
            updated_script = st.text_area("Edit Script / Notes", value=item["script"], height=220)
            correction = st.text_area(
                "Correction Instructions (required when requesting changes)",
                value=item["correction"], height=100,
            )
            decision = st.radio(
                "Review Decision",
                ["Save Draft", "Request Changes", "Submit for Review", "Approve"],
            )
            if st.form_submit_button("💾 Save Review Decision"):
                if decision == "Request Changes" and not correction.strip():
                    st.error("Write your correction instructions first.")
                else:
                    statuses = {
                        "Save Draft": "Draft",
                        "Request Changes": "Changes requested",
                        "Submit for Review": "Awaiting review",
                        "Approve": "Approved",
                    }
                    if updated_script != item["script"]:
                        # An old video cannot represent a newly edited script.
                        if has_video_table:
                            db_execute("DELETE FROM content_video WHERE content_id=?", (item["id"],))
                        if decision == "Approve":
                            st.error("Script changed. Saved as awaiting review; regenerate the video before approving it.")
                            statuses[decision] = "Awaiting review"
                    db_execute(
                        """UPDATE content SET script=?, correction=?, status=?, updated_at=?
                           WHERE id=?""",
                        (
                            updated_script, correction.strip(), statuses[decision],
                            datetime.now().strftime("%Y-%m-%d %H:%M"), item["id"],
                        ),
                    )
                    st.success(f"Saved. Status: {statuses[decision]}")
                    st.rerun()


with tab_ai:
    st.subheader("🤖 AI Script + Bangla Voice Production")
    st.caption("Select a draft → Generate / revise script → Create voice MP3 → Review → Approve")

    script_ready = bool(get_secret("OPENAI_API_KEY"))
    voice_ready = bool(get_secret("AZURE_SPEECH_KEY")) and bool(
        get_secret("AZURE_SPEECH_REGION")
    )
    st.write("Script Agent:", "🔑 Key configured" if script_ready else "🔒 API key required")
    st.write("Bangla Voice Agent:", "🔑 Credentials configured" if voice_ready else "🔒 Azure credentials required")

    if not items:
        st.info("Create your first content draft in the Approval Dashboard.")
    else:
        content_choices = {
            f"#{row['id']} — {row['title']} — {row['status']}": row
            for row in items
        }
        item_label = st.selectbox("Draft to produce", list(content_choices), key="ai_selected")
        current = content_choices[item_label]
        parent_channel = next(
            (channel for channel in channels if channel["id"] == current["channel_id"]),
            None,
        )
        st.write(f"**Channel:** {current['channel_name']}")
        if current["correction"]:
            st.write("**Correction instructions:**", current["correction"])

        seconds = st.select_slider(
            "Target narration length", options=[30, 60, 90, 120, 180], value=90
        )
        if st.button("✨ Generate or revise Bangla script", disabled=not script_ready):
            if parent_channel is None:
                st.error("Channel not found.")
            else:
                try:
                    with st.spinner("AI is writing the Bangla narration..."):
                        narration = create_narration(current, parent_channel, seconds)
                    db_execute(
                        """UPDATE content SET script=?, status='Awaiting review', updated_at=?
                           WHERE id=?""",
                        (narration, datetime.now().strftime("%Y-%m-%d %H:%M"), current["id"]),
                    )
                    # A regenerated script invalidates the previous video preview.
                    if db_query("SELECT name FROM sqlite_master WHERE type='table' AND name='content_video'"):
                        db_execute("DELETE FROM content_video WHERE content_id=?", (current["id"],))
                    st.success("Script generated. Review it before approval.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Script generation failed: {type(exc).__name__}: {exc}")

        st.subheader("Narration preview")
        if current["script"]:
            st.text_area("Current narration / notes (edit in Approval Dashboard)", current["script"], height=230, disabled=True)
        else:
            st.warning("This draft has no script yet. Generate one first.")

        voice_label = st.selectbox("Bangladesh Bangla voice", list(VOICE_CHOICES))
        selected_voice = VOICE_CHOICES[voice_label]
        if st.button(
            "🎙️ Generate Bangla MP3 voiceover",
            disabled=not (voice_ready and bool(current["script"].strip())),
        ):
            try:
                with st.spinner("Generating Bangla narration audio..."):
                    audio_path = create_bangla_voice(
                        current["script"], current["id"], selected_voice
                    )
                db_execute(
                    """INSERT INTO content_audio
                       (content_id, audio_path, narration_hash, voice_name, created_at)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(content_id) DO UPDATE SET
                       audio_path=excluded.audio_path,
                       narration_hash=excluded.narration_hash,
                       voice_name=excluded.voice_name,
                       created_at=excluded.created_at""",
                    (
                        current["id"], audio_path, script_digest(current["script"]),
                        selected_voice, datetime.now().strftime("%Y-%m-%d %H:%M"),
                    ),
                )
                db_execute(
                    "UPDATE content SET status='Awaiting review', updated_at=? WHERE id=?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M"), current["id"]),
                )
                st.success("Bangla MP3 generated. Listen below and review it.")
                st.rerun()
            except Exception as exc:
                st.error(f"Voice generation failed: {type(exc).__name__}: {exc}")

        audio_rows = db_query(
            "SELECT * FROM content_audio WHERE content_id=?", (current["id"],)
        )
        if audio_rows:
            audio_info = audio_rows[0]
            audio_file = Path(audio_info["audio_path"])
            if audio_info["narration_hash"] != script_digest(current["script"]):
                st.warning(
                    "The script has changed since this recording. Regenerate the voice."
                )
            elif audio_file.is_file():
                mp3_bytes = audio_file.read_bytes()
                st.audio(mp3_bytes, format="audio/mp3")
                st.download_button(
                    "⬇️ Download Bangla MP3",
                    data=mp3_bytes,
                    file_name=audio_file.name,
                    mime="audio/mpeg",
                )
            else:
                st.warning("The MP3 file is no longer available in this Codespace.")

        st.divider()
        st.info(
            "AI generation never publishes anything. After listening, use "
            "Approval Dashboard to request corrections or approve the draft. "
            "Demo MP4 creation is available in Video Studio. Posting is not enabled."
        )

st.divider()
st.caption("© 2026 REDPAD AI Studio | Human approval required before publishing")

with tab_video:
    from redpad_video_studio import show_video_studio
    show_video_studio(DB_PATH, MEDIA_DIR)
    st.divider()
    from redpad_pipeline.ui import show_production_studio
    show_production_studio(DB_PATH, MEDIA_DIR, get_secret)
