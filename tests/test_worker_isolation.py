"""CPU-only security contracts and optional kernel namespace denial canary."""
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from redpad_pipeline.agents import AgentError, AgentStore
from redpad_pipeline.native_execution import NativeExecution
from redpad_pipeline.native_local_bundle import digest_file
from redpad_pipeline.shared_model_services import profile, read_shared_text
from redpad_pipeline.screenwriter import WritingError
from redpad_pipeline.worker_isolation import (
    IsolationBlocked, RuntimeBindings, environment, isolation_command, source_digest,
)


class WorkerIsolationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / 'output'
        self.output.mkdir()
        self.private = self.root / 'private.txt'
        self.private.write_text('synthetic private canary')
        self.job = self.root / 'request.json'
        self.job.write_text('{}')
        self.store = AgentStore(self.root / 'agent_control.sqlite3')

    def system_files(self):
        # ldd examines the already-trusted test interpreter, never a model/runtime input.
        details = subprocess.check_output(['/usr/bin/ldd', sys.executable], env=environment(fixture_root=self.root), text=True)
        prefix = Path(sys.base_prefix).resolve()
        paths = (Path(label) for label in re.findall(r'(/[^\s]+) \(0x', details))
        return {str(path): {'bytes': path.stat().st_size, 'sha256': digest_file(path)}
                for path in paths if not path.resolve().is_relative_to(prefix)}

    def command(self, runtime, **kwargs):
        return isolation_command(self.job, self.output, [], runtime=runtime,
                                 worker='shared_model_worker', **kwargs)

    def test_only_explicit_files_are_mounted_and_environment_is_allowlisted(self):
        runtime = {'prefix': str(Path(sys.base_prefix)), 'interpreter': str(Path(sys.base_prefix) / 'bin/python3'), 'system_files': {}}
        model = self.root / 'checkpoint'
        model.mkdir()
        component = model / 'config.json'
        component.write_text('{}')
        (model / 'unapproved.txt').write_text('synthetic')
        with patch.object(Path, 'is_file', autospec=True, side_effect=lambda p: p == Path('/usr/bin/bwrap') or actual_is_file(p)):
            args = self.command(runtime, model=model, model_files={'config.json': {}})
        self.assertIn('--unshare-all', args)
        self.assertIn('--die-with-parent', args)
        self.assertEqual(args[args.index('--remount-ro') + 1], '/')
        self.assertEqual(args.count('--bind'), 1)
        self.assertIn(str(component), args)
        self.assertIn(str(self.job), args)
        for denied in (str(self.root), str(self.private), str(model / 'unapproved.txt')):
            self.assertNotIn(denied, args)
        with self.assertRaises(IsolationBlocked):
            isolation_command(self.job,self.output,['/dev/mem'],runtime=runtime,worker='shared_model_worker')
        with patch.object(Path, 'is_file', autospec=True, side_effect=lambda p: p != Path('/usr/bin/bwrap') and actual_is_file(p)):
            with self.assertRaisesRegex(IsolationBlocked,'Bubblewrap is unavailable'):
                self.command(runtime)
        with patch.dict(os.environ, {'HF_TOKEN':'fake','HTTPS_PROXY':'fake','LD_PRELOAD':'fake'}):
            self.assertTrue({'HF_TOKEN','HTTPS_PROXY','LD_PRELOAD'}.isdisjoint(environment(gpu=True)))

    def test_kernel_private_file_denial_and_readonly_request(self):
        if not Path('/usr/bin/bwrap').is_file():
            self.skipTest('Bubblewrap binary unavailable')
        runtime = {'prefix': str(Path(sys.base_prefix)), 'interpreter': str(Path(sys.base_prefix) / 'bin/python3'), 'system_files': self.system_files()}
        command = self.command(runtime)
        command[-3:] = ['-c', '''
from pathlib import Path
import sys
assert not Path(sys.argv[1]).exists()
job = Path('/redpad/input/request.json')
assert job.read_text() == '{}'
try:
    job.write_text('denied')
except OSError:
    pass
else:
    raise AssertionError('request is writable')
Path('/redpad/output/canary').write_text('passed')
''', str(self.private)]
        proc = subprocess.run(command, env=environment(), text=True, capture_output=True, timeout=15)
        if proc.returncode and ('uid map' in proc.stderr or 'namespace' in proc.stderr or 'NETLINK_ROUTE' in proc.stderr):
            self.skipTest(proc.stderr.strip())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.output / 'canary').read_text(), 'passed')

    def test_runtime_receipt_binds_exact_interpreter_dependencies_and_source(self):
        prefix = self.root / 'runtime'
        files = {'bin/python3': b'test interpreter fixture', 'lib/python3.14/encodings/__init__.py': b'# fixture'}
        lock = dict.fromkeys(('torch', 'transformers', 'bitsandbytes', 'accelerate'), '1.2.3')
        for package, version in lock.items():
            files[f'lib/python3.14/site-packages/{package}-1.2.3.dist-info/METADATA'] = f'Name: {package}\nVersion: {version}\n'.encode()
        manifest = {}
        for name, content in files.items():
            path = prefix / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            manifest[name] = {'bytes':len(content),'sha256':digest_file(path)}
        interpreter = prefix / 'bin/python3'
        interpreter.chmod(0o700)
        receipt = {'profile':'qwen35_27','revision':profile('qwen35_27')['revision'],
                   'prefix':str(prefix),'interpreter':str(interpreter),'files':manifest,
                   'dependency_lock':lock,'system_files':self.system_files(),'studio_sha256':source_digest()}
        service = RuntimeBindings(self.store)
        with self.assertRaises(IsolationBlocked):
            service.approve('qwen35_27', receipt, owner='fixture')
        digest = service.approve('qwen35_27', receipt, owner='fixture', confirmed=True)
        self.assertEqual(service.get('qwen35_27'), (receipt,digest))
        with self.assertRaises(IsolationBlocked):
            service.get('flux2_klein4')
        with self.assertRaises(IsolationBlocked):
            service.validate('qwen35_27', {**receipt,'dependency_lock':{}})
        with self.assertRaises(IsolationBlocked):
            service.validate('qwen35_27', {**receipt,'interpreter':sys.executable})
        with self.assertRaises(IsolationBlocked):
            service.validate('qwen35_27', {**receipt,'system_files':{str(self.private):{}}})
        interpreter.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            service.get('qwen35_27')

    def test_shared_kernel_block_preserves_terminal_evidence_and_never_launches_fallback(self):
        workers = NativeExecution(self.store)
        run_id = workers.queue_shared('qwen35_27',{}, {}, [],'test-receipt')
        with patch.object(NativeExecution,'_shared_job',side_effect=IsolationBlocked('fixture isolation refusal')), patch('subprocess.Popen') as launch:
            terminal = workers.run(run_id,authorized=True)
        launch.assert_not_called()
        self.assertEqual(terminal['state'],'ISOLATION BLOCKED')
        reopened = NativeExecution(self.store)
        self.assertEqual(reopened.recover(run_id),terminal)
        self.assertEqual(reopened.cancel(run_id),terminal)
        self.assertFalse(terminal['result']['production_ready'])

    def test_shared_cancellation_uses_persisted_controller_and_drops_partial_result(self):
        workers = NativeExecution(self.store)
        run_id = workers.queue_shared('qwen35_27', {}, {}, [], 'test-receipt')
        command = [sys.executable, '-m', 'redpad_pipeline.native_fixture_worker',
                   'timeout', str(workers.root / run_id)]
        results = []
        with patch.object(NativeExecution, '_shared_job', return_value=(command, 'test-receipt')), patch(
            'redpad_pipeline.native_execution.environment',
            return_value=environment(fixture_root=Path(__file__).resolve().parents[1]),
        ):
            run = threading.Thread(target=lambda: results.append(workers.run(run_id, authorized=True, timeout=8)))
            run.start()
            try:
                deadline = time.monotonic() + 5
                while not workers._row(run_id)['pid'] and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(workers._row(run_id)['pid'])
                NativeExecution(self.store).cancel(run_id)
            finally:
                run.join(timeout=9)
        self.assertEqual(results[0]['state'], 'CANCELLED')
        self.assertNotIn('worker', results[0]['result'])

    def test_shared_source_pin_and_terminal_receipt_detect_changes(self):
        workers = NativeExecution(self.store)
        run_id = workers.queue_shared('qwen35_27', {}, {}, [], 'test-receipt')
        with patch('redpad_pipeline.native_execution.source_digest', return_value='changed'), patch('subprocess.Popen') as launch:
            self.assertEqual(workers.run(run_id, authorized=True)['state'], 'STALE')
        launch.assert_not_called()
        with self.store.tx() as db:
            db.execute("UPDATE native_research_runs SET result='{}' WHERE id=?", (run_id,))
        with self.assertRaisesRegex(AgentError, 'receipt was altered'):
            workers.status(run_id)

    def test_shared_supervisor_rechecks_exact_versions_and_rights(self):
        from PIL import Image
        from redpad_pipeline.producer_references import References
        from redpad_pipeline.shared_model_services import SharedServices

        image=io.BytesIO()
        Image.new('RGB',(8,8),'gray').save(image,format='PNG')
        refs=References(self.store)
        unauthorized=refs.put('fixture.png',image.getvalue(),'character',source='synthetic',rights='reference_only')
        install={'manifest':{'sha256':'test fixture'}}
        workers=NativeExecution(self.store)
        request={'prompt':'synthetic','width':512,'height':512,'steps':4,'seed':3,
                 'references':[{'id':unauthorized['id'],'version':1}]}
        run=workers.queue_shared('flux2_klein4',request,install,[unauthorized],'unused')
        with patch.object(SharedServices,'installed',return_value=install):
            with self.assertRaisesRegex(AgentError,'rights-authorized'):
                workers._shared_inputs(json.loads(workers._row(run)['payload']))
            approved=refs.update(unauthorized['id'],1,rights='fictional_ai')
            request['references']=[{'id':approved['id'],'version':2}]
            wrong_pin=workers.queue_shared('flux2_klein4',request,install,[unauthorized],'unused')
            with self.assertRaisesRegex(AgentError,'changed after queueing'):
                workers._shared_inputs(json.loads(workers._row(wrong_pin)['payload']))
            correct_pin=workers.queue_shared('flux2_klein4',request,install,[approved],'unused')
            _,_,paths=workers._shared_inputs(json.loads(workers._row(correct_pin)['payload']))
            self.assertEqual(paths,[refs.path(approved)])

    def test_shared_text_handoff_denies_artifact_changes(self):
        raw = self.output / 'raw_response.txt'
        raw.write_text('synthetic output')
        receipt = {'artifact_sha256': digest_file(raw)}
        self.assertEqual(read_shared_text(self.output, receipt), 'synthetic output')
        raw.write_text('replaced output')
        with self.assertRaises(WritingError):
            read_shared_text(self.output, receipt)

    def test_direct_shared_worker_requires_kernel_namespace_before_torch_import(self):
        from redpad_pipeline.shared_model_worker import run
        self.job.write_text(json.dumps({'profile':{},'request':{},'output_dir':str(self.output)}))
        with patch.dict(sys.modules, {'torch': None}), self.assertRaises(PermissionError):
            run(self.job)


actual_is_file = Path.is_file
