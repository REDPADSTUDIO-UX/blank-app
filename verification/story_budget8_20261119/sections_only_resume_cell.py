# Section-only continuation. No canary, downloads, CUDA diagnostics or production route.
import base64,hashlib,json,os,re,signal,subprocess,threading,time
from pathlib import Path
import psutil
BASE=Path('/content/redpad_story_t4_20261114')
RESEARCH=BASE/'option_c_approved'; OUT=RESEARCH/'outputs'; LEDGER=RESEARCH/'call_ledger.json'
assert (BASE/'Qwen3.5-9B-Q4_K_M.gguf').is_file(), 'Approved cached model missing. Downloads are not authorized.'
receipt=json.loads((RESEARCH/'bundle_ready.json').read_text())
binding=json.loads((RESEARCH/'driver_binding_verified.json').read_text())
assert receipt['status']=='BUNDLE_VERIFIED' and receipt['model']['revision']=='3885219b6810b007914f3a7950a8d1b469d598a5'
assert receipt['model']['sha256']=='03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'
assert binding['status']=='VERIFIED_NO_MODEL_LOAD' and binding['driver_directory']=='/usr/lib64-nvidia'
WORKER_ENV=binding['worker_env']; SELECTED_DEVICE=binding['selected_device']; binary=Path(receipt['binary'])
assert re.fullmatch(r'CUDA[0-9]+',SELECTED_DEVICE)
assert WORKER_ENV['LD_LIBRARY_PATH']==receipt['runtime_libraries']+':/usr/lib64-nvidia'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5'
canary=json.loads((OUT/'driverbound_canary_v1.json').read_text())
assert canary['state']=='completed' and canary['finish_reason']=='stop'
assert hashlib.sha256(canary['raw_content'].encode()).hexdigest()=='1ff2f6a5c4173cdd1841c1ac043f48ca3ac3eb8586ebe1bf45a9aa418e76b7ff'

"""Explicit owner-scoped budget amendment. No model/runtime/network operations."""
import copy
import hashlib
import json

AUTHORIZATION='owner-story-total8-five-sections-20261119'
SECTIONS=('foundation','act_1','act_2','act_3','reflection')

"""Research-only structural handoff guard, embedded into the standalone runner.
No prose repair, ID aliasing, inference, ledger mutation or artistic acceptance.
"""

class StoryHandoffError(ValueError):
    def __init__(self, findings):
        self.findings = findings
        super().__init__('STORY_HANDOFF_INVALID: ' + '; '.join(
            f"{f['path']}: {f['code']}" for f in findings))


