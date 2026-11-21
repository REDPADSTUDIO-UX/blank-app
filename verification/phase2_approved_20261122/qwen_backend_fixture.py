"""Bind the synthetic policy to the exact Transformers guard with mocked CUDA facts."""
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, sys.argv.pop())
import torch
import transformers
from transformers import FineGrainedFP8Config
from transformers.quantizers.quantizer_finegrained_fp8 import FineGrainedFP8HfQuantizer
from qwen_preflight_fixture import REQUIRED, preflight

assert torch.version.cuda is None and not torch.cuda.is_available()
assert transformers.__version__ == "5.22.2"


class TestBackend(unittest.TestCase):
    def check(self, reported_capability):
        config = FineGrainedFP8Config(weight_block_size=(128, 128))
        quantizer = FineGrainedFP8HfQuantizer(config, pre_quantized=True)

        def validate():
            quantizer.validate_environment(device_map={"": "cuda:0"})
            return config.dequantize

        # Assigned-device evidence can disagree with the backend's ambient device.
        with patch.object(torch.cuda, "is_available", return_value=True), \
             patch.object(torch.cuda, "get_device_capability", return_value=reported_capability):
            preflight("cuda", [(8, 9)], dict.fromkeys(REQUIRED, lambda: None),
                      config.dequantize, validate)

    def test_exact_guard_passes_with_supported_mock(self):
        self.check((8, 9))

    def test_exact_guard_fallback_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "BF16 fallback"):
            self.check((8, 6))


if __name__ == "__main__":
    unittest.main(verbosity=2)
