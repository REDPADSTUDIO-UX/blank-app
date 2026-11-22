"""Resolve only already selected dependency versions against official metadata.

No wheels, weights or remote code are loaded. A failed payload digest is never
used as authority. Save metadata identities before retrying a pinned transfer.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href')

def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    pins=dict(re.findall(r'(?m)^([a-z][a-z0-9_-]*)==([^\s\\]+)',a.input.read_text()))
    rows=[];lock=['# Exact versions preserved; authoritative PyPI/PyTorch metadata hashes.\n']
    for name,version in sorted(pins.items()):
        if name in ('torch','torchaudio'):
            url='https://download.pytorch.org/whl/cpu/'+name+'/'
            raw=urllib.request.urlopen(url,timeout=30).read();parser=Links();parser.feed(raw.decode())
            wanted=f'{name}-{version}-cp311-cp311-manylinux_2_28_x86_64.whl'
            matches=[urllib.parse.urljoin(url,u) for u in parser.links
                     if urllib.parse.unquote(urllib.parse.urlsplit(u).path).endswith('/'+wanted)]
            if len(matches)!=1:raise RuntimeError('Exact official CPU wheel metadata missing: '+name)
            selected=urllib.parse.urlsplit(matches[0]);digest=selected.fragment.removeprefix('sha256=')
            assert re.fullmatch('[0-9a-f]{64}',digest)
            files=[{'filename':wanted,'sha256':digest,'url':matches[0]}]
        else:
            url='https://pypi.org/pypi/'+name+'/'+version+'/json'
            raw=urllib.request.urlopen(url,timeout=30).read();metadata=json.loads(raw)
            assert metadata['info']['version']==version
            files=[{'filename':v['filename'],'sha256':v['digests']['sha256'],'url':v['url']}
                   for v in metadata['urls'] if v['packagetype']=='bdist_wheel']
            if not files:raise RuntimeError('No approved binary wheels: '+name)
        rows.append({'name':name,'version':version,'metadata_url':url,
            'metadata_sha256':hashlib.sha256(raw).hexdigest(),'files':files})
        lock.append(name+'=='+version+' \\\n'+' \\\n'.join('    --hash=sha256:'+v for v in sorted({f['sha256'] for f in files}))+'\n')
    encoded=''.join(lock).encode();a.output.write_bytes(encoded)
    a.output.with_suffix('.sources.json').write_text(json.dumps({'pins':pins,'sources':rows,
        'lock_sha256':hashlib.sha256(encoded).hexdigest(),'weights_downloaded':False},indent=2)+'\n')
    print('RP_CANONICAL_LOCK_READY '+json.dumps({'pins':len(pins),'sha256':hashlib.sha256(encoded).hexdigest()}),flush=True)

if __name__=='__main__':main()
