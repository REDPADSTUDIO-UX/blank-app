"""Six specialists: local source-reviewed call preparation, never execution.

No inference imports, process launch, runtime probe, weights read, approval creation
or downloader. Source review is not installed-runtime verification.
"""
import math
import unicodedata
from pathlib import Path, PurePosixPath
from .agents import AgentError
from .no_gpu_staging import fields, text, integer, ref, fingerprint, load, resolve_profile

ROLES={'performance','motion','video','voice','music','casting'}
PINS={'wan_animate2':'3ad2fef7d61d6200c9c653e0fe47be7616b323f3',
      'ltx25':'f0f2f8607189c78a72420b2b63cb1975b5eca179',
      'ace15':'ca1e85fe9430179831e6bc6be790c332190a3866'}
LTX_SLOTS={'transformer':'diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors',
 'text_encoder':'text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors',
 'video_vae':'vae/ltx-2.5-video-vae-bf16.safetensors',
 'audio_vae':'vae/ltx-2.5-audio-vae-bf16.safetensors',
 'duration_head':'model_patches/ltx-2.5-duration-head-bf16.safetensors'}
LTX_AUXILIARY={'repo':'Lightricks/LTX-2.5','revision':'49b093a39c19169a8a81721dcc541e07e945232f',
 'path':'latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors',
 'sha256':None,'bytes':None,'download_approved':False,'license_approved':False,
 'purpose':'Official two-stage distilled spatial upsampler; not the optional temporal upsampler or DFR detailing LoRA'}


def finite(value,low,high):
    if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:
        raise AgentError('Finite bounded numeric control required.')


def relative(value):
    text(value,300);p=PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value or str(p)!=value:
        raise AgentError('Canonical local relative component path required.')
    return value


def component_inventory(profile_id,folder):
    """Metadata-only inventory; stat real files, NEVER open or hash model weights.

    Presence/size cannot authenticate bytes. A separate future approved manifest
    verifier must authenticate every component before any model is loaded.
    """
    if profile_id not in {'wan_animate2','ltx25','indic_speak','indicf5','ace15'}:
        raise AgentError('Use existing native bundle verifier for other models; unsupported specialist profile.')
    registry,_=load();p=resolve_profile(profile_id,registry);root=Path(folder)
    if any(x.is_symlink() for x in (root,*root.parents)):raise AgentError('Symlink model root prohibited.')
    result=[]
    for item in p['selected_weight_files']:
        part=root/relative(item['path'])
        if any(x.is_symlink() for x in (part,*part.parents)):raise AgentError('Symlink model component prohibited.')
        present=part.is_file();size=part.stat().st_size if present else None
        result.append({'path':item['path'],'present':present,'expected_bytes':item['bytes'],
                       'actual_bytes':size,'size_matches':present and size==item['bytes'],
                       'expected_sha256':item['sha256'],'hash_verified':False})
    extras=[]
    if profile_id=='ltx25':extras=['spatial upsampler: same pinned LTX-2.5 repository layout per official card; exact artifact SHA/size and approval still unresolved',
                                'local tokenizer/config components required by split text encoder']
    elif profile_id=='wan_animate2':extras=['YAML T5 checkpoint + tokenizer, VAE checkpoint, CLIP checkpoint + tokenizer; exact revisions/hashes and safe .pth loaders unreviewed']
    elif profile_id=='indic_speak':extras=['pinned local inference code, SNAC/Vocos/config/tokenizer/speaker catalogue; safe best.pt loading review']
    elif profile_id=='indicf5':extras=['pinned reviewed local custom code, tokenizer/vocoder/config and specific reference voice consent']
    elif profile_id=='ace15':extras=['complete local component configs/tokenizers and model-side code; offline initialization guard review']
    return {'profile':profile_id,'repo':p['repo'],'revision':p['revision'],'profile_sha256':fingerprint(p),
            'files':result,'unresolved_components':extras,'required_auxiliary':LTX_AUXILIARY if profile_id=='ltx25' else None,'weights_opened':False,
            'bundle_authenticated':False,'ready_to_load':False,'status':'RUNTIME VALIDATION BLOCKED'}


def media_metadata(r,kind):
    fields(r,('reference','width','height','fps','frames','duration_ms','evidence'))
    ref(r['reference']);integer(r['width'],16,8192);integer(r['height'],16,8192)
    finite(r['fps'],1,120);integer(r['frames'],1,3600);integer(r['duration_ms'],1,30000)
    text(r['evidence'],500)
    # Supplied metadata only, no decoder/probe or automatic padding/retiming.
    if abs(r['duration_ms']-r['frames']*1000/r['fps'])>max(2,1000/r['fps']):
        raise AgentError('Frame count, rate and duration disagree; no silent retiming.')
    if kind!='video':raise AgentError('Only supplied video timing metadata is supported here.')


