import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import urllib.request

from packaging.tags import compatible_tags, cpython_tags
from packaging.utils import parse_wheel_filename

platforms = [f"manylinux_2_{minor}_x86_64" for minor in range(28, 4, -1)]
platforms += ["manylinux2014_x86_64", "manylinux2010_x86_64", "manylinux1_x86_64"]
tags = list(cpython_tags((3, 11), platforms=platforms))
tags += list(compatible_tags((3, 11), interpreter="cp311", platforms=platforms))
ranking = {tag: i for i, tag in reversed(list(enumerate(tags)))}
lock = Path("qwen-candidate.lock").read_text()
blocks = re.split(r"(?m)^(?=[a-z][a-z0-9_-]*==)", lock)[1:]


def inspect(block):
    name, version = block.splitlines()[0].split()[0].split("==")
    hashes = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", block))
    metadata_url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(metadata_url, timeout=25) as response:
        document = response.read()
    choices = []
    for file in json.loads(document)["urls"]:
        if not file["filename"].endswith(".whl") or file["yanked"] or file["digests"]["sha256"] not in hashes:
            continue
        wheel_tags = parse_wheel_filename(file["filename"])[3]
        matching = wheel_tags & ranking.keys()
        if matching:
            choices.append((min(ranking[tag] for tag in matching), file["filename"], file))
    if not choices:
        raise ValueError(f"No locked platform wheel for {name}=={version}")
    _, _, wheel = min(choices)
    return {"name": name, "version": version, "filename": wheel["filename"],
            "url": wheel["url"], "sha256": wheel["digests"]["sha256"], "bytes": wheel["size"],
            "metadata_url": metadata_url, "metadata_sha256": hashlib.sha256(document).hexdigest()}


with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    wheels = list(pool.map(inspect, blocks))
assert len(wheels) == 79
Path("qwen-platform-wheels.json").write_text(json.dumps(
    {"platform": "CPython 3.11 Linux x86_64 glibc >=2.28", "status": "public candidate metadata only",
     "lock_sha256": hashlib.sha256(lock.encode()).hexdigest(), "wheels": wheels}, indent=2) + "\n")
print(f"{len(wheels)} compatible wheel filenames and hashes matched to the lock")
