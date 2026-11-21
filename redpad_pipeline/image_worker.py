"""Fixed SDXL class; offline components only, no downloaded/custom Python."""
import json,sys
from pathlib import Path

def run(job):
    import torch
    from diffusers import StableDiffusionXLPipeline
    from .worker_telemetry import start,finish
    start(torch)
    from .offline_image import validate_request
    data=json.loads(Path(job).read_text());r=validate_request(data['request'])
    pipe=StableDiffusionXLPipeline.from_pretrained(data['checkpoint'],torch_dtype=torch.float16,variant='fp16',local_files_only=True,trust_remote_code=False,use_safetensors=True)
    pipe.enable_model_cpu_offload()
    marker=Path(job).with_name('worker_state.json');marker.write_text(json.dumps({'inference_started':True,'inference_completed':False}))
    images=pipe(prompt=r['prompt'],width=r['width'],height=r['height'],num_inference_steps=r['steps'],num_images_per_prompt=1,
                generator=torch.Generator(device='cpu').manual_seed(r['seed'])).images
    if len(images)!=1:raise ValueError('Exactly one generated image required.')
    images[0].save(data['output'],format='PNG');marker.write_text(json.dumps({'inference_started':True,'inference_completed':True,'images_returned':1,'telemetry':finish(torch)}))

if __name__=='__main__':run(sys.argv[1])
