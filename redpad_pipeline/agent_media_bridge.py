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
    if operation=='shared_image' and key in ('character','art','location','costume','storyboard'):
        from .agents import AgentStore
        from .shared_model_services import SharedServices,profile
        services=SharedServices(AgentStore(sidecar));id=data.get('profile');p=profile(id)
        if p['adapter'] not in ('flux2_klein','z_image'):raise MediaBlocked('Selected shared candidate has no image generation adapter.')
        route=services.policy(key)
        if not route or route['profile']!=id or route['capability'] not in ('text_to_image','reference_edit'):raise MediaBlocked('Explicit approved development image route required.')
        folder,evidence=services.execute(id,data.get('request',{}))
        return {'path':str((folder/'image.png').relative_to(root)),'model':p['repo']+'@'+p['revision'],'actual_generation':True,'metadata':evidence}
    if operation=='offline_vision' and key in ('director','qc','continuity','character','art','location','costume','storyboard','performance','cinematographer','motion'):
        from .offline_vision import inspect
        return inspect(data.get('request'),sidecar)
    if operation=='mix_dialogue_cues' and key=='music':
        from .delivery import from_sidecar
        from .audio_post import mix
        return mix(from_sidecar(sidecar).p,data.get('music_task'),data.get('voice_task'),data.get('receipts'),data.get('seconds'))
    if operation=='assemble_delivery' and key=='editing':
        from .delivery import from_sidecar
        return from_sidecar(sidecar).render(data.get('editing_task'),data.get('receipts'),evaluation_only=data.get('evaluation_only') is True)
    if operation=='offline_audio' and key=='music':
        from .offline_audio import generate
        return generate(data.get('engine'),data.get('request'),sidecar)
    if operation=='offline_image' and key in ('character','art','location','costume','storyboard'):
        from .offline_image import generate
        return generate(data.get('request'),sidecar)
    if key=='video' and operation=='offline_video':
        from .offline_media import generate
        return generate(data.get('engine'),data.get('request'),sidecar)
    if key=='voice' and operation=='offline_speech':
        from .offline_speech import synthesize
        return synthesize(data.get('request'),sidecar)
    if operation=='specialist_video' and key=='video':
        from .specialist_adapters import LocalVideoAdapter
        request=data.get('request',{})
        return LocalVideoAdapter(request.get('provider')).generate(request,sidecar)
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
