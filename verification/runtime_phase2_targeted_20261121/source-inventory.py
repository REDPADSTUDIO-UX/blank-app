"""Publisher Git trees and reviewed source interfaces only. No model artifacts."""
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
LOCK=json.loads((ROOT/'assets/professional/phase3_native_source_lock.json').read_text())
PROJECTS={
    'wan_animate2':('Wan-Video/Wan-Animate-2',('infer/','pipelines/','wanxiang/'),
                    ('requirements.txt','pipelines/wan_animate_2_pipeline.py','infer/wan_animate_2.yaml')),
    'ltx25':('Lightricks/LTX-2',('packages/ltx-pipelines/','packages/ltx-core/'),
             ('packages/ltx-pipelines/pyproject.toml','packages/ltx-core/pyproject.toml',
              'packages/ltx-pipelines/src/ltx_pipelines/distilled.py')),
    'ace15':('ace-step/ACE-Step-1.5',('acestep/',),
             ('pyproject.toml','acestep/handler.py','acestep/inference.py')),
}


def get(url):
    try:
        with urllib.request.urlopen(url,timeout=18) as response:
            return response.status,response.read(7_000_001)
    except urllib.error.HTTPError as error:
        return error.code,b''


def scan(key):
    repo,prefixes,paths=PROJECTS[key]
    rev=LOCK['revisions'][key]
    tree_url=f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1'
    status,data=get(tree_url)
    tree=json.loads(data) if status==200 else {}
    entries={r['path']:{'git_blob_sha1':r['sha'],'bytes':r['size'],'mode':r['mode']} for r in tree.get('tree',[])
             if r['type']=='blob' and r['path'].startswith(prefixes)
             and Path(r['path']).suffix in ('.py','.toml','.yaml','.yml','.json','.txt','.sh','.cpp','.cu','.h')}
    body={'repo':repo,'revision':rev,'tree_url':tree_url,'http_status':status,
          'tree_truncated':tree.get('truncated'),'source_inventory':entries,
          'lock_review_complete':False,'source_execution_authorized_by_this_receipt':False,'inspected':{}}
    targets=sorted(set(paths)|LOCK['files'][key].keys())
    for path in targets:
        url=f'https://raw.githubusercontent.com/{repo}/{rev}/{path}'
        code,b=get(url)
        row={'url':url,'http_status':code}
        if code==200:
            sha=hashlib.sha256(b).hexdigest()
            blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            row.update(bytes=len(b),sha256=sha,git_blob_sha1=blob,
                       prior_sha256_matches=sha==LOCK['files'][key][path] if path in LOCK['files'][key] else None,
                       tree_blob_matches=entries[path]['git_blob_sha1']==blob if path in entries else None)
            if path.endswith('.py'):
                ast_tree=ast.parse(b)
                row['top_level_imports']=[ast.unparse(n) for n in ast_tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
                row['entrypoints']={}
                for node in ast_tree.body:
                    if isinstance(node,ast.ClassDef) and node.name in ('WanAnimate2MPIPipeline','DistilledPipeline','AceStepHandler'):
                        row['entrypoints'][node.name]={'bases':[ast.unparse(base) for base in node.bases],
                          'methods':{m.name:ast.unparse(m.args) for m in node.body if isinstance(m,ast.FunctionDef) and m.name in ('__init__','__call__','stream_chunks','initialize_service')}}
                    if isinstance(node,ast.FunctionDef) and node.name=='generate_music':
                        row['entrypoints'][node.name]=ast.unparse(node.args)
            if path.endswith('pyproject.toml') or path.endswith('requirements.txt'):
                (OUT/f'{key}-{Path(path).name}' if 'ltx_core' not in path and 'ltx-core' not in path else OUT/'ltx25-core-pyproject.toml').write_bytes(b)
        body['inspected'][path]=row
    return key,body


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        result=dict(pool.map(scan,PROJECTS))
    (OUT/'source-inventories.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':
    main()
