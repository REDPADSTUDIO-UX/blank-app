"""Additive Streamlit UI. Provider video writes are unavailable in this release."""
from datetime import datetime, timedelta, time
from pathlib import Path
import sqlite3
from contextlib import closing

import streamlit as st

from .youtube import (NISHIKOTHA_ID, NISHIKOTHA_NAME, DHAKA, OAuthConfig,
    Store, GoogleOAuth, Publishing, YouTubeError, mock_connect, publish_time)


def register_nishikotha(db_path):
    """Register existing remote channel locally; never create a YouTube channel."""
    with closing(sqlite3.connect(db_path)) as db, db:
        row = db.execute("SELECT id FROM channels WHERE name=? AND platform='YouTube'", (NISHIKOTHA_NAME,)).fetchone()
        if row:
            return row[0]
        return db.execute("""INSERT INTO channels(name,platform,niche,videos_per_day,publish_time)
            VALUES (?,'YouTube','বাংলা Horror — Nishikotha',0,'18:00')""", (NISHIKOTHA_NAME,)).lastrowid


def _cookie():
    return st.context.cookies.get("_streamlit_xsrf", st.context.cookies.get("_xsrf", ""))


def show_youtube(db_path, media_dir, get_secret):
    st.subheader("YouTube Connect & Publishing Review")
    st.warning("Live upload and publication are locked. All publishing tests here are MOCK / DRY RUN.")
    st.markdown(f"Existing channel: **নিশিকথা (Nishikotha)** · [Open YouTube](https://www.youtube.com/channel/{NISHIKOTHA_ID})")
    st.code(NISHIKOTHA_ID, language=None)
    config = OAuthConfig.load(get_secret)
    blockers = config.blockers()
    st.caption("Google Connect uses read-only channel permission. Upload permission is not requested in this release.")
    if blockers:
        st.info("Google connection setup pending: " + "; ".join(blockers))
    owner = bool(st.session_state.get("redpad_preview_authenticated", False))
    live_store = None
    if not blockers:
        try:
            live_store = Store(config.database_url, live=True)
        except Exception:
            st.error("Secure connection vault is unavailable. Google Connect is disabled.")

    # Handle the redirect only behind the existing private-owner gate. Clear
    # authorization codes before rendering any additional callback UI.
    if "state" in st.query_params and ("code" in st.query_params or "error" in st.query_params):
        state, code = st.query_params.get("state", ""), st.query_params.get("code", "")
        denied = "error" in st.query_params
        st.query_params.clear()
        if live_store is None:
            st.error("Secure Google connection setup is incomplete. No channel was connected.")
        else:
            try:
                identity = GoogleOAuth(config, live_store).finish(state, code, _cookie(), owner, denied)
                st.success("Google verified channel: " + identity["name"])
            except YouTubeError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Secure Google connection could not be saved. Reconnect after server setup is checked.")

    try:
        live_connections = live_store.list("channel:") if live_store else []
    except Exception:
        live_store = None
        live_connections = []
        st.error("Secure connection vault is unavailable. Google Connect is disabled.")
    target = next((c for c in live_connections if c["channel_id"] == NISHIKOTHA_ID), None)
    st.metric("Nishikotha Google connection", "Connected (read-only)" if target and target.get("connected") else "Not connected")
    st.caption("An existing YouTube channel, a local profile and a MOCK connection are three different states.")
    if st.button("Register Nishikotha in Studio (local only)", key="yt_register"):
        register_nishikotha(db_path)
        st.success("Existing Nishikotha channel registered locally. Google OAuth is still separate.")
        st.rerun()
    with closing(sqlite3.connect(db_path)) as db:
        channels = db.execute("SELECT id,name FROM channels WHERE platform='YouTube' ORDER BY id").fetchall()
    if not channels:
        st.info("Register Nishikotha locally or add a YouTube profile in Channel Manager to continue.")
        return
    internal = st.selectbox("Studio YouTube profile", [r[0] for r in channels],
        format_func=lambda cid: next(f"{r[1]} — #{cid}" for r in channels if r[0] == cid), key="yt_local")
    expected = st.text_input("Expected YouTube Channel ID", value=NISHIKOTHA_ID, key="yt_expected")

    if st.button("Prepare Google Connect", key="yt_connect", disabled=not (live_store and owner)):
        try:
            url = GoogleOAuth(config, live_store).begin(internal, expected, _cookie(), owner)
            st.session_state["yt_authorization_link"] = (internal, expected, url)
        except YouTubeError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Google Connect is unavailable until the secure vault is healthy.")
    link = st.session_state.get("yt_authorization_link")
    if link and link[:2] == (internal, expected):
        st.link_button("Continue to Google permission screen", link[2])
        st.caption("Choose the Nishikotha Brand Account. Only Google receives your Google password.")

    if live_connections:
        # Never send encrypted vault blobs, tokens or database URLs to widgets.
        st.dataframe([dict(Channel=c["name"], Channel_ID=c["channel_id"],
            Status="Connected (read-only)" if c.get("connected") else "Disconnected") for c in live_connections],
            hide_index=True)
        cid = st.selectbox("Google connection to manage", [c["channel_id"] for c in live_connections], key="yt_manage")
        if st.button("Refresh channel identity (read-only)", key="yt_refresh", disabled=not owner):
            try:
                oauth = GoogleOAuth(config, live_store)
                identity = oauth.identity(oauth.access_token(cid))
                if identity["id"] != cid:
                    raise YouTubeError("Google channel identity changed. Reconnect.")
                st.success("Google identity verified: " + identity["name"])
            except YouTubeError as exc:
                st.error(str(exc))
        revoke = st.checkbox("I approve disconnecting and revoking this Google connection", key="yt_revoke_confirm")
        if st.button("Disconnect Google connection", key="yt_disconnect", disabled=not (owner and revoke)):
            try:
                GoogleOAuth(config, live_store).disconnect(cid)
                st.success("Google access revoked; saved credentials removed.")
                st.rerun()
            except YouTubeError as exc:
                st.error(str(exc))
        forget = st.checkbox("Remove saved credentials locally if Google revocation is unavailable", key="yt_forget_confirm")
        if st.button("Forget saved credentials", key="yt_forget", disabled=not (owner and forget)):
            GoogleOAuth(config, live_store).forget(cid)
            st.warning("Saved credentials removed. Revoke remaining access in your Google Account if needed.")
            st.rerun()

    st.divider()
    st.subheader("Mock approval & scheduling workspace")
    st.caption("Separate local test records. No Google token, video upload, publication or background network job.")
    store = Store(Path(db_path).with_name("redpad_youtube_mock.db"))
    if st.button("Connect MOCK channel — no Google authorization", key="yt_mock_connect"):
        try:
            mock_connect(store, internal, expected)
            st.success("MOCK connection saved. Real Google connection status is unchanged.")
        except YouTubeError as exc:
            st.error(str(exc))
    mock, _ = store.get("channel:"+expected)
    st.write("Mock status:", "MOCK connected" if mock and mock.get("connected") else "Not connected")
    if mock and mock.get("connected") and st.button("Disconnect MOCK channel", key="yt_mock_disconnect"):
        mock["connected"] = False
        _, rev = store.get("channel:"+expected)
        store.put("channel:"+expected, mock, rev)
        st.rerun()

    with closing(sqlite3.connect(db_path)) as db:
        drafts = db.execute("SELECT id,title,status FROM content WHERE channel_id=? ORDER BY id DESC", (internal,)).fetchall()
    if not drafts:
        st.info("Create a free demo MP4 in Video Studio, then approve it in Approval Dashboard to test publishing plans.")
    else:
        draft = st.selectbox("Rendered draft for dry-run", [d[0] for d in drafts],
            format_func=lambda value: next(f"#{d[0]} {d[1]} — {d[2]}" for d in drafts if d[0] == value), key="yt_draft")
        with st.form("yt_plan"):
            title = st.text_input("YouTube title", value="নিশিকথা — প্রকাশনার পরীক্ষা", max_chars=100)
            description = st.text_area("YouTube description", value="MOCK / DRY RUN — no upload or publication.")
            schedule = st.checkbox("Schedule future publication in this dry-run")
            local_date = st.date_input("Publication date (Asia/Dhaka)", value=datetime.now(DHAKA).date()+timedelta(days=1))
            local_time = st.time_input("Publication time (Asia/Dhaka)", value=time(18, 0))
            kids = st.checkbox("Made for kids", value=False)
            synthetic = st.checkbox("Contains realistic altered or synthetic media", value=True)
            create = st.form_submit_button("Prepare dry-run publishing request")
        if create:
            try:
                stamp = publish_time(local_date, local_time) if schedule else ""
                rid = Publishing(store, db_path, media_dir).create(expected, draft, title, description, stamp, kids, synthetic)
                st.success("Request prepared for separate upload/publication approval. " + rid[:12])
            except YouTubeError as exc:
                st.error(str(exc))

    requests = [r for r in store.list("request:") if r["plan"]["channel_id"] == expected]
    if requests:
        chosen = st.selectbox("Publishing request", [r["id"] for r in requests],
            format_func=lambda rid: next(f"{r['id'][:12]} — {r['state']}" for r in requests if r["id"] == rid), key="yt_request")
        row = next(r for r in requests if r["id"] == chosen)
        st.json(dict(mode="MOCK / DRY RUN", channel=row["plan"]["channel_id"],
            status=row["state"], reviewed_video_sha256=row["plan"]["snapshot"]["video_sha256"],
            request_body=row["plan"]["body"]))
        st.caption("Private upload permission does not authorize scheduled publication. Both must be reviewed separately.")
        upload = st.checkbox("Approve this exact private upload plan (MOCK only)", key="yt_upload_"+chosen)
        publication = st.checkbox("Approve public publication at the exact scheduled time (MOCK only)", key="yt_publish_"+chosen)
        service = Publishing(store, db_path, media_dir)
        if st.button("Save dry-run owner approval", key="yt_approve", disabled=row["state"] != "awaiting_upload_approval"):
            try:
                # Mock approval is a simulated owner decision. Real connection
                # actions above always require the private owner login.
                service.approve(chosen, True, upload, publication)
                st.success("MOCK approval recorded for this exact file, channel, metadata and schedule.")
                st.rerun()
            except YouTubeError as exc:
                st.error(str(exc))
        if st.button("Run approved dry-run — no upload", key="yt_run", disabled=row["state"] != "approved"):
            try:
                st.json(service.dry_run(chosen))
                st.success("DRY RUN passed: 0 network calls; no remote Video ID created.")
            except YouTubeError as exc:
                st.error(str(exc))
        if st.button("Cancel this publishing request", key="yt_cancel", disabled=row["state"] == "cancelled"):
            service.cancel(chosen)
            st.rerun()
        if st.button("Check due schedules (simulation only)", key="yt_tick"):
            st.write("Dry-run schedules due:", len(service.tick()))
        st.dataframe([dict(Request=r["id"][:12], State=r["state"],
            Channel=r["plan"]["channel_id"], Scheduled_UTC=r["plan"]["body"]["status"].get("publishAt", "Private only"))
            for r in store.list("request:")], hide_index=True)
    st.button("Live upload / publish — locked in this release", key="yt_live_write", disabled=True)
    st.caption("Reliable live publishing also needs durable source database/media storage, scoped upload consent, resumable upload recovery and Google project validation. No local timer guarantees are claimed on Render free hosting.")
