"""One OS-held local model/media lease across projects; no stale-file deletion."""
import fcntl,os,threading
from functools import wraps
from pathlib import Path
from .agents import AgentError

LOCK=Path(__file__).resolve().parents[1]/'phase3_runs/.local-pipeline.lock'
_local=threading.local()
class ResourceBusy(AgentError):pass

def serialized(function):
    @wraps(function)
    def run(*args,**kwargs):
        if getattr(_local,'held',False):return function(*args,**kwargs)
        if any(p.is_symlink() for p in (LOCK,*LOCK.parents)):raise AgentError('Unsafe compute lease path.')
        LOCK.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(LOCK,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise ResourceBusy('Another local model/media pipeline is active; explicit retry after it stops. No compute provisioned.') from None
            _local.held=True
            try:return function(*args,**kwargs)
            finally:_local.held=False
        finally:os.close(fd)
    return run
