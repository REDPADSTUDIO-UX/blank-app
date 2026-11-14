"""Eleven-department deterministic inspection/assembly contracts, no model execution."""
import math
import unicodedata
from .agents import AgentError,encode
from .no_gpu_staging import fields,text,integer,ref,fingerprint

PARTIAL_ROLES={'qc','location','performance','cinematographer','motion','video','voice','continuity','music','editing','casting'}
VISUAL_ROLES={'qc','location','cinematographer','continuity','editing','motion'}
CATEGORIES={'framing','lighting','blocking','screen_direction','spatial','prop','character','costume','uncertain'}
CHECKS={'state_ledger':{'continuity','qc'},'edit_manifest':{'editing'},'cue_manifest':{'music'},
        'temporal_assessment':{'performance','motion','casting'},'voice_metadata':{'voice'},'casting_evidence':{'casting'},'casting_assessment':{'casting'}}


def inspection_spec(role,spec,images):
    if role not in VISUAL_ROLES:raise AgentError('Image inspection does not prove acting, voice or temporal physics.')
    fields(spec,('reference_ids','dimensions','source_scope','metadata'))
    if spec['reference_ids']!=[p['id'] for p in images]:raise AgentError('Inspection references must match the staged image order.')
    if spec['source_scope']!='supplied_references_only':raise AgentError('No unsupported real-world location/identity claims.')
    if not isinstance(spec['dimensions'],list) or not spec['dimensions'] or any(d not in CATEGORIES for d in spec['dimensions']):raise AgentError('Unsupported inspection dimension.')
    if not isinstance(spec['metadata'],dict) or set(spec['metadata'])-{'lens_mm','lens_source','state_ledger'}:raise AgentError('Unknown inspection metadata.')
    if 'lens_mm' in spec['metadata']:
        n=spec['metadata']['lens_mm']
        if type(n) not in (int,float) or not math.isfinite(n) or not 1<=n<=2000 or not spec['metadata'].get('lens_source'):
            raise AgentError('Lens value requires supplied metadata evidence, not inference from pixels.')
        text(spec['metadata']['lens_source'],300)
    if 'state_ledger' in spec['metadata']:state_findings(spec['metadata']['state_ledger'])
    return {'spec_sha256':fingerprint(spec),'automatic_artistic_acceptance':False,'real_world_location_verified':False}


def visual_response(raw,spec):
    """Validates grounding declarations only. It cannot verify what an image shows."""
    from .screenwriter import model_json
    try:r=model_json(raw)
    except ValueError:raise AgentError('Keep raw visual response; malformed/ambiguous JSON is not repaired.') from None
    fields(r,('findings','abstain'))
    if type(r['abstain']) is not bool or not isinstance(r['findings'],list) or len(r['findings'])>30:raise AgentError('Bounded findings/explicit abstention required.')
    if r['abstain'] and r['findings']:raise AgentError('Abstention cannot simultaneously demand revisions.')
    for f in r['findings']:
        fields(f,('category','reference_id','region','observation','certainty'))
        if f['category'] not in spec['dimensions'] or f['reference_id'] not in spec['reference_ids']:raise AgentError('Finding is outside supplied dimensions/references.')
        if f['certainty'] not in ('visible','inferred','uncertain'):raise AgentError('Separate observation from inference.')
        text(f['observation'],1200)
        box=f['region']
        if not isinstance(box,list) or len(box)!=4 or any(type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=1 for n in box) or box[0]>=box[2] or box[1]>=box[3]:raise AgentError('Evidence region must be normalized x1,y1,x2,y2.')
    return {'response':r,'grounding_contract_valid':True,'judgment_accuracy_verified':False,
            'independent_qc_required':True,'human_review_pending':True,'production_approved':False}


def state_findings(rows):
    """Conflicts in supplied state data, not claims about unseen generated footage."""
    if not isinstance(rows,list) or len(rows)>200:raise AgentError('Bounded state ledger required.')
    seen={};findings=[]
    for r in rows:
        fields(r,('entity','kind','scene','time_ms','property','value','evidence_id'))
        if r['kind'] not in ('character','costume','prop','location'):raise AgentError('Unknown state kind.')
        for k in ('entity','scene','property','value','evidence_id'):text(r[k],300)
        integer(r['time_ms'],0,4200000)
        key=(r['entity'],r['kind'],r['scene'],r['time_ms'],r['property'])
        if key in seen and seen[key]['value']!=r['value']:
            findings.append({'code':'supplied_state_contradiction','first':seen[key]['evidence_id'],'second':r['evidence_id'],'key':list(key)})
        seen[key]=r
    return {'findings':findings,'scope':'same-scene/time supplied assertions only; cross-time changes need context','actual_visual_inspection':False}


