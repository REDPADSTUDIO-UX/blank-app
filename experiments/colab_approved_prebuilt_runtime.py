"""Official pinned CUDA binaries; no model download, no public server."""
import hashlib,json,os,signal,subprocess,tarfile,time,urllib.request
from pathlib import Path
import psutil
BASE=Path('/content/redpad_phase3')
# Stop ONLY the owned compile process group left by notebook interruption.
owned=[]
compiler_names={'cmake','gmake','make','c++','cc1plus','gcc','g++','nvcc','cicc','ptxas','cc1','as'}
for p in psutil.process_iter(['pid','name']):
 try:
  if p.info['name'] in compiler_names and Path(p.cwd()).is_relative_to(BASE/'llama.cpp'):
   owned.append(p);p.kill()
 except (psutil.Error,OSError):pass
_,alive=psutil.wait_procs(owned,timeout=5)
if alive:raise RuntimeError('Owned source build still running; do not claim cleanup complete')
print('REDPAD_BUILD_STOPPED='+str(len(owned)),flush=True)
assets=[{'name': 'cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz', 'bytes': 594371580, 'url': 'https://github.com/ggml-org/llama.cpp/releases/download/b12318/cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz', 'digest': 'sha256:caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea'}, {'name': 'llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz', 'bytes': 197999267, 'url': 'https://github.com/ggml-org/llama.cpp/releases/download/b12318/llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz', 'digest': 'sha256:e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797'}]
runtime=BASE/'official-b12318';runtime.mkdir(exist_ok=True)
checks=[];started=time.monotonic()
for asset in assets:
 path=runtime/asset['name']
 if not path.exists() or path.stat().st_size!=asset['bytes']:
  h=hashlib.sha256()
  with urllib.request.urlopen(asset['url'],timeout=45) as response,path.open('wb') as out:
   for block in iter(lambda:response.read(4*1024*1024),b''):out.write(block);h.update(block)
 else:
  h=hashlib.sha256()
  with path.open('rb') as f:
   for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 if path.stat().st_size!=asset['bytes'] or 'sha256:'+h.hexdigest()!=asset['digest']:raise RuntimeError('Official runtime asset digest/size mismatch')
 with tarfile.open(path) as tar:tar.extractall(runtime,filter='data')
 checks.append({**asset,'verified_sha256':h.hexdigest()})
 print('REDPAD_RUNTIME_ASSET='+json.dumps(checks[-1]),flush=True)
binary=next(runtime.rglob('llama-server'))
libs={str(p.parent) for p in runtime.rglob('*.so*')}
os.environ['LD_LIBRARY_PATH']=':'.join(sorted(libs))+':'+os.environ.get('LD_LIBRARY_PATH','')
version=subprocess.run([str(binary),'--version'],capture_output=True,text=True,timeout=20)
if version.returncode:raise RuntimeError(version.stderr)
receipt=json.loads((BASE/'installation.json').read_text())
receipt.update(state='installed_not_yet_inferred',runtime_variant='official_prebuilt_cuda12.8_b12318',runtime_source_revision='release-b12318; embedded build version below',binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),runtime_version=version.stdout+version.stderr,runtime_assets=checks,runtime_prepare_seconds=time.monotonic()-started,source_build='interrupted_owned_group_stopped; partial objects retained; no model inference attempted')
(BASE/'installation.json').write_text(json.dumps(receipt,indent=2));print('REDPAD_INSTALL='+json.dumps(receipt),flush=True)
