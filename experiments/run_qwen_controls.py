"""Two final bounded controls; no new model or external provider."""
import json,time
from redpad_pipeline.local_ollama_session import local_cpu_session
from redpad_pipeline.screenwriter import LocalWriter
from redpad_pipeline.cpu_creative_trial import FOLDER,MODEL,call

if __name__=='__main__':
 with local_cpu_session():
  path=FOLDER/'control_probe.json'
  if not path.exists():
   writer=LocalWriter(MODEL,num_ctx=2048,num_predict=256,temperature=.4,seed=42,stream=True,timeout_seconds=180)
   prompt='Return JSON only: keys sum, holder, copied_name. Compute 2+2 for sum. A gives an umbrella to B; holder is the letter of whoever now holds it. For copied_name, copy EXACTLY the Bengali text তানিয়া. No explanation.'
   result=None;error='';start=time.monotonic()
   try:result=writer('Follow the task carefully. Do not invent facts. Return JSON only.',prompt)
   except Exception as exc:error=str(exc)
   checks=dict(arithmetic=isinstance(result,dict) and result.get('sum')==4,object_transfer=isinstance(result,dict) and result.get('holder')=='B',bangla_name_exact_copy=isinstance(result,dict) and result.get('copied_name')=='তানিয়া')
   data=dict(model=MODEL,device='CPU',prompt=prompt,result=result,raw=writer.last_raw_output,evidence=writer.last_evidence,error=error,checks=checks,seconds=round(time.monotonic()-start,3),creative_quality_verified=False)
   path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Control checks:',checks,flush=True)
  old=json.loads((FOLDER/'trial_dialogue_revision.json').read_text());r=old['request']
  call('trial_dialogue_task_last','script',r['instructions'],source=r['experimental_source'],brief=r['brief'],max_tokens=256,micro_kind='dialogue',temperature=.4,task_last=True)
