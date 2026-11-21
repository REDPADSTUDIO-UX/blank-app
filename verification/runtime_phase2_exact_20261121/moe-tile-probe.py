"""Synthetic FP8 expert conversion in the already tested Modern CPU prefix."""
import hashlib,inspect,json,sys
from pathlib import Path
from types import SimpleNamespace
import torch
from torch.nn import functional as F
from transformers import FineGrainedFP8Config, Qwen3_5MoeTextConfig
from transformers.integrations.finegrained_fp8 import FP8Experts, Fp8Quantize, replace_with_fp8_linear
from transformers.models.qwen3_5_moe.modeling_qwen3_5_moe import Qwen3_5MoeExperts

torch.manual_seed(17)
root=Path(__file__).resolve().parents[2]
config_file=root/'verification/runtime_phase2_remaining_20261121/qwen35_moe-publisher-config.json'
source=json.loads(config_file.read_text())
pinned=source['text_config']
assert source['architectures']==['Qwen3_5MoeForConditionalGeneration']
block=128
assert pinned['hidden_size']%block==0 and pinned['moe_intermediate_size']%block==0
cfg=Qwen3_5MoeTextConfig(hidden_size=block,moe_intermediate_size=block,num_experts=2)
quant=FineGrainedFP8Config(weight_block_size=(block,block))
with torch.device('meta'):
    model=torch.nn.Module()
    model.config=SimpleNamespace(get_text_config=lambda:cfg)
    model.block=torch.nn.Module()
    model.block.experts=Qwen3_5MoeExperts(cfg)
    replacement=replace_with_fp8_linear(model,[],quant).block.experts
assert isinstance(replacement,FP8Experts)
assert tuple(inspect.signature(replacement.forward).parameters)==tuple(inspect.signature(Qwen3_5MoeExperts(cfg).forward).parameters)==("hidden_states","top_k_index","top_k_weights")
reference=Qwen3_5MoeExperts(cfg)
with torch.no_grad():
    for param in reference.parameters():
        param.copy_(torch.randn_like(param)*.025)
converter=Fp8Quantize(SimpleNamespace(quantization_config=quant))
packed=converter.convert(dict(reference.named_parameters()))
restored={}
shapes={}
for key in ('gate_up_proj','down_proj'):
    value,scale=packed[key],packed[key+'_scale_inv']
    repeated=scale.repeat_interleave(block,-2).repeat_interleave(block,-1)
    assert value.dtype==torch.float8_e4m3fn
    assert tuple(value.shape)==tuple(getattr(replacement,key).shape)
    assert tuple(scale.shape)==tuple(getattr(replacement,key+'_scale_inv').shape)
    restored[key]=value.float()*repeated
    shapes[key]={'weight':list(value.shape),'scale':list(scale.shape),'dtype':str(value.dtype)}
x=torch.randn(3,block)
route=torch.tensor([[0,1],[1,0],[0,1]])
weights=torch.tensor([[.8,.2],[.7,.3],[.65,.35]])
expected=reference(x,route,weights)
# CPU reference forward checks routed tensor semantics after explicit dequantization.
out=torch.zeros_like(expected)
for expert in range(2):
    tokens,slots=torch.where(route==expert)
    g,u=F.linear(x[tokens],restored['gate_up_proj'][expert]).chunk(2,dim=-1)
    out.index_add_(0,tokens,F.linear(F.silu(g)*u,restored['down_proj'][expert])*weights[tokens,slots,None])
assert out.shape==expected.shape
torch.testing.assert_close(out,expected,atol=.025,rtol=.15)
print(json.dumps({'python':sys.version,'executable':sys.executable,'torch':torch.__version__,
     'model_revision':'59d61f3ce65a6d9863b86d2e96597125219dc754',
    'published_config_sha256':hashlib.sha256(config_file.read_bytes()).hexdigest(),
    'publisher_layout':{'num_experts':pinned['num_experts'],'hidden_size':pinned['hidden_size'],
                        'moe_intermediate_size':pinned['moe_intermediate_size']},
    'weight_block_size':[block,block],'meta_module':type(replacement).__name__,'packed_expert_tensors':shapes,
    'max_absolute_error':float((out-expected).abs().max().detach()),
    'reference_cpu_forward_pass':True,'quantized_kernel_forward_executed':False,
    'weights_loaded':False,'production_route_enabled':False},indent=2))
