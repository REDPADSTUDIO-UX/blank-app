# REDPAD Phase 2 final-three host eligibility, attempt 1. No model or GPU call.
import json, os, shutil, subprocess, datetime
from pathlib import Path
receipt = {'task':'phase2-final-three','attempt':'kaggle_host_20261122_v1',
           'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'bwrap':shutil.which('bwrap'),'unshare':shutil.which('unshare'),
           'weights_downloaded':False,'model_inference':False,'cuda_initialized':False}
if receipt['unshare']:
    command=[receipt['unshare'],'--user','--map-root-user','--mount','--pid','--net','--fork','/bin/true']
    try:
        proc=subprocess.run(command,capture_output=True,text=True,timeout=15)
        receipt.update(namespace_primitive_pass=proc.returncode==0,exit_code=proc.returncode,
                       error=proc.stderr.strip(),command=command)
    except subprocess.TimeoutExpired:
        receipt.update(namespace_primitive_pass=False,error='Bounded namespace probe timed out')
else:
    receipt.update(namespace_primitive_pass=False,error='unshare unavailable')
receipt['eligible_for_redpad_runtime']=False
receipt['next_gate']='Production sandbox/private-file/lifecycle tests still required' if receipt['namespace_primitive_pass'] else 'STOP: mandatory user/mount/pid/network isolation unavailable; no downloads or runtime imports'
print(json.dumps(receipt,ensure_ascii=False,indent=2))
