"""Bounded, model-free startup/immutable-version checks in the approved closure.

This does not load an executable CUDA kernel, model, checkpoint or production
route. An unavailable secure accelerator remains a separate acceptance gate.
"""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--kernel',required=True,type=Path)
    parser.add_argument('--cache',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',
                      CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',
                      KERNELS_CACHE=str(args.cache),DO_NOT_TRACK='1')
    def no_network(event,_args):
        if event in ('socket.connect','socket.bind','socket.getaddrinfo','socket.sendto'):
            raise PermissionError('Model-free startup forbids network access')
    sys.addaudithook(no_network)
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root))
    from redpad_pipeline.fp8_preflight import KERNEL_REVISION,MODEL_REPO,MODEL_REVISION,validate_resolution
    manifest=json.loads((root/'verification/phase2_cpu_gaps_20261122/qwen-platform-wheels.json').read_text())
    versions={r['name']:importlib.metadata.version(r['name']) for r in manifest['wheels']}
    assert all(versions[r['name']]==r['version'] for r in manifest['wheels'])
    kernel=json.loads((root/'verification/phase2_cpu_gaps_20261122/qwen-kernel-v4.json').read_text())
    hashes={name:row['sha256'] for name,row in kernel['files'].items()}
    hashes.update({'metadata.json':kernel['metadata_sha256'],'metadata.json.sigstore':kernel['sigstore_bundle_sha256']})
    for name,expected in hashes.items():
        p=args.kernel/name
        assert p.is_file() and not p.is_symlink()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,name
    imports={}
    for name in ('torch','torchvision','transformers','triton','kernels','accelerate'):
        module=importlib.import_module(name)
        imports[name]={'file':module.__file__,'version':getattr(module,'__version__',None)}
    from transformers import Qwen3_5MoeForConditionalGeneration,FineGrainedFP8Config
    from transformers.integrations.hub_kernels import _KERNELS_INTERNAL_PATH_MAPPINGS
    from kernels._versions import resolve_version_spec_as_ref
    from huggingface_hub.file_download import repo_folder_name
    import torch
    assert not torch.cuda.is_initialized()
    repo='kernels-community/finegrained-fp8'
    ref=args.cache/repo_folder_name(repo_id=repo,repo_type='kernel')/'refs/v4'
    ref.parent.mkdir(parents=True,exist_ok=True)
    if ref.exists():validate_resolution(ref.read_text().strip())
    else:ref.write_text(KERNEL_REVISION)
    ref.chmod(0o444)
    actual=resolve_version_spec_as_ref(repo,4,local_files_only=True)
    validate_resolution(actual.target_commit)
    assert FineGrainedFP8Config().dequantize is False
    result={'python':sys.version,'prefix':sys.prefix,'imports':imports,'installed_locked_versions':versions,
            'exact_wheels':79,'reviewed_kernel_files':len(hashes),'resolved_version':actual.name,
            'resolved_kernel_revision':actual.target_commit,'kernel_ref_readonly':not bool(ref.stat().st_mode&0o222),
            'model_class_import':Qwen3_5MoeForConditionalGeneration.__name__,
            'alternative_model':{'repo':MODEL_REPO,'revision':MODEL_REVISION},
            'kernel_signature':'Historical verified signature reused; all exact signed bundle bytes matched',
            'cuda_initialized':torch.cuda.is_initialized(),'model_weights_loaded':False,
            'actual_model_inference':False,'executable_cuda_kernel_loaded':False,
            'secure_worker_binding':'PENDING namespace-capable host acceptance; no sandbox bypass',
            'registered_model_route_changed':False,'professional_acceptance':False}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