def permission(r,identities,uses,references):
    fields(r,('identity_kind','actor_ids','uses','reference_ids','consent_reference'))
    if r['identity_kind'] not in ('fictional','authorized_person'):raise AgentError('Explicit fictional/authorized identity required.')
    if not isinstance(r['actor_ids'],list) or not r['actor_ids'] or r['actor_ids']!=identities:raise AgentError('Consent subject differs from actor identity lock.')
    for actor in identities:text(actor,100)
    if len(identities)!=len(set(identities)):raise AgentError('Actor identities must be distinct.')
    if r['uses']!=uses or r['reference_ids']!=references:raise AgentError('Permission must name exact requested uses and reference identities.')
    if r['consent_reference'] is not None:ref(r['consent_reference'])
    elif r['identity_kind']=='authorized_person':raise AgentError('Specific real-person likeness/voice consent evidence required.')
    return [r['consent_reference']] if r['consent_reference'] is not None else []


def video_spec(spec,r,pid):
    fields(spec,('width','height','fps','frames','reference_prompt','driving_metadata','actor_id','permission','frame_sequence','interactions'))
    for key in ('width','height'):integer(spec[key],256,1280)
    divisor=64 if pid=='ltx25' else 16
    if spec['width']%divisor or spec['height']%divisor:raise AgentError('Dimensions outside conservative local preparation policy.')
    integer(spec['fps'],8,30);integer(spec['frames'],9,153)
    multiple=8 if pid=='ltx25' else 4
    if (spec['frames']-1)%multiple or abs(spec['frames']/spec['fps']-r['seconds'])>1/spec['fps']:
        raise AgentError('Frames/rate must match bounded duration; no frame rounding or duration substitution.')
    if not isinstance(spec['reference_prompt'],str) or len(spec['reference_prompt'])>1000:raise AgentError('Bounded reference prompt required.')
    pins=[]
    if pid=='wan_animate2':
        if spec['driving_metadata'] is None:raise AgentError('Driving video metadata required for native motion transfer.')
        media_metadata(spec['driving_metadata'],'video');m=spec['driving_metadata']
        if m['reference']!=r['video_reference'] or m['fps']!=spec['fps'] or m['frames']<spec['frames']:
            raise AgentError('Driving reference timing differs or would require undocumented looping/resampling.')
        text(spec['reference_prompt']);text(spec['actor_id'],100)
        permission(spec['permission'],[spec['actor_id']],['likeness','motion_transfer'],[r['image_reference']['id'],r['video_reference']['id']])
    elif spec['driving_metadata'] is not None:raise AgentError('LTX distilled preparation does not expose driving-video transfer.')
    elif r['image_reference'] is not None:
        text(spec['actor_id'],100)
        permission(spec['permission'],[spec['actor_id']],['likeness'],[r['image_reference']['id']])
    elif spec['permission'] is not None or spec['actor_id'] is not None:raise AgentError('No identity authority without a corresponding reference.')
    if spec['permission'] is not None and spec['permission']['consent_reference'] is not None:pins.append((spec['permission']['consent_reference'],'document'))
    seq=spec['frame_sequence']
    if not isinstance(seq,list) or len(seq)>12:raise AgentError('Bounded temporal frame sequence required.')
    times=[];ids=[]
    for f in seq:
        fields(f,('reference','time_ms','source_video'));ref(f['reference']);ref(f['source_video']);integer(f['time_ms'],0,r['seconds']*1000-1)
        if f['source_video']!=r['video_reference']:raise AgentError('Frame extraction must name the same motion source.')
        times.append(f['time_ms']);ids.append(f['reference']['id']);pins.append((f['reference'],'image'))
    if times!=sorted(set(times)) or len(ids)!=len(set(ids)):raise AgentError('Distinct ordered frame samples required.')
    if seq and len(seq)<2:raise AgentError('Temporal frame review needs at least two distinct samples.')
    if not isinstance(spec['interactions'],list) or len(spec['interactions'])>20:raise AgentError('Bounded object interaction specifications required.')
    for i in spec['interactions']:
        fields(i,('subject','object','start_ms','end_ms','constraint'))
        for k in ('subject','object','constraint'):text(i[k],300)
        integer(i['start_ms'],0,r['seconds']*1000-1);integer(i['end_ms'],i['start_ms']+1,r['seconds']*1000)
    return pins


