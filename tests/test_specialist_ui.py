import tempfile,unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from redpad_pipeline.specialists import IMPLEMENTED

class SpecialistUI(unittest.TestCase):pass

def workspace_test(key):
    def check(self):
        with tempfile.TemporaryDirectory() as d:
            code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.agent_execution_ui import show_execution\nshow_execution(AgentStore('+repr(str(Path(d)/'agent_control.sqlite3'))+'),'+repr(key)+')'
            at=AppTest.from_string(code).run();self.assertFalse(at.exception)
            self.assertTrue(at.checkbox(key='specialist_mode_'+key).value)
            next(b for b in at.button if b.label=='Queue department task').click().run();self.assertFalse(at.exception)
            at.button(key='department_tick_'+key).click().run();self.assertFalse(at.exception)
            self.assertTrue(any('Awaiting QC' in j.value for j in at.json))
            self.assertTrue(any('specialist_' in j.value for j in at.json))
    return check
for key in sorted(IMPLEMENTED):setattr(SpecialistUI,'test_'+key+'_workspace_execution',workspace_test(key))

def test_approved_coverage_button(self):
    import json
    from redpad_pipeline.agents import AgentStore,AGENTS
    from tests.test_creative import samples
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'agent_control.sqlite3';store=AgentStore(path)
        tid=store.assign('script','Manual screenplay fixture')
        store.submit(tid,dict(schema_version=1,kind=AGENTS['script']['output_contract']['kind'],summary=json.dumps({'agent':'script','artifact':samples()['screenplay']},ensure_ascii=False),artifacts=[],provenance='manual'),0)
        store.review(tid,1,'Recommend','Fixture independent review','qc');store.review(tid,1,'Approve','Fixture owner approval','owner')
        code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.agent_execution_ui import show_execution\nshow_execution(AgentStore('+repr(str(path))+'),"storyboard")'
        at=AppTest.from_string(code).run();at.button(key='coverage_prepare').click().run();self.assertFalse(at.exception)
        inputs=json.loads(at.text_area(key='department_input_storyboard_specialist').value)
        self.assertEqual(sum(r['seconds'] for r in inputs['records']),300)
        next(b for b in at.button if b.label=='Queue department task').click().run()
        at.button(key='department_tick_storyboard').click().run();self.assertFalse(at.exception)
        self.assertTrue(any('Awaiting QC' in j.value for j in at.json))
SpecialistUI.test_approved_coverage_button=test_approved_coverage_button
