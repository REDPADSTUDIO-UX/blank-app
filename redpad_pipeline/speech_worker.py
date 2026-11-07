"""Offline CPU preset speech worker; no arbitrary reference voice or custom code."""
import json,sys,wave
from pathlib import Path

def run(path):
    import numpy as np
    import torch
    from .worker_telemetry import start,finish
    start(torch)
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    r=json.loads(Path(path).read_text());root=Path(r['checkpoint'])
    torch.manual_seed(r.get('seed',42))
    model=ParlerTTSForConditionalGeneration.from_pretrained(str(root),local_files_only=True,use_safetensors=True).to('cpu')
    tokenizer=AutoTokenizer.from_pretrained(str(root),local_files_only=True,trust_remote_code=False)
    description=AutoTokenizer.from_pretrained(str(root/'description_tokenizer'),local_files_only=True,trust_remote_code=False)
    d=description(r['description'],return_tensors='pt');p=tokenizer(r['text'],return_tensors='pt')
    marker=Path(path).with_name('worker_state.json');marker.write_text(json.dumps({'inference_started':True,'inference_completed':False}))
    with torch.inference_mode():
        result=model.generate(input_ids=d.input_ids,attention_mask=d.attention_mask,prompt_input_ids=p.input_ids,prompt_attention_mask=p.attention_mask,max_new_tokens=1024)
    marker.write_text(json.dumps({'inference_started':True,'inference_completed':True,'seed':r.get('seed',42),'max_new_tokens':1024,'telemetry':finish(torch)}))
    audio=result.cpu().numpy().squeeze();rate=int(model.config.sampling_rate)
    if audio.ndim!=1 or not np.isfinite(audio).all() or not .1<=len(audio)/rate<=30 or np.max(np.abs(audio))<1e-5:raise ValueError('Invalid speech signal')
    pcm=(np.clip(audio,-1,1)*32767).astype('<i2')
    with wave.open(r['output'],'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(pcm.tobytes())

if __name__=='__main__':run(sys.argv[1])
