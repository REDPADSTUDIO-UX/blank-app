"""Export the current registry and index Phase 2 receipts without relabeling tests."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from redpad_pipeline.worker_isolation import profile_requirements, IsolationBlocked

FAMILIES = {
    'media': ('wan22_5', 'svd_xt'),
    'speech': ('indic_parler',),
    'modern': ('qwen35_27','qwen36_27','qwen35_9','gemma3_27','gemma3_12','flux2_klein4','z_image_turbo'),
}
BLOCKERS = {
    'qwen35_moe': 'Registry contract only. Existing shared adapter has no MoE route.',
    'wan_animate2': 'Exact reviewed native source and complete dependency closure needed for WanAnimate2MPIPipeline.',
    'wan_animate2_distilled': 'Separate contract-only profile. No approved adapter or complete runtime lock.',
    'ltx25': 'Pinned LTX native code and dependency lock needed. Official spatial upscaler SHA-256 remains unavailable.',
    'indic_speak': 'Exact reviewed source and SNAC, Vocos, SoundFile and Torch stack not instantiated.',
    'indicf5': 'Exact reviewed F5 source and Vocos, SoundFile and matching TorchAudio stack not instantiated.',
    'ace15': 'Exact reviewed ACE-Step 1.5 source and TorchAudio, Diffusers and Transformers closure not instantiated.',
    'stable_audio_small': 'Exact reviewed stable-audio-tools and native audio runtime closure not instantiated.',
}
GPU = {
    'media': 'Verify selected CUDA wheel and driver, device binding, BF16/precision, video pipeline, decoder and offload memory.',
    'speech': 'Validate exact offline speech checkpoint, tokenizer and decoder; CPU path itself requires no GPU.',
    'modern': 'Verify exact CUDA wheel and driver, device binding, NF4 GPU extensions for text and precision/offload for image.',
}


def main():
    registry_path = ROOT/'assets/professional/phase3_candidates.json'
    registry = json.loads(registry_path.read_text())
    matrix = json.loads((ROOT/'verification/agent_implementation_matrix_current.json').read_text())
    readings = json.loads((HERE/'sandbox-results.json').read_text())
    rows = {}
    for key, model in registry['profiles'].items():
        family = next((name for name, keys in FAMILIES.items() if key in keys), None)
        try:
            required = sorted(profile_requirements(key, model['adapter'] if model['adapter'] in (
                'hf_text_nf4','flux2_klein','z_image') else None))
        except IsolationBlocked:
            required = None
        row = {
            'repo':model['repo'], 'pinned_revision':model['revision'],
            'registry_adapter':model['adapter'], 'runtime_family':family,
            'required_distribution_contract':required, 'license':model.get('license_metadata'),
            'production_runtime_approved':False, 'model_inference_verified':False,
        }
        if family:
            host = json.loads((HERE/f'{family}-host.json').read_text())
            case = readings[family]
            row.update(
                status='PASS — EXECUTED AND VERIFIED' if case['isolated_imports_passed'] else 'PARTIAL — SOME TESTS VERIFIED',
                status_scope='Model-free CPU package startup only',
                python=host['python'], architecture=host['architecture'],
                installed_host_interpreter=host['interpreter'],
                exact_lock_path=f'{family}.lock.txt', lock_sha256=host['dependency_lock_sha256'],
                key_versions={p:host['dependency_lock'].get(p) for p in (
                    'torch','torchaudio','transformers','diffusers','accelerate','bitsandbytes','tokenizers','safetensors')},
                host_import_evidence=f'{family}-host.json', sandbox_evidence=case,
                ffmpeg_scope='Synthetic H264/AAC host codec test in codec.json',
                outstanding=GPU[family],
            )
        else:
            row.update(status='BLOCKED — EXTERNAL DEPENDENCY', blocker=BLOCKERS[key],
                       exact_lock_path=None, installed_host_interpreter=None,
                       outstanding='Reviewed dependency closure and offline CPU startup first, then exact model/accelerator validation.')
        rows[key] = row
    agents = [{
        'name':agent['name'], 'role':agent['key'],
        'primary':registry['agents'][agent['key']]['primary_candidate'],
        'alternatives':registry['agents'][agent['key']]['secondary_candidates'],
        'selection':registry['agents'][agent['key']]['validated_selection'],
    } for agent in matrix['agents']]
    assert len(agents) == 21
    legacy = json.loads((ROOT/'assets/professional/models.json').read_text())['models']
    result = {'registry_sha256':hashlib.sha256(registry_path.read_bytes()).hexdigest(),
              'profiles':rows, 'agents':agents, 'legacy_inventory':{
                  k:{'repo':v['repo'], 'revision':v.get('revision'), 'status':'PASS — STATIC CONTRACT ONLY'}
                  for k,v in legacy.items()}}
    (HERE/'runtime-matrix.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')


if __name__ == '__main__':
    main()
