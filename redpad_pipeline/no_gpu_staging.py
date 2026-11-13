"""Pure candidate contracts. No runtime probes, model loading, network or promotion.

These drafts complement SharedServices; they are never executable model routes.
Publisher modalities, implemented controls and professional acceptance are separate.
"""
import hashlib
import json
import re
from pathlib import Path
from .agents import AGENTS, AgentError, encode

ROOT=Path(__file__).resolve().parents[1]
STAGING=ROOT/'assets/professional/phase3_19agent_no_gpu_staging.json'
REGISTRY=ROOT/'assets/professional/phase3_candidates.json'
EXCLUDED={'director','script'}
OPERATIONS={
 'qc':['text','image_inspection','audio_inspection'], 'story':['text'],
 'character':['text','reference_edit'], 'art':['text','reference_edit'],
 'location':['reference_edit','image_inspection'], 'costume':['reference_edit','text'],
 'storyboard':['reference_edit','text'], 'performance':['text','reference_video','video_inspection'],
 'cinematographer':['text','image_inspection'], 'motion':['reference_video','image_inspection'],
 'video':['image_to_video','text_to_video'], 'voice':['text_to_audio','reference_voice'],
 'continuity':['text','image_inspection'], 'music':['music','sound_effect'],
 'editing':['text','image_inspection','audio_inspection','assembly_receipt'],
 'production_manager':['text','schedule_check'], 'growth':['text','reference_edit','read_only_analytics'],
 'youtube':['text','read_only_analytics','release_manifest'],
 'casting':['text','reference_edit','reference_video','text_to_audio','video_inspection']}
TOOLS={'assembly_receipt','schedule_check','read_only_analytics','release_manifest'}
OFFLINE_TOOLS={'state_ledger':('continuity','qc'),'edit_manifest':('editing',),'cue_manifest':('music',),
               'temporal_assessment':('performance','motion','casting'),'voice_metadata':('voice',),'casting_evidence':('casting',)}
TOOLS.update(OFFLINE_TOOLS)
for _operation,_roles in OFFLINE_TOOLS.items():
    for _role in _roles:OPERATIONS[_role].append(_operation)
CONTRACT_ONLY={'wan_animate2','wan_animate2_distilled','ltx25','indic_speak','indicf5','ace15'}
LEGACY={'wan22_5':('offline_media','wan-local'),'svd_xt':('offline_media','local-svd'),
        'indic_parler':('offline_speech','bengali-tts'),'stable_audio_small':('offline_audio','stable-audio-small')}


def fingerprint(value):
    encode(value)
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def candidate_ids(role,row):
    ids=[row['primary_research_candidate']]+row['alternative_research_candidates']
    suite=json.loads((ROOT/'assets/professional/suite.json').read_text())
    if role not in EXCLUDED and 'image_inspection' in OPERATIONS[role] and 'vision7' in suite['agents'][role]['candidate_models']:ids+=['vision7']
    return ids


def resolve_profile(id,registry):
    if id!='vision7':return registry['profiles'][id]
    p=json.loads((ROOT/'assets/professional/models.json').read_text())['models']['vision7']
    if p.get('repo')!='Qwen/Qwen2.5-VL-7B-Instruct' or not re.fullmatch('[a-f0-9]{40}',p.get('revision','')):raise AgentError('Supplemental critic is not the exact supported pinned model family.')
    return {**p,'id':'vision7','adapter':'existing_vision_adapter','execution_modalities':['image_inspection'],
            'precision':p['precision_and_limits'],'license_conditions':p['commercial_use'],
            'planning_gpu_gib':max(p['gpu_vram_gib_planning_range']),
            'planning_ram_gib':p['host_ram_gib_planning'],
            'profile_catalog':'assets/professional/models.json'}


