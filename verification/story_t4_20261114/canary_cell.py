"""Standalone approved fallback benchmark. Existing Engine runtime gate unchanged.
Maximum seven generation submissions including failures. No automatic retry.
"""
import base64,hashlib,json,os,signal,subprocess,threading,time,urllib.request
from pathlib import Path
import psutil
BASE=Path('/content/redpad_story_t4_20261114'); OUT=BASE/'outputs';OUT.mkdir(exist_ok=True)
receipt=json.loads((BASE/'installation.json').read_text())
binary=Path(receipt['binary'])
assert hashlib.sha256(binary.read_bytes()).hexdigest()==receipt['binary_sha256']
runtime=BASE/'runtime'
os.environ['LD_LIBRARY_PATH']=':'.join(sorted({str(p.parent) for p in runtime.rglob('*.so*')}))+':'+os.environ.get('LD_LIBRARY_PATH','')
url='http://127.0.0.1:18082'
def http(path,payload=None,timeout=10):
 req=urllib.request.Request(url+path,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return r.read(4*1024*1024)
def run_one(case):
 file=OUT/(case['id']+'.json')
 if file.exists():raise RuntimeError('Existing attempt: inspect and never blindly repeat '+case['id'])
 if len(list(OUT.glob('*.json')))>=7:raise RuntimeError('Seven-call ceiling')
 server=None;log=BASE/(case['id']+'.server.log');started=time.monotonic()
 state={'case':case,'installation':receipt,'state':'preparing','human_review':'pending','production_approved':False,'automatic_retries':0}
 try:
  with log.open('w') as f:
   server=subprocess.Popen([str(binary),'-m',str(BASE/receipt['file']),'-ngl','99','--device','CUDA0','--no-warmup','-fa','off','-b','128','-ub','128','-tb','2','-lv','4','-c','4096','-np','1','-t','2','--host','127.0.0.1','--port','18082','--jinja','--no-webui'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+180
  while True:
   if server.poll() is not None:raise RuntimeError('Server exit: '+log.read_text()[-2500:])
   try:
    if json.loads(http('/health'))['status']=='ok':break
   except Exception:pass
   if time.monotonic()>deadline:raise RuntimeError('Model load timeout')
   time.sleep(1)
  apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
  assert any(x.split(',')[0].strip()==str(server.pid) and int(x.split(',')[1])>4000 for x in apps.splitlines()),apps
  state.update(load_seconds=time.monotonic()-started,owned_gpu_process=apps,offload_lines=[l for l in log.read_text().splitlines() if 'offloaded' in l or 'CUDA0 model buffer' in l])
  messages=[{'role':'system','content':case['system']},{'role':'user','content':case['prompt']}]
  template=json.loads(http('/apply-template',{'messages':messages,'chat_template_kwargs':{'enable_thinking':False}}))
  text=template['prompt']
  tokens=json.loads(http('/tokenize',{'content':text,'add_special':False}))['tokens']
  state.update(exact_prompt_tokens=len(tokens),context_tokens=4096,output_ceiling=case['max_new_tokens'],template_sha256=hashlib.sha256(text.encode()).hexdigest())
  assert len(tokens)+case['max_new_tokens']<=4096,'Token feasibility fails; no generation submitted'
  payload={'messages':messages,'max_tokens':case['max_new_tokens'],'temperature':case.get('temperature',0.7),'seed':117,'stream':False,'chat_template_kwargs':{'enable_thinking':False},'cache_prompt':False}
  state.update(state='submitted',request=payload)
  file.write_text(json.dumps(state,ensure_ascii=False,indent=2))
  rss=[];gpu=[];stop=threading.Event()
  def monitor():
   while not stop.wait(1):
    try:
     rss.append(psutil.Process(server.pid).memory_info().rss)
     gpu.append(int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True,timeout=5).strip()))
    except Exception:pass
  thread=threading.Thread(target=monitor,daemon=True);thread.start();t=time.monotonic()
  try:
   raw=http('/v1/chat/completions',payload,240);body=json.loads(raw);choice=body['choices'][0];content=choice['message'].get('content','')
   state.update(state='completed',raw_http_base64=base64.b64encode(raw).decode(),response=body,raw_content=content,raw_content_sha256=hashlib.sha256(content.encode()).hexdigest(),finish_reason=choice['finish_reason'])
   (OUT/(case['id']+'.raw.txt')).write_bytes(content.encode())
  finally:
   stop.set();thread.join(timeout=6)
   state.update(generation_seconds=time.monotonic()-t,peak_sampled_server_rss_bytes=max(rss,default=None),peak_sampled_device_used_mib=max(gpu,default=None),memory_scope='1s whole device sampling, includes baseline; not allocator peak')
  if state['finish_reason']!='stop':raise RuntimeError('Truncated output; stop under existing benchmark ceiling')
  parsed=json.loads(content)
  if case.get('schema'):
   import jsonschema
   jsonschema.validate(parsed,case['schema'])
  state['parsed']=parsed
 except Exception as e:
  state.update(error_type=type(e).__name__,error=str(e),state='stopped_with_evidence')
 finally:
  if server is not None and server.poll() is None:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait(timeout=5)
  state.update(total_seconds=time.monotonic()-started,server_stopped=server is None or server.poll() is not None)
  file.write_text(json.dumps(state,ensure_ascii=False,indent=2))
  print('REDPAD_RESULT='+json.dumps({k:v for k,v in state.items() if k not in ('raw_http_base64','request','case','response','installation')},ensure_ascii=False),flush=True)
 if state['state']!='completed':raise RuntimeError('Stop: '+state.get('error','unknown'))
 return state

CANARY=json.loads('{"system": "Return a JSON object only with cause, choice, consequence, knowledge. Each value is a short original Bengali sentence. No approval or quality score.", "prompt": "মানব-প্রণীত canary brief: নীরা এখনও টিকিটের কথা জানে না। হাসান টিকিট বাক্সে রেখেছেন। একটি ছোট বিশ্বাসযোগ্য সিদ্ধান্ত ও তার ফল লিখুন; আগে না জেনে নীরা টিকিটের প্রতিক্রিয়া দেখাবে না।", "max_new_tokens": 384, "seed": 117, "temperature": 0.2, "context_tokens": 4096, "thinking": false, "id": "canary", "schema": {"type": "object", "additionalProperties": false, "required": ["cause", "choice", "consequence", "knowledge"], "properties": {"cause": {"type": "string", "minLength": 1}, "choice": {"type": "string", "minLength": 1}, "consequence": {"type": "string", "minLength": 1}, "knowledge": {"type": "string", "minLength": 1}}}}')
canary_result=run_one(CANARY)
