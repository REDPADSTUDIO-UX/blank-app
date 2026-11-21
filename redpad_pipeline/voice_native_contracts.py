"""Exact selected voice contracts. Metadata/pure Python only; never inference.

The gated source was read, not executed. Public-engine and selected-checkpoint
recipes remain separate. Source access grants neither weights nor runtime rights.
"""
import hashlib,json,os,unicodedata,wave
from pathlib import Path
from .agents import AgentError

LOCK=Path(__file__).resolve().parents[1]/'assets/professional/phase3_voice_selected_source_lock.json'
VOICE_PINS={'indic_speak':'76e0814f189321efe550011850cd288dae366aad',
            'indicf5':'fb652a96e508091045890dae5bb99fe511facbcf'}
BENGALI_SPEAKERS=('Ishita','Sourav')  # Exact voices.md Bengali recommendation, not invented IDs.
TOKEN_FINGERPRINT='b645cf6612315393eea21d29e94304bdbcbfee131a25de5eecf6bae6ee9f39c5'
F5_DIT=dict(dim=1024,depth=22,heads=16,ff_mult=2,text_dim=512,conv_layers=4)
F5_MEL=dict(n_fft=1024,hop_length=256,win_length=1024,n_mel_channels=100,target_sample_rate=24000,mel_spec_type='vocos')

def source_lock():
    try:return json.loads(LOCK.read_text())
    except (OSError,ValueError):raise AgentError('Selected voice source review manifest missing or invalid; no model imports.') from None

def validate_source_receipt(record):
    pid=record['profile'];locked=source_lock()['models'][pid]
    if (record['repo'],record['revision'],record['source_revision'])!=(locked['repo'],locked['revision'],VOICE_PINS[pid]):
        raise AgentError('Exact selected voice source/checkpoint revision required.')
    for name,row in locked['files'].items():
        if record['source_files'].get(name)!={k:row[k] for k in ('bytes','sha256')}:
            raise AgentError('Reviewed selected voice source differs: '+name)
    if set(record['source_files'])!=set(locked['files']):raise AgentError('Only reviewed selected source files may enter the voice source bundle.')
    # Config/vocabulary must belong to this checkpoint, even when model/code roots differ.
    for name in ('config.json','tokenizer_config.json','generation_config.json') if pid=='indic_speak' else ('config.json','checkpoints/vocab.txt'):
        if record['model_files'].get(name)!={k:locked['files'][name][k] for k in ('bytes','sha256')}:
            raise AgentError('Selected voice configuration/vocabulary differs.')

def validate_voice_request(pid,r,spec=None):
    from .no_gpu_staging import load,resolve_profile,validate_request
    registry,_=load();p=resolve_profile(pid,registry)
    validate_request(p,'reference_voice' if pid=='indicf5' else 'text_to_audio',r)
    if pid=='indic_speak' and r['speaker_id'] not in BENGALI_SPEAKERS:
        raise AgentError('Use an exact reviewed Bengali preset speaker: Ishita or Sourav; no inferred identity.')
    if any(c in r['text'] for c in ('<|','|>')):raise AgentError('Embedded model-control tokens are unsupported.')
    if pid=='indicf5' and (not r['reference_transcript'].strip() or any(c in r['reference_transcript'] for c in ('<|','|>'))):
        raise AgentError('Explicit nonempty reference transcript required; automatic ASR disabled.')
    if spec is not None and (spec.get('style_notes') or spec.get('pronunciation_notes')):
        # Existing owner notes remain evidence, never silently applied as model controls.
        pass
    return unicodedata.normalize('NFC',r['text'])

def validate_speak_tokenizer(tok):
    """Check every audio/conditioning ID, not merely the base/range.
    No tokenizer/model is loaded here; fake maps exercise this in CPU QA.
    """
    expected={'<|begin_of_text|>':128000,'<|end_of_text|>':128001,'<|eot_id|>':128009,
      '<|reserved_0|>':128256,'<|start_of_speech|>':128257,'<|end_of_speech|>':128258,
      '<|start_of_human|>':128259,'<|end_of_human|>':128260,'<|start_of_ai|>':128261,
      '<|end_of_ai|>':128262,'<|pad|>':128263,'<|reserved_8|>':128264,'<|reserved_9|>':128265,
      '<|speaker>':156938,'<speaker|>':156939,'<|style>':156940,'<style|>':156941,'<|env>':156942,'<env|>':156943}
    expected.update({f'<|snac_{i}|>':128266+i for i in range(28672)})
    expected.update({f'<|nv_{name}|>':156944+i for i,name in enumerate(('breath','stammer','throat','laugh','swallow','sniff','sigh','cough','hum','gasp','wheeze','sneeze','snort','yawn','groan','burp'))})
    if len(tok)!=156960 or tok.bos_token_id!=128000 or tok.eos_token_id!=128001 or any(tok.convert_tokens_to_ids(k)!=v for k,v in expected.items()):
        raise AgentError('Incompatible selected Indic-Speak token contract; no tokenizer fallback.')

