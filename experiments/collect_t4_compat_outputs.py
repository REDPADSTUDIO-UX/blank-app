import base64, hashlib, json
from pathlib import Path
base=Path('/content/redpad_phase3')
files=[base/'model_load.json',base/'server_t4_compat_v2.log']+sorted((base/'trials_t4_compat_v2').glob('*.json'))
for f in files:
    data=f.read_bytes()
    if len(data)>2*1024*1024:raise RuntimeError('Unexpectedly large evidence')
    print('REDPAD_ARTIFACT='+json.dumps({'path':str(f.relative_to(base)),'sha256':hashlib.sha256(data).hexdigest(),'base64':base64.b64encode(data).decode()}))
summary=[{'case':json.loads(f.read_text())['case']['id'],'state':json.loads(f.read_text())['state'],'seconds':json.loads(f.read_text()).get('wall_seconds'),'finish':json.loads(f.read_text()).get('finish_reason')} for f in files if f.parent.name=='trials_t4_compat_v2']
print('REDPAD_SUMMARY='+json.dumps(summary))