def require_story_handoff(parts):
    """Validate a completed prefix without modifying any supplied artifact.
    JSON schema is checked separately. These checks enforce existing prompt
    identities and the cross-field rules of the full Story structural validator.
    A pass does not establish semantic knowledge or professional quality.
    """
    findings = []
    def issue(path, code):
        findings.append({'path': path, 'code': code, 'repair_applied': False})
    if parts == {}:
        return
    order = ('foundation', 'act_1', 'act_2', 'act_3', 'reflection')
    if not isinstance(parts, dict) or tuple(parts) != order[:len(parts)]:
        raise StoryHandoffError([{'path': '$', 'code': 'section_prefix_invalid', 'repair_applied': False}])
    foundation = parts['foundation']
    try:
        ids = [c['id'] for c in foundation['characters']]
        initial = foundation['initial_knowledge']
        if len(ids) != 2 or set(ids) != {'N', 'H'}:
            issue('foundation.characters', 'expected_exact_N_H_ids')
        if set(initial) != set(ids):
            issue('foundation.initial_knowledge', 'character_keys_mismatch')
        known = {k: set(v) for k, v in initial.items()}
        seen, plants, paid, last = set(), set(), set(), None
        for act in range(1, 4):
            name = f'act_{act}'
            if name not in parts:
                break
            rows = parts[name]
            if not isinstance(rows, list) or len(rows) != 4:
                issue(name, 'expected_four_beats')
                continue
            for offset, beat in enumerate(rows, 1):
                path = f'{name}[{offset - 1}]'
                bid = beat['id']
                if bid != f'B{(act - 1) * 4 + offset}' or bid in seen or beat['act'] != act:
                    issue(path + '.id', 'beat_identity_or_act_invalid')
                if beat['actor'] not in ids:
                    issue(path + '.actor', 'unknown_character')
                if (beat['cause'] != 'brief' if not seen else beat['cause'] not in seen):
                    issue(path + '.cause', 'earlier_causal_reference_required')
                if last is not None and beat['before'] != last:
                    issue(path + '.before', 'predecessor_state_mismatch')
                if set(beat['before']) != set(beat['after']) or beat['before'] == beat['after']:
                    issue(path + '.after', 'tracked_state_change_invalid')
                for field in ('requires', 'learns'):
                    for char, facts in beat[field].items():
                        if char not in known:
                            issue(path + '.' + field + '.' + char, 'unknown_knowledge_character')
                        elif field == 'requires' and not set(facts) <= known[char]:
                            issue(path + '.requires.' + char, 'knowledge_not_established')
                for payoff in beat['payoffs']:
                    if payoff not in plants or payoff in paid:
                        issue(path + '.payoffs', 'earlier_unresolved_plant_required')
                    paid.add(payoff)
                for plant in beat['plants']:
                    if plant in plants:
                        issue(path + '.plants', 'duplicate_plant')
                    plants.add(plant)
                if not set(beat['emotion_setups']) <= seen:
                    issue(path + '.emotion_setups', 'earlier_emotional_reference_required')
                for char, facts in beat['learns'].items():
                    if char in known:
                        known[char].update(facts)
                seen.add(bid)
                last = beat['after']
        if 'reflection' in parts:
            for row in parts['reflection']['self_critique']:
                if row['beat'] not in seen:
                    issue('reflection.self_critique', 'unknown_beat')
    except (KeyError, TypeError, AttributeError, ValueError):
        issue('$', 'malformed_handoff_shape')
    if findings:
        raise StoryHandoffError(findings)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate(ledger,baseline):
    if baseline['ceiling']!=7 or len(baseline['historical'])!=2 or len(baseline['new_calls'])!=1:
        raise ValueError('Exact three-consumed-call baseline required')
    if baseline['new_calls'][0]['id']!='driverbound_canary_v1' or baseline['new_calls'][0]['state']!='completed':
        raise ValueError('Successful genuine canary baseline required')
    if ledger['ceiling']!=8 or ledger.get('authorization')!=AUTHORIZATION:
        raise ValueError('This benchmark requires the exact explicit ceiling-eight authorization')
    if ledger['historical']!=baseline['historical'] or ledger['new_calls'][:1]!=baseline['new_calls']:
        raise ValueError('Historical calls or completed canary changed')
    extra=ledger['new_calls'][1:]
    if len(extra)>5:
        raise ValueError('Five additional calls exhausted')
    for section,entry in zip(SECTIONS,extra):
        if entry['section']!=section or entry['id']!='driverbound_'+section+'_v1':
            raise ValueError('Mandatory section order/attempt identity changed')
    return extra

def authorize(ledger,baseline,authorization):
    if authorization!=AUTHORIZATION:
        raise ValueError('Missing exact owner budget authorization')
    if ledger==baseline:
        upgraded=copy.deepcopy(ledger)
        upgraded.update(ceiling=8,authorization=AUTHORIZATION,
          amendment={'previous_ceiling':7,'revised_ceiling':8,'consumed_at_authorization':3,
                     'baseline_sha256':digest(baseline),'scope':'Five mandatory Story sections only'})
    else:
        upgraded=copy.deepcopy(ledger)
    validate(upgraded,baseline)
    return upgraded

def reserve(ledger,baseline,section,payload,*,context_tokens=4096,timeout_seconds=240):
    extra=validate(ledger,baseline)
    if len(extra)>=5:
        raise ValueError('Eight-call ceiling exhausted')
    if section!=SECTIONS[len(extra)]:
        raise ValueError('Cannot skip, repeat or substitute mandatory sections')
    if any(entry['state']!='completed' for entry in extra):
        raise ValueError('Required previous section is incomplete; inspect preserved failure')
    if payload.get('max_tokens')!=1536 or context_tokens!=4096 or timeout_seconds!=240:
        raise ValueError('Per-call token/context/time limits must remain unchanged')
    result=copy.deepcopy(ledger)
    result['new_calls'].append({'id':'driverbound_'+section+'_v1','section':section,
      'state':'submitted','payload_sha256':digest(payload)})
    return result

