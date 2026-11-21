"""Kernel-only process isolation and owner-pinned, self-contained Python runtimes."""
import hashlib
import importlib.metadata
import json
import os
import re
import sys
from email.parser import BytesParser
from pathlib import Path
from types import MappingProxyType

from .agents import AgentError, encode
from .native_local_bundle import digest_file, verify_tree

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PACKAGES = MappingProxyType({
    'hf_text_nf4': {'torch', 'transformers', 'bitsandbytes', 'accelerate'},
    'flux2_klein': {'torch', 'diffusers', 'transformers', 'pillow', 'accelerate'},
    'z_image': {'torch', 'diffusers', 'transformers', 'pillow', 'accelerate'},
    'wan22_5': {'torch', 'diffusers', 'transformers', 'accelerate'},
    'svd_xt': {'torch', 'diffusers', 'transformers'},
    'ltx25': {'torch', 'transformers', 'safetensors'},
    'wan_animate2': {'torch', 'omegaconf', 'transformers'},
    'ace15': {'torch', 'torchaudio', 'transformers'},
    'indic_parler': {'torch', 'transformers', 'parler-tts'},
    'indic_speak': {'torch', 'transformers', 'snac', 'vocos'},
    'indicf5': {'torch', 'torchaudio', 'transformers'},
    'stable_audio_small': {'torch', 'stable-audio-tools'},
})
DEVICES = frozenset('/dev/' + name for name in ('nvidia0', 'nvidiactl', 'nvidia-uvm', 'nvidia-uvm-tools'))
SYSTEM_LIBRARY = re.compile(
    r'/(?:usr/)?lib(?:64|/(?:x86_64|aarch64)-linux-gnu(?:/nvidia/[a-zA-Z0-9_.-]+)?)?/'
    r'(?:lib[a-zA-Z0-9_+.-]+\.so(?:\.[a-zA-Z0-9_.-]+)?|ld-linux-[a-zA-Z0-9_.-]+\.so\.\d+)'
)
SYSTEM_TOOLS = frozenset(('/usr/bin/ffmpeg', '/usr/bin/ffprobe'))
WORKERS = frozenset(('native_local_worker', 'shared_model_worker'))


class IsolationBlocked(AgentError):
    pass


def worker_source_files():
    files = [p for p in (ROOT / 'redpad_pipeline').iterdir() if p.suffix in ('.py', '.json')]
    files.extend(ROOT / name for name in (
        'redpad_video_studio.py', 'assets/professional/phase3_candidates.json',
        'assets/professional/phase3_native_source_lock.json',
        'assets/professional/phase3_voice_selected_source_lock.json',
        'assets/professional/phase3_voice_public_source_lock.json',
        'assets/professional/phase3_19agent_no_gpu_staging.json', 'assets/offline/engines.json',
        'assets/professional/suite.json', 'assets/professional/models.json',
    ))
    if any(p.is_symlink() or not p.is_file() for p in files):
        raise IsolationBlocked('Worker sources must be regular, materialized files.')
    return sorted(files)


def source_digest():
    return hashlib.sha256(encode({
        str(p.relative_to(ROOT)): digest_file(p) for p in worker_source_files()
    }).encode()).hexdigest()


def regular_tree(root):
    if not root.is_absolute() or '..' in root.parts or root == Path('/') or not root.is_dir():
        raise IsolationBlocked('An absolute, dedicated mount directory is required.')
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise IsolationBlocked('Mount roots must be materialized, without symlinks.')


def system_component(label, metadata):
    """Check the exact host ABI file and its namespace destination."""
    if not isinstance(label, str) or '..' in Path(label).parts or not (SYSTEM_LIBRARY.fullmatch(label) or label in SYSTEM_TOOLS):
        raise IsolationBlocked('System runtime component lies outside the Linux ABI allowlist.')
    try:
        source = Path(label).resolve(strict=True)
    except OSError as exc:
        raise IsolationBlocked('A pinned system runtime component is missing.') from exc
    if not (SYSTEM_LIBRARY.fullmatch(str(source)) or str(source) in SYSTEM_TOOLS):
        raise IsolationBlocked('System runtime link target lies outside the Linux ABI allowlist.')
    if not isinstance(metadata, dict) or set(metadata) != {'bytes', 'sha256'} or not source.is_file():
        raise IsolationBlocked('Expected system runtime size and SHA256.')
    if source.stat().st_size != metadata['bytes'] or digest_file(source) != metadata['sha256']:
        raise IsolationBlocked('Pinned system runtime component changed.')
    return source


def profile_requirements(profile, adapter=None):
    required = RUNTIME_PACKAGES.get(adapter or profile)
    if required is None:
        raise IsolationBlocked('No isolated runtime contract for this profile.')
    return required


