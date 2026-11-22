"""Real codec tests without provider credentials or paid API calls."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from redpad_video_studio import ffmpeg_binary, render_mp4


class RendererTests(unittest.TestCase):
    def test_audio_mix_and_rejected_inputs(self):
        ff = ffmpeg_binary()
        self.assertTrue(ff)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            voice = root / "test-tone.mp3"
            # A synthetic tone tests MP3 mixing; this is not a Bangla TTS test.
            subprocess.run([ff, "-v", "error", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=13", "-y", str(voice)], check=True)
            output = root / "mixed.mp4"
            result = render_mp4("Mix test", "Test narration", output,
                                 portrait=False, narration=voice.read_bytes())
            self.assertTrue(result["voice"])
            self.assertTrue(14 <= result["seconds"] <= 15)
            check = subprocess.run([ff, "-v", "error", "-i", str(output),
                                    "-f", "null", "-"], capture_output=True, timeout=60)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertFalse(check.stderr)
            original = output.read_bytes()
            with self.assertRaises(ValueError):
                render_mp4("Bad", "Test", output, narration=b"invalid MP3")
            with self.assertRaises(ValueError):
                render_mp4("Empty", "  ", output)
            long_voice = root / "long.mp3"
            subprocess.run([ff, "-v", "error", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=81", "-y", str(long_voice)], check=True)
            with self.assertRaisesRegex(ValueError, "at most 79"):
                render_mp4("Too long", "Test", output, narration=long_voice.read_bytes())
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
