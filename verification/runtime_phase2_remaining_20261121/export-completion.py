"""Merge current profile outcomes with unchanged historical CPU and isolation evidence."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
history=json.loads((HERE.parent/'runtime_phase2_20261121/runtime-matrix.json').read_text())
stable=json.loads((HERE/'stable-sandbox-receipt.json').read_text())
BLOCKERS={
    'qwen35_moe': ('BLOCKED — no approved executable MoE route',
                   'MoE class imported. The existing NF4 converter converted the Linear control and left both actual packed expert tensors unquantized on meta.',
                   'Approve and verify an exact expert-compatible offline quantization/precision recipe; existing dense route remains closed to this profile.'),
    'wan_animate2': ('PARTIAL — existing pinned native adapter',
                    'Four reviewed source files matched. Actual upstream entrypoint import was not executed.',
                    'Review and approve the full source and CPU diagnostic closure matching WanAnimate2MPIPipeline. The pinned source requirements select the CUDA 12.6 Torch stack.'),
    'wan_animate2_distilled': ('BLOCKED — exact pipeline absent',
                              'WanAnimate2Transformer3DModel imports; the pinned model_index requires WanAnimate2Pipeline, which Diffusers 0.43.0 does not export.',
                              'Publisher-supported, reviewed source and locked dependencies for the exact pipeline are required. Keep this separate from the base Animate route.'),
    'ltx25': ('PARTIAL — existing pinned native adapter',
              'Five reviewed source hashes matched. Pinned ltx-pipelines 1.6.2 metadata acquired; no full authorized CPU runtime.',
              'Review exact LTX source closure and its linked ltx-core; publisher must supply the gated artifact SHA-256 for checkpoint installation.'),
    'indic_speak': ('PARTIAL — existing gated native adapter',
                   'SNAC, SoundFile, CPU Torch/TorchAudio and Llama symbol import; publisher selected source URLs return HTTP 401.',
                   'Owner-approved access to exact reviewed gated source plus complete SNAC/Vocos dependency/license closure.'),
    'indicf5': ('PARTIAL — existing gated native adapter',
                'CPU Torch/TorchAudio and SoundFile import. Selected source returns HTTP 401 and Vocos imports require absent Encodec.',
                'Owner-approved exact gated F5 source and a commercially eligible reviewed Vocos/codec closure; retain reference consent gate.'),
    'ace15': ('PARTIAL — existing pinned native adapter',
              'Seven reviewed source hashes matched and fixed Diffusers VAE symbol imported separately; actual ACE native handler import was not executed.',
              'Approve complete pinned source and model-free CPU diagnostic lock distinct from publisher Linux Torch 2.10.0+cu128 production dependencies.'),
}
result={}
for k,profile in history['profiles'].items():
    row={'repo':profile['repo'],'revision':profile['pinned_revision'],'registry_adapter':profile['registry_adapter'],
         'model_loading_gpu':'GPU-DEPENDENT / NOT TESTED'}
    if k in BLOCKERS:
        contract,probe,blocker=BLOCKERS[k]
        row.update(runtime_contract=contract,cpu_model_free_startup='PARTIAL — supporting probes/source only; full entrypoint not verified',
                   secure_runtime_binding='NOT TESTED for exact runtime closure',observed=probe,remaining=blocker)
    elif k=='stable_audio_small':
        row.update(runtime_contract='IMPLEMENTED — existing native adapter; Python 3.10 isolated lock',
                   cpu_model_free_startup='PASS — actual required imports and synthetic WAV in production sandbox' if stable['isolated_pass'] else 'PARTIAL — host imports only',
                   secure_runtime_binding='PASS — actual interpreter, revision, exact dependency/file/ABI validation and isolated child' if stable['isolated_pass'] else 'NOT VERIFIED',
                   observed='Existing legacy audio dispatch repaired; no generation or model loading.',
                   evidence='stable-sandbox-receipt.json',
                   remaining='Explicit approval/licensing and manifest for exact model and auxiliary assets; CUDA launch and generation validation.')
    else:
        row.update(runtime_contract='IMPLEMENTED — historical tested CPU family '+profile['runtime_family'],
                   cpu_model_free_startup='PASS — historical',secure_runtime_binding='PASS — historical',
                   evidence='../runtime_phase2_20261121/sandbox-results.json')
    result[k]=row
assert len(result)==18
record={'new_verified':int(stable['isolated_pass']),'historical_verified':10,
        'total_verified':10+int(stable['isolated_pass']),'profiles':result}
(HERE/'final-18-profile-matrix.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
