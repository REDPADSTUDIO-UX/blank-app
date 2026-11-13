"""Reviewed public code is separate from gated pinned-checkpoint compatibility."""
from .agents import AgentError

PUBLIC_SOURCE={'indic_speak':{'repo':'Bodhan-AI/bodhan_genai','revision':'62090c5e8f77588f1adb1dd745af1b9b8530dfb7',
 'entry':'bodhan_genai.tts.engine.offline.IndicTTSEngine','adapter':'redpad_pipeline.native_voice_worker',
 'selected_repo':'bodhan-ai/indic-speak','selected_revision':'76e0814f189321efe550011850cd288dae366aad',
 'selected_source_verified':False,'missing':['inference.py','token_contract.md','voices.md','config.json','tokenizer_config.json','vocos matching decoder/config source'],
 'reason':'Public engine names the same repository; exact selected token/speaker/decoder contract remains gated. No inference.py or preview-v2 equivalence assumed.'},
 'indicf5':{'repo':'AI4Bharat/IndicF5','revision':'13f7c4d627cc10111aea8fe9c0039462cacacdc7',
 'entry':None,'adapter':None,'selected_repo':'ai4bharat/IndicF5','selected_revision':'fb652a96e508091045890dae5bb99fe511facbcf',
 'selected_source_verified':False,'missing':['model.py','config.json','checkpoints/vocab.txt','matching f5_tts package source'],
 'reason':'Public README delegates initialization to gated custom model.py; generic public Gradio defaults to a different SWivid checkpoint, which must not be substituted.'}}

def binding_status(pid):
    if pid=='indic_parler':return {'profile':pid,'adapter_implemented':True,'source_blocked':False,'runtime_verified':False,'fallback':None}
    if pid not in PUBLIC_SOURCE:raise AgentError('Not an existing selected voice candidate.')
    p=PUBLIC_SOURCE[pid]
    from .no_gpu_staging import load
    registry,_=load();selected=registry['profiles'][pid]
    if (selected['repo'],selected['revision'])!=(p['selected_repo'],p['selected_revision']):raise AgentError('Voice source/checkpoint identity changed; no version substitution.')
    return {'profile':pid,'adapter_implemented':pid=='indic_speak','source_blocked':not p['selected_source_verified'],
            'adapter_scope':'public engine only, not a verified selected checkpoint binding' if pid=='indic_speak' else 'exact gated loader disabled',
            'selected_binding_implemented':False,
            'runtime_verified':False,'fallback':None,'blocker':p['reason'],'missing_source':p['missing']}

def require_selected_source(pid):
    if binding_status(pid)['source_blocked']:raise AgentError('Exact selected voice source access/review pending; native loader disabled, no fallback.')
