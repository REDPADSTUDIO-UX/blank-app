"""Research-only driver binding recovery. No downloads or model loading."""
import hashlib, json, re, subprocess
from pathlib import Path

R=Path('/content/redpad_story_t4_20261114/option_c_approved')
ready=json.loads((R/'bundle_ready.json').read_text())
assert ready['status']=='BUNDLE_VERIFIED'
assert ready['model']['sha256']=='03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'
assert Path(ready['model_path']).is_file() and Path(ready['model_path']).stat().st_size==5680522464
assert hashlib.sha256(Path(ready['binary']).read_bytes()).hexdigest()==ready['binary_sha256']
ledger=json.loads((R/'call_ledger.json').read_text())
assert ledger['ceiling']==7 and len(ledger['historical'])==2
assert ledger['new_calls']==[], 'Inspect any existing new calls before recovery'
old_failure_hash=hashlib.sha256((R/'outputs/canary.json').read_bytes()).hexdigest()
assert not any(' /content/drive ' in x or 'drivefs' in x.lower() for x in Path('/proc/self/mountinfo').read_text().splitlines())
driver=Path('/usr/lib64-nvidia')
assert driver.is_dir() and (driver/'libcuda.so.1').is_file()
resolved=(driver/'libcuda.so.1').resolve()
assert resolved.parent==driver and resolved.name=='libcuda.so.580.82.07', 'Unexpected provider driver source'
env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(R),
 'LD_LIBRARY_PATH':ready['runtime_libraries']+':'+str(driver),
 'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','CUDA_VISIBLE_DEVICES':'0'}
cuda_libs=list((R/'runtime').rglob('libggml-cuda.so'))
assert len(cuda_libs)==1
dependency=subprocess.run(['/usr/bin/ldd',str(cuda_libs[0])],env=env,capture_output=True,text=True,timeout=20)
assert dependency.returncode==0 and 'not found' not in dependency.stdout, dependency.stdout+dependency.stderr
assert '/usr/lib64-nvidia/libcuda.so.1' in dependency.stdout, dependency.stdout
devices=subprocess.run([ready['binary'],'--list-devices'],env=env,cwd=R,capture_output=True,text=True,timeout=30)
listing=devices.stdout+devices.stderr
assert devices.returncode==0,listing
matches=re.findall(r'^\s*(CUDA\d+):[^\n]*Tesla T4[^\n]*',listing,re.MULTILINE)
assert len(matches)==1, 'No unambiguous T4 device: '+listing
binding={'status':'VERIFIED_NO_MODEL_LOAD','driver_directory':str(driver),'driver_resolved':str(resolved),
 'dependency_stdout':dependency.stdout,'dependency_stderr':dependency.stderr,
 'device_stdout':devices.stdout,'device_stderr':devices.stderr,'selected_device':matches[0],
 'worker_env':env,'previous_failed_launch_sha256':old_failure_hash,
 'model_loaded':False,'model_generation_submitted':False,'downloads':0,'system_driver_changes':False,
 'production_worker_changed':False,'studio_kernel_isolation_equivalent':False}
with (R/'driver_binding_verified.json').open('x') as f:json.dump(binding,f,ensure_ascii=False,indent=2)
print('DRIVER_BINDING='+json.dumps(binding),flush=True)
