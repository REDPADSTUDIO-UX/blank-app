"""Read-only runtime inventory. No account login, provisioning, or model download."""
import importlib.metadata,json,os,platform,shutil,subprocess,time
from pathlib import Path

PACKAGES=('torch','transformers','accelerate','bitsandbytes','diffusers','safetensors','huggingface_hub','numpy','Pillow','kaggle')

def probe(workdir=None):
    root=Path(workdir or ('/kaggle/working' if Path('/kaggle/working').is_dir() else Path.cwd()))
    versions={}
    for name in PACKAGES:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    mem={}
    if Path('/proc/meminfo').is_file():
        for line in Path('/proc/meminfo').read_text().splitlines():
            key,value=line.split(':',1)
            if key in ('MemTotal','MemAvailable'):mem[key+'_bytes']=int(value.strip().split()[0])*1024
    gpu=[];error=None;cuda_driver=None
    try:
        p=subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free,driver_version,compute_cap','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=12,check=True)
        for line in p.stdout.strip().splitlines():
            parts=[x.strip() for x in line.split(',')]
            if len(parts)!=6:raise ValueError('GPU inventory schema changed')
            gpu.append(dict(index=int(parts[0]),name=parts[1],total_bytes=int(float(parts[2])*2**20),free_bytes=int(float(parts[3])*2**20),driver=parts[4],compute_capability=parts[5]))
        banner=subprocess.run(['nvidia-smi'],capture_output=True,text=True,timeout=12).stdout
        import re
        match=re.search(r'CUDA Version:\s*([\d.]+)',banner);cuda_driver=match[1] if match else None
    except (OSError,ValueError,subprocess.SubprocessError) as exc:error=type(exc).__name__
    cgroup_available=None
    try:
        limit=(Path('/sys/fs/cgroup/memory.max')).read_text().strip();used=int(Path('/sys/fs/cgroup/memory.current').read_text())
        if limit!='max':cgroup_available=max(0,int(limit)-used)
    except (OSError,ValueError):pass
    disk=shutil.disk_usage(root)
    return {'schema_version':1,'captured_unix':time.time(),'provider':'kaggle_environment_marker' if Path('/kaggle/working').is_dir() and os.environ.get('KAGGLE_KERNEL_RUN_TYPE') else 'current_development_host_not_verified_as_kaggle',
        'python':platform.python_version(),'platform':platform.system(),'cpu_count':os.cpu_count(),'host_memory':mem,'cgroup_available_bytes':cgroup_available,'disk_free_bytes':disk.free,'disk_total_bytes':disk.total,'gpus':gpu,'gpu_probe_error':error,'cuda_driver_supported_version':cuda_driver,'libraries':versions,
        'kaggle_account_connected':None,'accelerator_setting':None,'remaining_gpu_quota_hours':None,'maximum_session_hours':None,'internet_download_available':None,'free_tier_verified':False,'quota_source':None,
        'scope':'Measured process-host inventory only. Driver CUDA support is not installed toolkit/runtime. System RAM can exceed container cgroup limits. Account, quota, accelerator setting and free tier require actual Kaggle settings inspection. No model inference or download.'}

def tensor_canary():
    if not(Path('/kaggle/working').is_dir() and os.environ.get('KAGGLE_KERNEL_RUN_TYPE')):raise ValueError('Tensor canary is restricted to an already running Kaggle session.')
    import torch
    if not torch.cuda.is_available():raise ValueError('CUDA unavailable; no GPU provisioned.')
    start=time.monotonic();torch.cuda.reset_peak_memory_stats();x=torch.arange(64,device='cuda',dtype=torch.float32).reshape(8,8)
    result=(x@x.T).sum().item();torch.cuda.synchronize()
    return {'kind':'tiny_tensor_runtime_canary_NOT_MODEL_INFERENCE','value':result,'elapsed_seconds':time.monotonic()-start,'torch_version':torch.__version__,'torch_cuda_runtime':torch.version.cuda,'peak_cuda_allocated_bytes':torch.cuda.max_memory_allocated(),'model_inference':False}

if __name__=='__main__':print(json.dumps(probe(),indent=2))
