"""Story/Colab metadata checkpoint, NOT an isolation probe or model launcher.

No bwrap/unshare/mount calls, installers, sockets, downloads, model imports,
weight reads or production-store access. Run in the owner's Colab UI; local CPU
fixtures cannot certify that browser, account or GPU allocation.
"""
import importlib.metadata
import json,os,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

MODEL={'repo':'unsloth/Qwen3.5-9B-GGUF','revision':'3885219b6810b007914f3a7950a8d1b469d598a5',
 'file':'Qwen3.5-9B-Q4_K_M.gguf','bytes':5680522464,
 'sha256':'03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'}
PRIMARY={'repo':'Qwen/Qwen3.5-27B','revision':'fc05daec18b0a78c049392ed2e771dde82bdf654','adapter':'hf_text_nf4'}
DEFAULT_ROOTS=(Path('/content/redpad_story_t4_20261114'),
 Path('/root/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF/snapshots')/MODEL['revision'])

def read_metadata(path):
    try:return Path(path).read_text().strip()
    except (OSError,UnicodeError):return None

def cache_metadata(roots):
    rows=[]
    for root in roots:
        root=Path(root)
        linked=any(p.is_symlink() for p in (root,*root.parents))
        weight=root/MODEL['file'];receipt=root/'installation.json'
        unsafe=linked or weight.is_symlink() or receipt.is_symlink()
        rows.append({'root':str(root),'symlink_rejected':unsafe,
          'root_present':not unsafe and root.is_dir(),
          'exact_filename_present':not unsafe and weight.is_file(),
          'bytes':weight.stat().st_size if not unsafe and weight.is_file() else None,
          'installation_receipt_present':not unsafe and receipt.is_file(),
          'weight_hash_verified':False,'receipt_contents_inspected':False})
    return rows

