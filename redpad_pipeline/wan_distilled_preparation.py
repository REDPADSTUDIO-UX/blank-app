"""Revision-locked, model-free preparation for the publisher modular loader.

Merged official source fixes the missing class exports. Component tensor
equivalence and secure runtime/GPU acceptance remain explicit blockers.
"""
import copy
import hashlib
import json
from pathlib import Path
from .agents import AgentError

REPO='Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers'
REVISION='59e4141466bcb1bf9733eca1bc78be6891c9fbdf'
SOURCE_REVISION='3a2f35d4efa4c059c8bfb3bc0d6c906264895c81'
COMPONENT_REVISION='ff28d41a9c0c331137691847cc8700593d785593'
INDEX_SHA256='ca29bd15a717e091b0aee14e22adc6669c511221e6e83ff82f42c339eee20827'
INDEX=Path(__file__).resolve().parents[1]/'assets/professional/wan_distilled_modular_index.json'


def locked_recipe(raw):
    if hashlib.sha256(raw).hexdigest()!=INDEX_SHA256:
        raise AgentError('Original pinned Wan modular index changed; no alias or pipeline substitution.')
    original=json.loads(raw)
    if (original.get('_class_name'),original.get('_blocks_class_name')) != (
            'WanAnimate2DistilledModularPipeline','WanAnimate2DistilledBlocks'):
        raise AgentError('Exact publisher loader and blocks required.')
    config=copy.deepcopy(original);mapping={}
    for name,row in config.items():
        if name.startswith('_'):continue
        if not isinstance(row,list) or len(row)!=3 or row[2].get('pretrained_model_name_or_path')!=REPO:
            raise AgentError('Unknown modular component origin.')
        before=row[2].get('revision')
        if before not in (None,'refs/pr/1'):
            raise AgentError('Unreviewed modular component revision.')
        after=COMPONENT_REVISION if before=='refs/pr/1' else REVISION
        row[2]['revision']=after
        mapping[name]={'publisher_ref':before,'immutable_revision':after}
    return {'profile':'wan_animate2_distilled','repo':REPO,'revision':REVISION,
            'diffusers_source_revision':SOURCE_REVISION,'publisher_pr':14413,
            'original_index_sha256':INDEX_SHA256,'local_loader_configuration':config,
            'explicit_component_revision_mapping':mapping,
            'processor_contract':'Official WanAnimate2VideoProcessor and modular CLIP preprocessing; not the old monolithic CLIPImageProcessor override',
            'component_weight_equivalence_verified':False,'native_worker_implemented':False,
            'launch_authorized':False,'runtime_verified':False,'production_ready':False,
            'blockers':['Immutable PR component tensor equivalence/owner artifact acceptance not established by config equality',
                        'Exact self-contained runtime must pass the existing secure supervisor on an eligible host',
                        'Real checkpoint/GPU and independent motion/performance evaluation remain pending']}


def prepare_staged(store,stage_id):
    from .no_gpu_staging import StagingLedger,fingerprint
    stage=StagingLedger(store).get(stage_id)
    if stage['plan']['profile']!='wan_animate2_distilled':
        raise AgentError('Exact staged distilled profile required.')
    recipe=locked_recipe(INDEX.read_bytes())
    recipe.update(stage_id=stage_id,stage_sha256=fingerprint(stage),
                  references=stage['references'],scope='Model-free loader preparation only; no worker launch')
    return recipe
