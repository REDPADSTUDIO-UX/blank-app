"""Exercise the exact upstream local loader with model-free component substitutes."""
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path[:0] = ["/source/src", "/overlay"]
from diffusers import FlowMatchEulerDiscreteScheduler, WanAnimate2Pipeline
from diffusers.pipelines import pipeline_utils

assert Path(pipeline_utils.__file__).is_relative_to("/source")
assert set(Path("/sys/class/net").iterdir()) == {Path("/sys/class/net/lo")}
asset = Path("/diagnostic/wan-pinned-model-index.json").read_bytes()
assert hashlib.sha256(asset).hexdigest() == "da26517859f8e2766366795750dbfe3f758968fc9dfa6650f4c9f5beb1e6bc1d"
index = json.loads(asset)
folder = Path("/tmp/local-model")
folder.mkdir()
(folder / "model_index.json").write_bytes(asset)

calls = {}
scheduler = FlowMatchEulerDiscreteScheduler()


def synthetic_component(**spec):
    name = spec["name"]
    calls[name] = [spec["library_name"], spec["class_name"]]
    return scheduler if name == "scheduler" else None


expected, _ = WanAnimate2Pipeline._get_signature_keys(WanAnimate2Pipeline)
init, unused, hidden = WanAnimate2Pipeline.extract_init_dict(index)
assert "image_processor" in hidden and "image_processor" not in init
assert "image_processor" not in expected
print("PASS config extraction ignores image_processor")

with patch.object(pipeline_utils, "load_sub_model", side_effect=synthetic_component):
    pipeline = WanAnimate2Pipeline.from_pretrained(folder, local_files_only=True)
    assert pipeline.scheduler is scheduler
    assert "image_processor" not in pipeline.components
    assert calls == {key: index[key] for key in expected}
print("PASS exact loader requests only constructor components", json.dumps(calls, sort_keys=True))

calls.clear()
with patch.object(pipeline_utils, "load_sub_model", side_effect=synthetic_component):
    explicit = WanAnimate2Pipeline.from_pretrained(folder, local_files_only=True, image_processor=object())
    assert explicit.scheduler is scheduler and "image_processor" not in calls
    assert "image_processor" not in explicit.components
print("PASS explicit processor override ignored")

calls.clear()
index.pop("scheduler")
(folder / "model_index.json").write_text(json.dumps(index))
with patch.object(pipeline_utils, "load_sub_model", side_effect=synthetic_component):
    try:
        WanAnimate2Pipeline.from_pretrained(folder, local_files_only=True)
    except ValueError as exc:
        assert "expected" in str(exc) and "scheduler" in str(exc)
    else:
        raise AssertionError("required scheduler omission must fail")
print("PASS required scheduler omission rejected")

from types import SimpleNamespace

import numpy as np
from PIL import Image
import torch
from transformers import CLIPImageProcessor

config = json.loads(Path("/diagnostic/wan-pinned-processor-config.json").read_text())
processor = CLIPImageProcessor.from_dict(config)
image = Image.fromarray(np.arange(239 * 371 * 3, dtype=np.uint8).reshape(239, 371, 3))
expected_pixels = processor(images=image, return_tensors="pt")["pixel_values"]


def encoder(*, pixel_values, output_hidden_states):
    assert output_hidden_states is True
    torch.testing.assert_close(pixel_values, expected_pixels, atol=0, rtol=0)
    return SimpleNamespace(hidden_states=[pixel_values, None])


pipeline.image_encoder = encoder
assert pipeline.encode_image(image, device="cpu").shape == (1, 3, 224, 224)
print("PASS exact encode_image default equals pinned CLIP preprocessing for synthetic RGB image")

import importlib
from importlib.metadata import version

components = json.loads(asset)
for key, spec in components.items():
    if key.startswith("_"):
        continue
    symbol = getattr(importlib.import_module(spec[0]), spec[1])
    assert isinstance(symbol, type) and callable(getattr(symbol, "from_pretrained", None)), spec
    if symbol.__name__ != spec[1]:
        print(f"OBSERVED exported alias {spec[0]}.{spec[1]} -> {symbol.__name__}", flush=True)
print("PASS pinned component class symbols import from exact diagnostic environment")

import cv2
import decord

assert callable(cv2.resize) and callable(decord.VideoReader)
print("PASS OpenCV and Decord native imports", json.dumps(
    {name: version(name) for name in ("opencv-python-headless", "decord", "pillow", "numpy")}))
