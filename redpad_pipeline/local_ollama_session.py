"""Development-only CPU runtime context; no installation/download or system service.

Some execution environments isolate loopback per command. Start the installed
runtime and client inside one process context, then stop only the owned runtime.
"""
from contextlib import contextmanager
from pathlib import Path
import json,os,subprocess,time,urllib.request
from .screenwriter import WritingError

ROOT=Path(__file__).resolve().parents[1]

@contextmanager
def local_cpu_session():
    root=ROOT/'phase3_models';runtime=root/'ollama-runtime';binary=runtime/'bin/ollama'
    if not binary.is_file() or binary.is_symlink():raise WritingError('Approved local Ollama installation unavailable.')
    env=os.environ.copy();env.update(OLLAMA_MODELS=str(root/'ollama-weights'),OLLAMA_HOST='127.0.0.1:11434',OLLAMA_NO_CLOUD='1',OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',OLLAMA_CONTEXT_LENGTH='8192',CUDA_VISIBLE_DEVICES='-1')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    process=None;log=None
    try:
        try:
            with opener.open('http://127.0.0.1:11434/api/version',timeout=1) as response:json.load(response)
        except Exception:
            log=(runtime/'owned-session.log').open('ab')
            process=subprocess.Popen([str(binary),'serve'],env=env,stdout=log,stderr=log)
            deadline=time.monotonic()+15
            while True:
                if process.poll() is not None:raise WritingError('Local Ollama startup failed; inspect private runtime log.')
                try:
                    with opener.open('http://127.0.0.1:11434/api/version',timeout=1) as response:json.load(response)
                    break
                except Exception:
                    if time.monotonic()>deadline:raise WritingError('Local Ollama startup timed out.')
                    time.sleep(.2)
        yield env
    finally:
        if process is not None:
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        if log:log.close()
