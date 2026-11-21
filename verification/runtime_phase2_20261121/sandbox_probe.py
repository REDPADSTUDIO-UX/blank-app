"""Bind an exact standalone CPU prefix to registry profiles and run an offline probe."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.native_local_bundle import digest_file
from redpad_pipeline.shared_model_services import profile
from redpad_pipeline.worker_isolation import (
    RuntimeBindings, environment, isolation_command, runtime_identity, source_digest, system_component,
)

GROUPS = {
    'media': ('wan22_5', 'svd_xt'),
    'speech': ('indic_parler',),
    'modern': ('qwen35_27', 'qwen36_27', 'qwen35_9', 'gemma3_27', 'gemma3_12',
               'flux2_klein4', 'z_image_turbo'),
}
BOOTSTRAP = """
import json, os, runpy, sys
from redpad_pipeline.worker_isolation import verify_running_runtime
assert os.readlink('/proc/self/ns/net') != sys.argv[3]
verify_running_runtime(json.loads(sys.argv[1]))
sys.argv=['/redpad/input/probe.py',sys.argv[2]]
runpy.run_path(sys.argv[0],run_name='__main__')
"""


def record(path):
    return {'bytes':path.stat().st_size,'sha256':digest_file(path)}


def dependencies(prefix, interpreter):
    found, unresolved = set(), set()
    objects = [interpreter, *sorted(p for p in prefix.rglob('*.so*')
                                   if p.is_file() and '.so' in p.name)]
    for path in objects:
        result = subprocess.run(['/usr/bin/ldd', str(path)], capture_output=True, text=True,
                                timeout=10, env={'PATH':'/usr/bin:/bin','LC_ALL':'C',
                                                 'LD_LIBRARY_PATH':str(prefix/'lib')})
        for match in re.findall(r'(/[^\s]+) \(0x', result.stdout):
            target=Path(os.path.normpath(match))
            if not target.resolve().is_relative_to(prefix):
                found.add(target)
        for name in re.findall(r'^\s*(\S+) => not found',result.stdout,re.MULTILINE):
            unresolved.add(name)
    system = {}
    for path in sorted(found):
        metadata = record(path)
        try:
            system_component(str(path), metadata)
        except ValueError as error:
            raise RuntimeError(f'Host ELF dependency {path} resolves to {path.resolve()} outside the binding contract') from error
        system[str(path)] = metadata
    return system, sorted(unresolved)


def main():
    family, raw_prefix = sys.argv[1:]
    prefix = Path(raw_prefix).resolve(strict=True)
    interpreter = prefix/'bin/python3.11'
    lock = dict(line.split('==', 1) for line in
                (Path(__file__).with_name(f'{family}.lock.txt')).read_text().splitlines())
    files = {p.relative_to(prefix).as_posix():record(p) for p in sorted(prefix.rglob('*')) if p.is_file()}
    system, unresolved = dependencies(prefix, interpreter)
    base = {'prefix':str(prefix),'interpreter':str(interpreter),'dependency_lock':lock,
            'files':files,'system_files':system,'studio_sha256':source_digest()}
    for identifier in GROUPS[family]:
        receipt = {**base,'profile':identifier,'revision':profile(identifier)['revision']}
        RuntimeBindings.validate(identifier, receipt)
    canonical = json.dumps(base,sort_keys=True,separators=(',',':')).encode()
    identity = runtime_identity(base,hashlib.sha256(canonical).hexdigest())
    print(json.dumps({'validated_profiles':GROUPS[family],'identity':identity,
                      'studio_sha256':base['studio_sha256'],'manifest_files':len(files),
                      'empty_files':sum(not f['bytes'] for f in files.values()),
                      'system_files':system,'unresolved_elf_sonames':unresolved},sort_keys=True),flush=True)
    with tempfile.TemporaryDirectory() as directory:
        output=Path(directory)/'output'
        output.mkdir()
        command=isolation_command(Path(__file__).with_name('probe.py').resolve(), output, [],
                                  runtime=base, worker='shared_model_worker' if family=='modern' else 'native_local_worker')
        return subprocess.run([*command[:-3],'-c',BOOTSTRAP,json.dumps(identity),family,
                               Path('/proc/self/ns/net').readlink().as_posix()],
                              env=environment(),timeout=75).returncode


if __name__ == '__main__':
    raise SystemExit(main())
