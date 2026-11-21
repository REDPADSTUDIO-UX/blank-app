"""Fixed prospective offline workers. No trust_remote_code, downloads, or servers."""
import json,sys,time
from pathlib import Path

def run(path):
    job=json.loads(Path(path).read_text());p=job['profile'];r=job['request'];root=Path(job['output_dir'])
    import torch
    if not torch.cuda.is_available():raise ValueError('CUDA unavailable')
    from .worker_telemetry import start,finish
    start(torch);begin=time.monotonic();dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    result={'inference_started':False,'inference_completed':False,'profile':p['id'],'repo':p['repo'],'revision':p['revision'],'dtype':str(dtype),'human_review_completed':False}
    def save():
        result['elapsed_seconds']=time.monotonic()-begin
        result['telemetry']=finish(torch);(root/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    try:
        if p['adapter']=='hf_text_nf4':
            import transformers
            from transformers import AutoProcessor,BitsAndBytesConfig,set_seed
            cls=transformers.Gemma3ForConditionalGeneration if p['id'].startswith('gemma3_') else transformers.Qwen3_5ForConditionalGeneration
            compute=torch.float16  # explicit T4/P100-compatible compute; experimental fit still unverified
            quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=compute)
            processor=AutoProcessor.from_pretrained(job['checkpoint'],local_files_only=True,trust_remote_code=False)
            model=cls.from_pretrained(job['checkpoint'],local_files_only=True,trust_remote_code=False,quantization_config=quant,torch_dtype=compute,device_map={'':0},attn_implementation='eager')
            set_seed(r['seed']);messages=[{'role':'system','content':r['system']},{'role':'user','content':r['prompt']}]
            rendered=processor.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=r['thinking'])
            (root/'rendered_prompt.txt').write_text(rendered)
            inputs=processor(text=rendered,return_tensors='pt');count=int(inputs['input_ids'].shape[-1])
            if count+r['max_new_tokens']>r['context_tokens']:raise ValueError('Prompt plus output budget exceeds fixed context; no silent truncation')
            inputs={k:v.to('cuda:0') for k,v in inputs.items()};result.update(input_tokens=count,inference_started=True)
            save();kwargs={'max_new_tokens':r['max_new_tokens'],'do_sample':r['temperature']>0}
            if r['temperature']>0:kwargs.update(temperature=r['temperature'],top_p=.9)
            with torch.inference_mode():tokens=model.generate(**inputs,**kwargs)
            torch.cuda.synchronize();new=tokens[0,count:];raw=processor.decode(new,skip_special_tokens=True)
            (root/'raw_response.txt').write_text(raw)
            eos=model.generation_config.eos_token_id;eos=eos if isinstance(eos,list) else [eos]
            truncated=len(new)>=r['max_new_tokens'] and (not len(new) or int(new[-1]) not in eos)
            result.update(inference_completed=True,output_tokens=len(new),truncated=truncated,transformers_version=transformers.__version__,dtype=str(compute),quantization='NF4 double quantization on load; original source weights',generation_kwargs=kwargs)
        elif p['adapter'] in ('flux2_klein','z_image'):
            import diffusers
            from PIL import Image
            cls=diffusers.Flux2KleinPipeline if p['adapter']=='flux2_klein' else diffusers.ZImagePipeline
            pipeline=cls.from_pretrained(job['checkpoint'],torch_dtype=dtype,local_files_only=True,trust_remote_code=False)
            pipeline.enable_model_cpu_offload();images=[]
            for file in job.get('reference_paths',[]):
                with Image.open(file) as im:images.append(im.convert('RGB').copy())
            args={'prompt':r['prompt'],'width':r['width'],'height':r['height'],'num_inference_steps':r['steps'],'guidance_scale':1.0 if p['adapter']=='flux2_klein' else 0.0,'generator':torch.Generator(device='cpu').manual_seed(r['seed'])}
            if images:args['image']=images
            result.update(inference_started=True);save()
            image=pipeline(**args).images[0]
            if image.size!=(r['width'],r['height']):raise ValueError('Native generated dimensions differ from request')
            image.save(root/'image.png');torch.cuda.synchronize();result.update(inference_completed=True,width=image.width,height=image.height,diffusers_version=diffusers.__version__,identity_preservation_verified=False)
        else:raise ValueError('Unsupported exact adapter, no substitution')
    except Exception as exc:
        result.update(error_type=type(exc).__name__);save();raise
    save()

if __name__=='__main__':run(sys.argv[1])
