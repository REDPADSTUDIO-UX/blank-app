import json, shutil, subprocess
from pathlib import Path
r={'kind':'current_runtime_read_only_NOT_inference','downloads':0,'model_inferences':0}
nv=shutil.which('nvidia-smi')
r['nvidia_smi_present']=bool(nv)
r['gpu_query']=subprocess.run([nv,'--query-gpu=name,memory.total,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=15).stdout.strip() if nv else None
r['meminfo']=[x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemTotal:','MemAvailable:'))]
r['disk']=dict(zip(('total','used','free'),shutil.disk_usage('/content')))
p=Path('/content/redpad_phase3/model/Qwen3.5-9B-Q4_K_M.gguf')
r['approved_model_file']={'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else None}
r['approved_model_hf_cache']=[str(p) for p in Path('/root/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF').glob('snapshots/*/Qwen3.5-9B-Q4_K_M.gguf')]
r['verified_runtime_exists']=Path('/content/redpad_phase3/official-b12318/llama-b12318/llama-server').is_file()
print('REDPAD_CURRENT_RUNTIME='+json.dumps(r,sort_keys=True))
