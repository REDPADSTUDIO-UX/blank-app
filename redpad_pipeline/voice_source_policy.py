"""Public history, exact selected source review and runtime authority are separate."""
from .agents import AgentError

PUBLIC_SOURCE={'indic_speak':{'repo':'Bodhan-AI/bodhan_genai','revision':'62090c5e8f77588f1adb1dd745af1b9b8530dfb7',
 'entry':'bodhan_genai.tts.engine.offline.IndicTTSEngine','adapter':'redpad_pipeline.native_voice_worker',
 'selected_repo':'bodhan-ai/indic-speak','selected_revision':'76e0814f189321efe550011850cd288dae366aad',
 'selected_source_verified':True,'selected_entry':'inference.TTS.__call__; offline constructor replacement in native_voice_worker',
 'missing':[],
 'reason':'Exact selected source reviewed through owner-authenticated Chrome. Local bundle/dependency/license approval and actual runtime/listening remain pending; no inference authority.'},
 'indicf5':{'repo':'AI4Bharat/IndicF5','revision':'13f7c4d627cc10111aea8fe9c0039462cacacdc7',
 'entry':'redpad_pipeline.native_voice_worker.build_selected_f5','adapter':'redpad_pipeline.native_voice_worker','selected_repo':'ai4bharat/IndicF5','selected_revision':'fb652a96e508091045890dae5bb99fe511facbcf',
 'selected_source_verified':True,'selected_entry':'fixed local INF5Model structure + exact f5_tts.infer.utils_infer.infer_process',
 'missing':[],
 'reason':'Exact custom source reviewed; model.py itself must NEVER execute (unguarded downloads/inference/upload). Fixed local constructor and strict selected wrapper state replace it. Actual checkpoint layout/shape/runtime/listening remain unverified.'}}

def binding_status(pid):
    if pid=='indic_parler':return {'profile':pid,'adapter_implemented':True,'source_blocked':False,'runtime_verified':False,'fallback':None}
    if pid not in PUBLIC_SOURCE:raise AgentError('Not an existing selected voice candidate.')
    p=PUBLIC_SOURCE[pid]
    from .no_gpu_staging import load
    registry,_=load();selected=registry['profiles'][pid]
    if (selected['repo'],selected['revision'])!=(p['selected_repo'],p['selected_revision']):raise AgentError('Voice source/checkpoint identity changed; no version substitution.')
    from .voice_native_contracts import source_lock
    reviewed=source_lock()['models'][pid]
    if (reviewed['repo'],reviewed['revision'])!=(p['selected_repo'],p['selected_revision']) or not reviewed['files']:raise AgentError('Selected voice source review identity differs.')
    return {'profile':pid,'adapter_implemented':True,'source_blocked':not p['selected_source_verified'],
            'adapter_scope':'exact selected source binding; runtime disabled until separate explicit authorization',
            'selected_binding_implemented':True,'source_evidence':'assets/professional/phase3_voice_selected_source_lock.json',
            'launch_authorized':False,'production_integrated':False,
            'runtime_verified':False,'fallback':None,'blocker':p['reason'],'missing_source':p['missing']}

def require_selected_source(pid):
    if binding_status(pid)['source_blocked']:raise AgentError('Exact selected voice source access/review pending; native loader disabled, no fallback.')
