"""Owner-approved single GGUF install, executed in the owner's free notebook UI.
No other weights, hosted fallback, private repo checkout or public endpoint.
"""
import hashlib,json,os,signal,subprocess,time
from pathlib import Path
from huggingface_hub import hf_hub_download

BASE=Path('/content/redpad_phase3');BASE.mkdir(exist_ok=True)
MODEL_REV='3885219b6810b007914f3a7950a8d1b469d598a5'
MODEL_SHA='03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'
SOURCE_REV='0fb8f157702702f33f4e018de8701b2569a1bc28'
receipt={'state':'started','model_repo':'unsloth/Qwen3.5-9B-GGUF','model_revision':MODEL_REV,'filename':'Qwen3.5-9B-Q4_K_M.gguf','expected_bytes':5680522464,'expected_sha256':MODEL_SHA,'runtime_source_revision':SOURCE_REV,'owner_download_approved':True,'model_inference':False,'paid_fallback':False}
def save():
 (BASE/'installation.json').write_text(json.dumps(receipt,indent=2))
 print('REDPAD_INSTALL='+json.dumps(receipt),flush=True)
def command(args,name,timeout,cwd=None):
 with (BASE/(name+'.log')).open('w') as log:
  p=subprocess.Popen(args,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:rc=p.wait(timeout=timeout)
  except BaseException:
   if p.poll() is None:os.killpg(p.pid,signal.SIGKILL);p.wait()
   raise
  if rc:raise RuntimeError(name+' failed; tail='+ (BASE/(name+'.log')).read_text()[-2500:])
try:
 save()
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total','--format=csv,noheader,nounits'],text=True).strip()
 if 'T4' not in gpu:raise RuntimeError('Approved T4 runtime changed; stop')
 receipt['actual_gpu']=gpu
 print('Downloading ONLY exact approved file',flush=True)
 started=time.monotonic()
 model=Path(hf_hub_download(repo_id=receipt['model_repo'],filename=receipt['filename'],revision=MODEL_REV,local_dir=BASE/'model',token=False))
 if model.stat().st_size!=receipt['expected_bytes']:raise RuntimeError('Model size mismatch')
 h=hashlib.sha256()
 with model.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 if h.hexdigest()!=MODEL_SHA:raise RuntimeError('Model digest mismatch')
 receipt.update(state='model_bytes_verified',actual_sha256=h.hexdigest(),download_and_hash_seconds=time.monotonic()-started,model_path=str(model));save()
 source=BASE/'llama.cpp'
 if not (source/'.git').exists():
  source.mkdir(exist_ok=True);command(['git','init'], 'git_init',30,str(source))
  command(['git','remote','add','origin','https://github.com/ggml-org/llama.cpp.git'],'git_remote',30,str(source))
 command(['git','fetch','--depth','1','origin',SOURCE_REV],'git_fetch',180,str(source))
 command(['git','checkout','--detach',SOURCE_REV],'git_checkout',30,str(source))
 actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
 if actual!=SOURCE_REV:raise RuntimeError('Runtime source revision mismatch')
 started=time.monotonic()
 command(['cmake','-S',str(source),'-B',str(source/'build'),'-DGGML_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=75','-DLLAMA_CURL=OFF','-DLLAMA_BUILD_TESTS=OFF','-DLLAMA_BUILD_EXAMPLES=ON','-DCMAKE_BUILD_TYPE=Release'],'configure',120)
 command(['cmake','--build',str(source/'build'),'--target','llama-server','-j','2'],'build',900)
 binary=source/'build/bin/llama-server'
 version=subprocess.run([str(binary),'--version'],capture_output=True,text=True,timeout=20)
 receipt.update(state='installed_not_yet_inferred',build_seconds=time.monotonic()-started,binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),runtime_version=version.stdout+version.stderr)
 save()
except Exception as e:
 receipt.update(state='failed_with_evidence',error_type=type(e).__name__,error=str(e));save();raise
