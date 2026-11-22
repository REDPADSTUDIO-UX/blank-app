import shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from redpad_pipeline.studio_program import StudioProgram
from redpad_pipeline.producer_control import Producer

ROOT=Path(__file__).resolve().parents[1]
class ProducerUI(unittest.TestCase):
 def test_home_navigation_director_persistence_desk_and_legacy_tools(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for name in ('streamlit_app.py','redpad_video_studio.py'):shutil.copy2(ROOT/name,root/name)
   for name in ('redpad_pipeline','assets'):shutil.copytree(ROOT/name,root/name)
   with patch('requests.Session.request',side_effect=AssertionError('No external call')), patch('redpad_pipeline.studio_program.PROGRAM_ROOT',root/'programs'), patch('redpad_pipeline.producer_ui.PROGRAM_ROOT',root/'programs'):
    at=AppTest.from_file(str(root/'streamlit_app.py'),default_timeout=90).run()
    self.assertFalse(at.exception)
    self.assertEqual(at.radio(key='producer_nav').options,['Dashboard Home','Director Studio','Approval Desk','Channel Manager','Growth & Analytics'])
    self.assertFalse(any(w.key=='agent_workspace' for w in at.selectbox))
    at.radio(key='producer_nav').set_value('Director Studio').run()
    next(w for w in at.text_input if w.label=='Project ID').set_value('ui-test')
    next(w for w in at.text_input if w.label=='Production title').set_value('ঢাকার সকাল')
    next(w for w in at.text_area if w.label=='Original idea / creative brief').set_value('মেয়ে বাসের টিকিট খুঁজছে।')
    next(b for b in at.button if b.label=='Create production').click().run()
    at.selectbox(key='producer_project').set_value('ui-test').run()
    self.assertFalse(at.exception)
    at.chat_input(key='producer_message').set_value('গল্পের চরিত্র নিয়ে কথা বলি।').run()
    self.assertFalse(at.exception)
    self.assertTrue(any('গল্পের চরিত্র' in m.value for m in at.markdown))
    next(b for b in at.button if b.label=='Continue Director’s queued work').click().run()
    self.assertFalse(at.exception)
    self.assertTrue(any('Blocked' in m.value for m in at.markdown))
    at.radio(key='producer_nav').set_value('Approval Desk').run();self.assertFalse(at.exception)
    at.radio(key='producer_nav').set_value('Channel Manager').run();self.assertFalse(at.exception)
    self.assertTrue(any(w.label=='Channel Name' for w in at.text_input))
    at.radio(key='producer_nav').set_value('Growth & Analytics').run();self.assertFalse(at.exception)
    at.checkbox(key='producer_advanced').check().run();at.selectbox(key='producer_advanced_tool').set_value('agents').run()
    self.assertEqual(len(at.selectbox(key='agent_workspace').options),21);self.assertFalse(at.exception)
 def test_associated_conversation_button_and_milestone_actions(self):
  # Use a project in an isolated module import root; no production SQLite touched.
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);script=root/'ui.py'
   script.write_text("from pathlib import Path\nimport redpad_pipeline.studio_program as m\nm.PROGRAM_ROOT=Path("+repr(str(root/'programs'))+")\nfrom redpad_pipeline.producer_ui import show_producer_control\nshow_producer_control(lambda name:None)\n")
   with patch('redpad_pipeline.studio_program.PROGRAM_ROOT',root/'programs'):
    p=StudioProgram('review-test');p.create('Review','Original test brief',1,300);c=Producer(p)
    rid=c.say('পরামর্শ দিন।');p.engine.execute(rid,complete=lambda *_:dict(reply='পরিকল্পনা পর্যালোচনা করুন।',delegations=[],risks=[]))
    # producer_ui imports PROGRAM_ROOT by value; patch it to the same isolated root.
    with patch('redpad_pipeline.producer_ui.PROGRAM_ROOT',root/'programs'):
     at=AppTest.from_file(str(script),default_timeout=90).run()
     at.radio(key='producer_nav').set_value('Approval Desk').run()
     at.selectbox(key='producer_project').set_value('review-test').run()
     self.assertFalse(at.exception)
     next(b for b in at.button if b.label=='Open associated Director conversation').click().run()
     self.assertEqual(at.radio(key='producer_nav').value,'Director Studio');self.assertFalse(at.exception)

if __name__=='__main__':unittest.main()
