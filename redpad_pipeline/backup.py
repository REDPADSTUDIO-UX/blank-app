"""Consistent SQLite + media backup, manifest and isolated restore verification.

No deployed service, account, cloud instance or database is changed.
This creates a LOCAL, *unencrypted* backup containing private user data: keep
it off public repositories and encrypt before off-host transfer.

Global SQLite/media consistency also requires a quiescent application:
do not run while a media export or draft edit is active.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

BACKUP_FORMAT = "REDPAD-FULL-SNAPSHOT-v1"
MAX_FILE_BYTES = 2 * 1024 ** 3
MAX_TOTAL_BYTES = 8 * 1024 ** 3
FILE_CHUNK = 1024 * 1024


class BackupError(RuntimeError):
    """A recovery prerequisite failed; never silently drop files or records."""


def _sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(FILE_CHUNK), b""):
            checksum.update(block)
    return checksum.hexdigest()


def _sqlite_readonly(path: Path):
    # URI mode=ro makes a missing DB an error, not an empty new SQLite file.
    return sqlite3.connect(f"file:{quote(str(path.resolve()))}?mode=ro", uri=True)


def _integrity(db_path: Path) -> dict:
    with _sqlite_readonly(db_path) as conn:
        check = [row[0] for row in conn.execute("PRAGMA integrity_check")]
        if check != ["ok"]:
            raise BackupError("SQLite integrity check did not return 'ok'.")
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise BackupError("SQLite foreign key check failed.")
        tables = []
        for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ):
            if name.startswith("sqlite_"):
                continue
            if not name or "\x00" in name:
                raise BackupError("Invalid SQLite table name.")
            rows = conn.execute(
                'SELECT * FROM "' + name.replace('"', '""') + '"'
            )
            digest = hashlib.sha256()
            count = 0
            for row in rows:
                values = []
                for value in row:
                    if isinstance(value, bytes):
                        values.append({"blob64": base64.b64encode(value).decode("ascii")})
                    else:
                        values.append(value)
                encoded = json.dumps(values, ensure_ascii=False, sort_keys=True,
                                     default=str, separators=(",", ":")).encode("utf-8")
                digest.update(len(encoded).to_bytes(8, "big"))
                digest.update(encoded)
                count += 1
            tables.append({"table": name, "rows": count, "row_sha256": digest.hexdigest()})
        return {"integrity_check": "ok", "foreign_key_errors": 0, "tables": tables}


def _media_inventory(media_dir: Path) -> list[dict]:
    if not media_dir.is_dir() or media_dir.is_symlink():
        raise BackupError("Media root is missing or is a symlink.")
    inventory = []
    total = 0
    for root, dirs, files in os.walk(media_dir, topdown=True, followlinks=False):
        base = Path(root)
        for directory in dirs:
            path = base / directory
            if path.is_symlink():
                raise BackupError("A media directory symlink requires explicit review.")
        for name in files:
            file_path = base / name
            if file_path.is_symlink() or not file_path.is_file():
                raise BackupError("Media contains a symlink or a nonregular file.")
            relative = file_path.relative_to(media_dir).as_posix()
            if not relative or relative.startswith("/") or ".." in Path(relative).parts:
                raise BackupError("Media contains an unsafe relative path.")
            metadata = file_path.stat()
            if metadata.st_size > MAX_FILE_BYTES:
                raise BackupError("An individual media file exceeds the backup limit.")
            total += metadata.st_size
            if total > MAX_TOTAL_BYTES:
                raise BackupError("Media exceeds the safe backup archive limit.")
            inventory.append({
                "path": relative, "size": metadata.st_size, "sha256": _sha256(file_path),
                "mtime_ns": metadata.st_mtime_ns,
            })
    return sorted(inventory, key=lambda item: item["path"])


def _compare_copy(path: Path, info: dict):
    meta = path.stat()
    if (path.is_symlink() or not path.is_file() or meta.st_size != info["size"]
            or meta.st_mtime_ns != info["mtime_ns"]
            or _sha256(path) != info["sha256"]):
        raise BackupError("Media changed during backup; a stable capture is required.")


def _copy_to_archive(archive, source: Path, archive_name: str, expected_hash: str):
    checksum = hashlib.sha256()
    with source.open("rb") as infile, archive.open(archive_name, "w") as out:
        for block in iter(lambda: infile.read(FILE_CHUNK), b""):
            checksum.update(block)
            out.write(block)
    if checksum.hexdigest() != expected_hash:
        raise BackupError("A file changed while being archived.")


def create_snapshot(source_db: str | Path, source_media: str | Path,
                    destination: str | Path) -> dict:
    """Create a verified ZIP snapshot; NEVER remove or modify source records.

    A successful artifact proves consistency of archived bytes and source
    DB snapshot, not that concurrent app/media writes were globally stopped.
    """
    db_path = Path(source_db).resolve()
    media_dir = Path(source_media).resolve()
    target = Path(destination).resolve()
    if not db_path.is_file() or db_path.is_symlink():
        raise BackupError("Source SQLite database does not exist.")
    if target.exists() or target.parent == media_dir or target.is_relative_to(media_dir):
        raise BackupError("Backup destination must be a NEW file outside the media directory.")
    target.parent.mkdir(parents=True, exist_ok=True)
    inventory = _media_inventory(media_dir)
    with tempfile.TemporaryDirectory(prefix="redpad-backup-", dir=str(target.parent)) as tmp:
        snapshot = Path(tmp) / "database.sqlite3"
        with _sqlite_readonly(db_path) as source, sqlite3.connect(snapshot) as copy:
            source.backup(copy)
        database_info = _integrity(snapshot)
        db_hash = _sha256(snapshot)
        manifest = {
            "format": BACKUP_FORMAT,
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "database": {"name": "database.sqlite3", "bytes": snapshot.stat().st_size,
                         "sha256": db_hash, **database_info},
            "media": [{"path": x["path"], "bytes": x["size"], "sha256": x["sha256"]}
                      for x in inventory],
            "media_file_count": len(inventory),
            "media_total_bytes": sum(x["size"] for x in inventory),
            "source_write_quiescence_attested": False,
            "source_disclaimer": "This archive contains private data and must be encrypted before off-site transfer.",
        }
        temporary = Path(tmp) / "backup.tmp.zip"
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as archive:
            _copy_to_archive(archive, snapshot, "database.sqlite3", db_hash)
            for entry in inventory:
                media_path = media_dir / entry["path"]
                _compare_copy(media_path, entry)
                _copy_to_archive(archive, media_path, "media/" + entry["path"],
                                 entry["sha256"])
                _compare_copy(media_path, entry)
            archive.writestr("manifest.json",
                             json.dumps(manifest, ensure_ascii=False, indent=2))
        verify_archive(temporary)
        shutil.copy2(temporary, target)
        verify_archive(target)
    return manifest


def _read_manifest(archive):
    try:
        info = json.loads(archive.read("manifest.json"))
    except (KeyError, ValueError, UnicodeDecodeError) as exc:
        raise BackupError("Backup manifest is missing or invalid.") from exc
    if info.get("format") != BACKUP_FORMAT:
        raise BackupError("Unsupported backup archive format.")
    return info


def _safe_members(archive, info):
    members = archive.infolist()
    names = [member.filename for member in members]
    expected = {"manifest.json", "database.sqlite3"}
    records = info.get("media")
    if not isinstance(records, list):
        raise BackupError("Media inventory is missing.")
    for item in records:
        rel = item.get("path")
        if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
            raise BackupError("Invalid media path in the manifest.")
        if ".." in Path(rel).parts or rel.startswith("media/"):
            raise BackupError("Unsafe media path in the manifest.")
        expected.add("media/" + rel)
    if len(names) != len(expected) or set(names) != expected:
        raise BackupError("Backup archive has missing, duplicate or unexpected members.")
    for member in members:
        if member.is_dir() or Path(member.filename).is_absolute() or ".." in Path(member.filename).parts:
            raise BackupError("Unsafe or unexpected archive entry.")
        # ZIP POSIX symlink bit, if present.
        if stat.S_ISLNK(member.external_attr >> 16):
            raise BackupError("Symlinks are forbidden in backups.")
    return records


def verify_archive(path: str | Path) -> dict:
    """Verify every archive byte, database row fingerprint and manifest row."""
    archive_path = Path(path)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise BackupError("Backup archive CRC test failed.")
            info = _read_manifest(archive)
            records = _safe_members(archive, info)
            if (info.get("media_file_count") != len(records) or
                    info.get("media_total_bytes") != sum(x["bytes"] for x in records)):
                raise BackupError("Media inventory counts do not match.")
            with tempfile.TemporaryDirectory(prefix="redpad-audit-") as tmp:
                snapshot = Path(tmp) / "database.sqlite3"
                with archive.open("database.sqlite3") as stream, snapshot.open("wb") as out:
                    shutil.copyfileobj(stream, out)
                db_info = info["database"]
                if (snapshot.stat().st_size != db_info.get("bytes") or
                        _sha256(snapshot) != db_info.get("sha256")):
                    raise BackupError("SQLite snapshot checksum mismatch.")
                verified = _integrity(snapshot)
                if verified != {key: db_info[key] for key in ("integrity_check", "foreign_key_errors", "tables")}:
                    raise BackupError("SQLite row fingerprints do not match.")
            for record in records:
                filename = "media/" + record["path"]
                digest = hashlib.sha256()
                size = 0
                with archive.open(filename) as stream:
                    for block in iter(lambda: stream.read(FILE_CHUNK), b""):
                        size += len(block)
                        digest.update(block)
                        if size > MAX_FILE_BYTES:
                            raise BackupError("Archive media entry exceeds the safety limit.")
                if size != record["bytes"] or digest.hexdigest() != record["sha256"]:
                    raise BackupError("Media file checksum mismatch.")
            return info
    except (OSError, zipfile.BadZipFile, EOFError) as exc:
        raise BackupError("Backup archive cannot be read safely.") from exc


def restore_isolated(archive: str | Path, destination: str | Path) -> dict:
    """Restore ONLY into a new empty folder, never overwrite a live app.

    The database copy is checked with SQLite PRAGMA and every media file hash.
    """
    target = Path(destination).resolve()
    if target.exists():
        raise BackupError("Restore destination exists; refusing to overwrite user data.")
    info = verify_archive(archive)
    target.mkdir(parents=True, exist_ok=False)
    try:
        with zipfile.ZipFile(archive) as z:
            for name in ("database.sqlite3", *("media/" + x["path"] for x in info["media"])):
                target_file = target / name
                if not target_file.resolve().is_relative_to(target):
                    raise BackupError("Archive contained an unsafe restore path.")
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with z.open(name) as src, target_file.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
        restored_db = target / "database.sqlite3"
        if _sha256(restored_db) != info["database"]["sha256"]:
            raise BackupError("Restored database checksum mismatch.")
        if _integrity(restored_db)["tables"] != info["database"]["tables"]:
            raise BackupError("Restored database differs from the archived snapshot.")
        for entry in info["media"]:
            file_path = target / "media" / entry["path"]
            if (_sha256(file_path) != entry["sha256"] or file_path.stat().st_size != entry["bytes"]):
                raise BackupError("A restored media file checksum mismatch.")
        return {"status": "ISOLATED_RESTORE_VERIFIED",
                "tables": info["database"]["tables"],
                "media_file_count": len(info["media"]),
                "backup_source_quiescence_confirmed": False}
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise
