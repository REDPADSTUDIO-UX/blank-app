import tempfile,unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class CreativeUITests(unittest.TestCase):
 def test_three_workspaces_and_story_execution(self):
  with tempfile.TemporaryDirectory() as d:
   path=str(Path(d)/'agent_control.sqlite3')
   for key in ('story','director','script'):
    code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.creative_ui import show_creative\nfrom redpad_pipeline.agent_execution_ui import show_execution\ns=AgentStore('+repr(path)+')\nshow_creative(s,'+repr(key)+')\nshow_execution(s,'+repr(key)+')'
    at=AppTest.from_string(code,default_timeout=60).run();self.assertFalse(at.exception)
    if key=='story':
     next(b for b in at.button if b.label=='Queue creative task').click().run()
     at.button(key='department_tick_story').click().run();self.assertFalse(at.exception)
     at.run();self.assertFalse(at.exception)
     self.assertTrue(any(w.label=='Creative artifact version' for w in at.selectbox))
     # Evidence required: empty/default scores cannot be saved as a real review.
     next(b for b in at.button if b.label=='Save evidence-based evaluation').click().run()
     self.assertTrue(any('Reviewer confirmation required' in e.value for e in at.error))
if __name__=='__main__':unittest.main()
