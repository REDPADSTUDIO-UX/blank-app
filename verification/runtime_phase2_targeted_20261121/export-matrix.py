"""Keep previously verified profiles and attach new evidence to the seven open rows."""
import copy
import json
from pathlib import Path

folder=Path(__file__).resolve().parent
previous=folder.parent/'runtime_phase2_remaining_20261121/final-18-profile-matrix.json'
data=json.loads(previous.read_text())
rows=copy.deepcopy(data['profiles'])
updates={
    'qwen35_moe':(
        'PARTIAL — synthetic FP8 conversion verified; full checkpoint startup not tested',
        'The existing Transformers FP8 converter quantized both packed expert projections on synthetic CPU tensors. '
        'The meta replacement accepted the same routed-forward arguments and a separate CPU dequantized reference passed tolerance.',
        'Exact offline expert-compatible recipe approval and actual quantized GPU kernel and checkpoint validation.',
        'moe-fp8.json'),
    'wan_animate2':(
        'PARTIAL — reviewed source interface only',
        'Immutable publisher source tree and WanAnimate2MPIPipeline signatures inventoried. Previously reviewed hashes matched.',
        'Complete source and CPU dependency closure review, then secure binding and current published cu126 runtime validation.',
        'source-inventories.json'),
    'wan_animate2_distilled':(
        'BLOCKED — exact pipeline missing',
        'Current Diffusers release and publisher model index disagree on the required pipeline symbol.',
        'Publisher-supported offline source and exact dependency pin for WanAnimate2Pipeline. No base pipeline substitution.',
        'publisher-dependency-evidence.json'),
    'ltx25':(
        'PARTIAL — twelve CPU support imports and native operations verified',
        'Pinned LTX Core/Pipeline 1.6.2 metadata and reviewed source matched. TorchVision CPU NMS, TorchAudio resampling, '
        'PyAV PCM roundtrip and Gemma4UnifiedProcessor at Transformers 5.14.1 passed in separate CPU prefix.',
        'Full exact LTX pipeline/core CPU import, OpenImageIO teardown warning investigation and per-profile sandbox binding. '
        'Publisher LFS SHA-256 still required for the exact spatial upscaler; installation fails closed.',
        'ltx-cpu-probe.json'),
    'indic_speak':(
        'BLOCKED — authenticated publisher source and review remain required',
        'Historical SNAC, SoundFile and Llama support imports preserved. No new authorized source entrypoint.',
        'Owner-authorized exact source and reviewed SNAC/Vocos dependency/license closure.',
        '../runtime_phase2_remaining_20261121/voice-support-host.json'),
    'indicf5':(
        'BLOCKED — gated source and codec rights',
        'Current Vocos metadata still pins Encodec 0.1.1; publisher license remains CC BY-NC 4.0.',
        'Authorized revision access and a reviewed commercially eligible codec route. Retain speaker consent gate.',
        'publisher-dependency-evidence.json'),
    'ace15':(
        'PARTIAL — reviewed source interface only',
        'Immutable source tree, handler and generate_music callable reviewed statically. Existing reviewed hashes matched.',
        'Complete reviewed CPU diagnostic closure and exact sandbox binding. CUDA 12.8 Torch/TorchAudio 2.10.0 remains hardware-dependent.',
        'source-inventories.json'),
}
for key,(status,observed,remaining,evidence) in updates.items():
    rows[key].update(cpu_model_free_startup=status,observed=observed,remaining=remaining,evidence=evidence)
assert len(rows)==18 and sum(v['cpu_model_free_startup'].startswith('PASS') for v in rows.values())==11
output={'new_verified':0,'previous_verified':11,'total_verified':11,'total_profiles':18,'profiles':rows}
(folder/'final-18-profile-matrix.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
