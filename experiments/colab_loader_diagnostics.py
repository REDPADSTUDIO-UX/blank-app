import json, subprocess, os, time
from pathlib import Path
base=Path('/content/redpad_phase3')
inst=json.loads((base/'installation.json').read_text())
t=time.monotonic()
try:
    p=subprocess.run([inst['binary'],'--list-devices'],capture_output=True,text=True,timeout=45)
    diag={'device_returncode':p.returncode,'device_stdout':p.stdout,'device_stderr':p.stderr,'seconds':time.monotonic()-t}
except subprocess.TimeoutExpired as e:
    diag={'device_timeout':True,'stdout':str(e.stdout),'stderr':str(e.stderr),'seconds':time.monotonic()-t}
diag['server_log']=(base/'server.log').read_text()
diag['runtime_libraries']=[str(p) for p in (base/'official-b12318').rglob('*.so*')]
diag['nvidia']=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.total','--format=csv,noheader,nounits'],text=True)
diag['ldd']=subprocess.run(['ldd',inst['binary']],capture_output=True,text=True,timeout=10).stdout
(base/'loader_diagnostics.json').write_text(json.dumps(diag,indent=2))
print('REDPAD_DIAGNOSTICS='+json.dumps(diag))
