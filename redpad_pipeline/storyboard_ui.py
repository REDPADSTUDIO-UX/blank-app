"""Streamlit Storyboard Studio: script -> editable shot cards -> review/export.

All images rendered here are free schematic sketches or user-provided files.
No model, Google, billing, upload or YouTube call is made.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import streamlit as st

from .storyboard import (
    SHOT_TYPES, CAMERA_MOVES, StoryboardError, approve_board, draft_board,
    export_board, initialize, is_current, load_board, load_reference, save_board,
    save_reference, shot_prompt, sketch_frame,
)


def show_storyboard(db_path: Path, media_dir: Path):
    st.subheader("🎬 Storyboard Studio — Shot-by-Shot")
    st.caption("Existing Bangla script → offline shot cards → visual sketches → manual shot direction → human approval.")
    st.info("Storyboard frames are FREE composition sketches, not AI-generated images. No paid API, publishing or deployment.")
    initialize(db_path)
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""SELECT c.id, c.title, c.script, c.status, ch.name AS channel_name
            FROM content c JOIN channels ch ON ch.id=c.channel_id ORDER BY c.id DESC""").fetchall()
    if not rows:
        st.warning("Create a script or draft in Approval Dashboard first.")
        return
    selected = st.selectbox(
        "Storyboard source script",
        [int(row["id"]) for row in rows],
        format_func=lambda cid: next(
            f"#{row['id']} · {row['title']} · {row['channel_name']}"
            for row in rows if row["id"] == cid
        ), key="sb_content",
    )
    record = next(row for row in rows if row["id"] == selected)
    if not record["script"].strip():
        st.warning("This draft has no script. Add a script in Approval Dashboard.")
        return
    board = load_board(db_path, selected)
    if board is None:
        aspect = st.radio("Storyboard framing", ["16:9", "9:16"], horizontal=True, key="sb_new_ratio")
        if st.button("Create Offline Storyboard", key="sb_create"):
            try:
                draft = draft_board(selected, record["title"], record["script"], aspect)
                save_board(db_path, draft, 0)
                st.rerun()
            except StoryboardError as error:
                st.error(str(error))
        return
    fresh = is_current(board, record["script"])
    if not fresh:
        st.error("SCRIPT CHANGED: this board belongs to an older draft. Approval/export are locked.")
        confirm = st.checkbox("I understand regenerating replaces the previous shot directions.",
                              key=f"sb_regen_confirm_{selected}")
        if st.button("Regenerate From Current Script", disabled=not confirm, key="sb_regenerate"):
            try:
                draft = draft_board(selected, record["title"], record["script"], board["ratio"])
                save_board(db_path, draft, board["revision"])
                st.rerun()
            except StoryboardError as error:
                st.error(str(error))
        return

    st.write(
        f"**{board['title']}** · {len(board['shots'])} shots · "
        f"{sum(x['seconds'] for x in board['shots'])}s planned · "
        f"{board['ratio']} · Revision {board['revision']}"
    )
    if board["review_status"] == "Approved":
        st.success("Storyboard APPROVED for this exact script version. No video has been generated or published.")
    else:
        st.caption("Storyboard status: Draft — shot changes need your review.")

    with st.expander("Character, location and look continuity", expanded=False):
        with st.form(f"sb_bible_{selected}_{board['revision']}"):
            character = st.text_area("Character continuity", value=board["character_bible"],
                                     help="Recurring people, wardrobe, hair, age and distinguishing features.")
            location = st.text_area("Location continuity", value=board["location_bible"],
                                    help="Set details to maintain between shots.")
            look = st.text_area("Visual style / lighting", value=board["look_bible"])
            save_bible = st.form_submit_button("Save Continuity Notes", disabled=not fresh)
        if save_bible:
            try:
                updated = dict(board, character_bible=character, location_bible=location, look_bible=look)
                save_board(db_path, updated, board["revision"])
                st.rerun()
            except StoryboardError as error:
                st.error(str(error))

    st.markdown("**Storyboard contact sheet**")
    st.caption("Schematic frames show rough composition. Upload your own image on a shot to replace its sketch.")
    page_size = 9
    pages = (len(board["shots"]) + page_size - 1) // page_size
    page = st.selectbox("Contact sheet page", range(1, pages + 1), key=f"sb_page_{selected}") if pages > 1 else 1
    shown = board["shots"][(page - 1)*page_size: page*page_size]
    for start in range(0, len(shown), 3):
        columns = st.columns(3)
        for column, shot in zip(columns, shown[start:start + 3]):
            with column:
                reference = load_reference(media_dir, shot["reference_path"])
                st.image(reference if reference is not None else sketch_frame(shot, board["ratio"]),
                         use_container_width=True)
                st.markdown(f"**Shot {shot['number']:02d} — {shot['shot_type']}**")
                st.caption(f"{shot['camera']} · {shot['seconds']}s")
                st.write(shot["visual"][:200] + ("…" if len(shot["visual"]) > 200 else ""))

    index = st.selectbox("Edit shot", range(len(board["shots"])),
                         format_func=lambda i: f"Shot {i+1:02d} · {board['shots'][i]['shot_type']}",
                         key=f"sb_shot_{selected}")
    shot = board["shots"][index]
    with st.form(f"sb_edit_{selected}_{index}_{board['revision']}"):
        narration = st.text_area("Narration / dialogue", value=shot["narration"], height=105)
        visual = st.text_area("Visual direction / frame action", value=shot["visual"], height=115)
        english = st.text_area("English subtitle translation (needed for Live AI Production)",
                               value=shot.get("english", ""), height=75)
        first, second, third = st.columns(3)
        with first:
            shot_type = st.selectbox("Shot size", SHOT_TYPES,
                                     index=SHOT_TYPES.index(shot["shot_type"]))
        with second:
            camera = st.selectbox("Camera movement", CAMERA_MOVES,
                                  index=CAMERA_MOVES.index(shot["camera"]))
        with third:
            seconds = st.number_input("Duration (seconds)", min_value=2, max_value=20,
                                      value=shot["seconds"], step=1)
        sfx_options = ["none", "whoosh", "impact", "chime"]
        sfx = st.selectbox("Sound effect", sfx_options,
                            index=sfx_options.index(shot.get("sfx", "none")))
        notes = st.text_area("Director / sound / lighting notes", value=shot["notes"], height=90)
        upload = st.file_uploader("Optional image reference (JPEG/PNG/WEBP, max 5 MB)",
                                  type=["jpg", "jpeg", "png", "webp"],
                                  key=f"sb_reference_{selected}_{index}_{board['revision']}")
        save_shot = st.form_submit_button("Save Shot", disabled=not fresh)
    if save_shot:
        try:
            updated = {**shot, "narration": narration, "visual": visual,
                       "english": english, "sfx": sfx,
                       "shot_type": shot_type, "camera": camera,
                       "seconds": int(seconds), "notes": notes}
            if upload is not None:
                updated["reference_path"] = save_reference(
                    media_dir, selected, shot["number"], upload.getvalue(), board["ratio"]
                )
            revised = dict(board, shots=[dict(x) for x in board["shots"]])
            revised["shots"][index] = updated
            save_board(db_path, revised, board["revision"])
            st.rerun()
        except StoryboardError as error:
            st.error(str(error))

    with st.expander("Shot production prompt", expanded=False):
        st.code(shot_prompt(board, shot), language=None)

    st.divider()
    st.download_button(
        "Download Shot-by-Shot Storyboard JSON", export_board(board),
        file_name=f"redpad-storyboard-{selected}.json", mime="application/json",
        key=f"sb_export_{selected}"
    )
    if board["review_status"] == "Approved":
        st.caption("Any saved shot or continuity edit returns this storyboard to Draft.")
    else:
        if st.button("Approve Storyboard", key="sb_approve"):
            try:
                approve_board(db_path, selected, board["revision"])
                st.rerun()
            except StoryboardError as error:
                st.error(str(error))
    st.divider()
    st.subheader("🎞️ Storyboard → Offline Motion Animatic")
    st.caption("Animates approved storyboard sketches or your reference photos with camera moves, "
               "burned Bangla captions, soundtrack and cut cues. It does NOT call generative AI.")
    if board["review_status"] != "Approved":
        st.info("First approve the current storyboard. Rendering requires separate MP4 approval afterward.")
    else:
        from .storyboard_render import render_approved_board, AnimaticError
        with st.form(f"sb_animatic_{selected}_{board['revision']}"):
            mood = st.selectbox("Soundtrack preset", ["Suspense / Horror", "Calm / Documentary"],
                                key=f"sb_mood_{selected}")
            st.caption("Optional narration: upload a recorded Bangla MP3/WAV if you want spoken dialogue. "
                       "Without it, the video has captions and music but NO spoken voice.")
            recorded = st.file_uploader("Optional full narration audio (MP3/WAV, max 20 MB)",
                                        type=["mp3", "wav"], key=f"sb_voice_{selected}")
            licensed_music = st.file_uploader("Optional licensed music (MP3/WAV, max 20 MB)",
                                              type=["mp3", "wav"], key=f"sb_music_{selected}")
            requested = st.form_submit_button("Render Approved Storyboard → MP4",
                                               disabled=not fresh)
        if requested:
            try:
                if (recorded is not None and recorded.size > 20 * 1024 * 1024
                        or licensed_music is not None and licensed_music.size > 20 * 1024 * 1024):
                    raise AnimaticError("Uploaded audio must be 20 MB or smaller.")
                with st.spinner("Rendering approved shot-by-shot storyboard; no API calls…"):
                    result = render_approved_board(
                        db_path, media_dir, selected,
                        narration_audio=recorded.getvalue() if recorded is not None else None,
                        music_audio=licensed_music.getvalue() if licensed_music is not None else None,
                        mood=mood,
                    )
                st.session_state["sb_render_notice"] = (
                    f"Animatic ready: {result['shots']} shots, {result['seconds']}s. "
                    "Open Approval Dashboard for final review."
                )
                st.rerun()
            except (StoryboardError, AnimaticError) as error:
                st.error(str(error))
            except Exception:
                st.error("Offline video rendering failed. Source draft and approvals were not changed.")
        if "sb_render_notice" in st.session_state:
            st.success(st.session_state.pop("sb_render_notice"))
        with sqlite3.connect(db_path) as db:
            table = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='content_video'"
            ).fetchone()
            output = db.execute(
                "SELECT video_path, voice_included FROM content_video WHERE content_id=?",
                (selected,),
            ).fetchone() if table else None
        if output and "storyboard_renders" in Path(output[0]).parts:
            clip = Path(output[0])
            if clip.is_file():
                st.warning("OFFLINE ANIMATIC: uploaded images/sketches animated by FFmpeg. "
                           "Not AI-generated video footage.")
                st.video(clip.read_bytes())
                st.download_button("Download Storyboard Animatic MP4", clip.read_bytes(),
                                   file_name=f"redpad-storyboard-{selected}.mp4", mime="video/mp4",
                                   key=f"sb_mp4_{selected}")
                subs = clip.with_name("subtitles.bn.srt")
                if subs.is_file():
                    st.download_button("Download Bangla Storyboard SRT", subs.read_bytes(),
                                       file_name=f"redpad-storyboard-{selected}.bn.srt",
                                       mime="application/x-subrip", key=f"sb_srt_{selected}")
                if not output[1]:
                    st.caption("This animatic has NO spoken Bangla narration. "
                               "Upload recorded audio to add real voice.")
            else:
                st.warning("Saved animatic file missing from local storage. Do not deploy without a backup.")
    st.caption("The animatic is a separate free review path. "
               "Generative image/video provider footage and automatic Bangla neural voice "
               "still require supported model access and explicit spend approval.")
