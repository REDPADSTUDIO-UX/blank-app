"""Run synthetic Phase 1 canaries on an already-authorized Linux host."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from redpad_pipeline.native_execution import cancel_owned_process, process_identity, terminate_group
from redpad_pipeline.worker_isolation import environment, isolation_command
from tests.test_worker_isolation import WorkerIsolationTests

BOUNDARIES = r"""
import errno,json,os,socket,sys
from pathlib import Path
def denied(action, *additional):
    try:
        action()
    except OSError as error:
        assert error.errno in (errno.ENOENT, errno.EACCES, errno.EPERM, errno.EROFS, *additional), error
    else:
        raise AssertionError('operation unexpectedly succeeded: '+str(action))
private,parent,port=sys.argv[1:]
assert 'HF_TOKEN' not in os.environ and 'HTTPS_PROXY' not in os.environ
assert 'LD_PRELOAD' not in os.environ
host=json.loads(parent)
for name in ('user','mnt','net','pid'):
    assert os.readlink('/proc/self/ns/'+name)!=host[name], name
denied(lambda:Path(private).read_bytes())
denied(lambda:list(Path(private).parent.iterdir()))
denied(lambda:Path('/redpad/output/../..' + private).read_bytes())
link=Path('/tmp/private-link')
link.symlink_to(private)
denied(link.read_bytes)
print('PASS A private read and enumeration',flush=True)
job=Path('/redpad/input/request.json')
assert job.read_text()=='synthetic authorized input'
denied(lambda:job.write_text('changed'))
denied(job.unlink, errno.EBUSY)
candidate=Path('/tmp/candidate')
candidate.write_text('candidate')
try:
    candidate.replace(job)
except OSError as error:
    assert error.errno in (errno.EXDEV,errno.EBUSY,errno.EACCES,errno.EPERM,errno.EROFS), error
else:
    raise AssertionError('replace succeeded')
assert job.read_text()=='synthetic authorized input'
print('PASS B read-only input',flush=True)
Path('/redpad/output/result.txt').write_text('canary')
Path('/tmp/allowed').write_text('canary')
assert Path('/redpad/model/component.txt').read_text()=='synthetic component'
assert Path('/redpad/source/component.txt').read_text()=='synthetic component'
for folder in ('/','/redpad','/redpad/input','/redpad/studio','/redpad/runtime','/redpad/model','/redpad/source','/dev','/proc'):
    try:
        denied(lambda: (Path(folder)/'unauthorized-phase1').write_text('canary'))
    except AssertionError as exc:
        raise AssertionError('unexpected write result at '+folder) from exc
with open('/dev/null','wb',buffering=0) as sink:
    assert sink.write(b'synthetic device I/O') == 20
print('PASS C writable output boundary',flush=True)
assert not Path('/proc/net/route').read_text().splitlines()[1:]
try:
    socket.create_connection(('127.0.0.1',int(port)),timeout=2).close()
except OSError:
    pass
else:
    raise AssertionError('connection to host listener succeeded')
print('PASS D network namespace and host loopback denied',flush=True)
"""

DUMMY = r"""
import subprocess,sys,time
grandchild = 'import time; print("ready",flush=True); time.sleep(30)'
child = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",sys.argv[1]],start_new_session=True); time.sleep(30)'
subprocess.Popen([sys.executable,'-c',child,grandchild],start_new_session=True)
time.sleep(30)
"""

CONTROLLER = """
import json, subprocess, sys, time
child=subprocess.Popen(json.loads(sys.argv[1]),start_new_session=True)
time.sleep(30)
"""


def ready(process):
    import selectors
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        if not selector.select(8) or process.stdout.readline().strip() != 'ready':
            raise RuntimeError('Sandboxed dummy failed to start')


def lifecycle(command, run_dir):
    for action in ('timeout', 'cancel', 'controller_loss'):
        argv = command if action != 'controller_loss' else [
            sys.executable, '-c', CONTROLLER, json.dumps(command),
        ]
        with subprocess.Popen(argv, env=environment(), stdout=subprocess.PIPE, text=True,
                              start_new_session=True) as process:
            try:
                ready(process)
                if action == 'timeout':
                    try:
                        process.wait(timeout=.1)
                    except subprocess.TimeoutExpired:
                        terminate_group(process)
                    else:
                        raise AssertionError('Dummy exited before timeout')
                elif action == 'cancel':
                    assert cancel_owned_process(process.pid, process_identity(process.pid), run_dir)
                else:
                    process.kill()
                # The child and its descendant inherit stdout. EOF confirms both
                # have released the pipe after namespace teardown.
                tail, _ = process.communicate(timeout=5)
                assert tail == '', tail
                print('PASS E', action, flush=True)
            finally:
                if process.poll() is None:
                    terminate_group(process)


def main():
    if subprocess.check_output(['findmnt', '-n', '-o', 'OPTIONS', '-T', '/proc/self/uid_map'],
                               text=True).strip().split(',')[0] == 'ro':
        print('BLOCKED — HOST LIMITATION: UID map is on read-only procfs')
        return 2
    print(subprocess.check_output(['uname', '-srmo'], text=True).strip())
    print(Path('/etc/os-release').read_text())
    bubblewrap = Path('/usr/bin/bwrap')
    if not bubblewrap.is_file():
        print('BLOCKED — HOST LIMITATION: /usr/bin/bwrap is unavailable')
        return 2
    print(subprocess.check_output([str(bubblewrap), '--version'], text=True).strip())
    os.environ['HF_TOKEN']='phase1-synthetic-marker'
    os.environ['HTTPS_PROXY']='phase1-synthetic-marker'
    print('Worker environment:', json.dumps(environment(), sort_keys=True))
    prefix = Path(sys.base_prefix).resolve()
    interpreter = Path(sys.executable).resolve()
    if prefix in (Path('/'), Path('/usr'), Path('/usr/local')) or not interpreter.is_relative_to(prefix):
        raise SystemExit('Use a dedicated standalone Python prefix containing only test runtime files.')
    fixture = WorkerIsolationTests()
    fixture.setUp()
    try:
        fixture.job.write_text('synthetic authorized input')
        runtime = {'prefix': str(prefix), 'interpreter': str(interpreter),
                   'system_files': fixture.system_files()}
        model=fixture.root/'model'
        source=fixture.root/'source'
        manifest={'component.txt': {}}
        for folder in (model,source):
            folder.mkdir()
            (folder/'component.txt').write_text('synthetic component')
        namespaces = {name: os.readlink('/proc/self/ns/'+name) for name in ('user','mnt','net','pid')}
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            for worker in ('native_local_worker', 'shared_model_worker'):
                cmd = isolation_command(fixture.job, fixture.output, [], runtime=runtime, worker=worker,
                                        model=model, model_files=manifest, source=(source, manifest))
                print('Worker mount command:', json.dumps(cmd), flush=True)
                base = cmd[:-3]
                subprocess.run([*base, '-c', BOUNDARIES, str(fixture.private), json.dumps(namespaces),
                                str(listener.getsockname()[1])], env=environment(), check=True, timeout=20)
                assert (fixture.output/'result.txt').read_text() == 'canary'
                assert fixture.job.read_text() == 'synthetic authorized input'
                lifecycle([*base, '-c', DUMMY], fixture.root)
                print('PASS F synthetic launch boundary:', worker, flush=True)
    finally:
        fixture.doCleanups()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
