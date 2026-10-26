"""Documented REST adapters. No POST retries; all errors omit provider payloads/URLs."""
import ipaddress
import json
import re
import socket
from urllib.parse import urljoin, urlparse
import html
import requests
from .models import ProductionError, validate_plan
from .video_models import resolve_model, scene_payload

RUNWAY = 'https://api.dev.runwayml.com/v1'
VERSION = '2024-11-06'


def request(session, method, url, **kwargs):
    try:
        response = session.request(method, url, timeout=(10, 90), allow_redirects=False, **kwargs)
    except requests.RequestException:
        raise ProductionError('Provider connection failed. An uncertain submission will not be repeated automatically.') from None
    if response.status_code not in (200, 201, 202):
        raise ProductionError(f'Provider returned HTTP {response.status_code}. Check credentials, quota and account access.')
    return response


def payload(response):
    try:
        return response.json()
    except (ValueError, TypeError):
        raise ProductionError('Provider returned an invalid JSON response.') from None


def safe_download(url, destination, session=None):
    """Accept only HTTPS public Runway/CDN results. No API credentials on downloads."""
    session = session or requests.Session()
    suffixes = ('cloudfront.net', 'runwayml.com', 'runway.com', 'amazonaws.com')
    current = url
    for _ in range(5):
        parts = urlparse(current)
        host = parts.hostname or ''
        if parts.scheme != 'https' or parts.username or parts.password or parts.port not in (None, 443):
            raise ProductionError('Unsafe generated media URL.')
        if not any(host == x or host.endswith('.' + x) for x in suffixes):
            raise ProductionError('Unrecognized media host; review the provider CDN allowlist.')
        try:
            addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
                raise ProductionError('Private media network destinations are forbidden.')
            with session.get(current, stream=True, timeout=(10, 90), allow_redirects=False) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    current = urljoin(current, response.headers.get('Location', ''))
                    continue
                if response.status_code != 200:
                    raise ProductionError(f'Media download failed (HTTP {response.status_code}).')
                temporary = destination.with_suffix('.download')
                size = 0
                try:
                    with temporary.open('wb') as out:
                        for block in response.iter_content(1024 * 1024):
                            size += len(block)
                            if size > 500 * 1024 * 1024:
                                raise ProductionError('Scene media exceeds the 500 MB limit.')
                            out.write(block)
                    if size < 1000:
                        raise ProductionError('Provider media is empty or invalid.')
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
                return
        except (requests.RequestException, OSError):
            raise ProductionError('Media transfer failed; resume will retry the download without regenerating the scene.') from None
    raise ProductionError('Too many media redirects.')


class LiveGateway:
    mode = 'live'

    def __init__(self, config, seconds, approved_usd, session=None, video_model='gen4.5'):
        self.video_model = resolve_model(video_model)
        config.require(seconds, approved_usd, self.video_model)
        if not re.fullmatch(r'[a-z0-9-]+', config.azure_region):
            raise ProductionError('Invalid Azure region.')
        self.approved_seconds = seconds
        self.config = config
        self.session = session or requests.Session()
        self.headers = {'Authorization': f'Bearer {config.runway_key}', 'X-Runway-Version': VERSION}

    def plan(self, topic, seconds, ratio, voice):
        if seconds != self.approved_seconds:
            raise ProductionError('This duration is outside the approved job quote.')
        scene = {'type': 'object', 'additionalProperties': False,
                 'properties': {'seconds': {'type': 'integer'}, 'bn': {'type': 'string'},
                                'en': {'type': 'string'}, 'prompt': {'type': 'string'},
                                'sfx': {'type': 'string', 'enum': ['none', 'whoosh', 'impact', 'chime']}},
                 'required': ['seconds', 'bn', 'en', 'prompt', 'sfx']}
        schema = {'type': 'object', 'additionalProperties': False,
                  'properties': {'title': {'type': 'string'}, 'scenes': {'type': 'array', 'items': scene}},
                  'required': ['title', 'scenes']}
        # requests has no implicit application-level retry of a billed POST.
        response = request(self.session, 'POST', 'https://api.openai.com/v1/responses',
            headers={'Authorization': f'Bearer {self.config.openai_key}'}, json={
                'model': 'gpt-4.1-mini', 'max_output_tokens': 16000, 'store': False,
                'instructions': ('You are a Bangladeshi film director. Create an original coherent fictional film. '
                    'Do not claim fictional events as facts. Preserve recurring character and location descriptions. '
                    f'Create exactly {seconds//6} scenes, each exactly 6 seconds. '
                    'Each bn is natural spoken Bangladesh Bangla, 7–12 words maximum, a single line. '
                    'Each en is an accurate English translation of bn. Prompt is an English cinematic moving-video '
                    'description with action, camera movement, lighting and continuity, under 900 characters. '
                    'No on-screen text, logos or baked-in subtitles. Choose a subtle transition sound effect.'),
                'input': topic[:6000],
                'text': {'format': {'type': 'json_schema', 'name': 'film_plan', 'schema': schema, 'strict': True}}})
        data = payload(response)
        try:
            text = ''.join(part.get('text', '') for output in data.get('output', [])
                           for part in output.get('content', []) if part.get('type') == 'output_text')
            plan = json.loads(text)
            plan.update(seconds=seconds, ratio=ratio, voice=voice)
            return validate_plan(plan)
        except (ValueError, TypeError, AttributeError):
            raise ProductionError('The script planner returned an incomplete or invalid film plan.') from None

    def voice(self, text, voice, path):
        if voice not in ('bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural'):
            raise ProductionError('Unsupported voice.')
        ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="bn-BD">'
                f'<voice name="{voice}">{html.escape(text, quote=False)}</voice></speak>')
        response = request(self.session, 'POST',
            f'https://{self.config.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1',
            headers={'Ocp-Apim-Subscription-Key': self.config.azure_key,
                     'Content-Type': 'application/ssml+xml; charset=utf-8',
                     'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm'}, data=ssml.encode())
        if not response.content.startswith(b'RIFF') or len(response.content) < 100:
            raise ProductionError('Azure did not return valid WAV audio.')
        temporary = path.with_suffix('.partial.wav')
        temporary.write_bytes(response.content)
        temporary.replace(path)

    def submit_video(self, scene, ratio):
        # The approved and checkpointed model is fixed. NEVER silently switch models
        # after an uncertain billable POST; that could charge twice.
        spec = scene_payload(self.video_model, scene, ratio)
        result = payload(request(self.session, 'POST', RUNWAY + '/text_to_video',
                                 headers=self.headers, json=spec))
        task_id = result.get('id')
        if not isinstance(task_id, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', task_id):
            raise ProductionError('Provider did not return a valid task ID; reconcile the submission in Runway.')
        return task_id

    def video_status(self, task_id, path):
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', task_id):
            raise ProductionError('Invalid saved video task ID.')
        result = payload(request(self.session, 'GET', RUNWAY + '/tasks/' + task_id, headers=self.headers))
        status = result.get('status')
        if status in ('FAILED', 'CANCELLED'):
            raise ProductionError('Video task failed or was cancelled. Review it in Runway; no automatic paid retry.')
        if status == 'SUCCEEDED':
            outputs = result.get('output')
            if not isinstance(outputs, list) or not outputs or not isinstance(outputs[0], str):
                raise ProductionError('Video task succeeded without downloadable output.')
            safe_download(outputs[0], path)
            return True
        if status not in ('PENDING', 'THROTTLED', 'RUNNING'):
            raise ProductionError('Unrecognized provider task state.')
        return False
