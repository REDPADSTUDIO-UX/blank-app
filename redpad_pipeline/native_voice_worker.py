"""Public Indic-Speak engine adapter; selected binding disabled pending gated review.
No model import at module scope, and no invocation during no-GPU tests.
"""
import json,math,unicodedata,wave
from pathlib import Path
from .agents import AgentError
from .voice_source_policy import require_selected_source


def checked_tensor_state(torch,state,maximum=150_000_000):
    if not isinstance(state,dict) or not state or len(state)>10000:raise AgentError('Bounded tensor-only codec state required.')
    count=0
    for key,value in state.items():
        if not isinstance(key,str) or not isinstance(value,torch.Tensor):raise AgentError('Unsafe or unsupported codec state object.')
        count+=value.numel()
        if count>maximum or not bool(torch.isfinite(value).all()):raise AgentError('Nonfinite or oversized codec tensor state.')
    return state


def safe_vocos(torch,path,build,device):
    if not Path(path).is_file() or Path(path).is_symlink() or Path(path).stat().st_size>600*1024*1024:raise AgentError('Authenticated bounded local Vocos checkpoint required.')
    obj=torch.load(str(path),weights_only=True,map_location='cpu')
    if not isinstance(obj,dict) or not isinstance(obj.get('config'),dict) or not isinstance(obj['config'].get('model'),dict):raise AgentError('Unreviewed Vocos configuration format; no unsafe pickle fallback.')
    config=obj['config']['model']
    if any(not isinstance(k,str) or type(v) not in (str,int,float,bool) for k,v in config.items()):raise AgentError('Primitive reviewed Vocos configuration required.')
    if any((type(v) is float and (not math.isfinite(v) or abs(v)>1_000_000)) or (type(v) is int and not 0<=v<=65536) or (isinstance(v,str) and len(v)>100) for v in config.values()):raise AgentError('Vocos configuration exceeds bounded native policy.')
    key='ema' if isinstance(obj.get('ema'),dict) else 'vocos'
    state=checked_tensor_state(torch,obj.get(key));decoder=build(config)
    decoder.load_state_dict(state,strict=True);return decoder.to(device).eval()


def build_public_engine(engine_class,backend_class,torch,model_class,tokenizer_class,snac_class,vocos_builder,vocos_wrapper,root):
    """Verified official injection seams, fixed local loaders; no upstream auto-fetch.
    Unit tests inject ordinary fake classes; real classes are imported only by run().
    """
    root=Path(root)
    class OfflineBackend(backend_class):
        def __init__(self):
            self._model=model_class.from_pretrained(str(root),local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.bfloat16,device_map='cuda').eval()
    tokenizer=tokenizer_class.from_pretrained(str(root),local_files_only=True,trust_remote_code=False)
    def codec(path,*,device,compile_model=False):
        if compile_model or Path(path)!=root/'snac':raise AgentError('Exact local SNAC recipe only.')
        folder=root/'snac'
        for name in ('config.json','pytorch_model.bin'):
            if not (folder/name).is_file():raise AgentError('Local SNAC component missing; no Hub request.')
        snac=snac_class.from_config(str(folder/'config.json'))
        state=torch.load(str(folder/'pytorch_model.bin'),weights_only=True,map_location='cpu')
        snac.load_state_dict(checked_tensor_state(torch,state),strict=True);snac=snac.to(device).eval()
        vocos=safe_vocos(torch,root/'vocos/best.pt',vocos_builder,device)
        return vocos_wrapper(snac,vocos)
    # Codec is already explicitly wrapped with Vocos. False here stops upstream
    # resolve_decoder from replacing it or fetching a second decoder, not SNAC fallback.
    return engine_class(str(root),backend=OfflineBackend(),tokenizer=tokenizer,
        snac_model_path=str(root/'snac'),device='cuda',dtype='bfloat16',snac_loader=codec,vocos=False)


def validate_wav(path,expected_rate,*,max_seconds=30):
    if type(expected_rate) is not int or not 8000<=expected_rate<=192000:raise AgentError('Explicit supported WAV sample rate required.')
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise AgentError('Original local WAV required.')
    try:
        with wave.open(str(path),'rb') as w:
            rate=w.getframerate();channels=w.getnchannels();frames=w.getnframes();width=w.getsampwidth()
            if rate!=expected_rate or channels!=1 or width!=2 or w.getcomptype()!='NONE' or not .1<=frames/rate<=max_seconds:raise AgentError('WAV rate/channel/format/duration differs.')
            if len(w.readframes(frames))!=frames*channels*width:raise AgentError('Truncated voice WAV.')
    except (wave.Error,EOFError,OSError):raise AgentError('Invalid voice WAV.') from None
    return {'sample_rate':rate,'channels':channels,'duration_seconds':frames/rate,'listening_reviewed':False,'speaker_verified':False}


def run(job):
    require_selected_source('indic_speak')  # Always before any dependency/model import.
    import torch
    from transformers import LlamaForCausalLM,AutoTokenizer
    from snac import SNAC
    from bodhan_genai.tts.engine.offline import IndicTTSEngine,_HfBackend
    from bodhan_genai.tts.codec.vocos import _build_from_config,VocosSnac
    if not torch.cuda.is_bf16_supported():raise AgentError('No silent voice precision fallback.')
    root=Path(job['install']['model_root']);r=job['request']
    # This catalogue cannot be invented from the model-card example; it must be
    # reviewed against the exact gated voices/token contract before binding is enabled.
    catalog=json.loads((root/'redpad_reviewed_voice_catalog.json').read_text())
    if (catalog.get('repo'),catalog.get('revision'))!=('bodhan-ai/indic-speak','76e0814f189321efe550011850cd288dae366aad') or r['speaker_id'] not in catalog.get('bengali_speaker_ids',[]):raise AgentError('Exact reviewed Bengali speaker catalogue required.')
    text=unicodedata.normalize('NFC',r['text']);engine=build_public_engine(IndicTTSEngine,_HfBackend,torch,LlamaForCausalLM,AutoTokenizer,SNAC,_build_from_config,VocosSnac,root)
    try:
        torch.manual_seed(r['seed']);result=engine.synthesize(text,speaker=r['speaker_id'],style='',temperature=.6,top_p=.95,repetition_penalty=1.1,max_new_tokens=2048)
        if result.sample_rate!=24000:raise AgentError('Unexpected voice output sample rate.')
        target=Path(job['output_dir'])/'voice.wav';result.save(target);validate_wav(target,24000)
        return str(target)
    finally:engine.close()