BASELINE=json.loads('{"ceiling": 7, "historical": [{"case": "canary", "state": "completed", "finish_reason": "stop", "usage": {"completion_tokens": 124, "prompt_tokens": 127, "total_tokens": 251, "prompt_tokens_details": {"cached_tokens": 0}}, "load_seconds": 71.12815384999999, "generation_seconds": 70.35668729099984, "total_seconds": 144.57331105899993, "sampled_device_used_mib": 5231, "sampled_server_rss_bytes": 1621516288, "offload_lines": ["0.24.336.465 I load_tensors: offloaded 33/33 layers to GPU", "0.24.336.476 I load_tensors:        CUDA0 model buffer size =  4861.28 MiB"], "template_sha256": "051a136079635359b9a55cc2fac4dacf3e3be05127ce7be999a6f73b86058306", "raw_sha256": "a9dd98d39e91e1eb4b794e6b5626878a5af19408aa294b762d26422f49541d5d", "server_stopped": true, "timings": {"cache_n": 0, "prompt_n": 127, "prompt_ms": 65937.343, "prompt_per_token_ms": 519.1916771653542, "prompt_per_second": 1.9260709367679558, "predicted_n": 124, "predicted_ms": 4413.226, "predicted_per_token_ms": 35.87988617886179, "predicted_per_second": 27.870768458266134}}, {"case": "foundation", "state": "stopped_with_evidence", "finish_reason": "length", "usage": {"completion_tokens": 1536, "prompt_tokens": 1135, "total_tokens": 2671, "prompt_tokens_details": {"cached_tokens": 0}}, "load_seconds": 4.228568951999932, "generation_seconds": 74.07867742000008, "total_seconds": 78.63082022799995, "sampled_device_used_mib": 5249, "sampled_server_rss_bytes": 1443651584, "offload_lines": ["0.02.191.595 I load_tensors: offloaded 33/33 layers to GPU", "0.02.191.605 I load_tensors:        CUDA0 model buffer size =  4861.28 MiB"], "template_sha256": "3cf9abff64e0769fe7ff6ac526c9feb1d03bad2e7533cee350af39e86d083cc4", "raw_sha256": "08ec7e2ada9d680cdfad3a1ada64f744cc1fb9c5331a966efd892f02770a2661", "server_stopped": true, "timings": {"cache_n": 0, "prompt_n": 1135, "prompt_ms": 1627.216, "prompt_per_token_ms": 1.4336704845814976, "prompt_per_second": 697.5103489641203, "predicted_n": 1536, "predicted_ms": 72443.023, "predicted_per_token_ms": 47.19415179153094, "predicted_per_second": 21.18906606092349}}], "new_calls": [{"id": "driverbound_canary_v1", "state": "completed", "payload_sha256": "241487f5015374a0b8da8d09e35db998b339a35a96047bead90f54f09c6d4bf2", "finish_reason": "stop", "raw_sha256": "1ff2f6a5c4173cdd1841c1ac043f48ca3ac3eb8586ebe1bf45a9aa418e76b7ff"}]}')
BUNDLE=json.loads('{"instructions": ["Write original natural Bengali story prose from the supplied existing professional brief. Do not copy another drama or imitate a living writer.", "Ask a central dramatic question requiring a costly protagonist decision. Father supports the job but fears solitude; daughter’s independence is not selfishness.", "Give each major character want, need, fear, contradiction, relationship, internal conflict, observable behavior and emotional change.", "Every beat changes information, relationships, emotion, stakes, goals or options through a credible cause. Track character knowledge and possessions.", "Earn at least two subtle emotional moments through earlier setup, small human actions and consequences; tragedy or speeches are not automatic emotion.", "Include one motivated humorous moment from personality, irony, awkwardness or relationship; avoid unrelated jokes.", "Use fair clues and information control for one earned reveal; escalate choices and consequences rather than repeat scenes.", "Use visible action, location or sound for filmability. Flag cultural and economic specifics as hypotheses unless supplied verified sources establish them.", "Return only the artifact contract. Self-critique is a proposal, never an independent professional score. Preserve exact owner locks and untargeted records."], "contracts": {"foundation": {"type": "object", "additionalProperties": false, "required": ["assumptions", "characters", "conflict_stakes", "dramatic_question", "initial_knowledge", "logline", "relationship_dynamics", "schema_version", "theme", "unresolved_questions"], "properties": {"assumptions": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "characters": {"type": "array", "minItems": 2, "maxItems": 4, "items": {"type": "object", "additionalProperties": false, "required": ["id", "want", "need", "fear", "contradiction", "relationship", "internal_conflict", "behavior", "emotional_change", "name", "biography"], "properties": {"id": {"type": "string", "minLength": 1, "maxLength": 2500}, "want": {"type": "string", "minLength": 1, "maxLength": 2500}, "need": {"type": "string", "minLength": 1, "maxLength": 2500}, "fear": {"type": "string", "minLength": 1, "maxLength": 2500}, "contradiction": {"type": "string", "minLength": 1, "maxLength": 2500}, "relationship": {"type": "string", "minLength": 1, "maxLength": 2500}, "internal_conflict": {"type": "string", "minLength": 1, "maxLength": 2500}, "behavior": {"type": "string", "minLength": 1, "maxLength": 2500}, "emotional_change": {"type": "string", "minLength": 1, "maxLength": 2500}, "name": {"type": "string", "minLength": 1, "maxLength": 1500}, "biography": {"type": "string", "minLength": 1, "maxLength": 1500}}}}, "conflict_stakes": {"type": "string", "minLength": 1, "maxLength": 2500}, "dramatic_question": {"type": "string", "minLength": 1, "maxLength": 2500}, "initial_knowledge": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "logline": {"type": "string", "minLength": 1, "maxLength": 2500}, "relationship_dynamics": {"type": "string", "minLength": 1, "maxLength": 2500}, "schema_version": {"const": 1}, "theme": {"type": "string", "minLength": 1, "maxLength": 2500}, "unresolved_questions": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}}, "act_1": {"type": "array", "minItems": 4, "maxItems": 6, "items": {"type": "object", "additionalProperties": false, "required": ["id", "act", "actor", "goal", "choice", "cause", "consequence", "action", "location", "sound", "emotion", "before", "after", "requires", "learns", "plants", "payoffs", "emotion_setups", "subtle_emotion", "humor", "humor_motivation"], "properties": {"id": {"type": "string", "minLength": 1, "maxLength": 2500}, "act": {"const": 1}, "actor": {"type": "string", "minLength": 1, "maxLength": 2500}, "goal": {"type": "string", "minLength": 1, "maxLength": 2500}, "choice": {"type": "string", "minLength": 1, "maxLength": 2500}, "cause": {"type": "string", "minLength": 1, "maxLength": 2500}, "consequence": {"type": "string", "minLength": 1, "maxLength": 2500}, "action": {"type": "string", "minLength": 1, "maxLength": 2500}, "location": {"type": "string", "minLength": 1, "maxLength": 2500}, "sound": {"type": "string", "minLength": 1, "maxLength": 2500}, "emotion": {"type": "string", "minLength": 1, "maxLength": 2500}, "before": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "after": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "requires": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "learns": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "plants": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "payoffs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "emotion_setups": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "subtle_emotion": {"type": "boolean"}, "humor": {"type": "string", "maxLength": 600}, "humor_motivation": {"type": "string", "maxLength": 600}}}}, "act_2": {"type": "array", "minItems": 4, "maxItems": 6, "items": {"type": "object", "additionalProperties": false, "required": ["id", "act", "actor", "goal", "choice", "cause", "consequence", "action", "location", "sound", "emotion", "before", "after", "requires", "learns", "plants", "payoffs", "emotion_setups", "subtle_emotion", "humor", "humor_motivation"], "properties": {"id": {"type": "string", "minLength": 1, "maxLength": 2500}, "act": {"const": 2}, "actor": {"type": "string", "minLength": 1, "maxLength": 2500}, "goal": {"type": "string", "minLength": 1, "maxLength": 2500}, "choice": {"type": "string", "minLength": 1, "maxLength": 2500}, "cause": {"type": "string", "minLength": 1, "maxLength": 2500}, "consequence": {"type": "string", "minLength": 1, "maxLength": 2500}, "action": {"type": "string", "minLength": 1, "maxLength": 2500}, "location": {"type": "string", "minLength": 1, "maxLength": 2500}, "sound": {"type": "string", "minLength": 1, "maxLength": 2500}, "emotion": {"type": "string", "minLength": 1, "maxLength": 2500}, "before": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "after": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "requires": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "learns": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "plants": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "payoffs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "emotion_setups": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "subtle_emotion": {"type": "boolean"}, "humor": {"type": "string", "maxLength": 600}, "humor_motivation": {"type": "string", "maxLength": 600}}}}, "act_3": {"type": "array", "minItems": 4, "maxItems": 6, "items": {"type": "object", "additionalProperties": false, "required": ["id", "act", "actor", "goal", "choice", "cause", "consequence", "action", "location", "sound", "emotion", "before", "after", "requires", "learns", "plants", "payoffs", "emotion_setups", "subtle_emotion", "humor", "humor_motivation"], "properties": {"id": {"type": "string", "minLength": 1, "maxLength": 2500}, "act": {"const": 3}, "actor": {"type": "string", "minLength": 1, "maxLength": 2500}, "goal": {"type": "string", "minLength": 1, "maxLength": 2500}, "choice": {"type": "string", "minLength": 1, "maxLength": 2500}, "cause": {"type": "string", "minLength": 1, "maxLength": 2500}, "consequence": {"type": "string", "minLength": 1, "maxLength": 2500}, "action": {"type": "string", "minLength": 1, "maxLength": 2500}, "location": {"type": "string", "minLength": 1, "maxLength": 2500}, "sound": {"type": "string", "minLength": 1, "maxLength": 2500}, "emotion": {"type": "string", "minLength": 1, "maxLength": 2500}, "before": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "after": {"type": "object", "minProperties": 1, "maxProperties": 30, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 2500}}, "requires": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "learns": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}}, "plants": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "payoffs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "emotion_setups": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true, "maxItems": 30}, "subtle_emotion": {"type": "boolean"}, "humor": {"type": "string", "maxLength": 600}, "humor_motivation": {"type": "string", "maxLength": 600}}}}, "reflection": {"type": "object", "additionalProperties": false, "required": ["ending_consequence", "filmability", "self_critique", "treatment"], "properties": {"ending_consequence": {"type": "string", "minLength": 1, "maxLength": 2500}, "filmability": {"type": "string", "minLength": 1, "maxLength": 2500}, "self_critique": {"type": "array", "minItems": 1, "maxItems": 15, "items": {"type": "object", "additionalProperties": false, "required": ["beat", "weakness", "suggestion"], "properties": {"beat": {"type": "string", "minLength": 1, "maxLength": 2500}, "weakness": {"type": "string", "minLength": 1, "maxLength": 2500}, "suggestion": {"type": "string", "minLength": 1, "maxLength": 2500}}}}, "treatment": {"type": "string", "minLength": 1, "maxLength": 2500}}}}, "brief": "ফিরতি টিকিট: ঢাকার কাঁঠালবাগানের ভাড়া বাসায় নীরা (২৭) রাজশাহীতে চাকরি নিতে চায়। বাবা হাসান (৫৮), দর্জি, মেয়ের যাওয়া চান কিন্তু একা থাকার ভয় লুকান। সকালে তিনি ব্যাগের হাতল সারান, বাসের টিকিট লাল টিনের বাক্সে রাখেন। নীরা টিকিট দেখার আগে তার কেনার কথা জানে না। ঘরে পূর্বে জানলা, পশ্চিমে প্রবেশদ্বার, উত্তরে রান্নাঘর। একই সকাল, একই পোশাক ও একটিমাত্র চাবি। পারিবারিক যত্ন কাজে ফুটবে, কৃত্রিম ত্যাগ বা অচেনা উদ্ধারকারী নয়।", "rubric": [{"id": "story.creative.1", "criterion": "originality", "question": "Distinct choices and situations; no originality guarantee without comparative review", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.2", "criterion": "causal_logic", "question": "Each turn follows an established action and consequence", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.3", "criterion": "character_agency", "question": "Protagonist chooses between costly alternatives", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.4", "criterion": "psychological_depth", "question": "Wants conflict with fears and observable behavior", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.5", "criterion": "relationship_credibility", "question": "Both father and daughter have defensible competing needs", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.6", "criterion": "emotional_authenticity", "question": "Earlier investment and restrained action earn emotional moments", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.7", "criterion": "organic_humor", "question": "Humor grows from a specific personality or situation", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.8", "criterion": "bangladesh_authenticity", "question": "Social details are specific, attributed where factual, and avoid stereotypes", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.9", "criterion": "hook_suspense", "question": "Fairly controlled information motivates curiosity", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.10", "criterion": "escalation", "question": "Choices narrow or costs increase instead of repetitive conflict", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.11", "criterion": "setup_payoff", "question": "Earlier visible plants motivate later consequences", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.12", "criterion": "ending_quality", "question": "Ending follows choices and changes both characters without a formulaic rescue", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.13", "criterion": "filmability", "question": "Action, location or sound communicates each major beat", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.14", "criterion": "consistency", "question": "Knowledge, timeline, possessions and locked facts remain coherent", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}, {"id": "story.creative.15", "criterion": "audience_engagement", "question": "Engagement is a reviewer hypothesis, not invented audience analytics", "anchors": {"1": "Cited beats show a substantial unresolved weakness", "3": "Cited evidence supports the aim with specific weaknesses remaining", "5": "Independent qualified reviewer supports convincing execution with exact beat evidence"}, "required_medium": "text"}], "checkpoint": "4d93a8c83e32ca17e9611797c10737ab9d76bed5"}')

