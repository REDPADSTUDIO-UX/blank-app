"""Test only the previously untested publisher modular index, with no model files."""
import hashlib
import json
from pathlib import Path
import sys

sys.path[:0] = ["/source/src", "/overlay"]
import diffusers
from diffusers import ModularPipeline
from diffusers.modular_pipelines.wan import WanAnimate2Blocks, WanAnimate2ModularPipeline

assert Path(diffusers.__file__).is_relative_to("/source")
assert [p.name for p in Path("/sys/class/net").iterdir()] == ["lo"]
asset = Path("/diagnostic/wan-modular-index.json").read_bytes()
assert hashlib.sha256(asset).hexdigest() == "ca29bd15a717e091b0aee14e22adc6669c511221e6e83ff82f42c339eee20827"
index = json.loads(asset)
assert "image_processor" not in index
assert all(index[k][2]["revision"] == "refs/pr/1" for k in ("scheduler", "transformer"))
print("PASS modular index omits processor and uses two mutable component refs", flush=True)

assert WanAnimate2ModularPipeline.default_blocks_name == WanAnimate2Blocks.__name__
for key in ("_class_name", "_blocks_class_name"):
    assert getattr(diffusers, index[key], None) is None
print("PASS pinned PR exports generic Wan classes but lacks both named Distilled modular exports", flush=True)

path = Path("/tmp/modular-model")
path.mkdir()
(path / "modular_model_index.json").write_bytes(asset)
try:
    ModularPipeline.from_pretrained(path, local_files_only=True, trust_remote_code=False)
except AttributeError as exc:
    assert index["_class_name"] in str(exc), str(exc)
    print("PASS exact local modular load reproduced missing pipeline class:", exc, flush=True)
else:
    raise AssertionError("unexpected success loading the exact publisher modular index")
