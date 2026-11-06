"""Provider boundary: capability checks, explicit preflight, isolated local execution.

Contracts for future backends are deliberately non-executable. This module has no
remote endpoint, package installer, downloader, cloud provisioning or publishing.
"""
from .agents import AgentError
from .agent_media_bridge import MediaBlocked,execute_media
from .specialist_media import PROVIDERS
from .specialists import example,prepare

class LocalVideoAdapter:
    def __init__(self,provider):
        if provider not in ('local-svd','wan-local','ltx-local'):raise AgentError('Unknown local video provider.')
        self.provider=provider
    def capabilities(self):return dict(PROVIDERS[self.provider])
    def validate(self,request):
        if not isinstance(request,dict) or request.get('provider')!=self.provider:raise AgentError('Provider request mismatch.')
        data=example('video');data['records']=[request]
        return prepare('video',data)
    def preflight(self):
        if self.provider!='local-svd':return {'ready':False,'blocker':'Future local backend adapter/checkpoint unavailable; no inference attempted.'}
        from .local_animation import readiness
        ready,reason=readiness();return {'ready':ready,'blocker':reason,'capability':'Existing single-image SVD adapter; request-level controls require separate verification.'}
    def generate(self,request,sidecar):
        self.validate(request)
        ready=self.preflight()
        if not ready['ready']:raise MediaBlocked(ready['blocker'])
        if (request['width'],request['height'],request['fps'])!=(1024,576,7) or abs(request['seconds']-25/7)>.001:
            raise AgentError('Existing SVD adapter supports only 1024×576, 25 frames at 7 fps; no stretching or interpolation fallback.')
        if len(request['characters'])>1:raise AgentError('SVD supports a single reference image; multi-character control is unverified.')
        from pathlib import PurePosixPath
        reference=PurePosixPath(request['reference'])
        if len(reference.parts)!=2 or reference.parts[0]!='references':raise AgentError('SVD reference must be under isolated references/.')
        result=execute_media('video',dict(operation='local_video',reference=reference.name,seed=request['seed']),sidecar)
        from .specialist_inspection import inspect_clip
        inspection=inspect_clip(result['path'],sidecar)
        video=next((s for s in inspection['streams'] if s.get('codec_type')=='video'),{})
        if (video.get('width'),video.get('height'))!=(1024,576) or abs(inspection['duration']-25/7)>.2:
            raise AgentError('Generated video does not match native SVD contract; QC submission blocked.')
        result.update(inspection=inspection,shot=request['shot'],prompt_control='SVD is image-conditioned; prompt retained as editorial guidance only',identity_quality_verified=False)
        return result

class LocalSpeechAdapter:
    def capabilities(self):return dict(PROVIDERS['bengali-tts-local'])
    def synthesize(self,request,sidecar):
        data=example('voice');data['records']=[request];prepare('voice',data)
        raise MediaBlocked('Approved local Bengali TTS backend unavailable. No remote fallback.')

class ReadOnlyAnalyticsAdapter:
    def __init__(self,fetch=None):self.fetch=fetch
    def query(self,operation,channel_id):
        from .youtube import channel_id as validate_channel
        validate_channel(channel_id)
        if operation not in ('channel_profile','video_statistics'):raise AgentError('Only read-only analytics operations allowed.')
        if self.fetch is None:raise MediaBlocked('Use existing authenticated YouTube Connect; no access token available to this adapter.')
        # Explicit dependency injection for the existing authenticated transport.
        # The caller controls consent; credentials are never an input/output field.
        try:return self.fetch(operation,channel_id)
        except Exception:raise MediaBlocked('Read-only analytics unavailable; inspect secure connection status.') from None