def temporal_spec(r):
    fields(r,('source_video','duration_ms','frame_times_ms','checks'))
    ref(r['source_video']);integer(r['duration_ms'],1,30000)
    times=r['frame_times_ms']
    if not isinstance(times,list) or not 2<=len(times)<=12:raise AgentError('Distinct ordered temporal sample times required.')
    for t in times:integer(t,0,r['duration_ms']-1)
    if times!=sorted(set(times)):raise AgentError('Distinct ordered temporal sample times required.')
    if not isinstance(r['checks'],list) or not r['checks'] or any(c not in ('contact','trajectory','occlusion','weight','listening','chemistry','gesture') for c in r['checks']):raise AgentError('Unsupported temporal assessment.')
    return {'contract_valid':True,'temporal_judgment_verified':False,'requires_actual_video_and_human_review':True}


def voice_metadata(r):
    fields(r,('original_text','language','speaker_id','pronunciation_notes','style_notes','reference','consent_reference'))
    text(r['original_text'],300);text(r['speaker_id'],100)
    if r['language']!='bn':raise AgentError('This workflow requires explicit Bengali speech.')
    for k in ('pronunciation_notes','style_notes'):
        if not isinstance(r[k],str) or len(r[k])>1000:raise AgentError('Bounded owner annotations required.')
    if r['reference'] is not None:
        ref(r['reference'])
        if r['consent_reference'] is None:raise AgentError('Reference-conditioned voice needs separate specific consent evidence.')
        ref(r['consent_reference'])
    elif r['consent_reference'] is not None:raise AgentError('Consent evidence must identify its voice reference.')
    normalized=unicodedata.normalize('NFC',r['original_text'])
    return {**r,'normalized_text':normalized,'normalization':'NFC only; no wording/pronunciation rewrite',
            'speaker_verified':False,'consent_verified':False,'listening_review_pending':True}


def cue_manifest(r):
    fields(r,('scene_id','scene_duration_ms','cues'))
    text(r['scene_id'],100);integer(r['scene_duration_ms'],1,4200000)
    if not isinstance(r['cues'],list) or not 1<=len(r['cues'])<=100:raise AgentError('Bounded cues required.')
    ids=set()
    for c in r['cues']:
        fields(c,('id','kind','start_ms','end_ms','beat','source_reference'))
        text(c['id'],100);text(c['beat'],300)
        if c['id'] in ids or c['kind'] not in ('music','sfx'):raise AgentError('Duplicate cue or unsupported mode.')
        ids.add(c['id']);integer(c['start_ms'],0,r['scene_duration_ms']-1);integer(c['end_ms'],c['start_ms']+1,r['scene_duration_ms'])
        if c['source_reference'] is not None:ref(c['source_reference'])
    return {'contract_valid':True,'cue_sha256':fingerprint(r),'audio_generated':False,'beat_alignment_listened':False}


def edit_manifest(r):
    fields(r,('duration_ms','tolerance_ms','sources','cuts'))
    integer(r['duration_ms'],1,4200000);integer(r['tolerance_ms'],0,100)
    if not isinstance(r['sources'],list) or not isinstance(r['cuts'],list) or not 1<=len(r['cuts'])<=100:raise AgentError('Bounded source/edit manifest required.')
    sources={}
    for s in r['sources']:
        fields(s,('reference','duration_ms','streams'));ref(s['reference']);integer(s['duration_ms'],1,4200000)
        if not isinstance(s['streams'],list) or not s['streams'] or any(v not in ('video','audio') for v in s['streams']):raise AgentError('Actual source stream metadata required.')
        if s['reference']['id'] in sources:raise AgentError('Duplicate source reference.')
        sources[s['reference']['id']]=s
    tracks={'video':[],'audio':[]};decisions=[]
    for c in r['cuts']:
        fields(c,('source_id','track','in_ms','out_ms','timeline_ms'))
        if c['source_id'] not in sources or c['track'] not in tracks:raise AgentError('Unknown source or track.')
        s=sources[c['source_id']]
        if c['track'] not in s['streams']:raise AgentError('Requested source stream missing.')
        integer(c['in_ms'],0,s['duration_ms']-1);integer(c['out_ms'],c['in_ms']+1,s['duration_ms']);integer(c['timeline_ms'],0,r['duration_ms']-1)
        end=c['timeline_ms']+c['out_ms']-c['in_ms']
        if end>r['duration_ms']:raise AgentError('Cut exceeds timeline.')
        tracks[c['track']].append((c['timeline_ms'],end));decisions.append({**c,'timeline_end_ms':end})
    for intervals in tracks.values():
        intervals.sort()
        if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):raise AgentError('Overlapping cuts require an explicitly supported mix/transition; no implicit effects.')
        if intervals and (intervals[0][0]!=0 or any(a[1]!=b[0] for a,b in zip(intervals,intervals[1:]))):raise AgentError('Timeline gaps need explicit approved black/silence sources; no fabricated filler.')
    if not tracks['video']:raise AgentError('Video edit needs video evidence.')
    if tracks['audio'] and (abs(tracks['audio'][0][0]-tracks['video'][0][0])>r['tolerance_ms'] or abs(tracks['audio'][-1][1]-tracks['video'][-1][1])>r['tolerance_ms']):raise AgentError('A/V boundaries exceed synchronization tolerance.')
    return {'edit_decisions':decisions,'ffmpeg_preparation':'fixed trim/atrim + setpts/asetpts; render through existing approved editing workflow only',
            'rendered':False,'actual_av_sync_verified':False,'source_sha256':fingerprint(r['sources']),
            'qc_required':True,'owner_approval_required':True}