class RuntimeBindings:
    """Local research approval. Validate files and metadata without importing model libraries."""
    def __init__(self, store):
        self.store = store
        with store.tx() as db:
            db.execute('CREATE TABLE IF NOT EXISTS worker_runtime_bindings (profile TEXT PRIMARY KEY, receipt TEXT, sha256 TEXT)')

    def approve(self, profile, receipt, *, owner, confirmed=False):
        if confirmed is not True or not isinstance(owner, str) or not owner.strip():
            raise IsolationBlocked('Explicit owner approval of this exact runtime is required.')
        self.validate(profile, receipt)
        raw = json.dumps(receipt, sort_keys=True, separators=(',', ':'), allow_nan=False)
        if len(raw) > 64 * 1024 * 1024:
            raise IsolationBlocked('Runtime receipt exceeds the supported manifest limit.')
        digest = hashlib.sha256(raw.encode()).hexdigest()
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            for row in db.execute('SELECT receipt FROM worker_runtime_bindings WHERE profile!=?', (profile,)):
                other = json.loads(row[0])
                if other['prefix'] == receipt['prefix'] and other['dependency_lock'] != receipt['dependency_lock']:
                    raise IsolationBlocked('Incompatible dependency locks cannot share one runtime prefix.')
            db.execute('INSERT OR REPLACE INTO worker_runtime_bindings VALUES (?,?,?)', (profile, raw, digest))
            self.store.event(db, '', 'owner', 'approve_isolated_worker_runtime', {'profile': profile, 'sha256': digest, 'owner': owner})
        return digest

    def pin(self, profile):
        with self.store.tx() as db:
            row = db.execute('SELECT sha256 FROM worker_runtime_bindings WHERE profile=?', (profile,)).fetchone()
        return row[0] if row else None

    def get(self, profile):
        with self.store.tx() as db:
            row = db.execute('SELECT receipt,sha256 FROM worker_runtime_bindings WHERE profile=?', (profile,)).fetchone()
        if row is None or hashlib.sha256(row[0].encode()).hexdigest() != row[1]:
            raise IsolationBlocked('Exact approved per-profile runtime receipt is absent or altered.')
        receipt = json.loads(row[0])
        self.validate(profile, receipt)
        return receipt, row[1]

    @staticmethod
    def validate(profile, receipt):
        from .shared_model_services import profile as candidate

        fields = {'profile', 'revision', 'prefix', 'interpreter', 'dependency_lock', 'files', 'system_files', 'studio_sha256'}
        if not isinstance(receipt, dict) or set(receipt) != fields:
            raise IsolationBlocked('Exact runtime receipt fields required.')
        model = candidate(profile)
        if receipt['profile'] != profile or receipt['revision'] != model['revision'] or receipt['studio_sha256'] != source_digest():
            raise IsolationBlocked('Runtime profile, model revision or Studio source changed.')
        if not isinstance(receipt['system_files'], dict) or not receipt['system_files']:
            raise IsolationBlocked('A pinned Linux host ABI manifest is required.')
        for path, metadata in receipt['system_files'].items():
            system_component(path, metadata)
        root = Path(receipt['prefix'])
        regular_tree(root)
        interpreter = Path(receipt['interpreter'])
        if interpreter.parent != root / 'bin' or not re.fullmatch(r'python3(?:\.\d+)?', interpreter.name):
            raise IsolationBlocked('Exact interpreter inside the standalone Python prefix required.')
        if 'pyvenv.cfg' in receipt['files'] or not any(re.fullmatch(r'lib/python3\.\d+/encodings/__init__\.py', name) for name in receipt['files']):
            raise IsolationBlocked('A self-contained Python prefix with its own standard library is required.')
        try:
            verify_tree(root, receipt['files'])
        except (AgentError, OSError) as exc:
            raise IsolationBlocked('Runtime file manifest failed validation.') from exc
        # Runtime trees are mounted as a unit. Deny the .git exception used by source bundles.
        if any('.git' in p.relative_to(root).parts or not (p.is_dir() or p.is_file()) for p in root.rglob('*')):
            raise IsolationBlocked('Unexpected runtime tree entry.')
        if interpreter.relative_to(root).as_posix() not in receipt['files'] or not os.access(interpreter, os.X_OK):
            raise IsolationBlocked('Interpreter absent from approved runtime manifest.')
        packages = {}
        for name in receipt['files']:
            if name.endswith('/METADATA') and name.split('/')[-2].endswith('.dist-info'):
                metadata = BytesParser().parsebytes((root / name).read_bytes(), headersonly=True)
                package = re.sub(r'[-_.]+', '-', (metadata['Name'] or '').lower())
                version = metadata['Version']
                if not package or not version or package in packages:
                    raise IsolationBlocked('Ambiguous runtime distribution metadata.')
                packages[package] = version
        required = profile_requirements(profile, model['adapter'] if model['adapter'] in ('hf_text_nf4', 'flux2_klein', 'z_image') else None)
        if receipt['dependency_lock'] != packages or not required <= packages.keys():
            raise IsolationBlocked('Installed distributions differ from the exact profile dependency lock.')


