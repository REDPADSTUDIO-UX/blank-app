"""Owned, timeout-bounded worker. Fixed local pipeline classes, no dynamic code."""
import json,sys
from pathlib import Path

def run(job):
    import torch
    import diffusers
    from .worker_telemetry import start,finish
    start(torch)
    from diffusers.utils import export_to_video
    from PIL import Image,ImageOps
    from .offline_media import CATALOG,validate_request
    data=json.loads(Path(job).read_text());key=data['engine'];r=data['request'];validate_request(key,r)
    spec=CATALOG[key];image=None
    if data['reference']:
        with Image.open(data['reference']) as im:image=ImageOps.fit(ImageOps.exif_transpose(im).convert('RGB'),(r['width'],r['height']))
    cls=spec['image_pipeline'] if r['mode']=='image_to_video' else spec['text_pipeline']
    # Names originate only from the source-controlled catalog, never user/model data.
    pipeline=getattr(diffusers,cls).from_pretrained(data['checkpoint'],torch_dtype=torch.float16 if key=='local-svd' else torch.bfloat16,local_files_only=True,trust_remote_code=False)
    pipeline.enable_model_cpu_offload()
    generator=torch.Generator(device='cpu').manual_seed(r['seed'])
    args=dict(num_frames=r['frames'],num_inference_steps=r['steps'],generator=generator)
    if key=='local-svd':
        pipeline.unet.enable_forward_chunking();args.update(image=image,decode_chunk_size=2,motion_bucket_id=127,noise_aug_strength=.02)
    else:
        args.update(prompt=r['prompt'],negative_prompt=r.get('negative_prompt',''),width=r['width'],height=r['height'],guidance_scale=spec['guidance'])
        if image is not None:args['image']=image
        if hasattr(pipeline.vae,'enable_tiling'):pipeline.vae.enable_tiling()
    marker=Path(job).with_name('worker_state.json')
    marker.write_text(json.dumps({'inference_started':True,'inference_completed':False}))
    frames=pipeline(**args).frames[0]
    marker.write_text(json.dumps({'inference_started':True,'inference_completed':True,'frames_returned':len(frames),'telemetry':finish(torch),'diffusers_version':getattr(diffusers,'__version__','not reported')}))
    if len(frames)!=r['frames']:raise ValueError('Incomplete generated frame count')
    export_to_video(frames,data['output'],fps=r['fps'])

if __name__=='__main__':run(sys.argv[1])