def _load():
    registry=json.loads(REGISTRY.read_text());stage=json.loads(STAGING.read_text())
    if stage.get('source_registry')!='assets/professional/phase3_candidates.json' or stage.get('source_registry_version')!=registry['version']:
        raise AgentError('Staging registry identity/version changed.')
    if any(stage.get(k) is not False for k in ('models_inferred','weights_downloaded','production_routes_changed')) or stage.get('validated_winners')!=0:
        raise AgentError('A no-inference staging file cannot assert production/model acceptance.')
    roles=stage.get('roles',[])
    if stage.get('excluded_agents')!=['director','script'] or stage.get('total_agents')!=19 or len(roles)!=19 or {r.get('agent') for r in roles}!=set(AGENTS)-EXCLUDED:
        raise AgentError('Staging must preserve exactly 19 roles and exclude Director/Script.')
    if set(OPERATIONS)!=set(AGENTS)-EXCLUDED:raise AgentError('Operation scope differs from the 21-agent catalog.')
    for row in roles:
        if row.get('production_routing_allowed') is not False or row.get('winner_selected') is not False:
            raise AgentError('Staging cannot promote a candidate.')
        original=registry['agents'][row['agent']]
        ids=[row['primary_research_candidate']]+row['alternative_research_candidates']
        if ids!=[original['primary_candidate']]+original['secondary_candidates'] or len(set(ids))!=len(ids):
            raise AgentError('Candidate binding drift; no silent replacement.')
        if [v['profile'] for v in row['model_links']]!=ids:raise AgentError('Staged model links differ.')
        for link in row['model_links']:
            p=registry['profiles'].get(link['profile'])
            if not p or not re.fullmatch('[a-f0-9]{40}',p['revision']) or link['repo']!=p['repo'] or link['adapter']!=p['adapter']:
                raise AgentError('Unpinned or mismatched candidate adapter.')
    return registry,{r['agent']:r for r in roles}


def load():
    try:return _load()
    except AgentError:raise
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        raise AgentError('Invalid no-GPU staging configuration; no execution enabled.') from None


def capabilities(profile):
    adapter=profile['adapter']
    if adapter=='hf_text_nf4':return {'text'}
    if adapter=='flux2_klein':return {'text_to_image','reference_edit'}
    if adapter=='z_image':return {'text_to_image'}
    if adapter=='existing_vision_adapter':return {'image_inspection'}
    if profile['id'] in LEGACY or profile['id'] in CONTRACT_ONLY:
        return set(profile['execution_modalities'])
    return set()


def fields(r,keys):
    if not isinstance(r,dict) or set(r)!=set(keys):raise AgentError('Exact bounded controls required; endpoints and unsupported controls prohibited.')
    encode(r)


def text(value,maximum=1000):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum:raise AgentError('Bounded nonempty text required.')


def integer(value,low,high):
    if type(value) is not int or not low<=value<=high:raise AgentError('Integer control exceeds staging bounds.')


def ref(value):
    fields(value,('id','version'));text(value['id'],100);integer(value['version'],1,2**31-1)


