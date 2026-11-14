"""Bounded owner-approved free Colab trials; localhost-only, closed in finally.
No downloads. Preserve requests/raw HTTP bytes and skip completed experiment IDs.
"""
import base64,hashlib,json,os,re,signal,subprocess,threading,time,urllib.request
from pathlib import Path
import psutil
BASE=Path('/content/redpad_phase3');receipt=json.loads((BASE/'installation.json').read_text())
if receipt['state']!='installed_not_yet_inferred':raise RuntimeError('Verified runtime installation required')
binary=Path(receipt['binary'])
if hashlib.sha256(binary.read_bytes()).hexdigest()!=receipt['binary_sha256']:raise RuntimeError('Runtime binary changed')
OUT=BASE/'trials';OUT.mkdir(exist_ok=True)
SETTINGS={'context_tokens':2048,'max_new_tokens':1024,'temperature':0.7,'seed':117,'enable_thinking':False,'parallel':1,'case_timeout_seconds':180}
# max_new_tokens1024 matches the existing suite/HF limit;2048 context is a distinct low-memory variant.
url='http://127.0.0.1:18081';started=time.monotonic();server=None

def request(path,payload=None,timeout=5):
 req=urllib.request.Request(url+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return r.read(2*1024*1024)
def run_case(case):
 identity={'case':case,'settings':SETTINGS,'model_sha256':receipt['actual_sha256'],'runtime_source_revision':receipt['runtime_source_revision'],'runtime_binary_sha256':receipt['binary_sha256']}
 token=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest();file=OUT/(case['id']+'.json')
 if file.exists():
  prior=json.loads(file.read_text())
  if prior.get('experiment_id')!=token:raise RuntimeError('Case identity changed; do not overwrite output')
  if prior.get('state')!='Completed' or hashlib.sha256(prior.get('raw_content','').encode()).hexdigest()!=prior.get('raw_content_sha256'):raise RuntimeError('Prior attempt uncertain or corrupted; investigate before retry')
  print('REDPAD_TRIAL_SKIP='+case['id'],flush=True);return
 payload={'messages':[{'role':'system','content':case['system']},{'role':'user','content':case['prompt']+'\n\nSOURCE MATERIAL:\n'+case['source']}],'max_tokens':SETTINGS['max_new_tokens'],'temperature':SETTINGS['temperature'],'seed':SETTINGS['seed'],'stream':False,'chat_template_kwargs':{'enable_thinking':False},'cache_prompt':False}
 state={'experiment_id':token,'case':case,'settings':SETTINGS,'request':payload,'installation':receipt,'state':'Running','actual_output_received':False,'human_review_completed':False,'professional_accepted':False,'automatic_retries':0}
 file.write_text(json.dumps(state,ensure_ascii=False,indent=2));rss=[];gpu=[];stop=threading.Event()
 def monitor():
  while not stop.wait(1):
   try:
    p=psutil.Process(server.pid);rss.append(p.memory_info().rss+sum(x.memory_info().rss for x in p.children(recursive=True)))
    sample=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True,timeout=5).strip();gpu.append(int(sample))
   except (OSError,ValueError,subprocess.SubprocessError,psutil.Error):pass
 thread=threading.Thread(target=monitor,daemon=True);thread.start();t=time.monotonic()
 try:
  raw=request('/v1/chat/completions',payload,180);body=json.loads(raw);choice=body['choices'][0];content=choice['message'].get('content','')
  state.update(state='Completed',actual_output_received=True,raw_http_base64=base64.b64encode(raw).decode(),response=body,raw_content=content,raw_content_sha256=hashlib.sha256(content.encode()).hexdigest(),finish_reason=choice.get('finish_reason'),truncated=choice.get('finish_reason')!='stop')
 except Exception as e:state.update(state='Failed With Evidence',error_type=type(e).__name__,error=str(e),completion_unknown=True)
 finally:
  stop.set();thread.join(timeout=6)
  state.update(wall_seconds=time.monotonic()-t,peak_server_rss_bytes=max(rss,default=None),peak_device_used_mib=max(gpu,default=None),memory_scope='Sampled1s; GPU whole-device used incl baseline, not isolated allocator peak')
  file.write_text(json.dumps(state,ensure_ascii=False,indent=2));print('REDPAD_TRIAL='+json.dumps(state,ensure_ascii=False),flush=True)
 if state['state']!='Completed':raise RuntimeError('Uncertain inference; stop without blind retries')

