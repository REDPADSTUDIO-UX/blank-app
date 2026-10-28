"""YouTube connection vault and owner-reviewed publishing plans.

This release has NO live video-write transport. Dry runs cannot reach Google.
OAuth uses read-only channel scope; upload permission is deliberately deferred.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager, closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from zoneinfo import ZoneInfo

import requests
from cryptography.fernet import Fernet, InvalidToken

NISHIKOTHA_ID = "UCtbHkj0GwJxjXZWbItDAyuQ"
NISHIKOTHA_NAME = "নিশিকথা"
READ_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
DHAKA = ZoneInfo("Asia/Dhaka")


class YouTubeError(ValueError):
    """Safe messages only. Never interpolate provider bodies or credentials."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def channel_id(value):
    if not re.fullmatch(r"UC[A-Za-z0-9_-]{22}", value or ""):
        raise YouTubeError("Enter a valid YouTube Channel ID.")
    return value


@dataclass(repr=False)
class OAuthConfig:
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    database_url: str = ""
    encryption_key: str = ""
    owner_password: str = ""
    owner_gate: bool = False

    @classmethod
    def load(cls, get):
        return cls(*(str(get(k) or "") for k in (
            "GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET",
            "GOOGLE_OAUTH_REDIRECT_URI", "REDPAD_YOUTUBE_DATABASE_URL",
            "REDPAD_YOUTUBE_TOKEN_KEY", "REDPAD_DASHBOARD_PASSWORD")),
            owner_gate=str(get("REDPAD_REQUIRE_PREVIEW_LOGIN")).lower() == "true")

    def blockers(self):
        missing = []
        if not self.owner_gate or not self.owner_password:
            missing.append("Private owner dashboard authentication")
        if not self.client_id or not self.client_secret:
            missing.append("Google Cloud Web OAuth client ID and secret")
        p = urlsplit(self.redirect_uri)
        if (p.scheme != "https" or not p.hostname or p.username or p.password
                or p.query or p.fragment or p.path not in ("", "/")):
            missing.append("Registered HTTPS callback URL at the dashboard root")
        if not self.database_url.startswith(("postgresql://", "postgres://")):
            missing.append("Durable PostgreSQL connection vault")
        try:
            Fernet(self.encryption_key.encode())
        except (ValueError, TypeError):
            missing.append("Valid server-side Fernet token encryption key")
        return missing

    def require(self):
        if self.blockers():
            raise YouTubeError("Google connection is locked until secure server setup is complete.")


