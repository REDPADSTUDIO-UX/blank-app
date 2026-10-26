"""Explicit, auditable Runway Dev multi-model options for REDPAD AI Studio.

These models share ONE Runway Developer API account. This is multi-MODEL,
not an integration with independent ByteDance/Kling billing accounts.
Prices are planning estimates copied from the official developer pricing page
on 2026-10-26 (USD 0.01 per credit), not live quotes or bill guarantees.
"""
from .models import ProductionError

# Fixed 720p text-to-video capabilities: all options support a 6-second scene.
# Do not silently substitute a different model after a billed submission.
VIDEO_MODELS = {
    'grok_imagine_1_5_lite': {
        'label': 'Grok Imagine 1.5 Lite — 720p (budget)',
        'usd_per_second': 0.03,
        'audio': None,
    },
    'kling3.0_standard': {
        'label': 'Kling 3 Standard — 720p (no native audio)',
        'usd_per_second': 0.09,
        'audio': False,
    },
    'wan3': {
        'label': 'WAN 3.0 — 720p',
        'usd_per_second': 0.10,
        'audio': None,
    },
    'gen4.5': {
        'label': 'Runway Gen-4.5 — 720p',
        'usd_per_second': 0.12,
        'audio': None,
    },
    'seedance2_mini': {
        'label': 'Seedance 2 Mini — 720p',
        'usd_per_second': 0.16,
        'audio': False,
    },
    'seedance2_fast': {
        'label': 'Seedance 2 Fast — 720p',
        'usd_per_second': 0.29,
        'audio': False,
    },
    'seedance2': {
        'label': 'Seedance 2 — 720p',
        'usd_per_second': 0.36,
        'audio': False,
    },
}
AUTO = 'auto_lowest_cost'
PLANNING_VOICE_SCRIPT_USD_30S = 0.25

def resolve_model(choice):
    """Resolve once, BEFORE costing/consent and before provider submission."""
    if choice == AUTO:
        return min(VIDEO_MODELS, key=lambda key: (VIDEO_MODELS[key]['usd_per_second'], key))
    if choice not in VIDEO_MODELS:
        raise ProductionError('Unsupported video model; choose a model from the verified catalog.')
    return choice

def video_cost_usd(seconds, choice):
    if type(seconds) is not int or not 30 <= seconds <= 600:
        raise ProductionError('Production duration must be 30–600 seconds.')
    model = resolve_model(choice)
    return round(seconds * VIDEO_MODELS[model]['usd_per_second'], 2)

def estimate_job_usd(seconds, choice):
    return round(video_cost_usd(seconds, choice) +
                 seconds / 30 * PLANNING_VOICE_SCRIPT_USD_30S, 2)

def scene_payload(model, scene, ratio):
    """Prepare model-specific direct /text_to_video request. NO network side effects."""
    model = resolve_model(model)
    if ratio not in ('720:1280', '1280:720'):
        raise ProductionError('Unsupported output ratio.')
    if not isinstance(scene, dict) or type(scene.get('seconds')) is not int:
        raise ProductionError('Invalid scene timing.')
    length = scene['seconds']
    if not 4 <= length <= 10:  # planner uses 6 seconds
        raise ProductionError('Selected model needs a scene between 4 and 10 seconds.')
    prompt = scene.get('prompt')
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 1000:
        raise ProductionError('Scene prompt must be 1–1000 characters.')
    payload = {'model': model, 'promptText': prompt, 'duration': length, 'ratio': ratio}
    audio = VIDEO_MODELS[model]['audio']
    if audio is not None:
        payload['audio'] = audio
    return payload
