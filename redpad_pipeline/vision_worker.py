"""Fixed local Qwen2.5-VL image critic, no remote code/network/approval."""
import json,socket,sys
from pathlib import Path

def main(payload):
    def blocked(*a,**k):raise RuntimeError('Network disabled in visual critic worker.')
    socket.socket.connect=blocked;socket.create_connection=blocked
    import torch
    from PIL import Image
    from transformers import AutoProcessor,Qwen2_5_VLForConditionalGeneration
    from .worker_telemetry import start,finish
    start(torch);torch.manual_seed(payload['request']['seed']);folder=payload['checkpoint']
    model=Qwen2_5_VLForConditionalGeneration.from_pretrained(folder,torch_dtype=torch.bfloat16,device_map='auto',local_files_only=True,trust_remote_code=False,use_safetensors=True)
    processor=AutoProcessor.from_pretrained(folder,local_files_only=True,trust_remote_code=False,min_pixels=256*28*28,max_pixels=512*28*28)
    images=[Image.open(i['path']).convert('RGB') for i in payload['images']]
    content=[{'type':'image','image':im} for im in images]+[{'type':'text','text':'Inspect only these images. Separate visible observation from inference, cite image numbers/regions, express uncertainty and abstain if unclear. No owner approval, script quotation or identity certainty. Question: '+payload['request']['question']}]
    text=processor.apply_chat_template([{'role':'user','content':content}],tokenize=False,add_generation_prompt=True)
    inputs=processor(text=[text],images=images,padding=True,return_tensors='pt').to(model.device)
    with torch.inference_mode():output=model.generate(**inputs,max_new_tokens=512,do_sample=False)
    raw=processor.batch_decode([ids[len(src):] for src,ids in zip(inputs.input_ids,output)],skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
    path=Path(payload['output']);path.write_text(raw);path.with_name('worker_state.json').write_text(json.dumps({'inference_completed':True,'resources':finish(torch)}))

if __name__=='__main__':main(json.loads(Path(sys.argv[1]).read_text()))
