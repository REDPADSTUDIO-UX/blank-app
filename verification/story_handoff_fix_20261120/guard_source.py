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
