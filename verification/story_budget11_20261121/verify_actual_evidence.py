"""CPU-only verification of NEW captured evidence; never import/run the launcher."""
import ast
import base64
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def pure_nodes(path, names):
    tree = ast.parse(path.read_text())
    return [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
            and n.name in names]


def main():
    evidence = json.loads((HERE / 'final_actual.json').read_text())
    old = json.loads((ROOT / 'verification/story_recovery10_20261120/recovery_v2_final_actual.json').read_text())
    ledger = evidence['ledger']
    checks = {}

    def check(name, condition):
        assert condition, name
        checks[name] = 'PASS'

    check('historical_seven_records_and_amendments_unchanged', all(
        ledger[k] == v for k, v in old['ledger'].items() if k != 'ceiling'))
    check('budget11_amendment_binds_exact_baseline',
          ledger['ceiling'] == 11 and ledger['budget11_authorization']['consumed'] == 7
          and ledger['budget11_authorization']['additional_calls'] == 4
          and ledger['budget11_authorization']['baseline_sha256'] == digest(old['ledger']))
    check('exactly_two_new_calls_no_dependent_calls',
          [x['section'] for x in ledger['budget11_calls']] == ['act_1', 'act_2']
          and set(evidence['sections']) == {'act_1', 'act_2'})
    check('foundation_v2_entire_receipt_unchanged', evidence['foundation'] == old['sections']['foundation'])
    check('runtime_source_hash_matches_executed_export',
          hashlib.sha256((HERE / 'runtime_cell.py').read_bytes()).hexdigest() == evidence['runtime_sha256'])
    check('all_three_authorized_artifact_receipts_match',
          len(evidence['bundle']['artifacts']) == 3 and all(
              a['expected_bytes'] == a['actual_bytes'] and a['expected_sha256'] == a['actual_sha256']
              for a in evidence['bundle']['artifacts']))

    guard_names = {'StoryHandoffError', 'require_story_handoff'}
    guard = pure_nodes(HERE / 'runtime_cell.py', guard_names)
    original_guard = pure_nodes(ROOT / 'verification/story_handoff_fix_20261120/guard_source.py', guard_names)
    check('existing_handoff_guard_unchanged',
          [ast.dump(n) for n in guard] == [ast.dump(n) for n in original_guard])
    env = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=guard, type_ignores=[])), '<existing-pure-guard>', 'exec'), env)
    prior = {'foundation': evidence['foundation']['parsed']}
    failures = None
    for section, result in evidence['sections'].items():
        response = json.loads(base64.b64decode(result['raw_http_base64']))
        raw = response['choices'][0]['message']['content']
        check(section + '_raw_http_response_content_hash_identity',
              response == result['response'] and raw == result['raw_content']
              and hashlib.sha256(raw.encode()).hexdigest() == result['raw_content_sha256'])
        reservation = next(x for x in ledger['budget11_calls'] if x['section'] == section)
        check(section + '_request_and_reservation_provenance',
              digest(result['request']) == reservation['payload_sha256']
              and reservation['raw_sha256'] == result['raw_content_sha256']
              and result['case']['prior_sections'] == prior)
        check(section + '_unchanged_generation_limits_and_nontruncation',
              result['context_tokens'] == 4096 and result['output_ceiling'] == 1536
              and result['request']['max_tokens'] == 1536
              and result['request']['seed'] == 117 and result['request']['temperature'] == 0.7
              and result['request']['repeat_penalty'] == 1.08
              and result['request']['chat_template_kwargs'] == {'enable_thinking': False}
              and result['finish_reason'] == 'stop'
              and response['usage']['completion_tokens'] <= 1536)
        parsed = json.loads(raw)
        jsonschema.validate(parsed, result['case']['schema'])
        check(section + '_original_case_schema_valid', True)
        try:
            env['require_story_handoff'](dict(prior, **{section: parsed}))
        except env['StoryHandoffError'] as error:
            failures = error.findings
            check(section + '_exact_failed_handoff_reproduced',
                  result['state'] == 'stopped_with_evidence'
                  and failures == result['handoff_findings'] and len(failures) == 7)
        else:
            check(section + '_completed_handoff_reproduced',
                  result['state'] == 'completed' and result['handoff_validated'] is True)
            prior[section] = parsed

    check('workers_stopped_and_no_compute_process_left',
          all(x['server_stopped'] for x in evidence['sections'].values())
          and evidence['postflight']['processes'] == '')
    # Exercise only the newly reached failed Act2 boundary, without launching anything.
    names = {'digest', 'validate', 'reserve'}
    ledger_env = {'copy': copy, 'json': json, 'hashlib': hashlib,
                  'BASELINE': old['ledger'], 'APPROVED_LEDGER': json.loads((HERE / 'authorized_ledger.json').read_text()),
                  'SECTIONS': ('act_1', 'act_2', 'act_3', 'reflection')}
    exec(compile(ast.fix_missing_locations(ast.Module(body=pure_nodes(HERE / 'runtime_cell.py', names), type_ignores=[])), '<pure-budget-guard>', 'exec'), ledger_env)
    try:
        ledger_env['reserve'](ledger, old['ledger'], 'act_3', {'max_tokens': 1536})
    except ValueError as error:
        check('failed_act2_blocks_act3_reservation_without_call',
              'failed predecessor' in str(error))
    else:
        raise AssertionError('Act3 reservation must fail')

    receipt = {
        'scope': 'New actual evidence CPU replay only; no model/runtime/GPU/network execution',
        'checks': checks, 'check_groups_passed': len(checks),
        'previous_model_calls': 7, 'new_model_calls': 2, 'consumed': 9, 'ceiling': 11,
        'remaining_arithmetic': 2, 'remaining_allocation': ['act_3', 'reflection'],
        'remaining_calls_eligible_now': 0, 'act2_retry_authorized': False,
        'act2_finding_counts': dict(Counter(x['code'] for x in failures)),
        'full_story_generated': False, 'complete_story_15_criterion_qc': 'NOT RUN',
        'independent_human_review': 'PENDING', 'producer_owner_acceptance': 'PENDING',
        'production_ready': False,
    }
    (HERE / 'actual_evidence_validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
