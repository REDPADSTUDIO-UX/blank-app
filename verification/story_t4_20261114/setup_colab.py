"""Fresh free-T4 standalone fallback evaluation; no production route changes."""
import hashlib,json,os,subprocess,tarfile,time,urllib.request
from pathlib import Path
import psutil
BASE=Path('/content/redpad_story_t4_20261114');BASE.mkdir(exist_ok=True)
def write(name,value):
 (BASE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def fetch(url,path,size,digest):
 if not path.exists():
  with urllib.request.urlopen(url,timeout=60) as response,path.open('xb') as out:
   for block in iter(lambda:response.read(8*1024*1024),b''):out.write(block)
 if path.stat().st_size!=size or sha(path)!=digest:raise RuntimeError('Exact source bytes mismatch: '+path.name)
 return path
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free','--format=csv,noheader,nounits'],text=True).strip()
assert 'T4' in gpu and int(gpu.split(',')[-1])>10000,gpu
assert psutil.virtual_memory().available>8*2**30
write('preflight.json',{'gpu':gpu,'ram':psutil.virtual_memory()._asdict(),'checkpoint':'4d93a8c83e32ca17e9611797c10737ab9d76bed5','free_account_ui':'not subscribed; zero paid compute units; up to 1h20m estimate, not guaranteed','model_inferences':0,'production_gate_unchanged':True})
repo='unsloth/Qwen3.5-9B-GGUF';rev='3885219b6810b007914f3a7950a8d1b469d598a5';filename='Qwen3.5-9B-Q4_K_M.gguf'
readme=urllib.request.urlopen(f'https://huggingface.co/{repo}/raw/{rev}/README.md',timeout=45).read()
assert hashlib.sha256(readme).hexdigest()=='e50f8066e39c38cbc2da5dd94b9a9a2712b64c4921f107a5adb4b3ca5b6bbac0'
assert b'license: apache-2.0' in readme.lower()
(BASE/'MODEL_README.md').write_bytes(readme)
print('APPROVED_EXACT_MODEL_DOWNLOAD_START',flush=True)
model=fetch(f'https://huggingface.co/{repo}/resolve/{rev}/{filename}',BASE/filename,5680522464,'03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8')
print('MODEL_SHA_VERIFIED',flush=True)
runtime=BASE/'runtime';runtime.mkdir(exist_ok=True)
assets=[('cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz',594371580,'caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea'),('llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz',197999267,'e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797')]
for name,size,digest in assets:
 path=fetch('https://github.com/ggml-org/llama.cpp/releases/download/b12318/'+name,runtime/name,size,digest)
 with tarfile.open(path) as tar:tar.extractall(runtime,filter='data')
 print('RUNTIME_ASSET_VERIFIED',name,flush=True)
binary=next(runtime.rglob('llama-server'))
assert sha(binary)=='0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5'
os.environ['LD_LIBRARY_PATH']=':'.join(sorted({str(p.parent) for p in runtime.rglob('*.so*')}))+':'+os.environ.get('LD_LIBRARY_PATH','')
version=subprocess.run([str(binary),'--version'],capture_output=True,text=True,timeout=20)
assert version.returncode==0,version.stderr
receipt={'repo':repo,'revision':rev,'file':filename,'sha256':sha(model),'bytes':model.stat().st_size,'binary':str(binary),'binary_sha256':sha(binary),'runtime_version':version.stdout+version.stderr,'license':'Apache-2.0 model; MIT runtime','variant':'qwen35_9_approved_gguf; standalone fallback; NOT qwen35_27 NF4','production_approved':False,'model_inferences':0}
write('installation.json',receipt)
print('REDPAD_SETUP_READY='+json.dumps(receipt),flush=True)
