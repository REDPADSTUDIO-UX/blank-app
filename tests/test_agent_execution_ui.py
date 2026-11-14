import json
import tempfile
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from tests.test_agent_foundation import fixture

class ExecutionUITest(unittest.TestCase):
 def test_enqueue_execute_inspect(self):
  with tempfile.TemporaryDirectory() as d:
   code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.agent_execution_ui import show_execution\nshow_execution(AgentStore('+repr(str(Path(d)/'agent_control.sqlite3'))+'),"story")'
   at=AppTest.from_string(code).run();self.assertFalse(at.exception)
   at.text_area(key='department_input_story').set_value(json.dumps(fixture('story')))
   next(b for b in at.button if b.label=='Queue department task').click().run()
   self.assertFalse(at.exception)
   at.button(key='department_tick_story').click().run()
   self.assertFalse(at.exception)
   self.assertTrue(any('Awaiting QC' in j.value for j in at.json))
 def test_failed_input_retry(self):
  with tempfile.TemporaryDirectory() as d:
   code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.agent_execution_ui import show_execution\nshow_execution(AgentStore('+repr(str(Path(d)/'agent_control.sqlite3'))+'),"story")'
   at=AppTest.from_string(code).run()
   at.text_area(key='department_input_story').set_value('{}')
   next(b for b in at.button if b.label=='Queue department task').click().run()
   at.button(key='department_tick_story').click().run();self.assertFalse(at.exception)
   next(w for w in at.text_area if w.label=='Retry input JSON').set_value(json.dumps(fixture('story')))
   next(b for b in at.button if b.label=='Retry selected execution').click().run()
   at.button(key='department_tick_story').click().run();self.assertFalse(at.exception)
   self.assertTrue(any('Awaiting QC' in j.value for j in at.json))
if __name__=='__main__':unittest.main()
