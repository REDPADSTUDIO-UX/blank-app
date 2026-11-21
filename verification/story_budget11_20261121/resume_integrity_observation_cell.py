# Read-only current-VM observation. No inference, download, diagnostics or ledger writes.
import json, hashlib, subprocess, shutil
from pathlib import Path
from datetime import datetime, timezone
expected = json.loads("{\"ledger_sha256\":\"eaf514076071daf70517398c41f3c6e3493ed0b1190c6b2506a650b2ca2523ee\",\"foundation_receipt_sha256\":\"2d4bad82ff92cc9d426e006d46024336d2418e587f9d1d32e9539e45690056ea\",\"sections\":{\"act_1\":{\"receipt_sha256\":\"1e24c493e45f301bb8414ceb96898db4c69a6ae5ddacc871ad824ff9d8c5e178\",\"raw_sha256\":\"a3986dbcb4e6a73c0e96c9e558e13d0af706e1418e55d01be290f33ed622d8be\",\"state\":\"completed\"},\"act_2\":{\"receipt_sha256\":\"dba9b5bee5c8aff78ffb5ce21f16deb3a709d9ac05fd1af288c9f7d7a6b7ea8c\",\"raw_sha256\":\"02ab4077f2814e70ca491380a1cb60cef286c1477f9d77f97b025e1bd41890fc\",\"state\":\"stopped_with_evidence\"}},\"runtime_sha256\":\"ba41bb73f69b2c9dfcbcba9d76ff5e295f2c45ada41e2bc78de090ca3ec14080\"}")
base = Path('/content/redpad_story_t4_20261114')
research = base/'option_c_approved'
out = research/'outputs'
def digest_obj(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def file_info(path, expected_sha=None, expected_bytes=None):
 row={'path':str(path),'present':path.is_file(),'symlink':path.is_symlink()}
 if row['present'] and not row['symlink']:
  row['bytes']=path.stat().st_size
  if expected_sha:
   h=hashlib.sha256()
   with path.open('rb') as f:
    for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
   row.update(sha256=h.hexdigest(),expected_sha256=expected_sha,hash_match=h.hexdigest()==expected_sha)
   if expected_bytes is not None:row['size_match']=row['bytes']==expected_bytes
 return row
ob={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'source_remote_head':'89d6ddb4e9137a91e1450aca8851f9ba85233f87','model_calls_this_resume':0,'downloads_this_resume':0,'engineering_changes_this_resume':0}
ob['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,driver_version','--format=csv,noheader,nounits'],text=True,timeout=15).strip()
ob['compute_processes']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True,timeout=15).strip()
ob['host_ram']={k:int(v.split()[0])*1024 for k,v in (ln.split(':',1) for ln in Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable')}
ob['disk_free_bytes']=shutil.disk_usage('/content').free
ob['drive_mount_detected']=any(' /content/drive ' in ln or 'drivefs' in ln.lower() for ln in Path('/proc/self/mountinfo').read_text().splitlines())
ob['artifacts']=[
 file_info(base/'Qwen3.5-9B-Q4_K_M.gguf','03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8',5680522464),
 file_info(base/'runtime/cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea',594371580),
 file_info(base/'runtime/llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797',197999267),
 file_info(research/'runtime/llama-b12318/llama-server','0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5'),
 file_info(research/'runtime_budget11.py',expected['runtime_sha256'])
]
ob['partial_files']=[str(p) for p in base.rglob('*') if p.is_file() and p.suffix in ('.part','.partial','.tmp')]
lp=research/'call_ledger.json'
if lp.is_file():
 ledger=json.loads(lp.read_text())
 ob['ledger']={'sha256':digest_obj(ledger),'matches_verified_github':digest_obj(ledger)==expected['ledger_sha256'],'ceiling':ledger.get('ceiling'),'counts':{k:len(ledger.get(k,[])) for k in ('historical','new_calls','recovery_calls','budget11_calls')},'budget11_calls':ledger.get('budget11_calls',[])}
 ob['ledger']['consumed']=sum(ob['ledger']['counts'].values())
else:ob['ledger']={'present':False}
ob['sections']={}
for name,filename in [('foundation','recovery10_foundation_v2.json'),('act_1','budget11_act_1_v3.json'),('act_2','budget11_act_2_v3.json')]:
 path=out/filename
 if path.is_file():
  s=json.loads(path.read_text()); actual=digest_obj(s)
  wanted=expected['foundation_receipt_sha256'] if name=='foundation' else expected['sections'][name]['receipt_sha256']
  ob['sections'][name]={'present':True,'receipt_sha256':actual,'receipt_matches_verified_github':actual==wanted,'state':s.get('state'),'raw_sha256':s.get('raw_content_sha256'),'schema_validated':s.get('schema_validated'),'handoff_validated':s.get('handoff_validated'),'findings':s.get('handoff_findings',[])}
 else:ob['sections'][name]={'present':False}
ob['next_action']='STOP: Act2 mandatory handoff failure already captured; no retry or dependent execution authorized.'
print('RESUME_VERIFY='+json.dumps(ob,ensure_ascii=False),flush=True)
