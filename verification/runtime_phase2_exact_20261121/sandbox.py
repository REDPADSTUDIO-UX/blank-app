"""Verify dependency/source pins, then import the real CPU entrypoints in Bubblewrap."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(HERE.parent/'runtime_phase2_20261121'))
from sandbox_probe import dependencies, record
from redpad_pipeline.native_local_bundle import verify_tree
from redpad_pipeline.shared_model_services import profile
from redpad_pipeline.worker_isolation import RuntimeBindings, environment, isolation_command, runtime_identity, source_digest

BOOTSTRAP="""
import json,os,runpy,sys
from redpad_pipeline.worker_isolation import verify_running_runtime
assert os.readlink('/proc/self/ns/net') != sys.argv[3]
verify_running_runtime(json.loads(sys.argv[1]))
sys.argv=['/redpad/input/probe.py',sys.argv[2],'/redpad/source']
runpy.run_path(sys.argv[0],run_name='__main__')
"""


def main():
    name,prefix,source=sys.argv[1:]
    prefix=Path(prefix).resolve(strict=True)
    source=Path(source).resolve(strict=True)
    python=prefix/'bin/python3.11'
    source_manifest=json.loads((HERE/f'{name}-source-lock.json').read_text())
    verify_tree(source,source_manifest,allow_empty=True)
    old=json.loads((ROOT/'assets/professional/phase3_native_source_lock.json').read_text())
    assert all(source_manifest[path]['sha256']==sha for path,sha in old['files'][name].items())
    lock=dict(line.split('==',1) for line in (HERE/f'{name}.lock.txt').read_text().splitlines())
    libraries,unresolved=dependencies(prefix,python)
    receipt={'profile':name,'revision':profile(name)['revision'],'prefix':str(prefix),
             'interpreter':str(python),'dependency_lock':lock,'studio_sha256':source_digest(),
             'files':{p.relative_to(prefix).as_posix():record(p) for p in sorted(prefix.rglob('*')) if p.is_file()},
             'system_files':libraries}
    RuntimeBindings.validate(name,receipt)
    identity=runtime_identity(receipt,hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest())
    print(json.dumps({'profile':name,'revision':receipt['revision'],'identity':identity,
                      'publisher_source_revision':old['revisions'][name],'source_files':len(source_manifest),
                      'source_lock_sha256':record(HERE/f'{name}-source-lock.json')['sha256'],
                      'runtime_files':len(receipt['files']),'system_files':libraries,
                      'potential_unresolved_elf_dependencies':unresolved},sort_keys=True),flush=True)
    with tempfile.TemporaryDirectory() as directory:
        output=Path(directory)/'output'
        output.mkdir()
        argv=isolation_command(HERE/'probe.py',output,[],runtime=receipt,worker='native_local_worker',
                               source=(str(source),source_manifest))
        return subprocess.run([*argv[:-3],'-c',BOOTSTRAP,json.dumps(identity),name,
                               os.readlink('/proc/self/ns/net')],env=environment(),timeout=90).returncode


if __name__=='__main__':
    raise SystemExit(main())