TRIAL_CASES=json.loads('[{"id": "runtime_text_canary", "system": "আপনি বাংলা সহকারী। নির্দেশনা অনুসরণ করুন।", "prompt": "কেবল এই বাক্যটি লিখুন: আজ সকালটা শান্ত।", "source": "এইটি runtime canary, creative benchmark নয়।", "required_keys": [], "expected_objective_defects": null}, {"id": "natural_dialogue", "roles": ["script"], "prompt": "রুবা ও আদনানের ১২টি সংক্ষিপ্ত line/action লিখুন; সম্পর্কের উষ্ণতা ও চাপ বোঝান। চরিত্রভিত্তিক ২টি witty exchange থাকুক, জোক শোনানো নয়। JSON: {\\"scene\\":\\"...\\"}", "source": "ঢাকার কল্যাণপুর। রুবা (২৯), বাসা থেকে খাবার বিক্রি করে; ছোট ভাই আদনান (২৪), ডেলিভারি দেয়। মা সালমা (৫৫) ভোরে স্কুলের চাকরির ইন্টারভিউতে যাবেন, কিন্তু সন্তানদের বলেন পাশের বাসায় যাচ্ছেন। রুবা মায়ের ব্যাগে পুরোনো সনদ দেখে; ইন্টারভিউর কথা এখনো জানে না। রান্নার গ্যাস বন্ধ, আজকের অর্ডারের অগ্রিম টাকা মাত্র একবার এসেছে এবং ফেরত দিতে হবে যদি খাবার না পৌঁছায়। মা টাকা আনতে পারেন না; সমাধান আসবে চরিত্রের সিদ্ধান্ত থেকে। একই সকাল, একটিমাত্র নীল ব্যাগ। নতুন বাইরের উদ্ধারকারী বা হঠাৎ পাওয়া টাকা নয়।", "dimensions": ["bengali_naturalness", "humor", "subtext"], "expected_objective_defects": null, "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["scene"]}, {"id": "causal_outline", "roles": ["story"], "prompt": "Brief থেকে ৬টি সংযুক্ত beat লিখুন। প্রতি beat-এ cause, choice, consequence, emotion, knowledge_change রাখুন। JSON: {\\"beats\\":[...]}. টাকা, ব্যাগ ও জানা-অজানা তথ্যের continuity অক্ষত রাখুন।", "source": "ঢাকার কল্যাণপুর। রুবা (২৯), বাসা থেকে খাবার বিক্রি করে; ছোট ভাই আদনান (২৪), ডেলিভারি দেয়। মা সালমা (৫৫) ভোরে স্কুলের চাকরির ইন্টারভিউতে যাবেন, কিন্তু সন্তানদের বলেন পাশের বাসায় যাচ্ছেন। রুবা মায়ের ব্যাগে পুরোনো সনদ দেখে; ইন্টারভিউর কথা এখনো জানে না। রান্নার গ্যাস বন্ধ, আজকের অর্ডারের অগ্রিম টাকা মাত্র একবার এসেছে এবং ফেরত দিতে হবে যদি খাবার না পৌঁছায়। মা টাকা আনতে পারেন না; সমাধান আসবে চরিত্রের সিদ্ধান্ত থেকে। একই সকাল, একটিমাত্র নীল ব্যাগ। নতুন বাইরের উদ্ধারকারী বা হঠাৎ পাওয়া টাকা নয়।", "dimensions": ["causality", "psychology", "continuity"], "expected_objective_defects": null, "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["beats"]}, {"id": "director_criticism", "roles": ["director"], "prompt": "শুধু supplied scene-এর objective continuity defect খুঁজুন। সঠিক quote verbatim দিন। subjective taste-কে defect করবেন না; evidence না থাকলে findings=[]। JSON: {\\"findings\\":[{\\"code\\":\\"prop_state\\",\\"quote\\":\\"exact source substring\\",\\"observation\\":\\"...\\",\\"category\\":\\"contract\\",\\"decision\\":\\"revise\\"}]}.", "source": "C2 — একই রান্নাঘর, একই সকাল, কোনো সময়ের বিরতি নেই। সালমা একমাত্র নীল ব্যাগটি তালাবদ্ধ আলমারিতে রেখে চাবি নিজের পকেটে নেন। কেউ আলমারি খোলে না। পরের action: রুবা একই নীল ব্যাগ হাতে করে ব্যাগের সনদ পড়ে আদনানকে দেখায়।", "dimensions": ["grounded_criticism"], "expected_objective_defects": ["prop_state"], "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["findings"]}, {"id": "clean_abstention", "roles": ["director", "qc"], "prompt": "শুধু supplied scene-এর objective continuity defect খুঁজুন। সঠিক quote verbatim দিন। subjective taste-কে defect করবেন না; evidence না থাকলে findings=[]। JSON: {\\"findings\\":[{\\"code\\":\\"prop_state\\",\\"quote\\":\\"exact source substring\\",\\"observation\\":\\"...\\",\\"category\\":\\"contract\\",\\"decision\\":\\"revise\\"}]}.", "source": "C1 — রান্নাঘর, সকাল। সালমা নীল ব্যাগটি নিজের চেয়ারের পাশে রাখেন। রুবা হাঁড়ির ঢাকনা তুলে আবার নামিয়ে রাখে। আদনান ফোনের অর্ডার তালিকা দেখায়। রুবা: \\"তুই সময়টা একটু কিনে আন।\\" আদনান খালি কাপ এগিয়ে দেয়: \\"বাকিতে দেবে?\\" সালমা চুলার নিভে থাকা শিখার দিকে তাকিয়ে নীরবে জানালাটি খোলেন। ব্যাগ চেয়ারের পাশেই থাকে।", "dimensions": ["abstention", "quotation_accuracy"], "expected_objective_defects": [], "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["findings"]}, {"id": "qc_defect_detection", "roles": ["qc"], "prompt": "শুধু supplied scene-এর objective continuity defect খুঁজুন। সঠিক quote verbatim দিন। subjective taste-কে defect করবেন না; evidence না থাকলে findings=[]। JSON: {\\"findings\\":[{\\"code\\":\\"prop_state\\",\\"quote\\":\\"exact source substring\\",\\"observation\\":\\"...\\",\\"category\\":\\"contract\\",\\"decision\\":\\"revise\\"}]}.", "source": "C2 — একই রান্নাঘর, একই সকাল, কোনো সময়ের বিরতি নেই। সালমা একমাত্র নীল ব্যাগটি তালাবদ্ধ আলমারিতে রেখে চাবি নিজের পকেটে নেন। কেউ আলমারি খোলে না। পরের action: রুবা একই নীল ব্যাগ হাতে করে ব্যাগের সনদ পড়ে আদনানকে দেখায়।", "dimensions": ["objective_detection", "quotation_accuracy"], "expected_objective_defects": ["prop_state"], "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["findings"]}, {"id": "targeted_rewrite", "roles": ["script"], "prompt": "শুধু C1-এর শেষ action beat-এর বিকল্প দিন: সালমা দ্বিধা প্রকাশ করবেন কাজ দিয়ে, নতুন dialogue নয়। অন্য action/dialogue পরিবর্তন করবেন না। JSON: {\\"target\\":\\"C1.final_action\\",\\"replacement\\":\\"...\\"}.", "source": "C1 — রান্নাঘর, সকাল। সালমা নীল ব্যাগটি নিজের চেয়ারের পাশে রাখেন। রুবা হাঁড়ির ঢাকনা তুলে আবার নামিয়ে রাখে। আদনান ফোনের অর্ডার তালিকা দেখায়। রুবা: \\"তুই সময়টা একটু কিনে আন।\\" আদনান খালি কাপ এগিয়ে দেয়: \\"বাকিতে দেবে?\\" সালমা চুলার নিভে থাকা শিখার দিকে তাকিয়ে নীরবে জানালাটি খোলেন। ব্যাগ চেয়ারের পাশেই থাকে।", "dimensions": ["rewrite_scope", "visual_subtext"], "expected_objective_defects": null, "system": "আপনি বাংলা চলচ্চিত্রের সংশ্লিষ্ট বিশেষজ্ঞ। নির্দেশিত JSON object ছাড়া আর কিছু লিখবেন না। সরবরাহ করা তথ্যের বাইরে কোনো ঘটনা বা quote বানাবেন না। কোনো score, approval বা unseen media inspection দাবি করবেন না।", "required_keys": ["target", "replacement"]}]')

