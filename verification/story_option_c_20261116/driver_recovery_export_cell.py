# Export only existing research evidence; no model launch or new generation.
import base64,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path('/content/redpad_story_t4_20261114/option_c_approved')
case_path=R/'outputs/driverbound_canary_v1.json'
result=json.loads(case_path.read_text())
ledger=json.loads((R/'call_ledger.json').read_text())
binding=json.loads((R/'driver_binding_verified.json').read_text())
old_hash=hashlib.sha256((R/'outputs/canary.json').read_bytes()).hexdigest()
assert old_hash==binding['previous_failed_launch_sha256']
assert len(ledger['historical'])==2 and ledger['ceiling']==7 and len(ledger['new_calls'])<=1
assert result['server_stopped'] is True
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,driver_version','--format=csv,noheader,nounits'],text=True,timeout=12)
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=12)
export={'observed_at_utc':datetime.now(timezone.utc).isoformat(),
 'binding':binding,'canary':result,'ledger':ledger,
 'server_log':(R/'driverbound_canary_v1.server.log').read_text(),
 'postflight':{'gpu':gpu,'gpu_processes':apps},
 'prior_failed_launch_sha256_unchanged':old_hash,
 'complete_story':None,'required_story_sections':['foundation','act_1','act_2','act_3','reflection'],
 'remaining_calls':7-2-len(ledger['new_calls']),
 'human_review':'PENDING','production_ready':False,'production_worker_changed':False,
 'downloads':0,'scope':'Option C research only; production kernel isolation not verified'}
(R/'driver_recovery_export.json').write_text(json.dumps(export,ensure_ascii=False,indent=2))
encoded=base64.b64encode(json.dumps(export,ensure_ascii=True).encode()).decode()
for offset in range(0,len(encoded),8000):print('RECOVERY_PART_'+str(offset//8000)+'='+encoded[offset:offset+8000])
print('RECOVERY_EXPORT_FINISHED parts='+str((len(encoded)+7999)//8000),flush=True)
