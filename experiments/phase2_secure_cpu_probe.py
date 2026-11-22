"""Exact new public runtime startup in the existing production sandbox boundary.

This diagnostic substitutes only the child probe, as the existing Phase 2
acceptance harness does. It never activates a registry route or loads a model.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.worker_isolation import (
    RuntimeBindings, environment, isolation_command, runtime_identity, source_digest,
)
from redpad_pipeline.shared_model_services import profile
from redpad_pipeline.native_local_bundle import digest_file, verify_tree
from verification.runtime_phase2_20261121.sandbox_probe import dependencies

CHILD = r'''
import hashlib, importlib.metadata, json, os, sys
from pathlib import Path
from redpad_pipeline.worker_isolation import verify_running_runtime
from redpad_pipeline.fp8_preflight import KERNEL_REVISION, validate_resolution
identity, namespace, private = json.loads(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
verify_running_runtime(identity)
assert os.readlink('/proc/self/ns/net') != namespace
assert not private.exists() and 'HF_TOKEN' not in os.environ and 'HTTPS_PROXY' not in os.environ
def deny_network(event, args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
        raise PermissionError('Offline model-free diagnostic')
sys.addaudithook(deny_network)
sys.path.insert(0,'/redpad/source/diffusers/src')
import torch, torchvision, transformers, triton, kernels, accelerate
from transformers import Qwen3_5MoeForConditionalGeneration, FineGrainedFP8Config
assert FineGrainedFP8Config().dequantize is False
rows=json.loads(Path('/redpad/source/kernel-lock.json').read_text())
for name, expected in rows.items():
    assert hashlib.sha256((Path('/redpad/source/kernel')/name).read_bytes()).hexdigest()==expected
os.environ['KERNELS_CACHE']='/tmp/kernel-cache'
from huggingface_hub.file_download import repo_folder_name
from kernels._versions import resolve_version_spec_as_ref
repo='kernels-community/finegrained-fp8'
ref=Path('/tmp/kernel-cache')/repo_folder_name(repo_id=repo,repo_type='kernel')/'refs/v4'
ref.parent.mkdir(parents=True);ref.write_text(KERNEL_REVISION);ref.chmod(0o444)
resolved=resolve_version_spec_as_ref(repo,4,local_files_only=True)
validate_resolution(resolved.target_commit)
from diffusers import ModularPipeline,WanAnimate2DistilledModularPipeline,WanAnimate2DistilledBlocks
metadata=Path('/tmp/model-metadata');metadata.mkdir()
metadata.joinpath('modular_model_index.json').write_bytes(Path('/redpad/source/modular_model_index.json').read_bytes())
pipeline=ModularPipeline.from_pretrained(str(metadata),local_files_only=True,trust_remote_code=False)
assert type(pipeline).__name__=='WanAnimate2DistilledModularPipeline'
assert not torch.cuda.is_initialized()
report={'status':'PASS','qwen_class':Qwen3_5MoeForConditionalGeneration.__name__,
 'kernel_version':resolved.name,'kernel_revision':resolved.target_commit,'kernel_files':len(rows),
 'wan_loader':type(pipeline).__name__,'wan_blocks':WanAnimate2DistilledBlocks.__name__,
 'torch':torch.__version__,'transformers':transformers.__version__,
 'cuda_initialized':False,'weights_loaded':False,'model_inference':False,
 'component_tensor_equivalence':False,'registry_routes_promoted':False,
 'production_ready':False,'independent_artistic_acceptance':False}
Path('/redpad/output/secure-startup.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,sort_keys=True),flush=True)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', type=Path)
    parser.add_argument('sources', type=Path)
    parser.add_argument('source_receipt', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    prefix, sources = args.prefix.resolve(strict=True), args.sources.resolve(strict=True)
    args.output.mkdir(parents=True, exist_ok=True)
    source_receipt = json.loads(args.source_receipt.read_text())
    if source_receipt['diffusers_revision'] != '3a2f35d4efa4c059c8bfb3bc0d6c906264895c81':
        raise ValueError('Unexpected reviewed Diffusers source')
    verify_tree(sources, source_receipt['source_files'], allow_empty=True)
    interpreter = prefix / 'bin/python3.11'
    lock = json.loads(subprocess.check_output([
        str(interpreter), '-B', '-c',
        "import importlib.metadata,json,re; print(json.dumps({re.sub(r'[-_.]+','-',d.metadata['Name'].lower()):d.version for d in importlib.metadata.distributions()}))"
    ], text=True, env={**environment(), 'PATH':'/usr/bin:/bin', 'PYTHONPATH':''}, timeout=20))
    files = {p.relative_to(prefix).as_posix(): {'bytes':p.stat().st_size,'sha256':digest_file(p)}
             for p in sorted(prefix.rglob('*')) if p.is_file()}
    system, unresolved = dependencies(prefix, interpreter)
    base = {'prefix': str(prefix), 'interpreter': str(interpreter), 'dependency_lock': lock,
            'files': files, 'system_files': system, 'studio_sha256': source_digest()}
    for identifier in ('qwen35_moe', 'wan_animate2_distilled'):
        RuntimeBindings.validate(identifier, {**base, 'profile':identifier,
                                             'revision':profile(identifier)['revision']})
    canonical = json.dumps(base, sort_keys=True, separators=(',',':')).encode()
    identity = runtime_identity(base, hashlib.sha256(canonical).hexdigest())
    (args.output/'binding.json').write_text(json.dumps({
        'identity':identity,'manifest_files':len(files),'system_files':system,
        'unresolved_elf_sonames':unresolved,'studio_sha256':base['studio_sha256'],
        'source_manifest_sha256':digest_file(args.source_receipt),
        'source_files':len(source_receipt['source_files']),
        'scope':'Model-free CPU diagnostic only, not a production runtime approval'
    },indent=2)+'\n')
    if args.validate_only:
        print('PASS exact files, ABI and both profile contracts; sandbox launch NOT performed',flush=True)
        return
    with tempfile.TemporaryDirectory() as temporary:
        private=Path(temporary)/'unmounted-private-marker';private.write_text('synthetic')
        job=Path(temporary)/'diagnostic.json';job.write_text('{}')
        for worker in ('shared_model_worker','native_local_worker'):
            command=isolation_command(job,args.output,[],runtime=base,worker=worker,
                                      source=(sources,source_receipt['source_files']))
            subprocess.run([*command[:-3],'-c',CHILD,json.dumps(identity),
                            os.readlink('/proc/self/ns/net'),str(private)],
                           env={**environment(),'CUDA_VISIBLE_DEVICES':''},check=True,timeout=90)
            (args.output/'secure-startup.json').rename(args.output/(worker+'.json'))


if __name__ == '__main__':
    main()
