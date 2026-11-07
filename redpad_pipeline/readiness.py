"""No automatic downloads or remote probes; optional fixed loopback metadata probe."""
import importlib.util
import json
from pathlib import Path
import shutil
import urllib.request


def inspect_resources(probe=False):
    result={'cuda_device':any(Path('/dev').glob('nvidia*')),'torch_installed':importlib.util.find_spec('torch') is not None,
            'ollama_executable':bool(shutil.which('ollama')),'local_models':[], 'local_probe':'Not requested',
            'inference_verified':False,'large_downloads':False,'paid_fallback':False}
    if probe:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs): return None
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
        try:
            with opener.open('http://127.0.0.1:11434/api/tags',timeout=2) as response:
                data=json.loads(response.read(1024*1024))
            result['local_models']=[m['name'] for m in data.get('models',[]) if isinstance(m,dict) and isinstance(m.get('name'),str)]
            result['local_probe']='Available; metadata only, not inference'
        except Exception: result['local_probe']='Blocked — local runtime unavailable or invalid response'
    return result
