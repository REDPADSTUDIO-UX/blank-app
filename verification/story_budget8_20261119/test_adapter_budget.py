"""Affected runner boundary tests; stop before any runtime or model operation."""
import ast
import json
import tempfile
import unittest
from pathlib import Path
from budget8 import AUTHORIZATION,SECTIONS,authorize,reserve,validate

HERE=Path(__file__).resolve().parent
BASELINE=json.loads((HERE.parent/'story_option_c_20261116/driver_recovery_call_ledger.json').read_text())

class AdapterBudgetTests(unittest.TestCase):
    def fixture(self,sections):
        ledger=authorize(BASELINE,BASELINE,AUTHORIZATION)
        for section in SECTIONS[:sections]:
            ledger=reserve(ledger,BASELINE,section,{'max_tokens':1536})
            ledger['new_calls'][-1]['state']='completed' # Explicit CPU fixture only
        return ledger

    def execute_guard(self,ledger,section):
        tree=ast.parse((HERE/'sections_only_resume_cell.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_one')
        with tempfile.TemporaryDirectory() as folder:
            def stop_before_runtime():raise RuntimeError('ELIGIBILITY_SENTINEL_NO_MODEL')
            scope={'OUT':Path(folder),'budget':lambda:ledger,'BASELINE':BASELINE,
              'SECTIONS':SECTIONS,'validate':validate,'section_eligibility':stop_before_runtime}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'runner-guard-only','exec'),scope)
            scope['run_one']({'id':'driverbound_'+section+'_v1','section':section})

    def test_eighth_total_call_reaches_eligibility_without_launch(self):
        with self.assertRaisesRegex(RuntimeError,'ELIGIBILITY_SENTINEL_NO_MODEL'):
            self.execute_guard(self.fixture(4),'reflection')

    def test_ninth_total_call_stops_before_eligibility(self):
        with self.assertRaisesRegex(RuntimeError,'Eight-call ceiling'):
            self.execute_guard(self.fixture(5),'reflection')

if __name__=='__main__':unittest.main(verbosity=2)
