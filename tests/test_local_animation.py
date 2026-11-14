import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from PIL import Image
from redpad_pipeline.local_animation import AnimationError, generate, readiness


class LocalAnimationTests(unittest.TestCase):
    def image(self):
        b = io.BytesIO()
        Image.new('RGB', (64, 64), 'blue').save(b, format='PNG')
        return b.getvalue()

    def test_unconfigured_host_does_not_load_model(self):
        with patch.dict(os.environ, {'REDPAD_SVD_CHECKPOINT': ''}):
            self.assertFalse(readiness()[0])
            with self.assertRaisesRegex(AnimationError, 'not configured'):
                generate(self.image(), '/unused')

    def test_bad_image_and_parameters(self):
        for raw, kwargs in [(b'bad', {}), (self.image(), {'seed': -1}), (self.image(), {'motion': 256})]:
            with self.assertRaises(AnimationError):
                generate(raw, '/unused', **kwargs)

    def test_local_only_pipeline_and_metadata(self):
        calls = {}
        class Pipeline:
            @classmethod
            def from_pretrained(cls, checkpoint, **kwargs):
                calls.update(kwargs)
                return cls()
            def enable_model_cpu_offload(self): pass
            unet = types.SimpleNamespace(enable_forward_chunking=lambda: None)
            def __call__(self, image, **kwargs):
                calls['inference'] = kwargs
                return types.SimpleNamespace(frames=[[image]*25])
        torch = types.SimpleNamespace(float16='float16', Generator=lambda **kw: types.SimpleNamespace(manual_seed=lambda seed: seed), cuda=types.SimpleNamespace(empty_cache=lambda: None))
        def export(frames, path, fps):
            Path(path).write_bytes(b'x'*1200)
        modules = {'torch': torch, 'diffusers': types.SimpleNamespace(StableVideoDiffusionPipeline=Pipeline), 'diffusers.utils': types.SimpleNamespace(export_to_video=export)}
        with tempfile.TemporaryDirectory() as folder, patch.dict('sys.modules', modules), patch('redpad_pipeline.local_animation.readiness', return_value=(True, 'ok')), patch.dict(os.environ, {'REDPAD_SVD_CHECKPOINT': folder}):
            output, metadata = generate(self.image(), folder)
            self.assertTrue(output.is_file())
            self.assertTrue(calls['local_files_only'])
            self.assertEqual(calls['inference']['num_frames'], 25)
            self.assertEqual(json.loads(output.with_name('provenance.json').read_text()), metadata)
            with patch.object(Pipeline, '__call__', side_effect=RuntimeError('private error')):
                with self.assertRaisesRegex(AnimationError, 'No clip was registered'):
                    generate(self.image(), folder)
            self.assertEqual(len(list((Path(folder)/'local_animation').iterdir())), 1)

if __name__ == '__main__':
    unittest.main()
