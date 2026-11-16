"""Reproduction of four new CPU checks already executed once. No model imports/launches.

Recorded in new_runner_cpu_guard_receipt.json; do not rerun on resume without a reason.
Only selected function AST nodes are compiled; runner top-level setup is never executed.
"""
import ast
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    source = ast.parse((HERE/'research_runner_cell.py').read_text())
    functions = [n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in ('budget','run_one')]
    history = json.loads((HERE.parent/'story_t4_20261114/call_summary.json').read_text())
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);out=root/'outputs';out.mkdir();ledger=root/'ledger.json'
        ns={'json':json,'HISTORICAL':history,'LEDGER':ledger,'OUT':out}
        exec(compile(ast.Module(body=functions,type_ignores=[]),'guard-functions-only','exec'),ns)
        def write(rows, old=history):
            ledger.write_text(json.dumps({'ceiling':7,'historical':old,'new_calls':rows}))
        write([])
        assert 7-len(ns['budget']()['historical'])==5
        write([{'id':str(i)} for i in range(5)])
        try:
            ns['run_one']({'id':'sixth'})
        except RuntimeError as error:
            assert 'Seven-call ceiling' in str(error)
        else:
            raise AssertionError('Budget bypass')
        write([{'id':'reserved'}])
        try:
            ns['run_one']({'id':'reserved'})
        except RuntimeError as error:
            assert 'Prior submitted' in str(error)
        else:
            raise AssertionError('Blind retry')
        write([],old=[])
        try:
            ns['budget']()
        except AssertionError:
            pass
        else:
            raise AssertionError('History reset')
    print('Four new guard checks PASS; no model execution')

if __name__=='__main__':
    main()
