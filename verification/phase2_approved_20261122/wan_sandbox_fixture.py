"""Docker-isolated CPU diagnostic for the reviewed public Diffusers source."""
import ast
import hashlib
import json
import inspect
import os
from pathlib import Path
import platform
import sys

source, overlay, sentinel = map(Path, sys.argv[1:])
assert os.getuid() != 0
assert Path("/proc/net/route").read_text().count("\n") == 1
assert set(os.listdir("/sys/class/net")) == {"lo"}
print("PASS loopback_only_no_routes", flush=True)

for name, operation in (
    ("unlisted_file_denied", lambda: sentinel.read_bytes()),
    ("source_write_denied", lambda: (source / "sentinel-write").touch()),
):
    try:
        operation()
    except OSError as exc:
        if exc.errno not in (2, 13, 30):
            raise
        print(f"PASS {name}", flush=True)
    else:
        raise AssertionError(name)

sys.path[:0] = [str(source / "src"), str(overlay)]
from importlib.metadata import version
import torch
import diffusers
from diffusers import DPMSolverMultistepScheduler, FlowMatchEulerDiscreteScheduler
from diffusers import WanAnimate2Pipeline, WanAnimate2Transformer3DModel

assert torch.version.cuda is None
assert Path(diffusers.__file__).is_relative_to(source)
print("PASS exact_pipeline_and_transformer_import", flush=True)
print(json.dumps({"network_interfaces": ["lo"], "kernel": platform.release(), "python": sys.version,
                  "diffusers": diffusers.__version__,
                  "packages": {n: version(n) for n in ("torch", "transformers", "huggingface-hub",
                              "safetensors", "accelerate", "opencv-python-headless", "decord")}}), flush=True)

scheduler = FlowMatchEulerDiscreteScheduler()
pipeline = WanAnimate2Pipeline(None, None, None, scheduler, None, None)
assert pipeline.scheduler is scheduler
assert pipeline.config.scheduler == ("diffusers", "FlowMatchEulerDiscreteScheduler")
print("PASS synthetic_pinned_scheduler_registration", flush=True)
assert "image_processor" not in inspect.signature(WanAnimate2Pipeline.__init__).parameters
print("OBSERVED pinned index lists image_processor, exact constructor does not", flush=True)

pipeline._guidance_scale = 1.0
assert not pipeline.do_classifier_free_guidance
pipeline._guidance_scale = 1.01
assert pipeline.do_classifier_free_guidance
print("PASS no_cfg_boundary", flush=True)

# Exercise the exact scheduler selection fragment without executing a forward pass.
path = source / "src/diffusers/pipelines/wan/pipeline_wan_animate_2.py"
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "f04b0e244e09a14ba0a67e5cde3712f408e5defaa941417b410f64466d35d8b8"
tree = ast.parse(raw)
pipeline_ast = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "WanAnimate2Pipeline")
call = next(n for n in pipeline_ast.body if isinstance(n, ast.FunctionDef) and n.name == "__call__")
start = next(i for i, n in enumerate(call.body) if isinstance(n, ast.If)
             and ast.unparse(n.test) == "flow_solver == 'euler'")
fragment = compile(ast.Module(body=call.body[start:start + 4], type_ignores=[]), str(path), "exec")
for solver, expected in (("dpm", DPMSolverMultistepScheduler), ("euler", FlowMatchEulerDiscreteScheduler)):
    args = dict(flow_solver=solver, sample_shift=5.0, device="cpu", num_inference_steps=10,
                self=pipeline, DPMSolverMultistepScheduler=DPMSolverMultistepScheduler)
    exec(fragment, args)
    assert isinstance(args["sample_scheduler"], expected)
    assert pipeline._num_timesteps == 10
    print(f"PASS ten_steps_{solver}", flush=True)