def casting_evidence(r):
    fields(r,('actor_id','identity_kind','image_references','voice_reference','performance_reference','partner_actor_id','consent_reference'))
    text(r['actor_id'],100)
    if r['identity_kind'] not in ('fictional','authorized_person'):raise AgentError('Explicit fictional or authorized identity required.')
    if not isinstance(r['image_references'],list) or not 1<=len(r['image_references'])<=3:raise AgentError('Bounded exact actor references required.')
    for p in r['image_references']:ref(p)
    for k in ('voice_reference','performance_reference','consent_reference'):
        if r[k] is not None:ref(r[k])
    if r['identity_kind']=='authorized_person' and r['consent_reference'] is None:raise AgentError('Real actor/speaker needs specific consent evidence.')
    if r['partner_actor_id'] is not None:
        text(r['partner_actor_id'],100)
        if r['partner_actor_id']==r['actor_id'] or r['performance_reference'] is None:raise AgentError('Chemistry assessment needs another actor and actual partner-performance evidence.')
    return {'acting_verified':False,'voice_verified':False,'chemistry_verified':False,'appearance_is_not_performance':True,
            'existing_casting_director_inspection_and_producer_lock_required':True}


def check(role,operation,request):
    if role not in CHECKS.get(operation,set()):raise AgentError('Offline check outside the eleven-agent responsibility scope.')
    from .offline_specialist_preparation import casting_assessment
    functions={'state_ledger':state_findings,'edit_manifest':edit_manifest,'cue_manifest':cue_manifest,
               'temporal_assessment':temporal_spec,'voice_metadata':voice_metadata,'casting_evidence':casting_evidence,'casting_assessment':casting_assessment}
    result=functions[operation](request)
    return {'role':role,'operation':operation,'request':request,'check_result':result,
            'scope':'CPU contract/supplied evidence only; no generation, runtime, artistic approval or publishing',
            'executed':False,'production_ready':False}


def reference_inputs_for_check(operation,r):
    image={'.png','.jpg','.jpeg','.webp'};audio={'.wav','.mp3','.m4a'};video={'.mp4','.mov','.webm'};doc={'.txt','.pdf','.docx'}
    if operation=='casting_assessment':
        from .offline_specialist_preparation import casting_assessment
        kinds={'image':image,'video':video,'audio':audio,'document':doc}
        return [(pin,kinds[kind],kind!='document') for pin,kind in casting_assessment(r)['reference_requirements']]
    if operation=='edit_manifest':return [(s['reference'],video|audio,True) for s in r['sources']]
    if operation=='cue_manifest':return [(c['source_reference'],audio,True) for c in r['cues'] if c['source_reference'] is not None]
    if operation=='temporal_assessment':return [(r['source_video'],video,False)]
    if operation=='voice_metadata':return [(r[k],extensions,identity) for k,extensions,identity in [('reference',audio,True),('consent_reference',doc,False)] if r[k] is not None]
    if operation=='casting_evidence':return [(p,image,True) for p in r['image_references']]+[(r[k],extensions,identity) for k,extensions,identity in [('voice_reference',audio,True),('performance_reference',video,True),('consent_reference',doc,False)] if r[k] is not None]
    return []


def critic_control(raw,spec,expected_categories):
    result=visual_response(raw,spec)
    if not isinstance(expected_categories,list) or any(c not in spec['dimensions'] for c in expected_categories):raise AgentError('Explicit seeded-control truth required.')
    findings=result['response']['findings']
    categories={f['category'] for f in findings if f['certainty']=='visible'}
    reported={f['category'] for f in findings}
    expected=set(expected_categories)
    return {**result,'control_pass':categories==expected and reported==expected,'false_positive_categories':sorted(reported-expected),
            'missed_categories':sorted(expected-categories),'artistic_acceptance':False}
