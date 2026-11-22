import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.free_voice import generate_google_bangla, VoiceError

class VoiceTests(unittest.TestCase):
    def test_validation(self):
        for text in ['', 'x'*5001, None]:
            with self.assertRaises(VoiceError): generate_google_bangla(text, '/unused')

    def test_failure_saves_nothing(self):
        with tempfile.TemporaryDirectory() as root, patch('gtts.gTTS', side_effect=RuntimeError('private')):
            with self.assertRaisesRegex(VoiceError, 'No voice was saved'): generate_google_bangla('কে ওখানে?', root)
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_registers_actual_returned_bytes(self):
        class Fake:
            def __init__(self, **kwargs):
                assert kwargs['lang']=='bn'
                assert kwargs['timeout']==(10,30)
            def write_to_fp(self, target): target.write(b'mp3'*1000)
        with tempfile.TemporaryDirectory() as root, patch('gtts.gTTS', Fake):
            out=generate_google_bangla('কে ওখানে?', root)
            self.assertEqual(out.read_bytes(), b'mp3'*1000)
            self.assertTrue(out.with_name('provenance.json').is_file())

if __name__=='__main__': unittest.main()