try:
 with (BASE/'server_explicit_cuda.log').open('w') as log:
  server=subprocess.Popen([str(binary),'-m',receipt['model_path'],'-ngl','99','--device','CUDA0','--no-warmup','-lv','5','-c','2048','-np','1','-t','2','--host','127.0.0.1','--port','18081','--jinja','--no-webui'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+240
  while True:
   if server.poll() is not None:raise RuntimeError('Server exited: '+(BASE/'server_explicit_cuda.log').read_text()[-2000:])
   try:
    health=json.loads(request('/health'))
    if health.get('status')=='ok':break
   except Exception:pass
   if time.monotonic()>deadline:raise RuntimeError('Bounded model-load timeout')
   time.sleep(1)
  logs=(BASE/'server_explicit_cuda.log').read_text()
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True,timeout=10).strip()
  gpu_rows=[line.split(',') for line in compute.splitlines() if line.strip()]
  owned_gpu=[{'pid':int(row[0].strip()),'used_mib':int(row[1].strip())} for row in gpu_rows if len(row)==2 and row[0].strip().isdigit() and row[1].strip().isdigit() and int(row[0].strip())==server.pid]
  if not owned_gpu or max(r['used_mib'] for r in owned_gpu)<4096:raise RuntimeError('Owned server PID must hold at least4GiB of GPU memory; no CPU fallback')
  (BASE/'model_load.json').write_text(json.dumps({'load_seconds':time.monotonic()-started,'actual_gpu_offload_lines':[l for l in logs.splitlines() if 'offload' in l or 'CUDA0' in l],'health':health,'localhost_only':True,'server_pid':server.pid,'actual_owned_gpu_process':owned_gpu,'nvidia_compute_apps':compute,'proof':'Actual owned server process GPU memory; independent of changing log wording'},indent=2))
  print('REDPAD_LOAD='+ (BASE/'model_load.json').read_text(),flush=True)
  for case in (c for c in TRIAL_CASES if c['id']!='qc_defect_detection'):
   if time.monotonic()-started>1200:raise RuntimeError('20minute bounded notebook session budget reached')
   run_case(case)
finally:
 if server and server.poll() is None:
  os.killpg(server.pid,signal.SIGTERM)
  try:server.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
 print('REDPAD_SERVER_STOPPED='+str(server is None or server.poll() is not None),flush=True)
