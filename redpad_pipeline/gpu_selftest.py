"""Owner-enabled one-shot backend check; uses only a geometric test fixture.

No authentication bypass or project data access: results stay behind the Studio
login. Default off. Never retry on quota errors, across reconnects or reruns.
"""
import json,threading
from pathlib import Path
_started=False
_lock=threading.Lock()


def start_once(media_dir):
    global _started
    with _lock:
        if _started:return
        _started=True
    root=Path(media_dir);result_file=root/'gpu_selftest_result.json'
    # A prior result in this runtime prevents repeat GPU quota consumption.
    if result_file.exists():return
    def worker():
        root.mkdir(parents=True,exist_ok=True)
        try:
            from .remote_gpu import free_account_token,generate,test_image
            if not free_account_token():raise RuntimeError('Authenticated free account is not configured.')
            output=generate(test_image(),'A red ball slowly rolls to the right across a gray tiled floor. Fixed camera. Preserve the room and lighting.',root)
            from .media import duration
            result=dict(status='success',path=str(output),seconds=duration(output),source='built-in geometric test fixture',mode='Studio authenticated free ZeroGPU')
            print('REDPAD_GPU_SELFTEST success; actual MP4 received and duration validated.',flush=True)
        except Exception as exc:
            # Only our sanitized operational error; never exception payloads containing credentials.
            from .remote_gpu import GPUError
            reason=str(exc) if isinstance(exc,GPUError) else 'Backend self-test did not complete.'
            result=dict(status='failed',reason=reason)
            print('REDPAD_GPU_SELFTEST failed: '+reason,flush=True)
        result_file.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    threading.Thread(target=worker,daemon=True,name='redpad-owner-gpu-check').start()
