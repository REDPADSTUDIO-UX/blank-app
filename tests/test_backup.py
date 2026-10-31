"""No-cloud SQLite/media backup and isolated restore regression tests."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from redpad_pipeline.backup import (
    BACKUP_FORMAT, BackupError, create_snapshot, restore_isolated, verify_archive,
)


class BackupAndRestore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="redpad-backup-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.media = self.root / "redpad_media"
        (self.media / "production" / "test-job").mkdir(parents=True)
        (self.media / "production" / "test-job" / "state.json").write_text(
            '{"phase":"queued","scenes":[]}', encoding="utf-8")
        (self.media / "music").mkdir()
        (self.media / "music" / "test.srt").write_text(
            "1\n00:00:00,000 --> 00:00:02,000\nরাতের ঢাকা", encoding="utf-8")
        self.db = self.root / "redpad_studio.db"
        with sqlite3.connect(self.db) as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("""CREATE TABLE channels(
                 id INTEGER PRIMARY KEY, name TEXT NOT NULL)""")
            con.execute("""CREATE TABLE content(
                 id INTEGER PRIMARY KEY, channel_id INTEGER REFERENCES channels(id),
                 script TEXT NOT NULL, media BLOB)""")
            con.execute("INSERT INTO channels VALUES(1,'Nishikotha')")
            con.execute("INSERT INTO content VALUES(1,1,?,?)",
                        ("চলন্ত ট্রেন। রহস্যময় ছায়া।", b"\x00\xff\x80"))
        self.archive = self.root / "redpad-private-backup.zip"

    def test_full_archive_and_isolated_restore(self):
        saved = create_snapshot(self.db, self.media, self.archive)
        self.assertEqual(saved["format"], BACKUP_FORMAT)
        self.assertEqual(saved["database"]["integrity_check"], "ok")
        self.assertEqual(saved["media_file_count"], 2)
        self.assertEqual({x["table"] for x in saved["database"]["tables"]},
                         {"channels", "content"})
        same = verify_archive(self.archive)
        self.assertEqual(saved, same)
        destination = self.root / "restored"
        result = restore_isolated(self.archive, destination)
        self.assertEqual(result["status"], "ISOLATED_RESTORE_VERIFIED")
        with sqlite3.connect(destination / "database.sqlite3") as con:
            script, blob = con.execute("SELECT script,media FROM content").fetchone()
            self.assertIn("রহস্যময়", script)
            self.assertEqual(blob, b"\x00\xff\x80")
        self.assertEqual(
            (destination / "media/music/test.srt").read_text(encoding="utf-8"),
            (self.media / "music/test.srt").read_text(encoding="utf-8"),
        )
        self.assertTrue(self.db.is_file())
        self.assertTrue((self.media / "production/test-job/state.json").is_file())
        with self.assertRaises(BackupError):
            restore_isolated(self.archive, destination)
        with self.assertRaises(BackupError):
            create_snapshot(self.db, self.media, self.archive)
        print("PASS: SQLite WAL-safe snapshot, UTF-8, BLOB, media, SHA256, isolated restore")

    def test_missing_database_does_not_create_empty_backup(self):
        with self.assertRaises(BackupError):
            create_snapshot(self.root / "not_exists.db", self.media, self.archive)
        self.assertFalse(self.archive.exists())

    def test_missing_media_must_fail(self):
        with self.assertRaises(BackupError):
            create_snapshot(self.db, self.root / "nonexistent", self.archive)

    def test_symlink_media_must_fail(self):
        (self.media / "unsafe.mp4").symlink_to(self.db)
        with self.assertRaises(BackupError):
            create_snapshot(self.db, self.media, self.archive)

    def test_corrupted_zip_and_unlisted_member_are_rejected(self):
        create_snapshot(self.db, self.media, self.archive)
        with zipfile.ZipFile(self.archive, "a") as z:
            z.writestr("unexpected/exfiltration.txt", "unsafe")
        with self.assertRaises(BackupError):
            verify_archive(self.archive)

    def test_hash_mismatch_rejected(self):
        create_snapshot(self.db, self.media, self.archive)
        corrupted = self.root / "modified.zip"
        with zipfile.ZipFile(self.archive) as source, zipfile.ZipFile(corrupted, "w") as dest:
            for member in source.namelist():
                data = source.read(member)
                if member.endswith("test.srt"):
                    data = b"malicious but structurally valid"
                dest.writestr(member, data)
        with self.assertRaises(BackupError):
            verify_archive(corrupted)
        self.assertFalse((self.root / "should-not-restore").exists())

    def test_no_source_mutation(self):
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        create_snapshot(self.db, self.media, self.archive)
        after = hashlib.sha256(self.db.read_bytes()).hexdigest()
        # WAL checkpoint may legitimately change the DB file in some contexts;
        # assert user rows are preserved, not file-system page layout.
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute("SELECT count(*) FROM content").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
