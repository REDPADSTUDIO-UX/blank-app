import tempfile
import unittest
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from tests.test_director import fixture

class DirectorUITest(unittest.TestCase):
 def test_plan_review_and_dispatch(self):
  with tempfile.TemporaryDirectory() as d:
   code='from redpad_pipeline.agents import AgentStore\nfrom redpad_pipeline.director_ui import show_director\nshow_director(AgentStore('+repr(str(Path(d)/'agent_control.sqlite3'))+'))'
   at=AppTest.from_string(code).run()
   at.text_area(key='director_brief').set_value('বাংলাদেশের পুরোনো বাড়ির দৃশ্য')
   next(w for w in at.number_input if w.label=='Target duration (seconds)').set_value(30)
   next(w for w in at.selectbox if w.label=='Planning mode').set_value('Manual JSON plan')
   at.text_area(key='director_json').set_value(json.dumps(fixture(),ensure_ascii=False))
   next(b for b in at.button if b.label=='Create Director plan').click().run()
   self.assertFalse(at.exception);self.assertTrue(at.button(key='director_dispatch').disabled)
   for action in ('Recommend','Approve'):
    next(w for w in at.selectbox if w.label=='Director plan review').set_value(action)
    next(w for w in at.text_area if w.label=='Director review evidence').set_value('মানব যাচাই')
    next(w for w in at.checkbox if w.label.startswith('I am the owner')).check()
    next(b for b in at.button if b.label=='Save Director review').click().run()
    self.assertFalse(at.exception)
   self.assertFalse(at.button(key='director_dispatch').disabled)
   at.button(key='director_dispatch').click().run();self.assertFalse(at.exception)
   self.assertTrue(any('Assigned task IDs' in x.value for x in at.success))
if __name__=='__main__':unittest.main()
