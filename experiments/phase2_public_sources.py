"""Fetch only exact public Python/metadata sources for model-free CPU acceptance.

No model artefacts, authentication, dependency installation or code execution.
The same source bundle can be mounted read-only by the existing supervisor.
"""
import argparse
import hashlib
import io
import json
import shutil
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

DIFFUSERS_REVISION = '3a2f35d4efa4c059c8bfb3bc0d6c906264895c81'
ARCHIVE_BYTES = 11229951
ARCHIVE_SHA256 = '64a73e17a64de2813f9e66743c2e1e9589552834ca14f09f0a883d15c9015245'


def checked_bytes(path, expected_hash, expected_size=None):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Regular reviewed source required')
    data = path.read_bytes()
    if (expected_size is not None and len(data) != expected_size) or hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError('Pinned publisher source integrity failed')
    return data


def fetch(url, path, digest, size=None):
    if path.exists() or path.is_symlink():
        return checked_bytes(path, digest, size)
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read((size or 1024 * 1024) + 1)
    if (size is not None and len(data) != size) or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('Official source response did not match reviewed content')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)
    return data


def extract_diffusers(raw, destination):
    """Extract regular src/ and LICENSE only. Reject selected links or traversal."""
    if len(raw) != ARCHIVE_BYTES or hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Unreviewed Diffusers archive')
    prefix = 'diffusers-' + DIFFUSERS_REVISION
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for member in archive:
            parts = PurePosixPath(member.name).parts
            if not parts or parts[0] != prefix or '..' in parts or member.name.startswith('/'):
                raise ValueError('Unsafe archive path')
            relative = PurePosixPath(*parts[1:])
            if not relative.parts or relative.parts[0] not in ('src', 'LICENSE'):
                continue
            if member.isdir():
                continue
            if not member.isfile() or member.size > 8 * 1024 * 1024:
                raise ValueError('Selected source is a link, special entry or oversized')
            path = destination.joinpath(*relative.parts)
            if any(p.is_symlink() for p in (path, *path.parents)):
                raise ValueError('Source output has a symlink')
            data = archive.extractfile(member).read()
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                if path.read_bytes() != data:
                    raise ValueError('Existing reviewed source changed')
            else:
                path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('--local-kernel', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination.parent / 'diffusers-merged.tar.gz'
    raw = fetch('https://codeload.github.com/huggingface/diffusers/tar.gz/' + DIFFUSERS_REVISION,
                archive, ARCHIVE_SHA256, ARCHIVE_BYTES)
    extract_diffusers(raw, destination / 'diffusers')
    kernel = json.loads((root / 'verification/phase2_cpu_gaps_20261122/qwen-kernel-v4.json').read_text())
    rows = {name: row['sha256'] for name, row in kernel['files'].items()}
    rows.update({'metadata.json': kernel['metadata_sha256'],
                 'metadata.json.sigstore': kernel['sigstore_bundle_sha256']})
    for name, digest in rows.items():
        parts = PurePosixPath(name).parts
        if not parts or PurePosixPath(name).is_absolute() or '..' in parts:
            raise ValueError('Unexpected kernel source path')
        target = destination / 'kernel' / name
        if args.local_kernel and not target.exists():
            original = args.local_kernel / name
            checked_bytes(original, digest)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
        fetch(kernel['raw_build_root'] + name, destination / 'kernel' / name, digest)
    (destination / 'modular_model_index.json').write_bytes(
        (root / 'assets/professional/wan_distilled_modular_index.json').read_bytes())
    (destination / 'kernel-lock.json').write_text(json.dumps(rows, sort_keys=True))
    manifest = {p.relative_to(destination).as_posix(): {
        'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()
    } for p in sorted(destination.rglob('*')) if p.is_file()}
    print(json.dumps({'diffusers_revision': DIFFUSERS_REVISION, 'source_files': manifest,
                      'model_weights': False, 'source_execution': False}, sort_keys=True))


if __name__ == '__main__':
    main()
