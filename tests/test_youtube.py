"""Offline authorization contracts and adversarial approval/scheduling tests.

No Google credentials and no external HTTP requests are used.
"""
import base64
import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, date, time, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet
from redpad_pipeline.youtube import (Store, OAuthConfig, GoogleOAuth, Publishing,
    YouTubeError, NISHIKOTHA_ID, READ_SCOPE, TOKEN_URL, CHANNELS_URL, REVOKE_URL,
    mock_connect, browser_binding, publish_time, digest)


class MemoryVault:
    """Fake durable store for contract tests. Never used by the app."""
    live = True

    def __init__(self):
        self.rows = {}

    def get(self, key):
        return copy.deepcopy(self.rows.get(key, (None, 0)))

    def put(self, key, value, revision):
        if self.get(key)[1] != revision:
            raise YouTubeError("Concurrent revision")
        self.rows[key] = (copy.deepcopy(value), revision+1)


def response(body, status=200):
    r = Mock(status_code=status, content=b"response")
    r.json.return_value = body
    return r


class OAuthTests(unittest.TestCase):
    def setUp(self):
        self.cfg = OAuthConfig("client.apps.googleusercontent.com", "CLIENT_SECRET",
            "https://studio.example/", "postgresql://vault.invalid/db", Fernet.generate_key().decode(),
            "OWNER_PASSWORD", True)
        self.store, self.http = MemoryVault(), Mock()
        self.now = 1000
        self.oauth = GoogleOAuth(self.cfg, self.store, self.http, lambda:self.now)
        self.cookie = "ab"*16

    def begin(self):
        return parse_qs(urlsplit(self.oauth.begin(1, NISHIKOTHA_ID, self.cookie, True)).query)

    def tokens(self):
        return {"access_token":"ACCESS_TOKEN", "refresh_token":"REFRESH_TOKEN", "scope":READ_SCOPE, "expires_in":3600}

    def channel(self, cid=NISHIKOTHA_ID):
        return {"items":[{"id":cid,"snippet":{"title":"নিশিকথা", "customUrl":"@NishikothaBangla"}}]}

    def connect(self):
        query = self.begin()
        self.http.request.side_effect = [response(self.tokens()), response(self.channel())]
        result = self.oauth.finish(query["state"][0], "CODE", self.cookie, True)
        return query, result

    def test_default_setup_is_locked_without_secrets(self):
        self.assertGreaterEqual(len(OAuthConfig().blockers()), 5)
        with self.assertRaises(YouTubeError):
            GoogleOAuth(OAuthConfig(), self.store, self.http)
        self.http.request.assert_not_called()

    def test_http_or_query_callback_and_unprotected_owner_rejected(self):
        for uri in ("http://studio.example/", "https://studio.example/?x=1", "https://u:p@studio.example/", "https://studio.example/callback"):
            self.cfg.redirect_uri = uri
            self.assertTrue(self.cfg.blockers())
        self.cfg.redirect_uri = "https://studio.example/"
        self.cfg.owner_gate = False
        self.assertTrue(self.cfg.blockers())

    def test_connect_url_readonly_state_pkce_offline(self):
        q = self.begin()
        self.assertEqual(q["scope"], [READ_SCOPE])
        self.assertEqual(q["access_type"], ["offline"])
        self.assertEqual(q["code_challenge_method"], ["S256"])
        self.assertGreaterEqual(len(q["state"][0]), 40)
        stored = json.dumps(self.store.rows)
        self.assertNotIn(self.cookie, stored)
        self.assertNotIn("CLIENT_SECRET", stored)
        self.http.request.assert_not_called()

    def test_browser_cookie_remasking_keeps_binding(self):
        raw = bytes.fromhex(self.cookie)
        def masked(mask):
            cipher = bytes(v ^ mask[i%4] for i,v in enumerate(raw))
            return f"2|{mask.hex()}|{cipher.hex()}|1000"
        self.assertEqual(browser_binding(masked(b"abcd")), browser_binding(masked(b"efgh")))
        self.assertEqual(browser_binding(self.cookie), browser_binding(masked(b"abcd")))
        for bad in ("", "bogus", "2|00|aa|1"):
            with self.assertRaises(YouTubeError):
                browser_binding(bad)

    def test_wrong_browser_owner_expired_and_unknown_state_make_no_http(self):
        state = self.begin()["state"][0]
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "CODE", "cd"*16, True)
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "CODE", self.cookie, False)
        with self.assertRaises(YouTubeError):
            self.oauth.finish("unknown", "CODE", self.cookie, True)
        self.cfg.owner_password = "CHANGED"
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "CODE", self.cookie, True)
        self.cfg.owner_password = "OWNER_PASSWORD"
        self.now += 601
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "CODE", self.cookie, True)
        self.http.request.assert_not_called()

    def test_denial_consumes_state_without_exchange(self):
        state = self.begin()["state"][0]
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "", self.cookie, True, denied=True)
        with self.assertRaises(YouTubeError):
            self.oauth.finish(state, "CODE", self.cookie, True)
        self.http.request.assert_not_called()

    def test_identity_verified_encrypted_and_state_single_use(self):
        q, identity = self.connect()
        self.assertEqual(identity["id"], NISHIKOTHA_ID)
        row, _ = self.store.get("channel:"+NISHIKOTHA_ID)
        self.assertTrue(row["connected"])
        serialized = json.dumps(self.store.rows)
        for secret in ("ACCESS_TOKEN", "REFRESH_TOKEN", "CLIENT_SECRET"):
            self.assertNotIn(secret, serialized)
        self.assertEqual(self.oauth.unseal(row["vault"])["refresh_token"], "REFRESH_TOKEN")
        self.assertEqual(self.http.request.call_args_list[1].args, ("GET", CHANNELS_URL))
        with self.assertRaises(YouTubeError):
            self.oauth.finish(q["state"][0], "CODE", self.cookie, True)
        self.assertEqual(self.http.request.call_count, 2)

    def test_wrong_channel_missing_scopes_and_missing_refresh_token_rejected(self):
        for tokens, identity in ((self.tokens(), self.channel("UC"+"x"*22)),
                ({**self.tokens(), "scope":""}, self.channel()),
                ({**self.tokens(), "refresh_token":""}, self.channel())):
            state = self.begin()["state"][0]
            self.http.request.side_effect = [response(tokens), response(identity)]
            with self.assertRaises(YouTubeError):
                self.oauth.finish(state, "CODE", self.cookie, True)
            self.assertIsNone(self.store.get("channel:"+NISHIKOTHA_ID)[0])

    def test_expiry_refresh_and_revocation(self):
        self.connect()
        self.now += 3600
        self.http.request.side_effect = [response({"access_token":"NEW_ACCESS", "expires_in":3600})]
        self.assertEqual(self.oauth.access_token(NISHIKOTHA_ID), "NEW_ACCESS")
        self.assertEqual(self.http.request.call_args.args, ("POST", TOKEN_URL))
        self.http.request.side_effect = [response({})]
        self.oauth.disconnect(NISHIKOTHA_ID)
        self.assertEqual(self.http.request.call_args.args, ("POST", REVOKE_URL))
        row, _ = self.store.get("channel:"+NISHIKOTHA_ID)
        self.assertNotIn("vault", row)
        self.assertFalse(row["connected"])

    def test_errors_do_not_expose_provider_secrets_or_retry(self):
        import requests
        for failure in (response({"error":"SECRET_REFRESH_TOKEN"}, 403),
                        requests.Timeout("SECRET_AUTH_HEADER")):
            self.http.reset_mock()
            self.http.request.side_effect = failure if isinstance(failure, Exception) else None
            self.http.request.return_value = failure
            with self.assertRaises(YouTubeError) as caught:
                self.oauth.call("POST", TOKEN_URL)
            self.assertNotIn("SECRET", str(caught.exception))
            self.assertEqual(self.http.request.call_count, 1)

    def test_revocation_failure_keeps_credentials_until_explicit_forget(self):
        self.connect()
        self.http.request.side_effect = [response({}, 503)]
        with self.assertRaises(YouTubeError):
            self.oauth.disconnect(NISHIKOTHA_ID)
        self.assertIn("vault", self.store.get("channel:"+NISHIKOTHA_ID)[0])
        self.oauth.forget(NISHIKOTHA_ID)
        self.assertNotIn("vault", self.store.get("channel:"+NISHIKOTHA_ID)[0])


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.db, self.media = root/"source.db", root/"media"
        self.media.mkdir()
        self.mp4 = self.media/"final.mp4"
        self.mp4.write_bytes(b"offline fixture bytes")
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TABLE content(id INTEGER PRIMARY KEY,channel_id INTEGER,script TEXT,status TEXT,updated_at TEXT)")
            db.execute("CREATE TABLE content_video(content_id INTEGER,video_path TEXT)")
            db.execute("CREATE TABLE production_exports(content_id INTEGER,video_path TEXT,script_hash TEXT,mode TEXT)")
            db.execute("INSERT INTO content VALUES(1,1,'story','Approved','version1')")
            db.execute("INSERT INTO content_video VALUES(1,?)", (str(self.mp4),))
            db.execute("INSERT INTO production_exports VALUES(1,?,?,'mock')", (str(self.mp4), digest("story")))
        self.store = Store(root/"mock.db")
        mock_connect(self.store, 1)
        self.now = 1000
        self.service = Publishing(self.store, self.db, self.media, lambda:self.now)

    def create(self, schedule=""):
        return self.service.create(NISHIKOTHA_ID, 1, "নিশিকথা", "Fictional horror", schedule)

    def update(self, sql, params=()):
        with sqlite3.connect(self.db) as db:
            db.execute(sql, params)

    def test_local_tokens_and_local_live_vault_rejected(self):
        with self.assertRaises(YouTubeError):
            self.store.put("oauth:x", {"vault":"secret"}, 0)
        with self.assertRaises(YouTubeError):
            Store(self.db, live=True)

    def test_compare_and_swap_detects_concurrent_session(self):
        self.store.put("test", {"x":1}, 0)
        with self.assertRaises(YouTubeError):
            self.store.put("test", {"x":2}, 0)
        self.store.put("test", {"x":2}, 1)
        with self.assertRaises(YouTubeError):
            self.store.put("test", {"x":3}, 1)

    def test_pending_draft_and_missing_render_rejected(self):
        self.update("UPDATE content SET status='Awaiting review'")
        with self.assertRaises(YouTubeError): self.create()
        self.update("UPDATE content SET status='Approved'")
        self.mp4.unlink()
        with self.assertRaises(YouTubeError): self.create()

    def test_no_approval_no_network_no_live_even_if_approved(self):
        rid = self.create()
        with patch("requests.Session.request", side_effect=AssertionError("Network forbidden")):
            with self.assertRaises(YouTubeError): self.service.dry_run(rid)
            with self.assertRaises(YouTubeError): self.service.approve(rid, False, True)
            self.service.approve(rid, True, True)
            result = self.service.dry_run(rid)
            self.assertEqual(result["network_calls"], 0)
            self.assertIsNone(result["remote_video_id"])
            self.assertEqual(result["request_body"]["status"]["privacyStatus"], "private")
            with self.assertRaises(YouTubeError): self.service.execute_live(rid)

    def test_scheduling_requires_separate_approval_and_is_idempotent(self):
        rid = self.create("1970-01-01T01:00:00Z")
        self.assertEqual(rid, self.create("1970-01-01T01:00:00Z"))
        with self.assertRaises(YouTubeError): self.service.approve(rid, True, True, False)
        self.service.approve(rid, True, True, True)
        result = self.service.dry_run(rid)
        self.assertEqual(result["request_body"]["status"]["publishAt"], "1970-01-01T01:00:00Z")
        self.assertEqual(self.service.tick(), [])
        self.now = 3601
        self.assertEqual(self.service.tick(), [rid])
        self.assertEqual(self.service.tick(), [])
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)

    def test_changed_script_render_metadata_or_channel_needs_new_approval(self):
        rid = self.create()
        self.service.approve(rid, True, True)
        self.mp4.write_bytes(b"different MP4")
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)
        new = self.create()
        self.assertNotEqual(new, rid)
        self.assertNotEqual(new, self.service.create(NISHIKOTHA_ID, 1, "Changed title", "Fictional horror"))
        self.update("UPDATE content SET script='edited'")
        with self.assertRaises(YouTubeError): self.create()

    def test_internal_channel_mismatch_and_disconnection(self):
        rid = self.create()
        self.service.approve(rid, True, True)
        mock_connect(self.store, 2)
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)
        with self.assertRaises(YouTubeError): self.create()
        mock_connect(self.store, 1)
        row, rev = self.store.get("channel:"+NISHIKOTHA_ID)
        row["connected"] = False
        self.store.put("channel:"+NISHIKOTHA_ID, row, rev)
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)

    def test_cancel_and_edited_or_revoked_draft_invalidates_due_schedule(self):
        rid = self.create("1970-01-01T01:00:00Z")
        self.service.approve(rid, True, True, True)
        self.service.dry_run(rid)
        self.update("UPDATE content SET status='Needs correction'")
        self.now = 3601
        self.assertEqual(self.service.tick(), [])
        self.assertEqual(self.store.get("request:"+rid)[0]["state"], "invalidated")
        self.service.cancel(rid)
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)

    def test_multi_channel_isolation(self):
        other = "UC"+"a"*22
        mock_connect(self.store, 2, other)
        self.assertEqual(len(self.store.list("channel:")), 2)
        with self.assertRaises(YouTubeError):
            self.service.create(other, 1, "wrong channel", "")
        self.assertEqual(self.create(), self.create())

    def test_reconnect_never_resurrects_old_upload_approval(self):
        rid = self.create()
        self.service.approve(rid, True, True)
        mock_connect(self.store, 1)
        with self.assertRaises(YouTubeError): self.service.dry_run(rid)
        self.assertNotEqual(rid, self.create())

    def test_path_escape_and_stale_schedule_rejected(self):
        self.update("UPDATE content_video SET video_path='/tmp/outside.mp4'")
        with self.assertRaises(YouTubeError): self.create()
        self.update("UPDATE content_video SET video_path=?", (str(self.mp4),))
        for stamp in ("1970-01-01T00:01:00Z", "2027-01-01T00:00:00", "bad"):
            with self.assertRaises(YouTubeError): self.create(stamp)

    def test_dhaka_conversion_future_date_and_metadata_validation(self):
        self.assertEqual(publish_time(date(2027,1,2), time(18), datetime(2027,1,1,tzinfo=timezone.utc)), "2027-01-02T12:00:00Z")
        with self.assertRaises(YouTubeError): publish_time(date(2020,1,1), time(18))
        for title, desc in (("", ""), ("x"*101, ""), ("bad<title", ""), ("ok", "ব"*1700)):
            with self.assertRaises(YouTubeError): self.service.create(NISHIKOTHA_ID, 1, title, desc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
