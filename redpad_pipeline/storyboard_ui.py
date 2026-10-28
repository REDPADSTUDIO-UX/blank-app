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
        notes = st.text_area("Director / sound / lighting notes", value=shot["notes"], height=90)
        upload = st.file_uploader("Optional image reference (JPEG/PNG/WEBP, max 5 MB)",
                                  type=["jpg", "jpeg", "png", "webp"],
                                  key=f"sb_reference_{selected}_{index}_{board['revision']}")
        save_shot = st.form_submit_button("Save Shot", disabled=not fresh)
    if save_shot:
        try:
            updated = {**shot, "narration": narration, "visual": visual,
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
    st.caption("Export is for manual review/production planning; it does not trigger video generation. "
               "Local image references require durable storage before deployment.")
