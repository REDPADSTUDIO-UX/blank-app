"""Owned local audio subprocess. No network, external code or pickle loader."""
import json,os,socket,sys
from pathlib import Path

def main(payload):
    # Exclude ambient caches: every auxiliary encoder/tokenizer must be inside
    # the reviewed bundle/config, not an unpinned model already in a user cache.
    cache=str(Path(payload['output']).parent/'empty_offline_cache')
    os.environ.update(HF_HOME=cache,HF_HUB_CACHE=cache,TRANSFORMERS_CACHE=cache,HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    def blocked(*a,**k):raise RuntimeError('Network forbidden in owned audio worker; materialize reviewed local auxiliary components.')
    socket.socket.connect=blocked;socket.create_connection=blocked
    import torch,soundfile as sf
    from .worker_telemetry import start,finish
    start(torch);torch.manual_seed(payload['request']['seed'])
    folder=Path(payload['checkpoint']);r=payload['request'];output=Path(payload['output'])
    if payload['engine']=='ace-step-v1':
        from acestep.pipeline_ace_step import ACEStepPipeline
        pipe=ACEStepPipeline(checkpoint_dir=str(folder),dtype='bfloat16',torch_compile=False,cpu_offload=True,quantized=False)
        result=pipe(format='wav',audio_duration=r['seconds'],prompt=r['prompt'],lyrics='[instrumental]',infer_step=r['steps'],manual_seeds=[r['seed']],
           audio2audio_enable=False,lora_name_or_path='none',task='text2music',save_path=str(output),batch_size=1)
        candidates=[Path(p) for p in result if isinstance(p,str) and p.endswith('.wav')]
        if len(candidates)!=1 or candidates[0].resolve()!=output.resolve():raise RuntimeError('ACE returned an unexpected output location; retained files are not substituted.')
    else:
        from safetensors.torch import load_file
        from stable_audio_tools.models.factory import create_model_from_config
        from stable_audio_tools.inference.generation import generate_diffusion_cond
        config=json.loads((folder/'model_config.json').read_text())
        # A fully local config may reference materialized auxiliary text encoders.
        # Network is blocked; missing dependencies fail instead of auto-pulling.
        model=create_model_from_config(config);model.load_state_dict(load_file(str(folder/'model.safetensors')),strict=True);model=model.to('cuda').eval()
        rate=config['sample_rate'];size=config['sample_size']
        from .offline_audio import STABLE_AUDIO_SMALL_RECIPE
        with torch.inference_mode():audio=generate_diffusion_cond(model,steps=r['steps'],cfg_scale=STABLE_AUDIO_SMALL_RECIPE['cfg_scale'],sampler_type=STABLE_AUDIO_SMALL_RECIPE['sampler_type'],batch_size=1,sample_size=size,sample_rate=rate,seed=r['seed'],device='cuda',conditioning=[{'prompt':r['prompt'],'seconds_start':0,'seconds_total':r['seconds']}])
        data=audio[0,:,:round(r['seconds']*rate)].detach().float().cpu().numpy().T
        sf.write(str(output),data,rate,subtype='PCM_16')
    output.with_name('worker_state.json').write_text(json.dumps({'inference_completed':True,'resources':finish(torch)}))

if __name__=='__main__':main(json.loads(Path(sys.argv[1]).read_text()))
