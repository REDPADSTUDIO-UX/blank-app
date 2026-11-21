"""Export only this run's evidence, never weights, account files or credentials."""
import base64,hashlib,io,json,subprocess,zipfile
from pathlib import Path
import psutil
BASE=Path('/content/redpad_story_t4_20261114')
files=[p for p in BASE.iterdir() if p.is_file() and p.suffix in ('.json','.md')]
files+=list((BASE/'outputs').glob('*.json'))+list((BASE/'outputs').glob('*.raw.txt'))
buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):z.writestr(str(p.relative_to(BASE)),p.read_bytes())
 for p in BASE.glob('*.server.log'):
  text=p.read_text(errors='replace')
  z.writestr('logs/'+p.name, text)
 owned=[{'pid':p.pid,'cmdline':p.cmdline()} for p in psutil.process_iter() if p.name()=='llama-server' and any(str(BASE) in x for x in p.cmdline())]
 z.writestr('export_status.json',json.dumps({'owned_servers_remaining':owned,'gpu_query':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free','--format=csv,noheader,nounits'],text=True),'model_calls':sum('request' in json.loads(p.read_text()) for p in (BASE/'outputs').glob('*.json'))}))
data=buffer.getvalue()
print('REDPAD_EVIDENCE_SHA256='+hashlib.sha256(data).hexdigest())
print('REDPAD_EVIDENCE_ZIP='+base64.b64encode(data).decode())
