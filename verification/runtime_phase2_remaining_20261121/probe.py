"""Remaining-profile CPU symbol checks; no model construction or weights."""
import importlib
import importlib.metadata
import json
import os
import sys
import tempfile

CHECKS={
    'stable': ('torch','torchaudio','torchvision','soundfile','safetensors.torch:load_file',
               'stable_audio_tools.models.factory:create_model_from_config',
               'stable_audio_tools.inference.generation:generate_diffusion_cond',
               'redpad_pipeline.audio_worker:run'),
    'modern-symbols': ('transformers:Qwen3_5MoeForConditionalGeneration',
                       'diffusers:WanAnimate2Pipeline','diffusers:WanAnimate2Transformer3DModel',
                       'diffusers:AutoencoderOobleck'),
    'voice-support': ('torch','torchaudio','snac:SNAC','soundfile','transformers:LlamaForCausalLM',
                      'vocos:Vocos','vocos.feature_extractors:MelSpectrogramFeatures',
                      'vocos.models:VocosBackbone','vocos.heads:ISTFTHead'),
}


def deny_network(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
        raise PermissionError('Offline package probe')


def silence_contract():
    import soundfile
    import numpy as np
    with tempfile.TemporaryFile() as target:
        soundfile.write(target,np.zeros((4800,2),dtype=np.float32),48000,format='WAV',subtype='PCM_16')
        target.seek(0)
        info=soundfile.info(target)
        assert (info.samplerate,info.channels,info.frames,info.subtype)==(48000,2,4800,'PCM_16')
        return {'rate':info.samplerate,'channels':info.channels,'subtype':info.subtype}


def main():
    group=sys.argv[1]
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',CUDA_VISIBLE_DEVICES='')
    sys.addaudithook(deny_network)
    results={}
    for entry in CHECKS[group]:
        module,_,symbol=entry.partition(':')
        try:
            obj=importlib.import_module(module)
            if symbol:
                getattr(obj,symbol)
            results[entry]={'passed':True,'module':getattr(obj,'__file__',None)}
        except Exception as exc:
            results[entry]={'passed':False,'error':f'{type(exc).__name__}: {exc}'}
    wav=silence_contract() if group in ('stable','voice-support') else None
    print(json.dumps({'family':group,'python':sys.version,'interpreter':sys.executable,
          'prefix':sys.prefix,'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
          'kernel_network_namespace':os.readlink('/proc/self/ns/net'),
          'imports':results,'synthetic_wav':wav,'weights_loaded':False,'inference':False},indent=2,sort_keys=True))
    return int(any(not row['passed'] for row in results.values()))


if __name__=='__main__':
    raise SystemExit(main())
