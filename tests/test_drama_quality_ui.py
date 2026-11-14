"""Real Streamlit form/review integration; no provider call or fake episode."""
import sqlite3,tempfile,unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from redpad_pipeline.drama_quality import Studio

class WorkbenchUITests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.db=self.root/'studio.db';self.media=self.root/'media'
  with sqlite3.connect(self.db) as db:db.executescript('CREATE TABLE channels(id INTEGER PRIMARY KEY,name TEXT);INSERT INTO channels VALUES(1,"Nishikotha");CREATE TABLE content(id INTEGER PRIMARY KEY,channel_id INTEGER,title TEXT,topic TEXT,script TEXT,status TEXT,created_at TEXT,updated_at TEXT);')
  self.studio=Studio(self.db,self.media);self.pid=self.studio.create('Unfinished realistic episode',300,channel_id=1)
 def app(self):return AppTest.from_string(f'from redpad_pipeline.drama_quality_ui import show\nshow({str(self.db)!r},{str(self.media)!r})',default_timeout=30).run()
 def test_unfinished_project_has_no_final_video_or_enabled_render(self):
  app=self.app();self.assertFalse(app.exception);self.assertFalse(app.get('video'))
  render=next(b for b in app.button if 'final MP4 render' in b.label);self.assertTrue(render.disabled)
  self.assertTrue(any('কোনো নতুন realistic episode render হয়নি' in x.value for x in app.warning))
 def test_research_form_creates_versioned_data_without_terminal_or_json(self):
  app=self.app();app.text_input(key='dq_id_research_নতুন আইটেম').set_value('R01')
  app.text_area(key='dq_field_research_নতুন আইটেম_claim').set_value('The family history is fictional.')
  app.text_area(key='dq_field_research_নতুন আইটেম_application').set_value('Use it as a fictional character motive.')
  next(b for b in app.button if b.label=='নতুন revision সংরক্ষণ').click();app.run()
  self.assertFalse(app.exception);self.assertIn('research/R01',self.studio.entries(self.pid))
  with sqlite3.connect(self.db) as db:self.assertEqual(db.execute('SELECT status FROM content').fetchone()[0],'Draft')
 def test_script_and_sound_departments_open_without_claiming_generation(self):
  app=self.app();app.radio(key='dq_script').set_value('line').run();self.assertFalse(app.exception)
  self.assertTrue(any(x.label=='শুধু কথ্য বাংলা সংলাপ' for x in app.text_area))
  app.radio(key='dq_sound').set_value('sfx').run();self.assertFalse(app.exception)
  self.assertTrue(any(x.label=='কোন বাস্তব ঘটনায় শব্দ হচ্ছে' for x in app.text_area))

if __name__=='__main__':unittest.main()
