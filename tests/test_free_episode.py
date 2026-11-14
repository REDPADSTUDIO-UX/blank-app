import tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from redpad_pipeline.free_episode import validate,render_shot,soundtrack,qa,perceptual
from redpad_pipeline.media import ff

class FreeEpisodeTests(unittest.TestCase):
    def test_duplicate_prompts_rejected_before_generation(self):
        s=dict(text='hello',prompt='A rainy house at night',seconds=5)
        with self.assertRaisesRegex(ValueError,'Repeated'):validate(dict(title='test',shots=[s,s]))
    def test_audio_not_truncated(self):
        with patch('redpad_pipeline.free_episode.duration',return_value=16),patch('redpad_pipeline.free_episode.ff') as runner:
            with self.assertRaisesRegex(ValueError,'exceeds'):render_shot('x','y',Path('z'),10,0)
            runner.assert_not_called()
    def test_perceptual_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/'a.jpg';b=Path(folder)/'b.jpg'
            Image.new('RGB',(640,360),(70,90,60)).save(a);Image.open(a).resize((320,180)).save(b)
            self.assertEqual(perceptual(a),perceptual(b))
    def test_real_encode_full_decode_and_gap_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            r=Path(folder);img=r/'a.png';Image.new('RGB',(832,480),(80,90,100)).save(img)
            ff(['-f','lavfi','-i','sine=frequency=320:duration=2',r/'voice.wav'])
            render_shot(img,r/'voice.wav',r/'shot.mp4',3,0)
            soundtrack(r/'score.wav',3,[0,2])
            ff(['-i',r/'shot.mp4','-i',r/'score.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac',r/'mixed.mp4'])
            report=qa(r/'mixed.mp4',3);self.assertTrue(report['full_decode'])
            ff(['-f','lavfi','-i','color=black:s=320x180:d=3','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','3','-c:v','libx264','-c:a','aac',r/'bad.mp4'])
            with self.assertRaisesRegex(ValueError,'Black section'):qa(r/'bad.mp4',3)

if __name__=='__main__':unittest.main()
