"""Acquire only the reviewed dependency wheels; never install or load models.

Completed archives are reused only after full size/SHA256 verification. Partial
files never become installable archives. The wheelhouse is outside the repo.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import shutil
import urllib.parse
import urllib.request


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_row(row):
    name = row['filename']
    url = urllib.parse.urlsplit(row['url'])
    if (Path(name).name != name or not name.endswith('.whl') or
            url.scheme != 'https' or url.netloc != 'files.pythonhosted.org' or
            url.query or url.fragment or urllib.parse.unquote(url.path).split('/')[-1] != name or
            type(row['bytes']) is not int or row['bytes'] <= 0 or
            not re.fullmatch('[0-9a-f]{64}', row['sha256'])):
        raise ValueError('Unapproved wheel filename, origin, size or SHA256')


def verified(path, row):
    return (path.is_file() and not path.is_symlink() and
            path.stat().st_size == row['bytes'] and digest(path) == row['sha256'])


def acquire(row, folder):
    validate_row(row)
    target = folder / row['filename']
    if target.is_symlink() or target.with_suffix('.partial').is_symlink():
        raise ValueError('Symlink archive refused')
    if verified(target, row):
        return {**row, 'status': 'verified_existing', 'downloaded_bytes': 0}
    if target.exists():
        raise ValueError('Existing complete archive failed integrity; retain it for inspection')
    partial = target.with_suffix('.partial')
    if partial.exists():
        raise ValueError('Incomplete prior transfer retained; explicit recovery required')
    total = 0
    hasher = hashlib.sha256()
    with urllib.request.urlopen(row['url'], timeout=60) as response:
        if urllib.parse.urlsplit(response.url).netloc != 'files.pythonhosted.org':
            raise ValueError('Download redirected outside approved package origin')
        if response.headers.get('Content-Length') != str(row['bytes']):
            raise ValueError('Official response size differs from approved wheel')
        with partial.open('xb') as stream:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > row['bytes']:
                    raise ValueError('Oversized wheel response')
                hasher.update(chunk)
                stream.write(chunk)
    if total != row['bytes'] or hasher.hexdigest() != row['sha256']:
        raise ValueError('Downloaded wheel integrity failed; retained as partial evidence')
    partial.replace(target)
    return {**row, 'status': 'verified_download', 'downloaded_bytes': total}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--lock', required=True, type=Path)
    parser.add_argument('--wheelhouse', required=True, type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text())
    if digest(args.lock) != data['lock_sha256']:
        raise ValueError('Reviewed dependency lock changed')
    rows = data['wheels']
    if len(rows) != 79 or len({r['filename'] for r in rows}) != 79:
        raise ValueError('Exact reviewed 79-wheel closure required')
    lock = args.lock.read_text()
    for row in rows:
        validate_row(row)
        if f"{row['name']}=={row['version']}" not in lock or row['sha256'] not in lock:
            raise ValueError('Wheel is not in the reviewed lock')
    args.wheelhouse.mkdir(parents=True, exist_ok=True)
    missing = sum(r['bytes'] for r in rows if not verified(args.wheelhouse/r['filename'], r))
    if shutil.disk_usage(args.wheelhouse).free < missing + 1024**3:
        raise ValueError('Insufficient staging disk; no partial bulk acquisition')
    receipt = {'manifest_sha256': digest(args.manifest), 'lock_sha256': digest(args.lock),
               'scope': 'dependency archives only; no model weights or inference', 'files': []}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks = [pool.submit(acquire, row, args.wheelhouse) for row in rows]
        for task in concurrent.futures.as_completed(tasks):
            result = task.result()
            receipt['files'].append(result)
            receipt['verified_files'] = len(receipt['files'])
            receipt['downloaded_bytes'] = sum(r['downloaded_bytes'] for r in receipt['files'])
            args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
            print(f"{receipt['verified_files']}/79 {result['filename']} {result['status']}", flush=True)
    print(f"COMPLETE {receipt['verified_files']} verified archives", flush=True)


if __name__ == '__main__':
    main()
