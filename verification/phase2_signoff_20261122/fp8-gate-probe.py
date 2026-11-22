"""Check the installed FP8 backend's actual CPU guard, with no model construction."""
import json
import sys

import torch
import transformers
from transformers import FineGrainedFP8Config
from transformers.quantizers.quantizer_finegrained_fp8 import FineGrainedFP8HfQuantizer

assert torch.version.cuda is None and not torch.cuda.is_available()
result={}
for pre_quantized in (False,True):
    recipe=FineGrainedFP8Config(weight_block_size=(128,128))
    assert not recipe.dequantize
    worker=FineGrainedFP8HfQuantizer(recipe,pre_quantized=pre_quantized)
    evidence={}
    try:
        worker.validate_environment()
    except RuntimeError as exc:
        evidence['rejection']=str(exc)
    evidence['dequantize_after_validation']=recipe.dequantize
    result['prequantized' if pre_quantized else 'quantize_on_load']=evidence
assert 'No GPU or XPU' in result['quantize_on_load']['rejection']
assert result['prequantized']['dequantize_after_validation']
print(json.dumps({'python':sys.version,'torch':torch.__version__,'transformers':transformers.__version__,
                  'backend_guard':result,'loaded_weights':False,'inference':False,
                  'route_enabled':False},indent=2))