previous_bytes=LEDGER.read_bytes()
previous=json.loads(previous_bytes)
updated=authorize(previous,BASELINE,AUTHORIZATION)
if previous!=updated:
 backup=RESEARCH/'call_ledger.before_budget8.json'
 if backup.exists():assert backup.read_bytes()==previous_bytes
 else:
  with backup.open('xb') as f:f.write(previous_bytes)
 temporary=RESEARCH/'call_ledger.budget8.tmp'
 with temporary.open('x') as f:
  json.dump(updated,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 temporary.replace(LEDGER)
def budget():
 value=json.loads(LEDGER.read_text());validate(value,BASELINE);return value
SOURCE_PATHS=[Path(receipt['model_path']),binary,RESEARCH/'bundle_ready.json',RESEARCH/'driver_binding_verified.json',OUT/'driverbound_canary_v1.json']
def fingerprint(p):
 assert p.is_file() and not any(q.is_symlink() for q in (p,*p.parents))
 s=p.stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
SOURCE_STATE={str(p):fingerprint(p) for p in SOURCE_PATHS}
def section_eligibility():
 assert SOURCE_STATE=={str(p):fingerprint(p) for p in SOURCE_PATHS},'Cached source changed'
 assert not any(' /content/drive ' in line or 'drivefs' in line.lower() for line in Path('/proc/self/mountinfo').read_text().splitlines())
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.free','--format=csv,noheader,nounits'],text=True,timeout=12).strip()
 assert 'T4' in gpu and int(gpu.split(',')[-1])>10000
 mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k=='MemAvailable'}
 assert mem['MemAvailable']>8*2**30
