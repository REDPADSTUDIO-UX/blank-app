"""Objective local inspection. Only isolated assets; never fetch URLs."""
import json,subprocess,hashlib,shutil
from pathlib import Path
from .agents import AgentError
from .agent_media_bridge import MediaBlocked
from .specialist_media import asset


def inspect_clip(name,sidecar):
    asset(name,pending=False)
    root=Path(sidecar).parent/'agent_media';path=root/name
    if root.is_symlink() or any(p.is_symlink() for p in [path,*path.parents]):raise AgentError('Symlink media paths prohibited.')
    if not path.resolve().is_relative_to(root.resolve()):raise AgentError('Media path escapes workspace.')
    if not path.is_file():raise MediaBlocked('Local media asset missing.')
    if path.stat().st_size>100*1024*1024:raise AgentError('Micro-test inspection limited to 100 MB.')
    with path.open('rb') as source:
        header=source.read(12)
    format_hint='mov' if len(header)>=8 and header[4:8]==b'ftyp' else 'wav' if header[:4]==b'RIFF' and header[8:12]==b'WAVE' else None
    if format_hint is None:raise AgentError('Inspection accepts MP4/MOV or WAV containers only; playlists are prohibited.')
    executable=shutil.which('ffprobe')
    if not executable:raise MediaBlocked('Local ffprobe missing.')
    try:
        result=subprocess.run([executable,'-v','error','-protocol_whitelist','file,pipe','-f',format_hint,'-show_format','-show_streams','-of','json',str(path.resolve())],capture_output=True,text=True,timeout=15,check=True)
        info=json.loads(result.stdout)
        if not info.get('streams'):raise ValueError()
        duration=float(info['format']['duration'])
        if not 0<duration<=3600:raise ValueError()
    except (subprocess.SubprocessError,ValueError,KeyError):raise AgentError('Invalid or unreadable media asset.') from None
    return dict(path=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),duration=duration,
                streams=[{k:s[k] for k in ('codec_type','codec_name','width','height','sample_rate') if k in s} for s in info['streams']],
                actual_generation=False,model='none — local ffprobe inspection',creative_quality_verified=False)
