"""Restore only the exact prior-authorized CPU runtime and baseline model.
No arbitrary URL/model arguments; reject a changed vendor artifact or model.
"""
import hashlib,json,subprocess,tarfile,urllib.request
from pathlib import Path
import zstandard
from redpad_pipeline.local_ollama_session import ROOT,local_cpu_session
from redpad_pipeline.model_routing import inventory

if __name__=='__main__':
    prior=json.loads((ROOT/'verification/master_studio/restoration.json').read_text())
    folder=ROOT/'phase3_models';folder.mkdir(exist_ok=True)
    archive=folder/'ollama-0.40.15.tar.zst'
    url='https://github.com/ollama/ollama/releases/download/v0.40.15/ollama-linux-amd64.tar.zst'
    if not archive.exists():
        with urllib.request.urlopen(url,timeout=120) as src,archive.with_suffix('.part').open('wb') as dst:
            while b:=src.read(4*1024*1024):dst.write(b)
        archive.with_suffix('.part').rename(archive)
    h=hashlib.sha256()
    with archive.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    if h.hexdigest()!=prior['expected_archive_sha256']:raise RuntimeError('Prior runtime checksum differs; refuse extraction.')
    runtime=folder/'ollama-runtime';runtime.mkdir(exist_ok=True)
    with archive.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as decompressed,tarfile.open(fileobj=decompressed,mode='r|') as tar:
        for member in tar:
            if not any(x in member.name.lower() for x in ('cuda','rocm','vulkan','mlx')):tar.extract(member,runtime,filter='data')
    model=prior['model']
    with local_cpu_session() as env:
        with (folder/'restore-pull.log').open('w') as log:
            subprocess.run([str(runtime/'bin/ollama'),'pull',model],env=env,stdout=log,stderr=log,timeout=1200,check=True)
        if inventory().get(model)!='sha256:'+prior['expected_runtime_manifest_digest']:raise RuntimeError('Prior model identity changed.')
        checks=[]
        for row in prior['verified_blobs']:
            p=folder/'ollama-weights/blobs'/row['digest'].replace(':','-');h=hashlib.sha256()
            with p.open('rb') as f:
                while b:=f.read(4*1024*1024):h.update(b)
            if p.stat().st_size!=row['bytes'] or 'sha256:'+h.hexdigest()!=row['digest']:raise RuntimeError('Prior model blob identity differs.')
            checks.append(dict(row,verified=True))
    out=ROOT/'verification/filmmaking_intelligence/restoration.json'
    out.write_text(json.dumps({'prior_authorization_reused':True,'new_variants':0,'model':model,'archive_sha256':prior['expected_archive_sha256'],'verified_blobs':checks,'GPU_used':False,'owned_server_stopped':True},indent=2)+'\n')
    print('Restored exact prior-authorized CPU baseline; no new variant.',flush=True)