class Store:
    """Small transactional document store; SQLite accepts mock records ONLY.

    Live records and encrypted credentials require external PostgreSQL. CAS
    revisions prevent double callback consumption and concurrent approvals.
    """
    def __init__(self, location, live=False):
        self.location, self.live = str(location), live
        if live and not self.location.startswith(("postgresql://", "postgres://")):
            raise YouTubeError("Live OAuth requires external PostgreSQL; local tokens are forbidden.")
        with self.db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS redpad_youtube_records (
                record_key TEXT PRIMARY KEY, data TEXT NOT NULL, revision INTEGER NOT NULL)""")

    @contextmanager
    def db(self):
        if self.live:
            import psycopg
            conn = psycopg.connect(self.location, connect_timeout=5, sslmode="require")
        else:
            conn = sqlite3.connect(self.location, timeout=10)
        try:
            yield _DB(conn, self.live)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get(self, key):
        with self.db() as db:
            row = db.execute("SELECT data,revision FROM redpad_youtube_records WHERE record_key=?", (key,)).fetchone()
        return (json.loads(row[0]), row[1]) if row else (None, 0)

    def put(self, key, data, revision):
        # A local dry-run database must never become a credential cache.
        if not self.live and (key.startswith("oauth:") or "vault" in data):
            raise YouTubeError("Credential storage is forbidden in the mock database.")
        with self.db() as db:
            if revision == 0:
                changed = db.execute("""INSERT INTO redpad_youtube_records VALUES (?,?,1)
                    ON CONFLICT(record_key) DO NOTHING""", (key, canonical(data))).rowcount
            else:
                changed = db.execute("""UPDATE redpad_youtube_records SET data=?,revision=revision+1
                    WHERE record_key=? AND revision=?""", (canonical(data), key, revision)).rowcount
        if changed != 1:
            raise YouTubeError("This record changed in another session. Refresh and review again.")

    def list(self, prefix):
        with self.db() as db:
            rows = db.execute("SELECT data FROM redpad_youtube_records WHERE record_key LIKE ? ORDER BY record_key",
                              (prefix + "%",)).fetchall()
        return [json.loads(row[0]) for row in rows]


class _DB:
    def __init__(self, conn, live):
        self.conn, self.live = conn, live

    def execute(self, sql, params=()):
        return self.conn.execute(sql.replace("?", "%s") if self.live else sql, params)


def browser_binding(cookie):
    """Normalize Streamlit/Tornado's remasked XSRF cookie across redirects.

    We use only a hash of the random token as the browser binding. Fail closed
    on absent or unfamiliar cookie formats; no internal Streamlit imports.
    """
    try:
        value = cookie.strip("\"'")
        if value.startswith("2|"):
            _, mask_hex, masked_hex, stamp = value.split("|")
            mask, masked = bytes.fromhex(mask_hex), bytes.fromhex(masked_hex)
            if len(mask) != 4 or len(masked) != 16 or not stamp.isdigit():
                raise ValueError()
            raw = bytes(b ^ mask[i % 4] for i, b in enumerate(masked))
        else:
            raw = bytes.fromhex(value)
            if len(raw) != 16:
                raise ValueError()
        return hashlib.sha256(raw).hexdigest()
    except (AttributeError, ValueError):
        raise YouTubeError("Browser security cookie is unavailable. Reopen the private dashboard.") from None


class GoogleOAuth:
    def __init__(self, config, store, http=None, clock=time.time):
        config.require()
        if not store.live:
            raise YouTubeError("Live Google authorization cannot use a mock store.")
        self.config, self.store = config, store
        self.cipher = Fernet(config.encryption_key.encode())
        self.http, self.clock = http or requests.Session(), clock

    def seal(self, data):
        return self.cipher.encrypt(canonical(data).encode()).decode()

    def unseal(self, data):
        try:
            return json.loads(self.cipher.decrypt(data.encode()))
        except (InvalidToken, ValueError, TypeError):
            raise YouTubeError("Connection vault key is invalid or the record is damaged.") from None

    def call(self, method, url, **kwargs):
        try:
            r = self.http.request(method, url, timeout=25, allow_redirects=False, **kwargs)
            if not 200 <= r.status_code < 300:
                if r.status_code == 429 or r.status_code == 403:
                    raise YouTubeError("Google permission or quota denied. No automatic retry was made.")
                if r.status_code in (400, 401):
                    raise YouTubeError("Google authorization expired or was refused. Reconnect the channel.")
                raise YouTubeError("Google request failed. No automatic retry was made.")
            return r.json() if r.content else {}
        except requests.RequestException:
            raise YouTubeError("Google connection failed. Reconnect or try again later.") from None
        except (ValueError, TypeError):
            raise YouTubeError("Google returned an invalid response.") from None

    def begin(self, local_channel, expected_channel, cookie, authenticated):
        if not authenticated:
            raise YouTubeError("Owner sign-in is required.")
        expected_channel = channel_id(expected_channel)
        state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        data = dict(browser=browser_binding(cookie), owner=digest(self.config.owner_password),
                    local_channel=int(local_channel), expected=expected_channel, verifier=verifier,
                    expires=self.clock()+600, used=False)
        self.store.put("oauth:"+digest(state), {"vault": self.seal(data)}, 0)
        return AUTH_URL + "?" + urlencode(dict(client_id=self.config.client_id,
            redirect_uri=self.config.redirect_uri, response_type="code", scope=READ_SCOPE,
            access_type="offline", prompt="consent", state=state,
            code_challenge=challenge, code_challenge_method="S256"))

    def finish(self, state, code, cookie, authenticated, denied=False):
        if not authenticated:
            raise YouTubeError("Owner sign-in is required before connecting.")
        key = "oauth:" + digest(state)
        wrapped, rev = self.store.get(key)
        if not wrapped:
            raise YouTubeError("Unknown Google authorization state. Start Connect again.")
        data = self.unseal(wrapped["vault"])
        if (data["used"] or data["expires"] < self.clock()
                or not hmac.compare_digest(data["browser"], browser_binding(cookie))
                or not hmac.compare_digest(data["owner"], digest(self.config.owner_password))):
            raise YouTubeError("Google authorization state expired, was used, or belongs to another browser.")
        # Consume before any network call. Ambiguous exchanges are never retried.
        data["used"] = True
        self.store.put(key, {"vault": self.seal(data)}, rev)
        if denied or not code:
            raise YouTubeError("Google permission was declined. The channel is not connected.")
        tokens = self.call("POST", TOKEN_URL, data=dict(code=code, client_id=self.config.client_id,
            client_secret=self.config.client_secret, redirect_uri=self.config.redirect_uri,
            grant_type="authorization_code", code_verifier=data["verifier"]))
        if (READ_SCOPE not in str(tokens.get("scope", "")).split()
                or not tokens.get("access_token") or not tokens.get("refresh_token")):
            raise YouTubeError("Read permission or offline authorization was not granted. Connect again.")
        identity = self.identity(tokens["access_token"])
        if identity["id"] != data["expected"]:
            raise YouTubeError("Google returned a different channel. Select the intended Brand Account and reconnect.")
        cid = identity["id"]
        _, revision = self.store.get("channel:" + cid)
        self.store.put("channel:" + cid, dict(channel_id=cid, name=identity["name"],
            handle=identity["handle"], local_channel=data["local_channel"], mode="live",
            connection_version=secrets.token_hex(16),
            connected=True, connected_at=self.clock(), scope=READ_SCOPE,
            vault=self.seal(dict(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"],
                                 expires=self.clock()+int(tokens.get("expires_in", 3600))))), revision)
        return identity

    def identity(self, access):
        result = self.call("GET", CHANNELS_URL, params={"part":"snippet", "mine":"true"},
                           headers={"Authorization":"Bearer " + access})
        rows = result.get("items", [])
        if len(rows) != 1:
            raise YouTubeError("Select exactly one YouTube channel during Google authorization.")
        item = rows[0]
        return dict(id=channel_id(item.get("id")), name=item.get("snippet", {}).get("title", ""),
                    handle=item.get("snippet", {}).get("customUrl", ""))

    def access_token(self, cid):
        row, rev = self.store.get("channel:" + channel_id(cid))
        if not row or not row.get("connected") or row.get("mode") != "live":
            raise YouTubeError("Channel is disconnected.")
        tokens = self.unseal(row["vault"])
        if tokens["expires"] < self.clock()+60:
            try:
                fresh = self.call("POST", TOKEN_URL, data=dict(client_id=self.config.client_id,
                    client_secret=self.config.client_secret, refresh_token=tokens["refresh_token"],
                    grant_type="refresh_token"))
                if not fresh.get("access_token"):
                    raise YouTubeError("Google refresh failed. Reconnect.")
                tokens.update(access_token=fresh["access_token"], expires=self.clock()+int(fresh.get("expires_in", 3600)))
                row["vault"] = self.seal(tokens)
                self.store.put("channel:"+cid, row, rev)
            except YouTubeError:
                # Keep the encrypted refresh token solely so owner can revoke it.
                row["connected"] = False
                self.store.put("channel:"+cid, row, rev)
                raise
        return tokens["access_token"]

    def disconnect(self, cid):
        row, rev = self.store.get("channel:" + channel_id(cid))
        if not row:
            return
        if row.get("vault"):
            token = self.unseal(row["vault"])["refresh_token"]
            # Do not claim revocation succeeded on HTTP/network failure.
            self.call("POST", REVOKE_URL, data={"token": token})
        row.pop("vault", None)
        row["connected"] = False
        self.store.put("channel:"+cid, row, rev)

    def forget(self, cid):
        """Remove local credentials even when Google revocation is unavailable."""
        row, rev = self.store.get("channel:"+channel_id(cid))
        if row:
            row.pop("vault", None)
            row["connected"] = False
            self.store.put("channel:"+cid, row, rev)


def mock_connect(store, local_channel, cid=NISHIKOTHA_ID):
    if store.live:
        raise YouTubeError("Mock connection must use the separate dry-run store.")
    cid = channel_id(cid)
    row, rev = store.get("channel:"+cid)
    store.put("channel:"+cid, dict(channel_id=cid, name=NISHIKOTHA_NAME if cid == NISHIKOTHA_ID else "Mock channel",
        mode="mock", connected=True, local_channel=int(local_channel), connection_version=secrets.token_hex(16)), rev)


def publish_time(local_date, local_time, now=None):
    dt = datetime.combine(local_date, local_time, tzinfo=DHAKA).astimezone(timezone.utc)
    if dt <= (now or datetime.now(timezone.utc)):
        raise YouTubeError("Publication must be in the future; past dates could publish immediately.")
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def snapshot(db_path, media_root, content_id):
    """Bind approval to current script, render bytes, revision and internal channel."""
    with closing(sqlite3.connect(db_path)) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM content WHERE id=?", (int(content_id),)).fetchone()
        if not row or row["status"] != "Approved":
            raise YouTubeError("Approve the current draft in Approval Dashboard first.")
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        video = db.execute("SELECT * FROM content_video WHERE content_id=?", (content_id,)).fetchone() if "content_video" in tables else None
        export = db.execute("SELECT * FROM production_exports WHERE content_id=?", (content_id,)).fetchone() if "production_exports" in tables else None
        if not video:
            raise YouTubeError("No final rendered MP4 is attached to this draft.")
        path = Path(video["video_path"]).resolve()
        if not path.is_relative_to(Path(media_root).resolve()) or path.suffix.lower() != ".mp4" or not path.is_file():
            raise YouTubeError("Final MP4 is missing or outside the studio media folder.")
        if export and (export["video_path"] != video["video_path"] or export["script_hash"] != digest(row["script"])):
            raise YouTubeError("Script and render no longer match. Render and review again.")
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(1024*1024):
                hasher.update(chunk)
        return dict(content_id=int(content_id), local_channel=row["channel_id"],
            script_hash=digest(row["script"]), updated_at=row["updated_at"],
            video_sha256=hasher.hexdigest(), video_path=str(path),
            render_mode=export["mode"] if export else "demo")


class Publishing:
    """Owner approvals, immutable requests, CAS execution, dry-run scheduler.

    There is deliberately no live API video write in this release. Even a
    connected Google account cannot bypass that release lock.
    """
    def __init__(self, store, source_db, media_root, clock=time.time):
        self.store, self.source_db, self.media_root, self.clock = store, source_db, media_root, clock

    def create(self, cid, content_id, title, description, schedule="", made_for_kids=False, synthetic=True):
        cid = channel_id(cid)
        conn, _ = self.store.get("channel:"+cid)
        if not conn or not conn.get("connected"):
            raise YouTubeError("Connect a channel first. A local channel record is not a Google connection.")
        snap = snapshot(self.source_db, self.media_root, content_id)
        if snap["local_channel"] != conn["local_channel"]:
            raise YouTubeError("This draft belongs to another internal channel.")
        if not title.strip() or len(title) > 100 or len(description.encode()) > 5000 or any(c in title for c in "<>"):
            raise YouTubeError("Use a title of 1–100 characters and description within 5000 UTF-8 bytes.")
        if schedule:
            self._future(schedule)
        body = dict(snippet=dict(title=title.strip(), description=description,
            categoryId="24", defaultLanguage="bn"), status=dict(privacyStatus="private",
            selfDeclaredMadeForKids=bool(made_for_kids), containsSyntheticMedia=bool(synthetic)))
        if schedule:
            body["status"]["publishAt"] = schedule
        plan = dict(channel_id=cid, snapshot=snap, body=body, mode=conn["mode"],
                    connection_version=conn["connection_version"])
        fingerprint = digest(canonical(plan))
        key = "request:"+fingerprint
        old, _ = self.store.get(key)
        if not old:
            self.store.put(key, dict(id=fingerprint, plan=plan, state="awaiting_upload_approval",
                upload_approved=False, publication_approved=False, created_at=self.clock()), 0)
        return fingerprint

    def _future(self, schedule):
        try:
            dt = datetime.fromisoformat(schedule.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.timestamp() <= self.clock():
                raise ValueError()
        except (ValueError, TypeError):
            raise YouTubeError("Scheduled publication must be a future timezone-aware timestamp.") from None

    def current(self, request_id):
        row, rev = self.store.get("request:"+request_id)
        if not row:
            raise YouTubeError("Publishing request not found.")
        conn, _ = self.store.get("channel:"+row["plan"]["channel_id"])
        if (not conn or not conn.get("connected") or conn["mode"] != row["plan"]["mode"]
                or conn.get("connection_version") != row["plan"].get("connection_version")
                or conn["local_channel"] != row["plan"]["snapshot"]["local_channel"]):
            raise YouTubeError("Connection changed or was disconnected. Create a new request.")
        current = snapshot(self.source_db, self.media_root, row["plan"]["snapshot"]["content_id"])
        if current != row["plan"]["snapshot"]:
            raise YouTubeError("Draft or MP4 changed after review. Create a new request and approve again.")
        return row, rev

    def approve(self, request_id, owner_authenticated, upload=False, publication=False):
        if not owner_authenticated:
            raise YouTubeError("Owner authentication is required for approval.")
        row, rev = self.current(request_id)
        if row["state"] != "awaiting_upload_approval":
            raise YouTubeError("This request cannot be approved again.")
        schedule = row["plan"]["body"]["status"].get("publishAt")
        if not upload or (schedule and not publication):
            raise YouTubeError("Upload approval and separate scheduled-publication approval are required.")
        if schedule:
            self._future(schedule)
        row.update(upload_approved=True, publication_approved=bool(publication),
                   approved_at=self.clock(), state="approved")
        self.store.put("request:"+request_id, row, rev)

    def cancel(self, request_id):
        row, rev = self.store.get("request:"+request_id)
        if not row:
            raise YouTubeError("Publishing request not found.")
        row.update(state="cancelled", upload_approved=False, publication_approved=False)
        self.store.put("request:"+request_id, row, rev)

    def dry_run(self, request_id):
        row, rev = self.current(request_id)
        if self.store.live or row["plan"]["mode"] != "mock":
            raise YouTubeError("Dry-run execution requires an explicitly mock connection.")
        if row["state"] != "approved" or not row["upload_approved"]:
            raise YouTubeError("Owner upload approval is missing, cancelled or already used.")
        schedule = row["plan"]["body"]["status"].get("publishAt")
        if schedule:
            self._future(schedule)
            if not row["publication_approved"]:
                raise YouTubeError("Publication approval is missing.")
        row.update(state="dry_run_scheduled" if schedule else "dry_run_private", dry_run_at=self.clock())
        self.store.put("request:"+request_id, row, rev)
        return dict(dry_run=True, network_calls=0, remote_video_id=None,
                    target_channel=row["plan"]["channel_id"], request_body=row["plan"]["body"])

    def tick(self):
        """Simulate due publishing. No timer/daemon or provider write is started."""
        changed = []
        for item in self.store.list("request:"):
            if item["state"] != "dry_run_scheduled":
                continue
            try:
                row, rev = self.current(item["id"])
                due = datetime.fromisoformat(row["plan"]["body"]["status"]["publishAt"].replace("Z", "+00:00")).timestamp()
                if row["publication_approved"] and due <= self.clock():
                    row["state"] = "dry_run_due"
                    self.store.put("request:"+row["id"], row, rev)
                    changed.append(row["id"])
            except YouTubeError:
                row, rev = self.store.get("request:"+item["id"])
                row.update(state="invalidated", upload_approved=False, publication_approved=False)
                self.store.put("request:"+item["id"], row, rev)
        return changed

    def execute_live(self, request_id):
        raise YouTubeError("Live upload and publication are locked in this release. No video was sent.")