def speech_spec(spec,r,pid):
    fields(spec,('style_notes','pronunciation_notes','reference_metadata','permission'))
    for k in ('style_notes','pronunciation_notes'):
        if not isinstance(spec[k],str) or len(spec[k])>1000:raise AgentError('Bounded owner speech annotations required.')
    pins=[]
    if pid=='indicf5':
        fields(spec['reference_metadata'],('reference','sample_rate','channels','duration_ms','transcript'))
        m=spec['reference_metadata'];integer(m['sample_rate'],8000,96000);integer(m['channels'],1,2);integer(m['duration_ms'],100,30000)
        if m['reference']!=r['reference'] or m['transcript']!=r['reference_transcript']:raise AgentError('Reference audio/transcript identity differs.')
        permission(spec['permission'],[r['speaker_id']],['voice_clone'],[r['reference']['id']])
        if spec['permission']['consent_reference']!=r['consent_reference']:raise AgentError('Voice clone consent document differs.')
        # Even fictional source voices require a specific consent/evidence review.
        pins.append((r['consent_reference'],'document'))
    elif spec['reference_metadata'] is not None or spec['permission'] is not None:
        raise AgentError('This preset model has no reference-voice cloning capability.')
    return pins


def music_spec(spec,r):
    fields(spec,('task_type','instrumental','lyrics','thinking','sample_rate','cue'))
    if spec['task_type']!='text2music' or spec['instrumental'] is not True or spec['lyrics']!='' or spec['thinking'] is not False or spec['sample_rate']!=48000:
        raise AgentError('Only bounded instrumental ACE 1.5 text2music preparation; no cover, vocals, LM or SFX substitution.')
    from .offline_department_contracts import cue_manifest
    cue_manifest(spec['cue'])
    if len(spec['cue']['cues'])!=1:raise AgentError('One exact scene cue per bounded audio request.')
    cue=spec['cue']['cues'][0]
    if cue['kind']!='music' or cue['end_ms']-cue['start_ms']!=r['seconds']*1000:raise AgentError('Instrumental request must match the music cue duration.')
    return [(cue['source_reference'],'audio')] if cue['source_reference'] is not None else []


def bind_pins(store,pins):
    from .producer_references import References
    refs=References(store);bound=[]
    extensions={'document':{'.txt','.pdf','.docx'},'image':{'.png','.jpg','.jpeg','.webp'},'audio':{'.wav','.mp3','.m4a'}}
    for pin,kind in pins:
        ref(pin);row=refs.get(pin['id'])
        if row['version']!=pin['version'] or row['archived'] or row['extension'] not in extensions[kind] or not row['source'].strip():raise AgentError('Current sourced specialist evidence of correct type required.')
        if kind!='document' and row['rights'] not in ('fictional_ai','authorized_person'):raise AgentError('Identity/motion/audio evidence rights unavailable.')
        refs.path(row);bound.append(row)
    return bound


def inspect_voice_reference(store,pin,metadata):
    """PCM WAV header/timing only; no listening, voice recognition or resampling."""
    import wave
    from .producer_references import References
    refs=References(store);row=refs.get(pin['id'])
    if row['version']!=pin['version'] or row['extension']!='.wav':raise AgentError('This offline reference preparation requires exact PCM WAV; no implicit conversion.')
    try:
        with wave.open(str(refs.path(row)),'rb') as w:
            channels=w.getnchannels();rate=w.getframerate();frames=w.getnframes();width=w.getsampwidth()
            if w.getcomptype()!='NONE' or width not in (1,2,3,4) or not 0<frames<=30*rate:raise AgentError('Bounded nonempty PCM voice reference required.')
            # readframes only the declared bounded audio, never any model files.
            if len(w.readframes(frames))!=frames*channels*width:raise AgentError('Truncated voice reference PCM data.')
    except (wave.Error,EOFError,OSError):raise AgentError('Invalid PCM voice reference.') from None
    if rate!=metadata['sample_rate'] or channels!=metadata['channels'] or abs(frames*1000/rate-metadata['duration_ms'])>2:
        raise AgentError('Actual WAV metadata differs from declared reference; no silent resampling.')
    return {'sample_rate':rate,'channels':channels,'duration_ms':frames*1000/rate,
            'metadata_checked':True,'transcript_verified':False,'speaker_verified':False,'listening_reviewed':False}


