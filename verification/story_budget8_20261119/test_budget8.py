"""Affected budget-amendment checks only; no model or GPU execution."""
import copy
import json
import unittest
from pathlib import Path
from budget8 import AUTHORIZATION,SECTIONS,authorize,reserve,validate

HERE=Path(__file__).resolve().parent
BASELINE=json.loads((HERE.parent/'story_option_c_20261116/driver_recovery_call_ledger.json').read_text())

class Budget8Tests(unittest.TestCase):
    def upgraded(self):return authorize(BASELINE,BASELINE,AUTHORIZATION)

    def test_amendment_keeps_all_three_real_calls(self):
        updated=self.upgraded()
        self.assertEqual(updated['historical'],BASELINE['historical'])
        self.assertEqual(updated['new_calls'],BASELINE['new_calls'])
        self.assertEqual(updated['ceiling'],8)
        self.assertEqual(authorize(updated,BASELINE,AUTHORIZATION),updated)

    def test_only_five_ordered_sections_can_reserve(self):
        ledger=self.upgraded()
        for section in SECTIONS:
            ledger=reserve(ledger,BASELINE,section,{'max_tokens':1536})
            ledger['new_calls'][-1]['state']='completed' # CPU fixture, not generated evidence
        self.assertEqual(len(ledger['historical'])+len(ledger['new_calls']),8)
        with self.assertRaises(ValueError):reserve(ledger,BASELINE,'reflection',{'max_tokens':1536})

    def test_no_extra_canary_or_skipped_section(self):
        for section in ('canary','act_1','reflection'):
            with self.assertRaises(ValueError):reserve(self.upgraded(),BASELINE,section,{'max_tokens':1536})

    def test_limits_and_incomplete_predecessor_fail_closed(self):
        for tokens,context,timeout in ((1537,4096,240),(1536,4097,240),(1536,4096,241)):
            with self.assertRaises(ValueError):reserve(self.upgraded(),BASELINE,'foundation',{'max_tokens':tokens},context_tokens=context,timeout_seconds=timeout)
        ledger=reserve(self.upgraded(),BASELINE,'foundation',{'max_tokens':1536})
        ledger['new_calls'][-1]['state']='stopped_with_evidence'
        with self.assertRaises(ValueError):reserve(ledger,BASELINE,'act_1',{'max_tokens':1536})

    def test_no_authorization_or_history_reset(self):
        with self.assertRaises(ValueError):authorize(BASELINE,BASELINE,'unapproved')
        changed=self.upgraded();changed['new_calls']=[]
        with self.assertRaises(ValueError):validate(changed,BASELINE)
        changed=copy.deepcopy(self.upgraded());changed['historical']=[]
        with self.assertRaises(ValueError):validate(changed,BASELINE)

if __name__=='__main__':unittest.main(verbosity=2)
