"""Materialize byte-checked public Python source, without model assets or Git hooks."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import urllib.request

HERE=Path(__file__).resolve().parent
INVENTORY=HERE.parent/'runtime_phase2_targeted_20261121'/'source-inventories.json'


def fetch(profile,destination):
    record=json.loads(INVENTORY.read_text())[profile]
    if record['tree_truncated'] is not False:
        raise ValueError('Incomplete publisher tree')
    entries={name:row for name,row in record['source_inventory'].items()
             if PurePosixPath(name).suffix in ('.py','.yaml','.yml') and row['mode'] in ('100644','100755')}
    base=f"https://raw.githubusercontent.com/{record['repo']}/{record['revision']}/"
    def materialize(item):
        name,row=item
        rel=PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or row['bytes']>2_000_000:
            raise ValueError(f'Invalid source entry: {name}')
        with urllib.request.urlopen(base+name,timeout=25) as reply:
            data=reply.read(row['bytes']+1)
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data)!=row['bytes'] or blob!=row['git_blob_sha1']:
            raise ValueError(f'Publisher byte pin mismatch: {name}')
        target=destination/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        return name,{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    with ThreadPoolExecutor(max_workers=12) as pool:
        return dict(pool.map(materialize,sorted(entries.items())))


if __name__=='__main__':
    profile,path=sys.argv[1:]
    print(json.dumps(fetch(profile,Path(path)),indent=2))
