"""Read-only cache audit and synthetic fail-closed tests."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
PRIOR = BASE.parent / "phase2_cpu_gaps_20261122"
sys.path.insert(0, str(BASE.parent / "phase2_approved_20261122"))
from qwen_preflight_fixture import REQUIRED, preflight

REV = "3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8"


def verify_file(path, size, digest):
    if path.stat().st_size != size:
        raise ValueError("size mismatch")
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != digest:
            raise ValueError("digest mismatch")


def verify_resolution(resolved_revision):
    if resolved_revision != REV:
        raise ValueError("kernel resolution drift")


def audit(roots):
    manifest = json.loads((PRIOR / "qwen-platform-wheels.json").read_text())
    lock = (PRIOR / "qwen-candidate.lock").read_bytes()
    assert hashlib.sha256(lock).hexdigest() == manifest["lock_sha256"]
    packages = {}
    for block in re.split(r"(?m)^(?=[a-z][a-z0-9_-]*==)", lock.decode())[1:]:
        name, version = block.splitlines()[0].split()[0].split("==")
        packages[name] = (version, set(re.findall(r"--hash=sha256:([a-f0-9]{64})", block)))
    wheels = manifest["wheels"]
    assert len(wheels) == len(packages) == 79 and {x["name"] for x in wheels} == packages.keys()
    files = {x["filename"]: [] for x in wheels}
    assert len(files) == 79
    for root in roots:
        for directory, _, names in os.walk(root):
            for name in files.keys() & set(names):
                files[name].append(Path(directory) / name)
    receipt = []
    for row in wheels:
        name = row["filename"]
        version, hashes = packages[row["name"]]
        assert version == row["version"] and row["sha256"] in hashes and row["bytes"] > 0
        assert name.endswith(".whl") and name.split("-")[0].replace("_", "-") == row["name"]
        assert name.split("-")[1] == version
        available = False
        for path in files[name]:
            try:
                verify_file(path, row["bytes"], row["sha256"])
            except (ValueError, OSError):
                continue
            available = True
            break
        receipt.append({"filename": name, "version": version, "bytes": row["bytes"],
                        "sha256": row["sha256"], "candidate_count": len(files[name]),
                        "verified_local_archive": available})
    missing = [row for row in receipt if not row["verified_local_archive"]]
    data = {"lock_entries_verified_against_saved_metadata": len(receipt),
            "verified_local_archives": len(receipt) - len(missing),
            "missing_archives": len(missing), "missing_bytes": sum(x["bytes"] for x in missing),
            "roots": roots, "entries": receipt}
    (BASE / "qwen-wheel-audit.json").write_text(json.dumps(data, indent=2) + "\n")
    print({k: v for k, v in data.items() if k not in ("roots", "entries")})


class FailClosed(unittest.TestCase):
    def test_tampered_same_size_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.whl"
            expected = hashlib.sha256(b"good").hexdigest()
            path.write_bytes(b"good")
            verify_file(path, 4, expected)
            path.write_bytes(b"evil")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                verify_file(path, 4, expected)

    def test_revision_drift(self):
        verify_resolution(REV)
        with self.assertRaisesRegex(ValueError, "drift"):
            verify_resolution("0fc209e04af4db8fb02cc9416d44a9a28d4b2c71")

    def test_preflight_rejects_faults(self):
        good = dict.fromkeys(REQUIRED, lambda: None)
        for args, message in (
            (([(8, 6)], good, lambda: False), "unsupported"),
            (([(8, 9)], {k: good[k] for k in REQUIRED[:-1]}, lambda: False), "missing"),
            (([(8, 9)], good, lambda: True), "BF16 fallback"),
        ):
            devices, kernels, validate = args
            with self.subTest(reason=message), self.assertRaisesRegex(RuntimeError, message):
                preflight("cuda", devices, kernels, False, validate)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--audit"]:
        audit(sys.argv[2:])
    else:
        unittest.main(verbosity=2)
