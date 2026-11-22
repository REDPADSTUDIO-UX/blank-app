"""Current-session cache eligibility only. No download, CUDA diagnostic or inference."""
import json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

base=Path('/content/redpad_story_t4_20261114')
research=base/'option_c_approved'
model='Qwen3.5-9B-Q4_K_M.gguf'
revision='3885219b6810b007914f3a7950a8d1b469d598a5'
paths=[base/model,
 Path('/root/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF/snapshots')/revision/model,
 research/'bundle_ready.json',research/'driver_binding_verified.json',
 research/'call_ledger.json',research/'outputs/driverbound_canary_v1.json',
 research/'runtime/llama-b12318/llama-server',
 base/'runtime/cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz',
 base/'runtime/llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz']
inventory=[]
for path in paths:
    unsafe=any(p.is_symlink() for p in (path,*path.parents))
    exists=not unsafe and path.is_file()
    inventory.append({'path':str(path),'present':exists,'bytes':path.stat().st_size if exists else None,'symlink_rejected':unsafe})
gpu=None;error=None
tool=shutil.which('nvidia-smi')
if tool:
    result=subprocess.run([tool,'--query-gpu=name,memory.total,memory.free,driver_version','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=15)
    gpu=result.stdout.strip();error=result.stderr.strip() or None
mem={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable')}
mounts=Path('/proc/self/mountinfo').read_text()
observation={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'gpu':gpu,'gpu_error':error,'host_ram':mem,
 'inventory':inventory,'drive_mount_detected':any(' /content/drive ' in x or 'drivefs' in x.lower() for x in mounts.splitlines()),
 'saved_github_call_budget':{'consumed':3,'authorized_ceiling':8,'remaining':5},
 'runtime_ledger_restored':False,'weight_bytes_read':False,'model_downloads':0,'model_inferences':0,
 'cuda_diagnostics_repeated':False,'successful_canary_repeated':False,
 'scope':'Current metadata only. Historical successful CUDA/canary evidence is retained in GitHub; saved notebook output is not evidence of current cache availability.'}
print('BUDGET8_ELIGIBILITY='+json.dumps(observation),flush=True)