def validate_request(p,operation,r):
    """Checks only; legacy preflight/generate are deliberately never called."""
    if operation not in capabilities(p):raise AgentError('Unsupported modality; a generator is not an image/video/audio critic.')
    if p['adapter'] in ('hf_text_nf4','flux2_klein','z_image'):
        from .shared_model_services import validate_request as existing
        existing(p,r)
        if p['adapter']!='hf_text_nf4' and ((operation=='reference_edit')!=bool(r['references'])):
            raise AgentError('Reference editing requires references; text-to-image must not imply reference control.')
    elif p['adapter']=='existing_vision_adapter':
        fields(r,('images','question','seed'));text(r['question'],1200);integer(r['seed'],0,2**31-1)
        if not isinstance(r['images'],list) or not 1<=len(r['images'])<=3:raise AgentError('One to three exact image/frame references required; no whole-video/audio claim.')
        for item in r['images']:ref(item)
    elif p['id'] in ('wan22_5','svd_xt'):
        from .offline_media import CATALOG,validate_request as existing
        engine=LEGACY[p['id']][1]
        fields(r,('mode','prompt','width','height','frames','fps','steps','seed','reference'))
        if r['mode']!=operation:raise AgentError('Native mode differs; no T2V/I2V substitution.')
        native=dict(r);reference=native.pop('reference')
        if operation=='image_to_video':ref(reference);native['reference']='references/STAGED_ONLY.png'
        elif reference is not None:raise AgentError('Text-to-video cannot silently consume reference media.')
        if CATALOG[engine]['model']!=p['repo']:raise AgentError('Legacy model differs from exact profile.')
        existing(engine,native)
        if p['id']=='svd_xt' and r['prompt'].strip():raise AgentError('SVD does not execute text prompt conditioning.')
    elif p['id']=='indic_parler':
        from .offline_speech import PRESETS,STYLES,MODEL
        fields(r,('text','language','preset','style','seed'))
        if MODEL!=p['repo'] or r['language']!='bn' or r['preset'] not in PRESETS or r['style'] not in STYLES:raise AgentError('Unsupported Bengali preset/style/model.')
        text(r['text'],300);integer(r['seed'],0,2**31-1)
        if not re.search('[\u0980-\u09ff]',r['text']):raise AgentError('Bengali transcript required.')
    elif p['id']=='stable_audio_small':
        from .offline_audio import ENGINES,STABLE_AUDIO_SMALL_RECIPE
        if ENGINES['stable-audio-small']['model']!=p['repo']:raise AgentError('Audio profile identity differs.')
        fields(r,('prompt','seconds','seed','steps'));text(r['prompt'],1000);integer(r['seed'],0,2**31-1)
        if type(r['seconds']) not in (int,float) or not .5<=r['seconds']<=11 or type(r['steps']) is not int or r['steps']!=STABLE_AUDIO_SMALL_RECIPE['steps']:raise AgentError('Pinned Small profile uses native 8-step recipe, bounded to 11 seconds; not the older audio default.')
    elif operation in ('text_to_video','image_to_video','audio_video','reference_video'):
        fields(r,('prompt','seconds','seed','image_reference','video_reference'))
        text(r['prompt']);integer(r['seconds'],1,5);integer(r['seed'],0,2**31-1)
        for k in ('image_reference','video_reference'):
            if r[k] is not None:ref(r[k])
        if operation=='reference_video' and (r['image_reference'] is None or r['video_reference'] is None):raise AgentError('Animation/motion transfer needs distinct image AND video references.')
        if operation=='image_to_video' and r['image_reference'] is None:raise AgentError('Image-to-video needs an image reference.')
        if operation in ('text_to_video','audio_video') and any(r[k] is not None for k in ('image_reference','video_reference')):raise AgentError('Unsupported reference conditioning for this draft operation.')
        if operation=='image_to_video' and r['video_reference'] is not None:raise AgentError('Image-to-video is not motion transfer.')
    elif operation in ('text_to_audio','reference_voice'):
        keys=('text','language','speaker_id','seed')
        if operation=='reference_voice':keys+=('reference','reference_transcript','consent_reference')
        fields(r,keys);text(r['text'],300);text(r['speaker_id'],100);integer(r['seed'],0,2**31-1)
        if r['language']!='bn' or not re.search('[\u0980-\u09ff]',r['text']):raise AgentError('Bengali speech contract required.')
        if operation=='reference_voice':ref(r['reference']);ref(r['consent_reference']);text(r['reference_transcript'],1000)
    elif operation=='music':
        fields(r,('prompt','seconds','seed'));text(r['prompt']);integer(r['seconds'],1,15);integer(r['seed'],0,2**31-1)
    else:raise AgentError('No safe non-inference contract for this exact candidate.')
    return r


