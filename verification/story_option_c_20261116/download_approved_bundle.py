"""Owner-authorized three-artifact download. No inference, extra downloads or Studio changes."""
import hashlib, json, os, subprocess, tarfile, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/content/redpad_story_t4_20261114')
RESEARCH = BASE/'option_c_approved'
MODEL = {'repo':'unsloth/Qwen3.5-9B-GGUF','revision':'3885219b6810b007914f3a7950a8d1b469d598a5',
 'file':'Qwen3.5-9B-Q4_K_M.gguf','bytes':5680522464,
 'sha256':'03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'}
ASSETS = [
 {'file':'cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','bytes':594371580,'sha256':'caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea'},
 {'file':'llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','bytes':197999267,'sha256':'e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797'}]
BINARY_SHA = '0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5'
def safe_path(path):
 assert not any(p.is_symlink() for p in (path,*path.parents)), 'Symlink rejected'
 return path
def sha(path):
 h=hashlib.sha256()
 with safe_path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def save(name,value):
 safe_path(RESEARCH/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
def fetch(item,url,path):
 safe_path(path)
 row={'file':item['file'],'url':url,'expected_bytes':item['bytes'],'expected_sha256':item['sha256'],'downloaded':False}
 if not path.exists():
  part=safe_path(path.with_name(path.name+'.partial'))
  assert not part.exists(), 'Prior partial download preserved; inspect before retry'
  count=0;start=time.monotonic()
  with urllib.request.urlopen(url,timeout=60) as response,part.open('xb') as out:
   for chunk in iter(lambda:response.read(8*1024*1024),b''):
    count+=len(chunk)
    assert count<=item['bytes'],'Unexpected oversized artifact'
    out.write(chunk)
  row.update(downloaded=True,download_seconds=time.monotonic()-start)
  assert count==item['bytes'],'Download size mismatch; partial file preserved'
  assert sha(part)==item['sha256'],'Download checksum mismatch; stop'
  part.rename(path)
 assert path.stat().st_size==item['bytes'],'Existing artifact size mismatch'
 row.update(actual_bytes=path.stat().st_size,actual_sha256=sha(path))
 assert row['actual_sha256']==item['sha256'],'Existing artifact checksum mismatch'
 print('VERIFIED_ARTIFACT='+json.dumps(row),flush=True)
 return row
def main():
 safe_path(BASE);BASE.mkdir(exist_ok=True)
 safe_path(RESEARCH);RESEARCH.mkdir(exist_ok=True)
 assert not (RESEARCH/'bundle_ready.json').exists(),'Already verified; reuse receipt without repeating setup'
 receipt={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'research_only':True,
  'owner_download_authorization':'Current user explicitly authorized ONLY the three pinned artifacts',
  'model_inferences':0,'historical_calls_consumed':2,'total_call_ceiling':7,'artifacts':[]}
 try:
  mounts=Path('/proc/self/mountinfo').read_text()
  assert not any(' /content/drive ' in x or 'drivefs' in x.lower() for x in mounts.splitlines()),'Drive mount present; stop'
  gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,driver_version,compute_cap','--format=csv,noheader,nounits'],text=True,timeout=15).strip()
  assert 'T4' in gpu and int(gpu.split(',')[2])>10000,gpu
  mem={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable')}
  assert mem['MemAvailable']>8*2**30,'Insufficient current host RAM'
  import shutil
  disk=shutil.disk_usage(BASE)
  assert disk.free>10*2**30,'Insufficient free disk'
  receipt.update(gpu=gpu,host_ram=mem,disk_free_bytes=disk.free,drive_mount_detected=False)
  print('DOWNLOAD_PREFLIGHT='+json.dumps(receipt),flush=True)
  model=BASE/MODEL['file']
  cached=Path('/root/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF/snapshots')/MODEL['revision']/MODEL['file']
  if not model.exists() and cached.is_file():model=safe_path(cached)
  receipt['artifacts'].append(fetch(MODEL,f"https://huggingface.co/{MODEL['repo']}/resolve/{MODEL['revision']}/{MODEL['file']}",model))
  runtime=safe_path(BASE/'runtime');runtime.mkdir(exist_ok=True)
  for item in ASSETS:
   url='https://github.com/ggml-org/llama.cpp/releases/download/b12318/'+item['file']
   receipt['artifacts'].append(fetch(item,url,runtime/item['file']))
  # All three full artifact checksums passed before any extraction/execution.
  extracted=safe_path(RESEARCH/'runtime')
  assert not extracted.exists(),'Existing extraction preserved; inspect before reuse'
  extracted.mkdir()
  for item in ASSETS:
   with tarfile.open(runtime/item['file']) as tar:tar.extractall(extracted,filter='data')
  binaries=list(extracted.rglob('llama-server'))
  assert len(binaries)==1,'Ambiguous runtime binary'
  binary=safe_path(binaries[0]);assert sha(binary)==BINARY_SHA,'Extracted binary checksum mismatch'
  libs=':'.join(sorted({str(p.parent) for p in extracted.rglob('*.so*')}))
  env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(RESEARCH),'LD_LIBRARY_PATH':libs,
    'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','CUDA_VISIBLE_DEVICES':'0'}
  result=subprocess.run([str(binary),'--version'],env=env,capture_output=True,text=True,timeout=25)
  assert result.returncode==0,'Runtime version check failed: '+result.stderr[-2000:]
  version=result.stdout+result.stderr
  assert '12318' in version and '7021f7e09' in version,version
  receipt.update(model=MODEL,model_path=str(model),binary=str(binary),binary_sha256=BINARY_SHA,
    runtime_version=version,runtime_libraries=libs,license='Apache-2.0 model; MIT runtime; prior pinned source evidence retained',
    runtime_compatibility='Exact binary version executes; model-load compatibility remains untested',
    production_worker_changed=False,security_equivalent_to_studio=False,status='BUNDLE_VERIFIED')
  save('bundle_ready.json',receipt)
  print('BUNDLE_READY='+json.dumps(receipt),flush=True)
 except Exception as exc:
  receipt.update(status='STOPPED',error_type=type(exc).__name__,error=str(exc))
  save('download_error.json',receipt);print('DOWNLOAD_STOP='+json.dumps(receipt),flush=True);raise

main()
