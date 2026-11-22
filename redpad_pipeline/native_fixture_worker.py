"""Fixed CPU software fixture, no imports of models, GPU queries or media generation."""
import json,sys,time,subprocess
from pathlib import Path

def main(case,folder):
    root=Path(folder)
    if case=='failure':raise ValueError('EXPECTED SOFTWARE FIXTURE FAILURE')
    if case=='child':
        child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'])
        (root/'fixture_child.json').write_text(json.dumps({'pid':child.pid}))
    if case in ('timeout','child'):time.sleep(20)
    if case=='network':
        from .native_local_worker import audit_event
        try:audit_event('socket.connect',(None,('example.invalid',443)))
        except PermissionError:pass
        else:raise AssertionError('Offline policy failed')
    result={'software_fixture':True,'inference_completed':case=='invalid_output','human_reviewed':False,'production_ready':False}
    (root/'worker_state.json').write_text(json.dumps(result))

if __name__=='__main__':main(sys.argv[1],sys.argv[2])
