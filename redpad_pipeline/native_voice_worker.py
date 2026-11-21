"""Reviewed selected Voice bindings, plus the preserved public-engine adapter.
All heavy imports/external source execution are behind isolated runtime authority.
No real model or retrieved Python is executed by no-GPU QA.
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


def safe_vocos(torch,path,build,device,*,require_ema=False):
    if not Path(path).is_file() or Path(path).is_symlink() or Path(path).stat().st_size>600*1024*1024:raise AgentError('Authenticated bounded local Vocos checkpoint required.')
    obj=torch.load(str(path),weights_only=True,map_location='cpu')
    if not isinstance(obj,dict) or not isinstance(obj.get('config'),dict) or not isinstance(obj['config'].get('model'),dict):raise AgentError('Unreviewed Vocos configuration format; no unsafe pickle fallback.')
    config=obj['config']['model']
    if any(not isinstance(k,str) or type(v) not in (str,int,float,bool) for k,v in config.items()):raise AgentError('Primitive reviewed Vocos configuration required.')
    if any((type(v) is float and (not math.isfinite(v) or abs(v)>1_000_000)) or (type(v) is int and not 0<=v<=65536) or (isinstance(v,str) and len(v)>100) for v in config.values()):raise AgentError('Vocos configuration exceeds bounded native policy.')
    if require_ema and not isinstance(obj.get('ema'),dict):raise AgentError('Selected v9 EMA decoder state required; no old decoder fallback.')
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


def selected_decoder_config(config):
    allowed={'dim','intermediate_dim','num_blocks_pre','num_blocks_post','upsample','n_fft','hop','noise_inject','head_type'}
    if not isinstance(config,dict) or not set(config)<=allowed:raise AgentError('Unknown selected Vocos architecture configuration.')
    defaults=dict(dim=512,intermediate_dim=1536,num_blocks_pre=2,num_blocks_post=8,upsample=2,n_fft=1024,hop=256,noise_inject=False,head_type='istft')
    c={**defaults,**config}
    limits={'dim':(64,1024),'intermediate_dim':(128,4096),'num_blocks_pre':(1,16),'num_blocks_post':(1,32),'upsample':(1,4),'n_fft':(256,2048),'hop':(128,512)}
    if any(type(c[k]) is not int or not lo<=c[k]<=hi for k,(lo,hi) in limits.items()) or type(c['noise_inject']) is not bool or c['head_type'] not in ('istft','timedomain') or c['upsample']*c['hop']!=512 or (c['head_type']=='timedomain' and c['upsample']!=4):
        raise AgentError('Selected Vocos dimensions exceed reviewed architecture policy.')
    return c


def reviewed_module(path,name):
    """Only the isolated authorized caller may execute these source-locked files.
    Never used for IndicF5 model.py (contains unguarded inference/upload code).
    """
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def build_selected_speak(tts_class,torch,model_class,tokenizer_class,snac_class,decoder_class,root):
    """Use exact inference.TTS call methods, replace its unsafe/networking constructor.
    Injected ordinary fake classes cover this contract without loading models.
    """
    from .voice_native_contracts import validate_speak_tokenizer
    root=Path(root)
    for name in ('config.json','tokenizer.json','tokenizer_config.json','generation_config.json','model.safetensors','snac/config.json','snac/pytorch_model.bin','vocos/best.pt'):
        if not (root/name).is_file():raise AgentError('Selected local voice component missing; no download: '+name)
    tts=tts_class.__new__(tts_class);tts.device='cuda'
    tts.tok=tokenizer_class.from_pretrained(str(root),local_files_only=True,trust_remote_code=False)
    validate_speak_tokenizer(tts.tok)
    tts.lm=model_class.from_pretrained(str(root),local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
    tts.snac=snac_class.from_config(str(root/'snac/config.json'))
    tts.snac.load_state_dict(checked_tensor_state(torch,torch.load(str(root/'snac/pytorch_model.bin'),weights_only=True,map_location='cpu')),strict=True)
    tts.snac=tts.snac.to('cuda').eval()
    tts.vocos=safe_vocos(torch,root/'vocos/best.pt',lambda c:decoder_class(latent_dim=768,**selected_decoder_config(c)),'cuda',require_ema=True)
    tts._base=128266;tts._eos=128258
    return tts


def build_selected_f5(torch,cfm_class,dit_class,vocoder,root,state_loader):
    """Exact INF5Model attribute/key layout, FP32; never calls unsafe model.py.
    Selected HF wrapper safetensors must strictly match ema_model + vocoder.
    Their real key/shape compatibility is explicitly NOT verified by fake tests.
    """
    from .voice_native_contracts import f5_vocab,F5_DIT,F5_MEL
    root=Path(root);vocab,size=f5_vocab(root/'checkpoints/vocab.txt')
    if not (root/'model.safetensors').is_file():raise AgentError('Selected IndicF5 safetensors missing; no generic F5 checkpoint.')
    class LocalINF5(torch.nn.Module):
        def __init__(self):
            super().__init__();self.vocoder=vocoder
            self.ema_model=cfm_class(transformer=dit_class(**F5_DIT,text_num_embeds=size,mel_dim=100),mel_spec_kwargs=dict(F5_MEL),odeint_kwargs={'method':'euler'},vocab_char_map=vocab)
    model=LocalINF5()
    state=checked_tensor_state(torch,state_loader(str(root/'model.safetensors'),device='cpu'),maximum=400_000_000)
    state=selected_f5_state(state)
    model.load_state_dict(state,strict=True)
    return model.to(dtype=torch.float32,device='cuda').eval()


def selected_f5_state(state):
    """Two explicit wrapper layouts only. Source torch.compile adds _orig_mod.
    No generic F5/EMA checkpoint unpacking, partial loading or fuzzy key matching.
    Actual selected file layout must still pass the later authorized weight test.
    """
    if not state or not all(k.startswith(('ema_model.','vocoder.')) for k in state) or not all(any(k.startswith(prefix) for k in state) for prefix in ('ema_model.','vocoder.')):
        raise AgentError('Unsupported selected IndicF5 wrapper layout; no checkpoint substitution.')
    compiled={k.split('.',2)[1]=='_orig_mod' for k in state}
    if len(compiled)!=1:raise AgentError('Mixed compiled/uncompiled IndicF5 state is unsupported.')
    result={k.replace('._orig_mod.','.',1) if True in compiled else k:v for k,v in state.items()}
    if len(result)!=len(state) or any('._orig_mod.' in k for k in result):raise AgentError('Ambiguous IndicF5 compiled state mapping.')
    return result


def f5_modules(source):
    """Expose only reviewed inference modules; skip training package initializer.
    Original model.py and trainer/CLI/demo code are never imported.
    """
    import sys,types,importlib
    source=Path(source)
    for name,sub in [('f5_tts','f5_tts'),('f5_tts.model','f5_tts/model'),('f5_tts.model.backbones','f5_tts/model/backbones'),('f5_tts.infer','f5_tts/infer')]:
        if name in sys.modules:raise AgentError('Unexpected preloaded F5 package; exact isolated source required.')
        module=types.ModuleType(name);module.__path__=[str(source/sub)];sys.modules[name]=module
    cfm=importlib.import_module('f5_tts.model.cfm');dit=importlib.import_module('f5_tts.model.backbones.dit')
    sys.modules['f5_tts.model'].CFM=cfm.CFM
    utils=importlib.import_module('f5_tts.infer.utils_infer')
    return cfm.CFM,dit.DiT,utils


def run(job):
    from .voice_native_contracts import require_voice_job,validate_voice_request
    require_voice_job(job)  # Before any heavy imports, source execution or weight access.
    import torch
    import soundfile as sf
    import numpy as np
    root=Path(job['install']['model_root']);source=Path(job['install']['source_root']);r=job['request'];pid=job['profile']
    target=Path(job['output_dir'])/'voice.wav';text=validate_voice_request(pid,r)
    torch.manual_seed(r['seed'])
    if pid=='indic_speak':
        if not torch.cuda.is_bf16_supported():raise AgentError('Selected Indic-Speak BF16 required; no precision fallback.')
        from transformers import LlamaForCausalLM,AutoTokenizer
        from snac import SNAC
        implementation=reviewed_module(source/'inference.py','redpad_selected_speak_inference')
        decoder=reviewed_module(source/'vocos/model.py','redpad_selected_speak_vocos')
        tts=build_selected_speak(implementation.TTS,torch,LlamaForCausalLM,AutoTokenizer,SNAC,decoder.VocosDecoder,root)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('error',RuntimeWarning)  # Truncation warning is failed evidence.
            audio=tts(text,speaker=r['speaker_id'],style='',temperature=.6,top_p=.9,top_k=50,max_new_tokens=2048,seed=r['seed'],stock=False)
    else:
        from safetensors.torch import load_file
        from vocos import Vocos
        from vocos.feature_extractors import MelSpectrogramFeatures
        from vocos.models import VocosBackbone
        from vocos.heads import ISTFTHead
        # Fixed classes/arguments from charactr pinned config; never dynamic YAML classes.
        vocoder=Vocos(feature_extractor=MelSpectrogramFeatures(sample_rate=24000,n_fft=1024,hop_length=256,n_mels=100,padding='center'),backbone=VocosBackbone(input_channels=100,dim=512,intermediate_dim=1536,num_layers=8),head=ISTFTHead(dim=512,n_fft=1024,hop_length=256,padding='center'))
        cfm,dit,utils=f5_modules(source);model=build_selected_f5(torch,cfm,dit,vocoder,root,load_file)
        # No ASR, trimming, silence removal or loudness rewrite of the supplied reference.
        # Original transcript is hashed verbatim; upstream punctuation adaptation is recorded.
        ref_text=r['reference_transcript']
        if not ref_text.endswith(('. ','。')):ref_text+=' ' if ref_text.endswith('.') else '. '
        audio,rate,_=utils.infer_process(job['references']['reference'],ref_text,text,model.ema_model,model.vocoder,mel_spec_type='vocos',speed=1.0,nfe_step=32,cfg_strength=2.0,sway_sampling_coef=-1.0,device='cuda',show_info=lambda *a:None)
        if rate!=24000:raise AgentError('Selected IndicF5 sample rate differs.')
    audio=np.asarray(audio)
    if audio.dtype.kind!='f' or audio.ndim!=1 or not 2400<=audio.size<=720000 or not np.isfinite(audio).all() or np.max(np.abs(audio))>1.0:raise AgentError('Invalid/nonfinite/out-of-range bounded voice output; no silent normalization.')
    np.save(str(Path(job['output_dir'])/'raw_audio.npy'),audio,allow_pickle=False)  # Preserve native dtype/values before PCM conversion.
    sf.write(str(target),audio,24000,subtype='PCM_16');validate_wav(target,24000)
    return str(target)
