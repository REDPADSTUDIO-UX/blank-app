"""Adapters to existing local media code, restricted to isolated agent_media.

No arbitrary database paths, URLs, production database, or remote voice endpoint.
"""
from pathlib import Path
import re
from .agents import AgentError

class MediaBlocked(AgentError):
    pass


def execute_media(key,data,sidecar):
    root=Path(sidecar).parent/'agent_media'
    if root.is_symlink():raise AgentError('Media workspace must not be a symlink.')
    root=root.resolve()
    operation=data.get('operation')
    if operation=='inspect_clip' and key in ('video','voice','music','editing'):
        from .specialist_inspection import inspect_clip
        return inspect_clip(data.get('asset'),sidecar)
    if key=='video' and operation=='local_video':
        from .local_animation import readiness,generate
        ready,reason=readiness()
        if not ready:raise MediaBlocked(reason)
        name=data.get('reference')
        if not isinstance(name,str) or Path(name).name!=name:raise AgentError('Use a reference filename within agent_media/references.')
        refs=root/'references';path=refs/name
        if refs.is_symlink() or path.is_symlink() or not path.is_file():raise MediaBlocked('Isolated reference image is unavailable.')
        if path.stat().st_size>10*1024*1024:raise AgentError('Reference image too large.')
        result,metadata=generate(path.read_bytes(),root,seed=data.get('seed',42),motion=data.get('motion',127))
        return {'path':str(result.relative_to(root)),'metadata':metadata,'actual_generation':True,'model':'local-svd-xt'}
    if key in ('editing','music') and operation in ('render_quality_project','compose_quality_cue'):
        if (key=='editing') != (operation=='render_quality_project'):raise AgentError('Operation does not match department.')
        pid=data.get('project_id')
        if not isinstance(pid,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',pid):raise AgentError('Invalid isolated project identifier.')
        db=root/'quality_workspace.sqlite3'
        if not db.is_file() or db.is_symlink():raise MediaBlocked('No isolated quality project exists. Use validated assets; production database is never opened.')
        # No symlink may redirect the local renderer to production assets.
        if any(p.is_symlink() for p in root.rglob('*')):raise AgentError('Symlink in isolated media workspace.')
        from .drama_quality import Studio,QualityError
        from .drama_finish import render,local_cue
        studio=Studio(db,root)
        try:
            studio.project(pid)
            for asset in studio.assets(pid):
                if not Path(asset['path']).resolve().is_relative_to(root):
                    raise AgentError('Asset path escapes isolated media workspace.')
            if operation=='render_quality_project':
                output=render(studio,pid)
                return {'path':str(output.relative_to(root)),'actual_generation':True,'model':'none — local FFmpeg assembly'}
            component=data.get('component');target=data.get('target')
            if component not in ('music','sfx') or not isinstance(target,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',target):raise AgentError('Invalid cue target.')
            asset=local_cue(studio,pid,component,target)
            return {'asset_id':asset,'actual_generation':True,'model':'none — local sound composition'}
        except QualityError as exc:raise MediaBlocked('Existing quality gate: '+str(exc)) from None
    if key=='voice':raise MediaBlocked('No approved local Bengali voice synthesis backend installed; remote gTTS is not called automatically.')
    raise MediaBlocked('Select a supported local media operation with isolated approved assets. No media generated.')