def f5_vocab(path):
    """Match upstream newline-based indices without dropping space/combining marks."""
    p=Path(path)
    if not p.is_file() or p.is_symlink() or not 1<=p.stat().st_size<=128*1024:raise AgentError('Exact bounded local IndicF5 vocabulary required.')
    with p.open(encoding='utf-8',newline='') as f:lines=f.readlines()
    if any(not line.endswith('\n') for line in lines):raise AgentError('Unsupported vocabulary line endings.')
    vocab={line[:-1]:i for i,line in enumerate(lines)}
    if vocab.get(' ')!=0 or not all(c in vocab for c in 'বাংলা'):raise AgentError('Wrong IndicF5 character vocabulary.')
    return vocab,len(vocab)

def inspect_f5_reference(path):
    """Bounded signal/header guard only; no recognition or speaker/listening claim.
    infer_batch_process divides by RMS, so zero-energy input must fail before loading.
    """
    p=Path(path)
    if not p.is_file() or p.is_symlink():raise AgentError('Original local reference PCM WAV required.')
    try:
        with wave.open(str(p),'rb') as w:
            if w.getframerate()!=24000 or w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getcomptype()!='NONE' or not 2400<=w.getnframes()<=360000:
                raise AgentError('IndicF5 reference must be mono PCM16 24 kHz, 0.1–15 seconds; no implicit conversion.')
            raw=w.readframes(w.getnframes())
            if len(raw)!=w.getnframes()*2:raise AgentError('Truncated IndicF5 reference.')
        if not any(raw):raise AgentError('Zero-energy IndicF5 reference rejected before RMS division or model imports.')
    except (wave.Error,EOFError,OSError):raise AgentError('Invalid IndicF5 reference WAV.') from None
    return {'header_signal_checked':True,'listening_reviewed':False,'speaker_verified':False}

def require_voice_job(job):
    """Future execution authority is independent of source review and engineering."""
    pid=job.get('profile')
    if pid not in VOICE_PINS:raise AgentError('Exact selected native voice candidate required.')
    if job.get('research_execution_authorized') is not True or job.get('network_namespace_required') is not True:
        raise AgentError('Explicit isolated research launch authorization required; source access is insufficient.')
    parent=job.get('parent_network_namespace')
    if not parent or parent==os.readlink('/proc/self/ns/net'):raise AgentError('Kernel network isolation required before voice imports.')
    from .voice_source_policy import require_selected_source
    require_selected_source(pid)
    if job.get('install',{}).get('revision')!=VOICE_PINS[pid] or job['install'].get('profile')!=pid:raise AgentError('Voice installation revision differs.')
    validate_voice_request(pid,job.get('request',{}))
    if pid=='indicf5' and not job.get('consent',{}).get('explicit_human_review_recorded'):raise AgentError('Current scoped reference consent required before loading.')
    if pid=='indicf5':inspect_f5_reference(job.get('references',{}).get('reference',''))

def require_reference_consent(store,staged,spec):
    """Rechecked on prepare, queue, run and result, including revocation/staleness."""
    from .voice_consent import VoiceConsents
    r=staged['plan']['request'];task=staged['context']['task'];scope=task;receipt=spec.get('consent_review')
    with store.tx() as db:
        table=db.execute("SELECT 1 FROM sqlite_master WHERE name='casting_voice_drafts'").fetchone()
        row=db.execute('SELECT id,payload,sha256 FROM casting_voice_drafts WHERE voice_task=?',(task,)).fetchone() if table else None
    if row:
        from .no_gpu_staging import fingerprint
        d=json.loads(row['payload'])
        if hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256'] or fingerprint(d)!=row['id'] or d['plan']['profile']!='indicf5' or d['plan']['request']!=r or d['spec']!=spec:
            raise AgentError('Exact Casting voice consent handoff required.')
        scope=d['snapshot']['task'];receipt=d['consent_review']
    if not receipt:raise AgentError('Specific explicit human voice consent review required; document/rights metadata is insufficient.')
    return VoiceConsents(store).require(receipt,actor_id=r['speaker_id'],reference=r['reference'],document=r['consent_reference'],transcript=r['reference_transcript'],scope_task=scope)
