"""CPU-only regressions. All transports/processes below are explicit fixtures."""
import ast,copy,hashlib,json,os,signal,tempfile,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUNNER=ROOT/'verification/story_budget8_20261119/sections_only_resume_cell.py'
TREE=ast.parse(RUNNER.read_text())
NAMES={'StoryHandoffError','require_story_handoff','digest','validate','authorize','reserve','budget','run_one','generate_section'}
NODES=[n for n in TREE.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in NAMES]
def declarations():
    scope={'json':json,'copy':copy,'hashlib':hashlib}
    exec(compile(ast.Module(body=NODES,type_ignores=[]),'existing-runner-declarations','exec'),scope)
    return scope

def fixture():
    f={'characters':[{'id':'N'},{'id':'H'}],'initial_knowledge':{'N':['job'],'H':['ticket']}}
    beats=[]
    for i in range(1,5):
        beats.append({'id':f'B{i}','act':1,'actor':'N','cause':'brief' if i==1 else f'B{i-1}',
          'before':{'progress':str(i-1)},'after':{'progress':str(i)},'requires':{'N':['job']},
          'learns':{'N':['ticket']} if i==2 else {},'plants':['ticket'] if i==1 else [],
          'payoffs':['ticket'] if i==4 else [],'emotion_setups':['B1'] if i>1 else []})
    return {'foundation':f,'act_1':beats}

