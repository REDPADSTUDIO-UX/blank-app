"""Check NF4 conversion coverage without instantiating a full model."""
import json
import os

os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='')
import bitsandbytes as bnb
import torch
from transformers import BitsAndBytesConfig
from transformers.integrations.bitsandbytes import replace_with_bnb_linear
from transformers.models.qwen3_5_moe.configuration_qwen3_5_moe import Qwen3_5MoeTextConfig
from transformers.models.qwen3_5_moe.modeling_qwen3_5_moe import Qwen3_5MoeExperts

config=Qwen3_5MoeTextConfig(hidden_size=8,moe_intermediate_size=4,num_experts=2)
with torch.device('meta'):
    parent=torch.nn.Module()
    parent.control=torch.nn.Linear(8,8,bias=False)
    parent.experts=Qwen3_5MoeExperts(config)
converted=replace_with_bnb_linear(parent,modules_to_not_convert=[],
                                  quantization_config=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4'))
control=isinstance(converted.control,bnb.nn.Linear4bit)
packed={name:{'type':type(param).__name__,'shape':list(param.shape),'device':str(param.device),
              'is_bitsandbytes_4bit':isinstance(param,bnb.nn.Params4bit)}
        for name,param in converted.experts.named_parameters()}
print(json.dumps({'control_converted':control,'packed_experts':packed,
                  'torch':torch.__version__,'bitsandbytes':bnb.__version__,
                  'weights_loaded':False,'inference':False},indent=2))
assert control and set(packed)=={'gate_up_proj','down_proj'}
assert all(row['device']=='meta' and not row['is_bitsandbytes_4bit'] for row in packed.values())
