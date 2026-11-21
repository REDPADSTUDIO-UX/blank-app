"""Model-free publisher entrypoint import. Never instantiate a model or a pipeline."""
import importlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import sys

PROFILE_IMPORTS={
    'ltx25': ('ltx_pipelines.distilled:DistilledPipeline',
              'ltx_pipelines.utils.model_paths:ModelPaths',
              'ltx_pipelines.utils.media_io:encode_media_segments',
              'ltx_core.text_encoders.gemma.gemma_assets'),
    'wan_animate2': ('pipelines.wan_animate_2_pipeline:WanAnimate2MPIPipeline',),
    'ace15': ('acestep.handler:AceStepHandler', 'acestep.inference:generate_music',
              'acestep.models.turbo.modeling_acestep_v15_turbo:AceStepConditionGenerationModel'),
}


def deny_network(event, args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
        raise PermissionError('Offline CPU import probe')


def main():
    profile, source=sys.argv[1:3]
    root=Path(source)
    sys.path.insert(0,str(root))
    if profile=='ltx25':
        for name in ('ltx-core','ltx-pipelines'):
            sys.path.insert(0,str(root/'packages'/name/'src'))
    sys.addaudithook(deny_network)
    checks={}
    for entry in PROFILE_IMPORTS[profile]:
        name,_,symbol=entry.partition(':')
        try:
            module=importlib.import_module(name)
            assert Path(module.__file__).resolve().is_relative_to(root.resolve())
            row={'ok':True,'file':module.__file__}
            if symbol:
                item=getattr(module,symbol)
                row['signature']=str(inspect.signature(item))
                if symbol=='DistilledPipeline':
                    row['stream_chunks']=str(inspect.signature(item.stream_chunks))
            checks[entry]=row
        except Exception as exc:
            checks[entry]={'ok':False,'error':f'{type(exc).__name__}: {exc}'}
    print(json.dumps({'profile':profile,'python':sys.version,'interpreter':sys.executable,
          'prefix':sys.prefix,'versions':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
          'imports':checks,'loaded_weights':False,'inference':False},indent=2,sort_keys=True))
    return int(not all(r['ok'] for r in checks.values()))


if __name__=='__main__':
    raise SystemExit(main())
