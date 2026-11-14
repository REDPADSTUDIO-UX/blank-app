"""Measured owned-worker resources; no synthetic performance estimates."""
import sys
try:import resource
except ImportError:resource=None

def start(torch):
    cuda=getattr(torch,'cuda',None)
    if cuda is not None and cuda.is_available():cuda.reset_peak_memory_stats()

def finish(torch):
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024) if resource else None
    device=getattr(torch,'cuda',None);cuda=device is not None and device.is_available()
    return {'torch_version':str(getattr(torch,'__version__','not reported')),'peak_worker_process_rss_bytes':rss,
            'peak_cuda_allocated_bytes':device.max_memory_allocated() if cuda else None,
            'peak_cuda_reserved_bytes':device.max_memory_reserved() if cuda else None,
            'cuda_device':device.get_device_name() if cuda else None,
            'scope':'Measured owned process/model phase; host RSS excludes child processes and is not total machine RAM. CUDA figures exclude driver/non-PyTorch allocations.'}