def prepare(role,profile_id,operation,request):
    if any(not isinstance(s,str) or not s for s in (role,profile_id,operation)):raise AgentError('Explicit agent/profile/operation identifiers required.')
    registry,roles=load()
    if role not in roles:raise AgentError('Outside 19-agent scope; Director/Script are untouched.')
    row=roles[role];ids=candidate_ids(role,row)
    if profile_id not in ids or operation not in set(OPERATIONS[role])|{'text_to_image'}:raise AgentError('Agent/candidate/operation binding not authorized.')
    p=resolve_profile(profile_id,registry);validate_request(p,operation,request)
    blockers=['No-GPU staging only: no model/runtime queried or executed.',
              'Exact installed files, revision, precision, component hashes, owner download/license approval and measured runtime must pass existing execution gates.',
              'Raw output and provenance, technical benchmark, independent specialist review and owner acceptance remain mandatory.']
    if profile_id in CONTRACT_ONLY:blockers.append('Exact execution adapter is not implemented; contract validation only. No legacy replacement.')
    if profile_id in LEGACY:blockers.append('Legacy native controls reused; exact profile installation binding and runtime API still need verification. No executable route enabled.')
    if profile_id=='vision7':blockers.append('Existing suite-authorized image critic staged explicitly as supplemental, not a primary replacement. Exact installation binding/API/calibration unverified; no whole-video or listening capability.')
    if operation=='reference_voice':blockers.append('Specific voice-reference consent and speaker identity need independent confirmation; reference rights metadata alone is insufficient.')
    payload={'role':role,'profile':profile_id,'operation':operation,'request':request,
             'profile_sha256':fingerprint(p),'repo':p['repo'],'revision':p['revision'],
             'precision':p['precision'],'license_conditions':p['license_conditions'],
             'planning_gpu_gib':p['planning_gpu_gib'],'planning_ram_gib':p['planning_ram_gib'],
             'configuration_validated':True,'runtime_verified':False,'inference_verified':False,
             'production_ready':False,'human_reviewed':False,'fallback':None,'blockers':blockers,
             'output_requirements':{'raw_response_or_original_media_required':True,
                                    'exact_model_manifest_and_precision_required':True,
                                    'request_source_and_reference_hashes_required':True,
                                    'finish_truncation_and_runtime_metrics_required':True,
                                    'artistic_acceptance':'existing independent QC / ProfessionalLab / owner gates only'}}
    return json.loads(encode(payload))