class HandoffTests(unittest.TestCase):
    def setUp(self):self.s=declarations();self.guard=self.s['require_story_handoff'];self.error=self.s['StoryHandoffError']
    def codes(self,parts):
        with self.assertRaises(self.error) as error:self.guard(parts)
        return {f['code'] for f in error.exception.findings}
    def test_valid_prefix_is_lossless_and_accepts_explicit_discovery(self):
        p=fixture();before=copy.deepcopy(p);self.guard(p);self.assertEqual(p,before)
    def test_actual_outputs_reject_unknown_knowledge_without_repair(self):
        v=json.loads((ROOT/'verification/story_budget8_20261120/restored_foundation_actual.json').read_text())
        a=json.loads((ROOT/'verification/story_budget8_20261120/restored_act1_actual.json').read_text())
        p={'foundation':v['sections']['foundation']['parsed'],'act_1':a['section']['parsed']};before=copy.deepcopy(p)
        codes=self.codes(p)
        self.assertTrue({'expected_exact_N_H_ids','unknown_knowledge_character','predecessor_state_mismatch'}<=codes)
        self.assertEqual(p,before)
    def test_character_aliases_are_not_silently_normalized(self):
        p=fixture();p['foundation']['characters'][0]['id']='N-01'
        self.assertIn('expected_exact_N_H_ids',self.codes(p))
    def test_duplicate_identity_and_missing_knowledge_are_rejected(self):
        p=fixture();p['foundation']['characters'][1]['id']='N'
        self.assertIn('character_keys_mismatch',self.codes(p))
    def test_unsupported_and_premature_knowledge_are_rejected(self):
        p=fixture();p['act_1'][0]['requires']={'knowledge':['ticket']}
        self.assertIn('unknown_knowledge_character',self.codes(p))
        p=fixture();p['act_1'][0]['requires']={'N':['ticket']}
        self.assertIn('knowledge_not_established',self.codes(p))
    def test_causal_and_state_breaks_are_reported(self):
        p=fixture();p['act_1'][1]['cause']='B9';p['act_1'][1]['before']={'progress':'wrong'}
        self.assertTrue({'earlier_causal_reference_required','predecessor_state_mismatch'}<=self.codes(p))
    def test_unsupported_reveal_and_emotional_reference_are_rejected(self):
        p=fixture();p['act_1'][0]['payoffs']=['unseen'];p['act_1'][0]['emotion_setups']=['B12']
        self.assertTrue({'earlier_unresolved_plant_required','earlier_emotional_reference_required'}<=self.codes(p))
    def test_malformed_shapes_and_section_skips_fail_deterministically(self):
        for p in ([],{'foundation':{}},{'act_1':[]}):
            with self.subTest(parts=p):self.codes(p)
    def test_embedded_guard_matches_reviewable_source(self):
        source=ast.parse((HERE/'guard_source.py').read_text())
        extract=lambda tree:[ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'StoryHandoffError','require_story_handoff'}]
        self.assertEqual(extract(source),extract(TREE))
    def test_existing_act2_entry_rejects_before_runtime_and_preserves_files(self):
        source=json.loads((ROOT/'verification/story_budget8_20261120/restored_foundation_actual.json').read_text())
        act=json.loads((ROOT/'verification/story_budget8_20261120/restored_act1_actual.json').read_text())
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);rows={'driverbound_canary_v1':{'state':'completed','finish_reason':'stop'},'driverbound_foundation_v1':source['sections']['foundation'],'driverbound_act_1_v1':act['section']}
            for key,value in rows.items():(out/(key+'.json')).write_text(json.dumps(value))
            ledger=out/'ledger.json';ledger.write_text(json.dumps(act['ledger']))
            before={p.name:p.read_bytes() for p in out.iterdir()}
            def forbidden(*a,**k):self.fail('Runtime/model dispatch must not occur')
            self.s.update(OUT=out,SECTIONS=('foundation','act_1','act_2','act_3','reflection'),run_one=forbidden)
            with self.assertRaises(self.error):self.s['generate_section']('act_2')
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
    def test_new_invalid_model_output_is_preserved_but_never_completed(self):
        """Mock transport only: not real model/GPU evidence."""
        baseline=json.loads((ROOT/'verification/story_option_c_20261116/driver_recovery_call_ledger.json').read_text())
        self.s.update(BASELINE=baseline,AUTHORIZATION='owner-story-total8-five-sections-20261119',SECTIONS=('foundation','act_1','act_2','act_3','reflection'))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ledger=root/'call_ledger.json'
            ledger.write_text(json.dumps(self.s['authorize'](baseline,baseline,self.s['AUTHORIZATION'])))
            original_prefix=copy.deepcopy(baseline)
            class FakeProcess:
                pid=123
                returncode=None
                def poll(self):return self.returncode
                def wait(self,**kwargs):self.returncode=0;return 0
            process=FakeProcess()
            class ProcessTools:
                STDOUT=-2
                Popen=staticmethod(lambda *a,**k:process)
                check_output=staticmethod(lambda *a,**k:'123, 5000\n')
                TimeoutExpired=TimeoutError
            bad=fixture()['foundation'];bad['characters'][0]['id']='N-01'
            content=json.dumps(bad)
            def transport(path,payload=None,timeout=10):
                if path=='/health':return b'{"status":"ok"}'
                if path=='/apply-template':return b'{"prompt":"CPU fixture"}'
                if path=='/tokenize':return b'{"tokens":[1]}'
                return json.dumps({'choices':[{'message':{'content':content},'finish_reason':'stop'}]}).encode()
            self.s.update(OUT=root,RESEARCH=root,LEDGER=ledger,binary=Path('/nonexistent/FIXTURE'),receipt={'model_path':'NO_WEIGHTS'},WORKER_ENV={},SELECTED_DEVICE='FIXTURE',section_eligibility=lambda:None,http=transport,subprocess=ProcessTools,time=time,threading=threading,psutil=SimpleNamespace(),base64=__import__('base64'),os=SimpleNamespace(killpg=lambda *a:None),signal=signal)
            case={'id':'driverbound_foundation_v1','section':'foundation','prior_sections':{},'system':'CPU FIXTURE','prompt':'CPU FIXTURE','max_new_tokens':1536,'schema':{'type':'object','properties':{k:{'type':'array'} for k in ('assumptions','unresolved_questions','characters')}}}
            with self.assertRaisesRegex(RuntimeError,'STORY_HANDOFF_INVALID'):self.s['run_one'](case)
            result=json.loads((root/'driverbound_foundation_v1.json').read_text());after=json.loads(ledger.read_text())
            self.assertEqual(result['raw_content'],content)
            self.assertEqual(result['state'],'stopped_with_evidence')
            self.assertTrue(result['schema_validated']);self.assertNotIn('parsed',result)
            self.assertTrue(result['handoff_findings']);self.assertNotIn('handoff_validated',result)
            self.assertEqual(after['historical'],original_prefix['historical'])
            self.assertEqual(after['new_calls'][:1],original_prefix['new_calls'])
            self.assertEqual(after['new_calls'][-1]['state'],'stopped_with_evidence')

if __name__=='__main__':unittest.main(verbosity=2)
