"""Explicit dependency-only preparation on the owner-authorized private CPU host.

No gated source, credentials, checkpoint or model execution. Persistent task
storage survives ordinary shell reconnection; every reusable receipt is pinned.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

COMMIT='dfbcd2412d0b31f737d34f18a5519e20a0d4f2aa'
PYTHON='3.11.18'


def remove_bootstrap_pip_metadata(original_prefix,prefix,target):
    """Remove only byte-identical obsolete bootstrap metadata in our own copy.

    --prefix installation overlays code but cannot uninstall the original
    standalone interpreter's pip metadata. Ambiguous metadata must never enter
    a runtime binding. Preserve the upstream interpreter and package code.
    """
    original_site=original_prefix/'lib/python3.11/site-packages'
    site=prefix/'lib/python3.11/site-packages'
    replacement=site/('pip-'+target+'.dist-info/METADATA')
    if not replacement.is_file():raise RuntimeError('Pinned replacement pip metadata missing')
    removed=[]
    for old in original_site.glob('pip-*.dist-info'):
        if old.name=='pip-'+target+'.dist-info':continue
        candidate=site/old.name
        if not candidate.exists():continue
        before={p.relative_to(old).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in old.rglob('*') if p.is_file()}
        after={p.relative_to(candidate).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
               for p in candidate.rglob('*') if p.is_file()}
        if candidate.is_symlink() or before!=after:
            raise RuntimeError('Unexpected modification to obsolete bootstrap metadata')
        removed.append({'directory':old.name,'files':before})
        shutil.rmtree(candidate)
    return removed


def execute(command, log, *, cwd=None, env=None, timeout=240):
    with log.open('a') as stream:
        subprocess.run(command,cwd=cwd,env=env,check=True,timeout=timeout,
                       stdout=stream,stderr=subprocess.STDOUT)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('root',type=Path);p.add_argument('lock',type=Path)
    p.add_argument('lock_sha256');a=p.parse_args()
    os.umask(0o077)
    rawroot=a.root.absolute()
    if rawroot.is_symlink() or any(x.is_symlink() for x in rawroot.parents):
        raise RuntimeError('Materialized private task root required')
    root=rawroot.resolve()
    marker=root/'REDPAD_PHASE2_TASK'
    if root.exists() and any(root.iterdir()) and (not marker.is_file() or marker.read_text()!=COMMIT):
        raise RuntimeError('Refuse to overwrite another task directory')
    root.mkdir(parents=True,exist_ok=True);marker.write_text(COMMIT)
    lock=a.lock.read_bytes()
    if hashlib.sha256(lock).hexdigest()!=a.lock_sha256:
        raise RuntimeError('Dependency lock changed')
    pins=dict(re.findall(r'(?m)^([a-z][a-z0-9_-]*)==([^\s\\]+)',lock.decode()))
    if pins.get('torch')!='2.7.1+cpu' or pins.get('torchaudio')!='2.7.1+cpu':
        raise RuntimeError('Exact declared CPU diagnostic wheels required')
    if any(n.startswith(('nvidia-','cuda-')) or n in ('triton','encodec','vocos') for n in pins):
        raise RuntimeError('No CUDA/Encodec/pip-Vocos stack in this CPU diagnostic')
    (root/'voice-cpu.lock').write_bytes(lock)
    log=root/'dependency-setup.log'
    # Never expose account credentials to dependency installers or test workers.
    for name in ('install-home','tmp','wheels'):(root/name).mkdir(exist_ok=True)
    env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(root/'install-home'),
         'TMPDIR':str(root/'tmp'),'LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1',
         'PIP_CONFIG_FILE':'/dev/null','CUDA_VISIBLE_DEVICES':''}
    if not shutil.which('bwrap'):
        execute(['sudo','-n','apt-get','update'],log,timeout=180)
        execute(['sudo','-n','apt-get','install','-y','--no-install-recommends','bubblewrap'],log,timeout=120)
    repo=root/'studio'
    if not repo.exists():
        execute(['git','clone','--quiet','--depth','1','--branch','feature/video-music-editing-studio',
                 'https://github.com/REDPADSTUDIO-UX/blank-app.git',str(repo)],log,timeout=90)
    actual=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    if actual!=COMMIT:raise RuntimeError('Owner checkpoint changed; no blind update')
    if subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--untracked-files=no'],text=True):
        raise RuntimeError('Existing public source checkout changed')
    execute(['/usr/local/bin/uv','python','install',PYTHON,'--install-dir',str(root/'python'),'--no-bin'],log,timeout=180)
    originals=list((root/'python').glob('cpython-'+PYTHON+'-linux-*/bin/python3.11'))
    if len(originals)!=1:raise RuntimeError('Exact standalone CPython source not found')
    original=originals[0];prefix=root/'voice-runtime'
    if not prefix.exists():shutil.copytree(original.parent.parent,prefix,symlinks=False)
    interpreter=prefix/'bin/python3.11'
    offline={**env,'PYTHONPATH':str(repo)}
    # Reuse success on the same kernel; replacement VMs require fresh isolation evidence.
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    gate=root/'kernel-host.json'
    prior=json.loads(gate.read_text()) if gate.is_file() else {}
    if prior.get('boot_id')!=boot or prior.get('python')!=str(interpreter):
        execute([str(interpreter),'-B',str(repo/'verification/kernel_phase1_20261121/probe.py')],
                root/'kernel-private.log',cwd=repo,env=offline,timeout=90)
        gate.write_text(json.dumps({'boot_id':boot,'python':str(interpreter),'result':'PASS',
            'log_sha256':hashlib.sha256((root/'kernel-private.log').read_bytes()).hexdigest()}))
    print('RP_PRIVATE_HOST_READY '+json.dumps({'root':str(root),'kernel_contract':'PASS',
          'python':PYTHON,'source_commit':COMMIT,'gated_source_transferred':False}),flush=True)
    if shutil.disk_usage(root).free<3*1024**3:raise RuntimeError('Insufficient private staging disk')
    receipt=root/'install-receipt.json'
    if receipt.is_file():
        previous=json.loads(receipt.read_text())
        if previous.get('lock_sha256')!=a.lock_sha256:
            raise RuntimeError('Completed runtime belongs to a different lock')
        for item in previous['wheels']:
            wheel=root/'wheels'/item['filename']
            if not wheel.is_file() or hashlib.sha256(wheel.read_bytes()).hexdigest()!=item['sha256']:
                raise RuntimeError('Previously verified wheel changed')
        print('RP_PRIVATE_INSTALL_REUSED '+json.dumps({'root':str(root),'lock_sha256':a.lock_sha256}),flush=True)
        return
    # Separate official indexes: identically named PyPI/mirror wheels may have
    # different bytes. Never accept a replacement hash from a failed transfer.
    blocks=re.split(r'(?m)(?=^[a-z][a-z0-9_-]*==)',lock.decode())
    for family,index in (('pypi','https://pypi.org/simple'),('cpu','https://download.pytorch.org/whl/cpu')):
        selected=[]
        for block in blocks:
            match=re.match(r'([a-z][a-z0-9_-]*)==',block)
            if match and ((match[1] in ('torch','torchaudio'))==(family=='cpu')):
                selected.append(block)
        part=root/(family+'.lock');part.write_text(''.join(selected))
        download=[str(original),'-m','pip','--isolated','download','--dest',str(root/'wheels'),
                  '--index-url',index,'--find-links',str(root/'wheels'),
                  '--require-hashes','--only-binary=:all:','--no-deps','--retries','1','-r',str(part)]
        execute(download,log,env=env,timeout=600)
    wheels=[]
    for file in sorted((root/'wheels').glob('*.whl')):
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if digest not in lock.decode():raise RuntimeError('Unapproved wheel in private wheelhouse')
        wheels.append({'filename':file.name,'bytes':file.stat().st_size,'sha256':digest})
    if len(wheels)!=len(pins):raise RuntimeError('Exact selected dependency closure required')
    execute([str(original),'-m','pip','--isolated','install','--prefix',str(prefix),
             '--no-index','--find-links',str(root/'wheels'),'--require-hashes','--only-binary=:all:',
             '--no-deps','--no-compile','--ignore-installed','-r',str(root/'voice-cpu.lock')],log,env=env,timeout=240)
    removed=remove_bootstrap_pip_metadata(original.parent.parent,prefix,pins['pip'])
    execute([str(interpreter),'-B','-m','pip','check'],log,env=env,timeout=30)
    for cache in list(prefix.rglob('__pycache__')):
        if cache.is_dir():shutil.rmtree(cache)
    for pyc in prefix.rglob('*.pyc'):pyc.unlink()
    result={'root':str(root),'python':PYTHON,'interpreter':str(interpreter),'pins':pins,
            'lock_sha256':a.lock_sha256,'wheels':wheels,'pip_check':'PASS',
            'gpu':False,'checkpoint':False,'gated_source_executed':False,
            'obsolete_bootstrap_metadata_removed':removed}
    (root/'install-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RP_PRIVATE_INSTALL_DONE '+json.dumps({'root':str(root),'wheels':len(wheels),
          'bytes':sum(x['bytes'] for x in wheels),'pip_check':'PASS'}),flush=True)


if __name__=='__main__':main()
