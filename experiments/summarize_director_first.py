"""Recheck preserved Director outputs; never launches inference or selects a model."""
import hashlib
import json
from pathlib import Path

from redpad_pipeline.kaggle_benchmark import cases, technical_validation

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'verification/director_first_20261113'


def summarize():
    controls = {c['id']: c for c in cases()['cases']}
    rows = []
    for case_id in ('clean_abstention', 'director_criticism'):
        path = EVIDENCE / f'gemma_{case_id}_raw.txt'
        raw = path.read_text()
        # Exact, reversible removal of a single outer Markdown fence, not repair.
        stripped = raw.strip()
        normalized = stripped[7:-3].strip() if stripped.startswith('```json\n') and stripped.endswith('```') else stripped
        (EVIDENCE / f'gemma_{case_id}_derived.json').write_text(normalized + '\n')
        strict = technical_validation(controls[case_id], raw, {'truncated': True})
        content = technical_validation(controls[case_id], normalized, {'truncated': True})
        rows.append({
            'case': case_id, 'raw_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'strict_protocol_validation': strict,
            'derived_content_validation': content,
            'raw_copy_method': 'final assistant Copy message button in existing Chrome Space',
            'ui_response_completed': True, 'finish_reason': None, 'truncation': 'unknown',
            'artistic_acceptance': False, 'independent_human_review': 'pending',
        })
    result = {
        'date': '2026-11-13', 'resumed_checkpoint': '7f665cbbb819a5cb62750d62740160fffed25eea',
        'reported_model': 'google/gemma-3-12b-it',
        'source': 'https://huggingface.co/spaces/huggingface-projects/gemma-3-12b-it',
        'exact_weights_revision': None, 'serving_code_revision_today': None,
        'classification': 'exploratory_hosted_UI_outputs_not_verified_local_inference',
        'hypothesis': 'Owner preferred A to B; test whether hosted Gemma abstains on the clean control that Qwen falsely criticized, without assuming overall superiority.',
        'calls_with_preserved_new_responses': 2,
        'settings': {'system_and_user': 'per-case request JSON', 'displayed_token_input': 1024,
                     'displayed_slider': 1020, 'effective_token_cap': None,
                     'temperature': None, 'seed': None, 'context': None},
        'hardware': {'gpu': None, 'ram': None, 'peak_memory': None},
        'latency_seconds': None,
        'runtime_limitations': 'No server metrics exposed; do not invent inference latency from operator wall time.',
        'controls': rows, 'selected_production_model': None,
        'professional_ready': False,
        'finding': 'Gemma clean control abstains correctly after fence stripping. Defect control quotes the source and identifies the bag access contradiction, but returns category continuity instead of required contract; wording also confuses the cupboard lock with the bag. Both raw responses violate JSON-only protocol. No overall technical or artistic acceptance.',
    }
    (EVIDENCE / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(summarize(), ensure_ascii=False, indent=2))