url='http://127.0.0.1:18082'

def http(path,payload=None,timeout=10):
 req=urllib.request.Request(url+path,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return r.read(4*1024*1024)

def run_one(case):
 file=OUT/(case['id']+'.json')
 if file.exists():raise RuntimeError('Existing attempt: inspect and never blindly repeat '+case['id'])
 ledger=budget()
 if len(ledger['historical'])+len(ledger['new_calls'])>=8:raise RuntimeError('Eight-call ceiling including all three previously consumed calls')
 extra=validate(ledger,BASELINE)
 if case.get('section')!=SECTIONS[len(extra)]:raise RuntimeError('Only the next mandatory section is authorized')
 if any(e['state']!='completed' for e in extra):raise RuntimeError('Required prior section incomplete')
 require_story_handoff(case.get('prior_sections',{}))
 section_eligibility()
 if any(x['id']==case['id'] for x in ledger['new_calls']):raise RuntimeError('Prior submitted attempt; never retry blindly')
 server=None;log=RESEARCH/(case['id']+'.server.log');started=time.monotonic()
 state={'case':case,'installation':receipt,'state':'preparing','human_review':'pending','production_approved':False,'automatic_retries':0,'variant':'option_c_driverbound_schema_v1','historical_calls':2,'kernel_isolation_verified':False}
 try:
  with log.open('w') as f:
   server=subprocess.Popen([str(binary),'-m',receipt['model_path'],'-ngl','99','--device',SELECTED_DEVICE,'--no-warmup','-fa','off','-b','128','-ub','128','-tb','2','-lv','4','-c','4096','-np','1','-t','2','--host','127.0.0.1','--port','18082','--jinja','--no-webui'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=WORKER_ENV,cwd=RESEARCH)
  deadline=time.monotonic()+180
  while True:
   if server.poll() is not None:raise RuntimeError('Server exit: '+log.read_text()[-2500:])
   try:
    if json.loads(http('/health'))['status']=='ok':break
   except Exception:pass
   if time.monotonic()>deadline:raise RuntimeError('Model load timeout')
   time.sleep(1)
  apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
  assert any(x.split(',')[0].strip()==str(server.pid) and int(x.split(',')[1])>4000 for x in apps.splitlines()),apps
  state.update(load_seconds=time.monotonic()-started,owned_gpu_process=apps,offload_lines=[l for l in log.read_text().splitlines() if 'offloaded' in l or 'CUDA0 model buffer' in l])
  messages=[{'role':'system','content':case['system']},{'role':'user','content':case['prompt']}]
  template=json.loads(http('/apply-template',{'messages':messages,'chat_template_kwargs':{'enable_thinking':False}}))
  text=template['prompt']
  tokens=json.loads(http('/tokenize',{'content':text,'add_special':False}))['tokens']
  state.update(exact_prompt_tokens=len(tokens),context_tokens=4096,output_ceiling=case['max_new_tokens'],template_sha256=hashlib.sha256(text.encode()).hexdigest())
  assert len(tokens)+case['max_new_tokens']<=4096,'Token feasibility fails; no generation submitted'
  payload={'messages':messages,'max_tokens':case['max_new_tokens'],'temperature':case.get('temperature',0.7),'seed':117,'stream':False,'chat_template_kwargs':{'enable_thinking':False},'cache_prompt':False}
  if case.get('schema'):
   import copy
   constrained=copy.deepcopy(case['schema'])
   if case.get('section')=='foundation':
    constrained['properties']['assumptions']['maxItems']=4
    constrained['properties']['unresolved_questions']['maxItems']=4
    constrained['properties']['characters']['maxItems']=2
   payload['response_format']={'type':'json_schema','schema':constrained}
  payload['repeat_penalty']=1.08
  ledger=reserve(ledger,BASELINE,case['section'],payload,context_tokens=4096,timeout_seconds=240)
  LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
  state.update(state='submitted',request=payload)
  file.write_text(json.dumps(state,ensure_ascii=False,indent=2))
  rss=[];gpu=[];stop=threading.Event()
  def monitor():
   while not stop.wait(1):
    try:
     rss.append(psutil.Process(server.pid).memory_info().rss)
     gpu.append(int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True,timeout=5).strip()))
    except Exception:pass
  thread=threading.Thread(target=monitor,daemon=True);thread.start();t=time.monotonic()
  try:
   raw=http('/v1/chat/completions',payload,240);body=json.loads(raw);choice=body['choices'][0];content=choice['message'].get('content','')
   state.update(state='completed',raw_http_base64=base64.b64encode(raw).decode(),response=body,raw_content=content,raw_content_sha256=hashlib.sha256(content.encode()).hexdigest(),finish_reason=choice['finish_reason'])
   (OUT/(case['id']+'.raw.txt')).write_bytes(content.encode())
  finally:
   stop.set();thread.join(timeout=6)
   state.update(generation_seconds=time.monotonic()-t,peak_sampled_server_rss_bytes=max(rss,default=None),peak_sampled_device_used_mib=max(gpu,default=None),memory_scope='1s whole device sampling, includes baseline; not allocator peak')
  if state['finish_reason']!='stop':raise RuntimeError('Truncated output; stop under existing benchmark ceiling')
  parsed=json.loads(content)
  if case.get('schema'):
   import jsonschema
   jsonschema.validate(parsed,case['schema'])
  state['schema_validated']=True
  require_story_handoff(dict(case['prior_sections'],**{case['section']:parsed}))
  state['handoff_validated']=True
  state['parsed']=parsed
 except Exception as e:
  state.update(error_type=type(e).__name__,error=str(e),state='stopped_with_evidence')
  if isinstance(e,StoryHandoffError):state['handoff_findings']=e.findings
 finally:
  if server is not None and server.poll() is None:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait(timeout=5)
  state.update(total_seconds=time.monotonic()-started,server_stopped=server is None or server.poll() is not None)
  file.write_text(json.dumps(state,ensure_ascii=False,indent=2))
  ledger=budget()
  for entry in ledger['new_calls']:
   if entry['id']==case['id']:entry.update(state=state['state'],finish_reason=state.get('finish_reason'),raw_sha256=state.get('raw_content_sha256'))
  LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
  print('REDPAD_RESULT='+json.dumps({k:v for k,v in state.items() if k not in ('raw_http_base64','request','case','response','installation')},ensure_ascii=False),flush=True)
 if state['state']!='completed':raise RuntimeError('Stop: '+state.get('error','unknown'))
 return state

