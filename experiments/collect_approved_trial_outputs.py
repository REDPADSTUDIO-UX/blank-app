import psutil, os, signal
"""Read-only notebook evidence export. Excludes weights, tokens and unrelated files."""
import base64,hashlib,json
from pathlib import Path
base=Path('/content/redpad_phase3')
residual=[]
for proc in psutil.process_iter(['pid','name']):
    try:
        cwd=proc.cwd()
        if cwd.startswith(str(base/'llama.cpp')) and proc.info['name'] in ('cmake','gmake','make','c++','cc1plus','gcc','g++','nvcc','cicc','ptxas','cc1','as'):
            residual.append({'pid':proc.pid,'name':proc.info['name'],'cwd':cwd,'cmdline':proc.cmdline()})
            proc.kill()
    except (psutil.Error,OSError):pass
(base/'owned_build_cleanup.json').write_text(json.dumps({'residual_owned_compile_processes_stopped':residual,'reason':'Only owned runtime source/build cwd and compiler executables; no model or owner data deleted'},indent=2))
selected=['owned_build_cleanup.json','installation.json','model_load.json','loader_diagnostics.json','server.log','server_explicit_cuda.log']
files=[base/n for n in selected if (base/n).is_file()]+sorted((base/'trials').glob('*.json'))
for p in files:
 data=p.read_bytes()
 if len(data)>2*1024*1024:raise RuntimeError('Evidence file unexpectedly large')
 print('REDPAD_ARTIFACT='+json.dumps({'path':str(p.relative_to(base)),'sha256':hashlib.sha256(data).hexdigest(),'base64':base64.b64encode(data).decode()}))
