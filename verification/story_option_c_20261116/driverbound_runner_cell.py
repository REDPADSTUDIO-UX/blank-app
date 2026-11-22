# Reuse current reviewed runner functions and exact contracts; no downloads.
import hashlib,json,re,subprocess,time
from pathlib import Path
binding=json.loads((RESEARCH/'driver_binding_verified.json').read_text())
assert binding['status']=='VERIFIED_NO_MODEL_LOAD'
assert re.fullmatch(r'CUDA[0-9]+',binding['selected_device'])
assert binding['driver_directory']=='/usr/lib64-nvidia'
assert binding['worker_env']['LD_LIBRARY_PATH']==receipt['runtime_libraries']+':/usr/lib64-nvidia'
assert hashlib.sha256((OUT/'canary.json').read_bytes()).hexdigest()==binding['previous_failed_launch_sha256']
assert hashlib.sha256(json.dumps(BUNDLE['contracts'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()=='96cd27f97f0d718228c14460dccfdf7af0831c11f487c4c27913a5002b61d31e'
WORKER_ENV=binding['worker_env']
SELECTED_DEVICE=binding['selected_device']
current_gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free','--format=csv,noheader,nounits'],text=True,timeout=12).strip()
assert 'T4' in current_gpu and int(current_gpu.split(',')[2])>10000
mem={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable')}
assert mem['MemAvailable']>8*2**30
print('MODEL_PREFLIGHT='+json.dumps({'gpu':current_gpu,'ram':mem,'selected_device':SELECTED_DEVICE,'remaining_calls':7-2-len(budget()['new_calls'])}),flush=True)

def run_one(case):
 file=OUT/(case['id']+'.json')
 if file.exists():raise RuntimeError('Existing attempt: inspect and never blindly repeat '+case['id'])
 ledger=budget()
 if len(ledger['historical'])+len(ledger['new_calls'])>=7:raise RuntimeError('Seven-call ceiling including two historical calls')
 if any(x['id']==case['id'] for x in ledger['new_calls']):raise RuntimeError('Prior submitted attempt; never retry blindly')
 server=None;log=RESEARCH/(case['id']+'.server.log');started=time.monotonic()
 state={'case':case,'installation':receipt,'state':'preparing','human_review':'pending','production_approved':False,'automatic_retries':0,'variant':'option_c_driverbound_schema_v1','historical_calls':2,'kernel_isolation_verified':False}
 try:
  with log.open('w') as f:
   server=subprocess.Popen([str(binary),'-m',receipt['model_path'],'-ngl','99','--device',SELECTED_DEVICE,'--no-warmup','-fa','off','-b','128','-ub','128','-tb','2','-lv','4','-c','4096','-np','1','-t','2','--host','127.0.0.1','--port','18082','--jinja','--no-webui'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=WORKER_ENV,cwd=RESEARCH)
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
  if case.get('schema'):
   import copy
   constrained=copy.deepcopy(case['schema'])
   if case.get('section')=='foundation':
    constrained['properties']['assumptions']['maxItems']=4
    constrained['properties']['unresolved_questions']['maxItems']=4
    constrained['properties']['characters']['maxItems']=2
   payload['response_format']={'type':'json_schema','schema':constrained}
  payload['repeat_penalty']=1.08
  ledger['new_calls'].append({'id':case['id'],'state':'submitted','payload_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
  LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
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
  ledger=budget()
  for entry in ledger['new_calls']:
   if entry['id']==case['id']:entry.update(state=state['state'],finish_reason=state.get('finish_reason'),raw_sha256=state.get('raw_content_sha256'))
  LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
  print('REDPAD_RESULT='+json.dumps({k:v for k,v in state.items() if k not in ('raw_http_base64','request','case','response','installation')},ensure_ascii=False),flush=True)
 if state['state']!='completed':raise RuntimeError('Stop: '+state.get('error','unknown'))
 return state

def generate_section(name):
 canary=json.loads((OUT/'driverbound_canary_v1.json').read_text())
 assert canary['state']=='completed' and canary['finish_reason']=='stop'
 prior={}
 for n in ('foundation','act_1','act_2','act_3','reflection'):
  if n==name:break
  result=json.loads((OUT/('driverbound_'+n+'_v1.json')).read_text())
  assert result['state']=='completed' and result['finish_reason']=='stop'
  prior[n]=result['parsed']
 foundation=prior.get('foundation')
 beats=[b for n in ('act_1','act_2','act_3') for b in prior.get(n,[])]
 context={}
 if foundation:
  context['foundation']={k:foundation[k] for k in ('logline','dramatic_question','characters','initial_knowledge')}
 if beats:
  context['prior_beats']=[{k:b[k] for k in ('id','choice','consequence','plants','payoffs','learns')} for b in beats]
  context['last_state']=beats[-1]['after']
  known={k:list(v) for k,v in foundation['initial_knowledge'].items()}
  for b in beats:
   for k,v in b['learns'].items():known[k]=list(dict.fromkeys(known[k]+v))
  context['known']=known
 if name=='reflection':
  # Actual generated actions/consequences only; no authored story substitution.
  context={'logline':foundation['logline'],'characters':[{k:c[k] for k in ('id','name','want','fear')} for c in foundation['characters']], 'actual_beats':[{k:b[k] for k in ('id','action','choice','consequence','emotion')} for b in beats]}
 details={
 'foundation':'Only foundation. Exactly two characters N and H, Nira and Hasan. Be concise: each character value 2-5 Bengali words. Give initial knowledge as short ASCII fact IDs with meaning apparent from the brief. N must NOT initially know ticket bought/hidden. At most FOUR distinct assumptions and FOUR unresolved questions. Never repeat an assumption. No plot event has yet happened beyond the supplied brief. Do not reveal how the story resolves.',
 'act_1':'Exactly FOUR short beats B1-B4 act=1. Start the same morning with bag repair, concealed ticket and a credible costly choice. First cause=brief; later cause must cite earlier beat. No knowledge without shown discovery. Establish humor and emotional investment. Preserve time, room geography, one key and clothes.',
 'act_2':'Exactly FOUR short beats B5-B8 act=2. Continue exact prior state/knowledge. Each choice creates a new consequence; escalate cost. Earn discovery before reaction. Develop an earlier plant; no stranger, illness, sudden money or repetitive obstruction.',
 'act_3':'Exactly FOUR short beats B9-B12 act=3. Resolve same-morning choices credibly without claiming arrival in another city. Earn an ending through both characters actions. Pay off an earlier unresolved plant; include two subtle_emotion=true beats referencing earlier emotional setup IDs if not already present. No miraculous reconciliation.',
 'reflection':'Only reflection based on actual supplied beats. Write treatment as complete flowing Bengali story from opening to ending, roughly 160-220 Bengali words, not instructions or future plan. ending_consequence states exact changed relationship. filmability is practical. self_critique cites an actual beat ID and genuine weakness. Never claim acceptance or scores.'}
 system='\n'.join(BUNDLE['instructions'])+'\nYou are generating one bounded section of ONE story. JSON only, minified, no markdown, no thinking. All required schema fields must be present. Be brief to finish within 1536 output tokens. No scores or human-review claims.'
 if name.startswith('act_'):
  system+=' Use concise Bengali phrases: goal/choice/consequence/action/emotion each 2-5 words, location/sound 1-2 words. Track before/after with ONE compact progress key and copy exact previous after to next before. Knowledge facts use short ASCII IDs; no needless new facts. Empty requires/learns maps when no knowledge change; empty plants/payoffs/emotion_setups arrays when inapplicable. humor/humor_motivation empty unless motivated. Exactly 4 beats. This is a compact causal treatment, not dialogue.'
 prompt='ORIGINAL BRIEF (unchanged):\n'+BUNDLE['brief']+'\nSECTION: '+name+'\n'+details[name]+'\nACTUAL PRIOR GENERATED CONTEXT:\n'+json.dumps(context,ensure_ascii=False,separators=(',',':'))+'\nEXACT SECTION SCHEMA:\n'+json.dumps(BUNDLE['contracts'][name],separators=(',',':'))
 return run_one({'id':'driverbound_'+name+'_v1','section':name,'system':system,'prompt':prompt,'max_new_tokens':1536,'schema':BUNDLE['contracts'][name]})

NEW_CANARY=dict(CANARY,id='driverbound_canary_v1')
canary_result=run_one(NEW_CANARY)
