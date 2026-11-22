"""Retrieve publisher source/config metadata only. Never follow a model-file redirect."""
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
registry = json.loads((ROOT/'assets/professional/phase3_candidates.json').read_text())['profiles']
native = json.loads((ROOT/'assets/professional/phase3_native_source_lock.json').read_text())
voice = json.loads((ROOT/'assets/professional/phase3_voice_selected_source_lock.json').read_text())

def get(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.status, response.read(200_001)
    except urllib.error.HTTPError as error:
        return error.code, b''

def snapshot(url, expected=None):
    code, body = get(url)
    row = {'url':url,'http_status':code}
    if code == 200:
        if len(body)>200_000:
            raise ValueError('Oversized source metadata response')
        row.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        if expected:
            row['expected_sha256']=expected
            row['sha256_matches']=row['sha256']==expected
    return row,body

def main():
    rows = {}
    for name, relative in [('qwen35_moe','config.json'),('wan_animate2_distilled','model_index.json')]:
        p=registry[name]
        url=f"https://huggingface.co/{p['repo']}/raw/{p['revision']}/{relative}"
        row,body=snapshot(url)
        if body:
            cfg=json.loads(body)
            row['declared_symbols']=cfg.get('architectures') or cfg.get('_class_name')
            expected=next((f for f in p.get('auxiliary_files',[]) if f['path']==relative),None)
            if expected:
                blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
                row['pinned_blob_matches']=(expected.get('git_blob_sha1')==blob and expected['bytes']==len(body))
                row['git_blob_sha1']=blob
        rows[name]=row
    repos={'ltx25':('Lightricks/LTX-2','packages/ltx-pipelines/pyproject.toml'),
           'wan_animate2':('Wan-Video/Wan-Animate-2','requirements.txt'),
           'ace15':('ace-step/ACE-Step-1.5','pyproject.toml')}
    for name,(repo,requirements) in repos.items():
        rev=native['revisions'][name]
        base=f'https://raw.githubusercontent.com/{repo}/{rev}/'
        rows[name]={'source_revision':rev,'reviewed_source':{}}
        for path,sha in native['files'][name].items():
            rows[name]['reviewed_source'][path]=snapshot(base+path,sha)[0]
        row,body=snapshot(base+requirements)
        rows[name]['requirements']=row
        if body:
            (OUT/f'{name}-upstream-requirements.txt').write_bytes(body)
    for name in ('indic_speak','indicf5'):
        model=voice['models'][name]
        rows[name]={'source_revision':model['revision'],'runtime_authorized':voice['runtime_authorized'],
                    'reviewed_source':{path:snapshot(meta['url'],meta['sha256'])[0]
                                       for path,meta in model['files'].items() if path.endswith('.py')}}
    ltx=registry['ltx25']
    url=f"https://huggingface.co/api/models/{ltx['repo']}/tree/{ltx['revision']}/latent_upscale_models?expand=true"
    code,body=get(url)
    entries=json.loads(body) if code==200 else []
    rows['ltx25']['auxiliary_tree']={'url':url,'http_status':code,
        'matching_entries':[{'path':r['path'],'size':r['size'],'lfs':r.get('lfs')}
                            for r in entries if 'latent-spatial-upscaler-x2-bf16-1.0' in r['path']]}
    (OUT/'publisher-evidence.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__':
    main()
