"""Validated scene plans, explicit spend permission, and credential-safe config."""
from dataclasses import dataclass, field
import hashlib
import json
import math


class ProductionError(RuntimeError):
    """Only safe, actionable messages belong in this exception."""


@dataclass
class Config:
    runway_key: str = field(default='', repr=False)
    azure_key: str = field(default='', repr=False)
    azure_region: str = ''
    openai_key: str = field(default='', repr=False)
    paid_enabled: bool = False
    max_job_usd: float = 0.0

    @classmethod
    def load(cls, get):
        try:
            cap = float(get('REDPAD_MAX_JOB_USD') or 0)
        except (ValueError, TypeError):
            cap = 0.0
        return cls(get('RUNWAY_API_KEY'), get('AZURE_SPEECH_KEY'),
                   get('AZURE_SPEECH_REGION'), get('OPENAI_API_KEY'),
                   str(get('REDPAD_ENABLE_PAID_GENERATION')).lower() == 'true', cap)

    def require(self, seconds, approved_usd, video_model='gen4.5'):
        if type(seconds) is not int or not 30 <= seconds <= 600:
            raise ProductionError('Live job duration must be 30–600 seconds.')
        quote = estimate_usd(seconds, video_model)
        if not self.paid_enabled:
            raise ProductionError('Paid generation is disabled by the server owner.')
        if not all((self.runway_key, self.azure_key, self.azure_region, self.openai_key)):
            raise ProductionError('Configure RUNWAY_API_KEY, OPENAI_API_KEY, AZURE_SPEECH_KEY and AZURE_SPEECH_REGION securely.')
        if not math.isfinite(approved_usd) or not math.isfinite(self.max_job_usd) or approved_usd < quote or self.max_job_usd < quote:
            raise ProductionError('Explicit job cost approval and a sufficient server job limit are required.')


def estimate_usd(seconds, video_model='gen4.5'):
    # Planning allowance only, not a provider invoice guarantee. Prices may change.
    from .video_models import estimate_job_usd
    return estimate_job_usd(seconds, video_model)


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def narration(plan):
    return '\n'.join(scene['bn'] for scene in plan['scenes'])


def validate_plan(plan):
    if not isinstance(plan, dict) or not isinstance(plan.get('title'), str) or not plan['title'].strip():
        raise ProductionError('The scene plan needs a title.')
    scenes = plan.get('scenes')
    if not isinstance(scenes, list) or not 3 <= len(scenes) <= 120:
        raise ProductionError('A plan needs 3–120 scenes.')
    total = 0
    for scene in scenes:
        if not isinstance(scene, dict):
            raise ProductionError('Invalid scene.')
        seconds = scene.get('seconds')
        if type(seconds) is not int or not 2 <= seconds <= 10:
            raise ProductionError('Scene duration must be an integer between 2 and 10 seconds.')
        for key, limit in [('prompt', 1000), ('bn', 220), ('en', 350)]:
            value = scene.get(key)
            if not isinstance(value, str) or not value.strip() or len(value.encode('utf-16-le')) // 2 > limit:
                raise ProductionError('Each scene needs a bounded motion prompt and Bangla/English narration.')
            if any(c in value for c in ('\x00', '\r', '\n')):
                raise ProductionError('Scene text must be a single paragraph.')
        if scene.get('sfx') not in ('none', 'whoosh', 'impact', 'chime'):
            raise ProductionError('Unsupported sound effect.')
        total += seconds
    if type(plan.get('seconds')) is not int or plan['seconds'] != total or not 30 <= total <= 600:
        raise ProductionError('Scene durations must total the requested 30–600 seconds.')
    if plan.get('ratio') not in ('720:1280', '1280:720'):
        raise ProductionError('Unsupported aspect ratio.')
    if plan.get('voice') not in ('bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural'):
        raise ProductionError('Unsupported Bangla voice.')
    # Backward compatible: previous saved plans did not record the provider model.
    if 'video_model' in plan:
        from .video_models import resolve_model
        chosen = plan['video_model']
        if chosen == 'auto_lowest_cost':
            raise ProductionError('Resolve automatic model selection before saving a job.')
        resolve_model(chosen)
    return plan


def mock_plan(topic, seconds=30, ratio='720:1280', voice='bn-BD-PradeepNeural'):
    if seconds not in (30, 60, 120, 300, 600):
        raise ProductionError('Choose a supported target duration.')
    lines = [
        ('রাতের ঢাকা। শেষ ট্রেনের অপেক্ষায় দাঁড়িয়ে ছিল এক তরুণ।', 'Night in Dhaka. A young man waited for the last train.'),
        ('হঠাৎ ফাঁকা প্ল্যাটফর্মে ভেসে এল একটি পরিচিত কণ্ঠ।', 'A familiar voice suddenly echoed across the empty platform.'),
        ('কণ্ঠটা তার বাবার। অথচ বাবা আর বেঁচে নেই।', 'It was his father, who was no longer alive.'),
        ('সে পেছনে তাকাল। বেঞ্চের ওপর পড়ে আছে বাবার ঘড়ি।', 'He turned. His father’s watch lay on a bench.'),
        ('ট্রেন চলে গেল। ঘড়িটা আবার চলতে শুরু করল।', 'The train left. The watch began to tick again.'),
    ]
    scenes = []
    for i in range(seconds // 6):
        bn, en = lines[i % len(lines)]
        scenes.append(dict(seconds=6, bn=bn, en=en, sfx='chime' if i % 5 == 4 else 'whoosh',
                           prompt=f'Cinematic Dhaka railway station at night, shot {i+1}, slow dolly forward, moving mist, realistic lighting.'))
    return validate_plan(dict(title=f'MOCK TEST — {topic[:100]}', seconds=seconds,
                              ratio=ratio, voice=voice, scenes=scenes))


def canonical(plan):
    return json.dumps(plan, ensure_ascii=False, sort_keys=True)