def runtime_identity(receipt, sha256):
    relative = Path(receipt['interpreter']).relative_to(receipt['prefix'])
    return {'interpreter': '/redpad/runtime/' + relative.as_posix(),
            'dependency_lock': receipt['dependency_lock'], 'sha256': sha256}


def verify_running_runtime(identity):
    if not isinstance(identity, dict) or sys.executable != identity.get('interpreter'):
        raise PermissionError('Worker interpreter differs from the approved runtime.')
    actual = {}
    for item in importlib.metadata.distributions():
        name = re.sub(r'[-_.]+', '-', (item.metadata['Name'] or '').lower())
        if not name or name in actual:
            raise PermissionError('Ambiguous distribution in worker Python environment.')
        actual[name] = item.version
    if actual != identity.get('dependency_lock'):
        raise PermissionError('Worker Python distributions differ from the approved runtime.')


def environment(*, fixture_root=None, gpu=False):
    env = {
        'PATH': '/usr/bin:/bin' if fixture_root else '/redpad/runtime/bin:/usr/bin:/bin',
        'HOME': '/tmp', 'TMPDIR': '/tmp',
        'PYTHONPATH': str(fixture_root) if fixture_root else '/redpad/studio',
        'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1', 'PYTHONSAFEPATH': '1',
        'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_DATASETS_OFFLINE': '1',
        'HF_HUB_DISABLE_TELEMETRY': '1', 'TORCH_FORCE_WEIGHTS_ONLY_LOAD': '1',
    }
    if gpu:
        env['CUDA_VISIBLE_DEVICES'] = '0'
    return env


def isolation_command(job_path, output, devices, *, runtime, worker, model=None, model_files=None, source=None, inputs=()):
    if worker not in WORKERS or not isinstance(devices, list) or any(d not in DEVICES for d in devices):
        raise IsolationBlocked('Only fixed worker modules and authorized local GPU devices may be bound.')
    binary = Path('/usr/bin/bwrap')
    if not binary.is_file():
        raise IsolationBlocked('Bubblewrap is unavailable; isolated worker launch blocked.')
    prefix = Path(runtime['prefix'])
    for root in (prefix, output, *([Path(model)] if model else [])):
        regular_tree(root)
    roots = [prefix, output] + ([Path(model)] if model else [])
    if any(a == b or a in b.parents or b in a.parents for i, a in enumerate(roots) for b in roots[i+1:]):
        raise IsolationBlocked('Runtime, checkpoint and output mounts must be disjoint.')
    # Fixed destination aliases prevent a host path from shadowing sandbox system paths.
    args = [str(binary), '--unshare-all', '--unshare-user', '--unshare-net', '--cap-drop', 'ALL',
            '--die-with-parent', '--new-session',
            '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp',
            '--setenv', 'LD_LIBRARY_PATH', '/redpad/runtime/lib:/lib/x86_64-linux-gnu:/lib/aarch64-linux-gnu:/usr/lib/x86_64-linux-gnu:/usr/lib/aarch64-linux-gnu']
    for name, metadata in sorted(runtime['system_files'].items()):
        system_path = system_component(name, metadata)
        args += ['--ro-bind', str(system_path), name]
    args += ['--ro-bind', str(prefix), '/redpad/runtime']
    for host_root, files, destination in (
        (model, model_files, '/redpad/model'),
        (*(source or (None, None)), '/redpad/source'),
    ):
        if host_root:
            from .native_local_bundle import local_path
            args += ['--dir', destination]
            for name in sorted(files):
                args += ['--ro-bind', str(local_path(host_root, name)), destination + '/' + name]
    for path in worker_source_files():
        args += ['--ro-bind', str(path), '/redpad/studio/' + path.relative_to(ROOT).as_posix()]
    for path in (job_path, *inputs):
        if path.is_symlink() or not path.is_file():
            raise IsolationBlocked('Sandbox inputs must be regular files.')
        args += ['--ro-bind', str(path), '/redpad/input/' + path.name]
    for device in devices:
        args += ['--dev-bind', device, device]
    interpreter = Path(runtime['interpreter']).relative_to(prefix)
    args += ['--bind', str(output), '/redpad/output',
             '--remount-ro', '/dev', '--remount-ro', '/', '--chdir', '/redpad/output',
             '--', '/redpad/runtime/' + interpreter.as_posix(), '-m',
             'redpad_pipeline.' + worker, '/redpad/input/' + job_path.name]
    return args
