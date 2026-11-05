import shutil
import tempfile
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from redpad_pipeline.agents import AGENTS

class AgentUITests(unittest.TestCase):
 def test_full_dashboard_workspaces(self):
  source=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for name in ('streamlit_app.py','redpad_video_studio.py'): shutil.copy2(source/name,root/name)
   for name in ('redpad_pipeline','assets'): shutil.copytree(source/name,root/name)
   at=AppTest.from_file(str(root/'streamlit_app.py'),default_timeout=90).run()
   self.assertFalse(at.exception)
   self.assertEqual(len(at.selectbox(key='agent_workspace').options),20)
   for key in AGENTS:
    at.selectbox(key='agent_workspace').set_value(key).run()
    self.assertFalse(at.exception)
   at.selectbox(key='agent_workspace').set_value('story').run()
   at.text_input(key='agent_model_story').set_value('fixture:7b')
   next(b for b in at.button if b.label=='Save agent configuration').click().run()
   at.text_area(key='agent_brief').set_value('Manual test story')
   next(b for b in at.button if b.label=='Assign development task').click().run()
   next(t for t in at.text_area if t.label=='Output summary').set_value('A manual fixture')
   next(b for b in at.button if b.label=='Save versioned output').click().run()
   self.assertFalse(at.exception)
   self.assertTrue((root/'agent_control.sqlite3').is_file())
   for action in ('Recommend','Approve'):
    next(w for w in at.selectbox if w.label=='Review action').set_value(action)
    next(w for w in at.text_area if w.label.startswith('Review evidence')).set_value('Owner verified fixture')
    next(w for w in at.checkbox if w.label.startswith('I am recording')).check()
    next(b for b in at.button if b.label=='Record review').click().run()
    self.assertFalse(at.exception)

if __name__=='__main__': unittest.main()