def collect(*,proc=Path('/proc'),roots=DEFAULT_ROOTS,runner=None,tool=None):
    """Current metadata only. Historical mount failure must not be replayed here."""
    proc=Path(proc);status={}
    for line in (read_metadata(proc/'self/status') or '').splitlines():
        if ':' in line:
            key,value=line.split(':',1)
            if key in ('CapEff','NoNewPrivs','Seccomp','Seccomp_filters'):status[key]=value.strip()
    cap=status.get('CapEff')
    try:admin=bool(int(cap,16)&(1<<21)) if cap else None
    except ValueError:admin=None
    mem={}
    for line in (read_metadata(proc/'meminfo') or '').splitlines():
        parts=line.split()
        if parts and parts[0] in ('MemTotal:','MemAvailable:'):
            try:mem[parts[0][:-1]+'_bytes']=int(parts[1])*1024
            except (ValueError,IndexError):pass
    libs={}
    for name in ('torch','transformers','psutil','jsonschema','safetensors','accelerate','bitsandbytes'):
        try:libs[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:libs[name]=None
    command=tool if tool is not None else shutil.which('nvidia-smi')
    gpu={'queried':False,'stdout':None,'error':None}
    if command:
        try:
            result=(runner or subprocess.run)([command,'--query-gpu=name,memory.total,memory.free,driver_version,compute_cap','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=12,check=True)
            gpu.update(queried=True,stdout=result.stdout.strip())
        except (OSError,subprocess.SubprocessError) as exc:gpu['error']=type(exc).__name__
    else:gpu['error']='nvidia-smi unavailable'
    disk=shutil.disk_usage('/content' if Path('/content').is_dir() else '.')
    return {'schema':'story-colab-readonly-v1','observed_at_utc':datetime.now(timezone.utc).isoformat(),
      'execution_context':'Caller must attest actual Colab through browser; this script cannot certify it.',
      'python':platform.python_version(),'kernel_release':platform.release(),'gpu':gpu,'ram':mem,
      'disk':{'free_bytes':disk.free,'total_bytes':disk.total},'dependency_metadata':libs,
      'kernel_metadata':{'status':status,'cap_sys_admin_effective':admin,'lsm_profile':read_metadata(proc/'self/attr/current'),
       'max_user_namespaces':read_metadata(proc/'sys/user/max_user_namespaces'),
       'apparmor_restrict_unprivileged_userns':read_metadata(proc/'sys/kernel/apparmor_restrict_unprivileged_userns')},
      'bwrap_executable':shutil.which('bwrap'),'cache_metadata':cache_metadata(roots),
      'isolation_operations_attempted':[],'kernel_isolation_verified':False,'security_equivalence_verified':False,
      'model_bytes_read':False,'model_downloads':0,'model_inferences':0,'remaining_free_quota':None,
      'primary_preserved':PRIMARY,'previously_approved_fallback':MODEL,
      'scope':'Read-only metadata/size inspection only. New VM/kernel identity is not evidence mount restrictions changed. No receipt, launch, license or research-boundary approval is created.'}

def boundary_plan():
    """Concrete Option C review packet, not a grant or a second execution engine."""
    return {'scope':'Story only; one fictional existing brief; quarantined research outputs',
      'exact_fallback':MODEL,'fallback_model_authorization':'already granted; no identical model approval requested',
      'primary':PRIMARY,'primary_status':'NOT TESTED; no T4 fit claim',
      'execution_authorized':False,'security_boundary_authorized':False,'launch_enabled':False,
      'security_equivalent_to_studio':False,'kernel_network_egress_guarantee':False,
      'fresh_proc_pid_mount_guarantee':False,
      'new_owner_decision':'Whether to allow explicitly separate research-only Colab execution without the Studio worker kernel mount/PID/network guarantees. Approval must be given explicitly outside this file; editing a flag is not itself owner authorization.',
      'required_conditions':['Fresh research-only runtime; no Drive mount, Studio secrets, production database or private media',
       'Exact previously approved GGUF and reviewed llama runtime; full local source/artifact hashes and installed dependencies verified before launch',
       'No hosted model APIs/public endpoint, model substitution or automatic dependency/model downloads',
       'Kernel egress isolation remains unverified; loopback/offline library settings are mitigations, not equivalent isolation',
       'Existing seven-call ceiling includes failures/reservations; two historical calls retained, never reset or relabeled',
       'Do not repeat successful canary; inspect failed foundation and obtain a concrete changed-test hypothesis before any retry',
       'Original prompt/raw response/finish reason/runtime/hash receipts retained; no automatic retry or prose repair',
       'Raw research results quarantined; StoryBridge/QC/Director/owner gates remain unchanged'],
      'prior_calls':2,'existing_total_ceiling':7,'conservative_unspent_slots':5,
      'budget_feasibility':'A fresh canary + five new sections needs six calls and exceeds five unspent slots. Do not silently reset budget; reuse valid evidence or obtain a separately scoped budget decision before promising a complete story.',
      'notebook_scope':'Reproducible read-only preflight and explicit research-boundary pause. No alternate inference launcher implemented or enabled.'}


# Option C owner authorized in the current task. Metadata only; no launcher/downloads.
import hashlib
option_c_observation = collect()
option_c_observation['option_c_owner_authorized'] = True
option_c_observation['production_worker_unchanged'] = True
option_c_observation['call_budget'] = {'ceiling':7,'historical_consumed':2,'new_calls':0,'remaining':5}
base = Path('/content/redpad_story_t4_20261114')
paths = [base/'runtime/llama-b12318/llama-server',
 base/'runtime/cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz',
 base/'runtime/llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz',base/'installation.json']
option_c_observation['runtime_files'] = [
 {'path':str(p),'present':p.is_file() and not any(q.is_symlink() for q in (p,*p.parents)),
  'symlink_rejected':any(q.is_symlink() for q in (p,*p.parents))} for p in paths]
mounts = Path('/proc/self/mountinfo').read_text()
option_c_observation['research_boundary_checks'] = {
 'drive_mount_detected':any(' /content/drive ' in line or 'drivefs' in line.lower() for line in mounts.splitlines()),
 'drive_mount_performed':False,'secrets_values_inspected':False,
 'production_database_or_private_media_accessed':False,
 'hosted_inference_used':False,'production_security_equivalence':False,
 'complete_host_confidentiality_certified':False}
option_c_observation['runtime_compatibility'] = 'NOT TESTED; only metadata inspected'
option_c_observation['stop_before_launch'] = True
print(json.dumps(option_c_observation,ensure_ascii=False,indent=2))