def generate_section(name):
 if name not in SECTIONS:raise StoryHandoffError([{'path':'section','code':'unknown_section','repair_applied':False}])
 canary=json.loads((OUT/'driverbound_canary_v1.json').read_text())
 assert canary['state']=='completed' and canary['finish_reason']=='stop'
 prior={}
 for n in ('foundation','act_1','act_2','act_3','reflection'):
  if n==name:break
  result=json.loads((OUT/('driverbound_'+n+'_v1.json')).read_text())
  assert result['state']=='completed' and result['finish_reason']=='stop'
  prior[n]=result['parsed']
 require_story_handoff(prior)
 foundation=prior.get('foundation')
 beats=[b for n in ('act_1','act_2','act_3') for b in prior.get(n,[])]
 context={}
 if foundation:
  context['foundation']={k:foundation[k] for k in ('logline','dramatic_question','characters','initial_knowledge')}
 if beats:
  context['prior_beats']=[{k:b[k] for k in ('id','choice','consequence','plants','payoffs','learns')} for b in beats]
  context['last_state']=beats[-1]['after']
  known={k:list(v) for k,v in foundation['initial_knowledge'].items()}
  for b in beats:
   for k,v in b['learns'].items():known[k]=list(dict.fromkeys(known[k]+v))
  context['known']=known
 if name=='reflection':
  # Actual generated actions/consequences only; no authored story substitution.
  context={'logline':foundation['logline'],'characters':[{k:c[k] for k in ('id','name','want','fear')} for c in foundation['characters']], 'actual_beats':[{k:b[k] for k in ('id','action','choice','consequence','emotion')} for b in beats]}
 details={
 'foundation':'Only foundation. Exactly two characters N and H, Nira and Hasan. Be concise: each character value 2-5 Bengali words. Give initial knowledge as short ASCII fact IDs with meaning apparent from the brief. N must NOT initially know ticket bought/hidden. At most FOUR distinct assumptions and FOUR unresolved questions. Never repeat an assumption. No plot event has yet happened beyond the supplied brief. Do not reveal how the story resolves.',
 'act_1':'Exactly FOUR short beats B1-B4 act=1. Start the same morning with bag repair, concealed ticket and a credible costly choice. First cause=brief; later cause must cite earlier beat. No knowledge without shown discovery. Establish humor and emotional investment. Preserve time, room geography, one key and clothes.',
 'act_2':'Exactly FOUR short beats B5-B8 act=2. Continue exact prior state/knowledge. Each choice creates a new consequence; escalate cost. Earn discovery before reaction. Develop an earlier plant; no stranger, illness, sudden money or repetitive obstruction.',
 'act_3':'Exactly FOUR short beats B9-B12 act=3. Resolve same-morning choices credibly without claiming arrival in another city. Earn an ending through both characters actions. Pay off an earlier unresolved plant; include two subtle_emotion=true beats referencing earlier emotional setup IDs if not already present. No miraculous reconciliation.',
 'reflection':'Only reflection based on actual supplied beats. Write treatment as complete flowing Bengali story from opening to ending, roughly 160-220 Bengali words, not instructions or future plan. ending_consequence states exact changed relationship. filmability is practical. self_critique cites an actual beat ID and genuine weakness. Never claim acceptance or scores.'}
 system='\n'.join(BUNDLE['instructions'])+'\nYou are generating one bounded section of ONE story. JSON only, minified, no markdown, no thinking. All required schema fields must be present. Be brief to finish within 1536 output tokens. No scores or human-review claims.'
 if name.startswith('act_'):
  system+=' Use concise Bengali phrases: goal/choice/consequence/action/emotion each 2-5 words, location/sound 1-2 words. Track before/after with ONE compact progress key and copy exact previous after to next before. Knowledge facts use short ASCII IDs; no needless new facts. Empty requires/learns maps when no knowledge change; empty plants/payoffs/emotion_setups arrays when inapplicable. humor/humor_motivation empty unless motivated. Exactly 4 beats. This is a compact causal treatment, not dialogue.'
 prompt='ORIGINAL BRIEF (unchanged):\n'+BUNDLE['brief']+'\nSECTION: '+name+'\n'+details[name]+'\nACTUAL PRIOR GENERATED CONTEXT:\n'+json.dumps(context,ensure_ascii=False,separators=(',',':'))+'\nEXACT SECTION SCHEMA:\n'+json.dumps(BUNDLE['contracts'][name],separators=(',',':'))
 return run_one({'id':'driverbound_'+name+'_v1','section':name,'prior_sections':prior,'system':system,'prompt':prompt,'max_new_tokens':1536,'schema':BUNDLE['contracts'][name]})
print('SECTION_ONLY_BUDGET8_READY: no generation submitted; call generate_section for the next mandatory section only.')