def tool_request(role,operation,request):
    if role not in OPERATIONS or operation not in set(OPERATIONS[role])&TOOLS:raise AgentError('Deterministic operation is not authorized for this role.')
    if operation in OFFLINE_TOOLS:
        from .offline_department_contracts import check
        return check(role,operation,request)
    if operation=='read_only_analytics':
        fields(request,('operation','channel_id'))
        from .youtube import channel_id
        channel_id(request['channel_id'])
        if request['operation'] not in ('channel_profile','video_statistics'):raise AgentError('Read-only channel operations only; never upload/publish/schedule.')
    elif operation=='schedule_check':
        fields(request,('tasks','budget_seconds'));integer(request['budget_seconds'],1,86400)
        if not isinstance(request['tasks'],list) or not 1<=len(request['tasks'])<=100:raise AgentError('Bounded task schedule required.')
        names=set();cost=0
        for t in request['tasks']:
            fields(t,('id','seconds','depends_on'));text(t['id'],100);integer(t['seconds'],1,86400)
            if t['id'] in names or not isinstance(t['depends_on'],list) or any(not isinstance(d,str) or d not in names for d in t['depends_on']):raise AgentError('Schedule must be unique and topologically ordered.')
            names.add(t['id']);cost+=t['seconds']
        if cost>request['budget_seconds']:raise AgentError('Sequential schedule exceeds resource budget.')
    else:
        fields(request,('sources',))
        if not isinstance(request['sources'],list) or not request['sources']:raise AgentError('Actual source receipts required; no fabricated assembly/release.')
        for s in request['sources']:
            fields(s,('id','revision','sha256'));text(s['id'],100);integer(s['revision'],1,2**31-1)
            if not isinstance(s['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',s['sha256']):raise AgentError('Source content hash required.')
    return {'role':role,'operation':operation,'request':json.loads(encode(request)),
            'scope':'validation_only_no_external_query_no_assembly_no_publication',
            'executed':False,'production_ready':False}


def readiness():
    registry,roles=load();result={}
    for role,row in roles.items():
        ids=candidate_ids(role,row)
        coverage={op:[k for k in ids if op in capabilities(resolve_profile(k,registry))] for op in OPERATIONS[role] if op not in TOOLS}
        gaps=[op for op,ids_for_op in coverage.items() if not ids_for_op]
        missing=[k for k in ids if k in CONTRACT_ONLY or k in LEGACY or k=='vision7']
        result[role]={'engineering_status':'PARTIAL' if gaps or missing else 'NO-GPU ENGINEERING COMPLETE',
                      'configuration_validated':True,'operation_candidates':coverage,
                      'unsupported_required_operations':gaps,'execution_binding_pending':missing,
                      'deterministic_operations':sorted(set(OPERATIONS[role])&TOOLS),
                      'gpu_status':'GPU TEST BLOCKED','human_status':'OWNER REVIEW PENDING',
                      'production_ready':False,'runtime_verified':False,
                      'vision_dependency_note':'Existing suite-authorized models.json vision7 staged separately; image/frame inspection only, no whole-video or audio judgment.' if 'vision7' in ids else None}
    from .offline_preparation import readiness_updates
    return readiness_updates(result)


def reference_inputs(p,operation,request):
    if operation in OFFLINE_TOOLS:
        from .offline_department_contracts import reference_inputs_for_check
        return reference_inputs_for_check(operation,request)
    image={'.png','.jpg','.jpeg','.webp'};video={'.mp4','.mov','.webm'};audio={'.wav','.mp3','.m4a'}
    if operation=='reference_edit':return [(r,image,True) for r in request['references']]
    if operation=='image_inspection':return [(r,{'.png','.jpg','.jpeg'},False) for r in request['images']]
    if p['id'] in ('wan22_5','svd_xt') and operation=='image_to_video':return [(request['reference'],image,True)]
    result=[]
    for key,extensions in (('image_reference',image),('video_reference',video),('reference',audio),('consent_reference',{'.txt','.pdf','.docx'})):
        if request.get(key) is not None:result.append((request[key],extensions,key!='consent_reference'))
    return result


class StagingLedger:
    """Existing task store, additional immutable drafts only. Never a run executor."""
    def __init__(self,store):
        self.store=store
        from .agent_engine import Engine
        from .producer_references import References
        self.engine=Engine(store);self.references=References(store)
        with store.tx() as db:db.execute('CREATE TABLE IF NOT EXISTS shared_staging_requests(id TEXT PRIMARY KEY,run TEXT,payload TEXT,sha256 TEXT)')

    def _context(self,db,run):
        row=db.execute('SELECT * FROM agent_runs WHERE id=?',(run,)).fetchone()
        if not row or row['state']!='Ready for Input':raise AgentError('Stage only an existing queued run; no execution or retry.')
        task=self.store._task(db,row['task'])
        if task['agent'] in EXCLUDED or task['revision']!=row['expected_revision'] or task['state'] not in ('Assigned','Revision requested'):
            raise AgentError('Task role/revision/state changed or excluded.')
        sources,refs=self.engine._sources(db,row)
        self.store._current(db,dict(task,refs=encode(refs)))
        bound=self.engine._bind(json.loads(row['inputs']),sources)
        review=db.execute("SELECT id,actor,action,detail FROM events WHERE task=? AND action IN ('Request revision','Reject') ORDER BY id DESC LIMIT 1",(task['id'],)).fetchone()
        return {'run':run,'task':task['id'],'role':task['agent'],'expected_revision':task['revision'],
                'queued_mode':row['mode'],
                'revision_review_sha256':fingerprint(dict(review) if review else None),
                'inputs_sha256':hashlib.sha256(row['inputs'].encode()).hexdigest(),
                'bound_inputs_sha256':fingerprint(bound),
                'source_sha256':fingerprint(sources),'source_revisions':refs,
                'source_payload_hashes':{k:fingerprint(v) for k,v in sources.items()},
                'task_refs_sha256':hashlib.sha256(task['refs'].encode()).hexdigest()}

    def _pins(self,p,operation,request):
        result=[]
        for pin,extensions,identity in reference_inputs(p,operation,request):
            row=self.references.get(pin['id'])
            if row['version']!=pin['version'] or row['archived'] or row['extension'] not in extensions or not row['source'].strip():
                raise AgentError('Current exact reference version, type and source required.')
            if identity and row['rights'] not in ('fictional_ai','authorized_person'):
                raise AgentError('Identity reference rights unavailable; no voice/person substitution.')
            self.references.path(row)
            if p['id']=='vision7' and (row['bytes']>10*1024*1024 or row.get('width',0)*row.get('height',0)>4_000_000):
                raise AgentError('Image critic exceeds its bounded native inspection size.')
            result.append(row)
        return result

    def stage(self,run,profile_id,operation,request):
        registry,_=load()
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');context=self._context(db,run)
            plan=prepare(context['role'],profile_id,operation,request)
            pins=self._pins(resolve_profile(profile_id,registry),operation,request)
            payload={'schema':'no-gpu-task-bound-draft-v1','context':context,'plan':plan,'references':pins}
            token=fingerprint(payload);encoded=encode(payload)
            db.execute('INSERT OR IGNORE INTO shared_staging_requests VALUES (?,?,?,?)',(token,run,encoded,hashlib.sha256(encoded.encode()).hexdigest()))
            return {'id':token,**payload}

    def get(self,id):
        registry,_=load()
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM shared_staging_requests WHERE id=?',(id,)).fetchone()
            if not row or hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Unknown or altered staged draft.')
            payload=json.loads(row['payload']);plan=payload['plan']
            if fingerprint(payload)!=id or self._context(db,row['run'])!=payload['context']:raise AgentError('Task/source revision changed; staged draft is stale.')
            current=prepare(payload['context']['role'],plan['profile'],plan['operation'],plan['request']) if 'profile' in plan else tool_request(payload['context']['role'],plan['operation'],plan['request'])
            pins=self._pins(resolve_profile(plan['profile'],registry),plan['operation'],plan['request']) if 'profile' in plan else self._pins({'id':'deterministic'},plan['operation'],plan['request'])
            if current!=plan or pins!=payload['references']:
                raise AgentError('Profile/reference changed; staged draft is stale.')
            return {'id':id,**payload}

    def stage_tool(self,run,operation,request):
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');context=self._context(db,run)
            plan=tool_request(context['role'],operation,request)
            if operation in ('assembly_receipt','release_manifest'):
                revisions={s['id']:s['revision'] for s in context['source_revisions']}
                for source in request['sources']:
                    if revisions.get(source['id'])!=source['revision'] or context['source_payload_hashes'].get(source['id'])!=source['sha256']:
                        raise AgentError('Assembly/release source must match an actual approved task output; no invented receipt.')
            pins=self._pins({'id':'deterministic'},operation,request)
            payload={'schema':'no-gpu-task-bound-draft-v1','context':context,'plan':plan,'references':pins}
            token=fingerprint(payload);encoded=encode(payload)
            db.execute('INSERT OR IGNORE INTO shared_staging_requests VALUES (?,?,?,?)',(token,run,encoded,hashlib.sha256(encoded.encode()).hexdigest()))
            return {'id':token,**payload}
