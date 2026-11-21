"""Model-free worker dependency and ABI probes. Run with the candidate interpreter."""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

CHECKS = {
    'media': ['torch', 'transformers:AutoTokenizer', 'diffusers:WanPipeline',
              'diffusers:WanImageToVideoPipeline', 'diffusers:StableVideoDiffusionPipeline',
              'accelerate', 'tokenizers', 'safetensors.torch', 'PIL.Image', 'imageio_ffmpeg'],
    'speech': ['torch', 'torchaudio', 'transformers:AutoTokenizer',
               'parler_tts:ParlerTTSForConditionalGeneration', 'dac',
               'soundfile', 'librosa', 'tokenizers', 'safetensors.torch'],
    'modern': ['torch', 'transformers:AutoProcessor', 'transformers:BitsAndBytesConfig',
               'transformers:Qwen3_5ForConditionalGeneration',
               'transformers:Gemma3ForConditionalGeneration',
               'diffusers:Flux2KleinPipeline', 'diffusers:ZImagePipeline',
               'bitsandbytes', 'accelerate', 'tokenizers', 'safetensors.torch', 'PIL.Image'],
}

OFFLINE = {'HF_HUB_OFFLINE':'1', 'TRANSFORMERS_OFFLINE':'1', 'HF_DATASETS_OFFLINE':'1',
           'HF_HUB_DISABLE_TELEMETRY':'1', 'CUDA_VISIBLE_DEVICES':'', 'DO_NOT_TRACK':'1',
           'PYTHONDONTWRITEBYTECODE':'1', 'TOKENIZERS_PARALLELISM':'false'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory():
    return dict(sorted(
        (re.sub(r'[-_.]+', '-', d.metadata['Name'].lower()), d.version)
        for d in importlib.metadata.distributions()
    ))


def forbid_network(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
        raise PermissionError('Phase 2 package probe forbids network access')


def import_checks(family):
    sys.addaudithook(forbid_network)
    results = {}
    for check in CHECKS[family]:
        name, _, symbol = check.partition(':')
        try:
            module = importlib.import_module(name)
            if symbol:
                getattr(module, symbol)
            if name == 'torch':
                assert module.tensor([1, 2], device='cpu').sum().item() == 3
            results[check] = {'ok': True, 'file': getattr(module, '__file__', None)}
        except Exception as error:
            results[check] = {'ok': False, 'error': f'{type(error).__name__}: {error}'}
    torch = sys.modules.get('torch')
    return {'imports':results, 'torch':getattr(torch, '__version__', None),
            'torch_cuda_build':getattr(getattr(torch, 'version', None), 'cuda', None)}


def codec_check():
    ffmpeg, ffprobe = (shutil.which(tool) for tool in ('ffmpeg', 'ffprobe'))
    if not ffmpeg or not ffprobe:
        raise RuntimeError('FFmpeg and FFprobe must be explicitly available for this case')
    with tempfile.TemporaryDirectory() as folder:
        target = str(Path(folder) / 'synthetic.mp4')
        run = [ffmpeg, '-v', 'error', '-f', 'lavfi', '-i', 'color=black:s=64x64:r=10:d=0.3',
               '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-shortest',
               '-c:v', 'libx264', '-c:a', 'aac', target]
        subprocess.run(run, check=True, timeout=20)
        inspect = [ffprobe, '-v', 'error', '-show_streams', '-of', 'json', target]
        results = json.loads(subprocess.check_output(inspect, text=True, timeout=10))
        codecs = sorted((s['codec_type'], s['codec_name']) for s in results['streams'])
        assert codecs == [('audio', 'aac'), ('video', 'h264')], codecs
    tools = {}
    for path in (ffmpeg, ffprobe):
        abi = subprocess.check_output(['ldd', path], text=True, timeout=10)
        assert 'not found' not in abi
        tools[path] = {'sha256':digest(path), 'ldd':abi,
                       'version':subprocess.check_output([path,'-version'], text=True, timeout=10).splitlines()[0]}
    return {'commands':[run,inspect], 'streams':codecs, 'tools':tools}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('family', choices=[*CHECKS, 'codec'])
    parser.add_argument('--inventory-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(OFFLINE)
    lock = inventory()
    executable = Path(sys.executable).resolve()
    result = {
        'family':args.family, 'python':sys.version, 'interpreter':sys.executable,
        'real_interpreter':str(executable), 'interpreter_sha256':digest(executable),
        'prefix':sys.prefix, 'base_prefix':sys.base_prefix,
        'platform':platform.platform(), 'architecture':platform.machine(),
        'dependency_lock':lock,
        'dependency_lock_sha256':hashlib.sha256(json.dumps(lock,sort_keys=True).encode()).hexdigest(),
        'offline_env':OFFLINE, 'weights_loaded':False, 'gpu_inference':False,
    }
    if not args.inventory_only:
        if args.family == 'codec':
            result['codec'] = codec_check()
        else:
            result.update(import_checks(args.family))
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return int(any(not status['ok'] for status in result.get('imports',{}).values()))


if __name__ == '__main__':
    raise SystemExit(main())