def prepare_specialist(staged,store,spec):
    plan=staged['plan'];role=plan['role'];pid=plan['profile'];r=plan['request']
    if role not in ROLES or pid not in ('wan_animate2','ltx25','indic_speak','indicf5','ace15'):raise AgentError('Unsupported specialist model binding.')
    registry,_=load();p=resolve_profile(pid,registry)
    # Shared staging has already checked role/candidate/operation/version/source locks.
    if pid in ('wan_animate2','ltx25'):pins=video_spec(spec,r,pid)
    elif pid in ('indic_speak','indicf5'):pins=speech_spec(spec,r,pid)
    else:pins=music_spec(spec,r)
    bound=bind_pins(store,pins)
    identity_rows=[row for row in staged.get('references',[])+bound if row['extension'] not in ('.txt','.pdf','.docx')]
    if any(row['rights']=='authorized_person' for row in identity_rows):
        permission_spec=spec.get('permission')
        if not permission_spec or permission_spec['identity_kind']!='authorized_person' or permission_spec['consent_reference'] is None:
            raise AgentError('Real-person reference cannot be relabeled fictional to bypass specific consent.')
    audio_header=inspect_voice_reference(store,r['reference'],spec['reference_metadata']) if pid=='indicf5' else None
    native={};blockers=[]
    if pid=='wan_animate2':
        native={'entry':'infer/wan_animate_2_demo.py','call':'WanAnimate2MPIPipeline.__call__',
                'arguments':{'width':spec['width'],'height':spec['height'],'fps':spec['fps'],'clip_len':spec['frames'],
                 'step':40,'sample_guide_scale':3.0,'seed':r['seed'],'prompt':r['prompt'],'prompt_ref':spec['reference_prompt']},
                'reference_bindings':{'refer_img_path':r['image_reference'],'tpl_video_path':r['video_reference']},
                'configuration':'infer/wan_animate_2.yaml; template only, never evaluated or passed through unchecked',
                'required_components':['selected BF16 transformer','T5 .pth + tokenizer','VAE .pth','CLIP .pth + tokenizer']}
        blockers=['Exact auxiliary revisions/hashes and .pth loading safety incomplete.',
                  'Native worker/process supervision implemented; actual MPI/device/dependency and owner full-code review remain runtime gates.']
    elif pid=='ltx25':
        native={'entry':'ltx_pipelines.distilled','call':'DistilledPipeline(model_paths=ModelPaths.from_split(...), spatial_upsampler_path=...)',
                'component_slots':LTX_SLOTS,'spatial_upsampler':None,
                'required_auxiliary':LTX_AUXILIARY,
                'arguments':{'prompt':r['prompt'],'seed':r['seed'],'width':spec['width'],'height':spec['height'],'num_frames':spec['frames'],'frame_rate':spec['fps'],'enhance_prompt':False},
                'image_conditioning':r['image_reference'],'precision_policy':'selected BF16 split only; no quantized substitute; version-specific quantization options require separate validation'}
        if any(v not in {f['path'] for f in p['selected_weight_files']} for v in LTX_SLOTS.values()):raise AgentError('Pinned LTX split component recipe changed.')
        blockers=['Spatial upsampler belongs to pinned LTX-2.5 repository layout per card, but exact file SHA/size, recipe inclusion and owner download/license approval unresolved.',
                  'Packed text encoder includes tokenizer/config assets; actual embedded metadata and BF16 runtime/package loading remain weight/runtime gates.']
    elif pid=='indicf5':
        native={'entry':'reviewed local IndicF5 callable required; remote AutoModel custom-code execution disabled',
                'arguments':{'text':unicodedata.normalize('NFC',r['text']),'ref_audio_path':r['reference'],'ref_text':r['reference_transcript']},'sample_rate':24000}
        blockers=['Pinned gated custom code and transitive local auxiliary loader not reviewed; no trust_remote_code enabled.', 'Specific voice consent and identity require independent confirmation.']
    elif pid=='indic_speak':
        native={'entry':None,'documented_current_card':'inference.TTS(local_directory), __call__(text,speaker), save(...); card example refers to preview-v2',
                'arguments':{'text':unicodedata.normalize('NFC',r['text']),'speaker':r['speaker_id']},'sample_rate':24000}
        blockers=['Exact selected revision inference implementation/speaker catalogue unavailable; current preview-v2 example cannot bind selected model.', 'Vocos best.pt/SNAC and gated upstream terms need review; no fallback or implicit download.']
    else:
        native={'entry':'acestep.inference.generate_music','handler':'acestep.handler.AceStepHandler',
                'arguments':{'params':{'task_type':'text2music','caption':r['prompt'],'lyrics':'','instrumental':True,'thinking':False,'use_cot_metas':False,'use_cot_caption':False,'use_cot_language':False,'duration':r['seconds'],'seed':r['seed'],'inference_steps':8},
                             'config':{'batch_size':1,'audio_format':'wav'}},
                'sample_rate':48000,'unsafe_auxiliary_policy':{'file':'acestep-v15-turbo/silence_latent.pt','expected_loader':'torch.load(weights_only=True) on authenticated local file; tensor type/shape/size/finite validation required before use'},
                'initialization_policy':{'automatic_download':False,'model_code_sync':False,'custom_code':False}}
        blockers=['Upstream auto-download/code-sync hooks are replaced by implemented deny-download/sync local bridge; authenticated full bundle and actual runtime remain mandatory.',
                  'Implemented bounded weights-only silence tensor checks; actual tensor compatibility and owner complete dependency/code approval remain required.']
    implemented=pid in PINS
    return {'stage_id':staged['id'],'profile':pid,'repo':p['repo'],'revision':p['revision'],
            'profile_sha256':fingerprint(p),'source_revision':PINS.get(pid),
            'native_call_preparation':native,'spec_sha256':fingerprint(spec),'extra_reference_pins':bound,
            'reference_audio_header':audio_header,'video_metadata_independently_verified':False,
            'original_request':r,'owner_annotations':spec,'status':'RUNTIME VALIDATION BLOCKED',
            'contract_only':not implemented,'worker_module':'redpad_pipeline.native_local_worker' if implemented else None,
            'native_worker_implemented':implemented,'launch_authorized':False,'inference_completed':False,
            'consent_verified':False,'human_reviewed':False,'production_ready':False,
            'required_output_evidence':['raw artifact and SHA256','exact approved complete model/code/dependency manifests','source/revision/reference pins','actual runtime/settings/finish status','independent QC','independent visual/listening review','owner acceptance'],
            'blockers':blockers}


