import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class Phase3UI(unittest.TestCase):
    def test_open_queue_block_export_without_runtime(self):
        with tempfile.TemporaryDirectory() as d,patch('redpad_pipeline.phase3.LAB_ROOT',Path(d)/'phase3_runs'):
            at=AppTest.from_string('from redpad_pipeline.phase3_ui import show_phase3\nshow_phase3()').run()
            self.assertFalse(at.exception);at.button(key='phase3_open').click().run();self.assertFalse(at.exception)
            next(b for b in at.button if b.label=='Queue bounded local experiment').click().run();self.assertFalse(at.exception)
            with patch('urllib.request.OpenerDirector.open',side_effect=OSError('No installed runtime')):
                at.button(key='phase3_execute').click().run()
            self.assertFalse(at.exception);self.assertTrue(any('blocked_preflight_or_dependency' in j.value and '1' in j.value for j in at.json))
            self.assertTrue(any('real_inference_completed' in j.value and '0' in j.value for j in at.json))
            self.assertTrue((Path(d)/'phase3_runs'/'bengali-phase3'/'agent_control.sqlite3').is_file())
