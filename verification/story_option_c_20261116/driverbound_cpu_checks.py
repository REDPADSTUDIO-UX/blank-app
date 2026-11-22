"""Three affected section-routing checks; no runner setup, model or GPU execution."""
import ast, json, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent

def main():
    source=ast.parse((HERE/'driverbound_runner_cell.py').read_text())
    factory=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='generate_section')
    bundle=json.loads((HERE.parent/'story_t4_20261114/benchmark_bundle.json').read_text())
    checks=[]
    with tempfile.TemporaryDirectory() as folder:
        out=Path(folder);calls=[]
        ns={'OUT':out,'BUNDLE':bundle,'json':json,'run_one':lambda case:calls.append(case) or case}
        exec(compile(ast.Module(body=[factory],type_ignores=[]),'factory-only','exec'),ns)
        def fixture(name,state):
            (out/name).write_text(json.dumps({'state':state,'finish_reason':'stop'}))
        fixture('canary.json','stopped_with_evidence')
        fixture('driverbound_canary_v1.json','completed')
        before=(out/'canary.json').read_bytes()
        case=ns['generate_section']('foundation')
        assert case['id']=='driverbound_foundation_v1' and case['section']=='foundation'
        assert case['schema']==bundle['contracts']['foundation'] and case['max_new_tokens']==1536
        assert (out/'canary.json').read_bytes()==before
        checks.append('New unique section ID preserves exact original schema and output limit; old failure untouched')
        fixture('canary.json','completed');fixture('driverbound_canary_v1.json','stopped_with_evidence')
        prior=len(calls)
        try:ns['generate_section']('foundation')
        except AssertionError:pass
        else:raise AssertionError('Old successful canary reused instead of new failed canary')
        assert len(calls)==prior
        checks.append('New failed canary cannot be replaced by old success')
        fixture('driverbound_canary_v1.json','completed')
        fixture('driverbound_foundation_v1.json','stopped_with_evidence')
        try:ns['generate_section']('act_1')
        except AssertionError:pass
        else:raise AssertionError('Incomplete prior section skipped')
        assert len(calls)==prior
        checks.append('Act generation refuses incomplete required foundation')
    receipt={'checks':checks,'distinct_checks':3,'passed':3,
      'scope':'CPU fixtures only; no generated evidence, GPU, model, network or production worker execution',
      'previous_successful_tests_rerun':False}
    (HERE/'driverbound_cpu_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Three affected CPU routing checks PASS; no inference')

if __name__=='__main__':main()