def casting_assessment(spec):
    """A grounded future-review schema; cannot grant casting/identity approval."""
    fields(spec,('actor_id','character_id','portrait','performance','voice','voice_transcript','partner_actor_id','partner_performance','consent_reference','identity_kind','findings'))
    for k in ('actor_id','character_id'):text(spec[k],100)
    pins=[]
    for k,kind in [('portrait','image'),('performance','video'),('voice','audio'),('partner_performance','video'),('consent_reference','document')]:
        if spec[k] is not None:ref(spec[k]);pins.append((spec[k],kind))
    if spec['portrait'] is None:raise AgentError('Fictional/authorized casting portrait required.')
    if spec['identity_kind'] not in ('fictional','authorized_person') or (spec['identity_kind']=='authorized_person' and spec['consent_reference'] is None):raise AgentError('Specific real-person likeness/voice consent evidence required.')
    if spec['voice'] is not None:
        text(spec['voice_transcript'],1000)
        if spec['consent_reference'] is None:raise AgentError('Voice reference requires separate scoped consent evidence.')
    elif spec['voice_transcript'] is not None:raise AgentError('No transcript without voice evidence.')
    if spec['partner_actor_id'] is not None:
        text(spec['partner_actor_id'],100)
        if spec['partner_actor_id']==spec['actor_id'] or spec['partner_performance'] is None or spec['performance'] is None:raise AgentError('Chemistry needs distinct actor and actual pair performance evidence.')
    elif spec['partner_performance'] is not None:raise AgentError('Partner performance must identify the second actor.')
    if not isinstance(spec['findings'],list) or len(spec['findings'])>20:raise AgentError('Bounded casting findings required.')
    evidence={'appearance':[spec['portrait']],'performance':[spec['performance']],'voice':[spec['voice']],
              'chemistry':[spec['performance'],spec['partner_performance']]}
    for f in spec['findings']:
        fields(f,('category','reference_ids','observation','certainty'))
        if f['category'] not in evidence or f['certainty'] not in ('observed','inferred','abstain'):raise AgentError('Unsupported casting criterion/certainty.')
        text(f['observation'],1000)
        required=evidence[f['category']]
        if not isinstance(f['reference_ids'],list) or len(f['reference_ids'])!=len(set(f['reference_ids'])):raise AgentError('Distinct casting evidence IDs required.')
        if f['certainty']=='abstain':
            if f['reference_ids']:raise AgentError('Abstention cannot claim performance evidence.')
        elif any(x is None for x in required) or f['reference_ids']!=[p['id'] for p in required]:raise AgentError('A portrait cannot substantiate acting, voice or chemistry.')
    return {'reference_requirements':[[pin,kind] for pin,kind in pins],'schema_valid':True,'acting_verified':False,'chemistry_verified':False,
            'independent_qc_required':True,'director_inspection_required':True,'producer_identity_lock_required':True,
            'human_review_pending':True,'production_ready':False}
