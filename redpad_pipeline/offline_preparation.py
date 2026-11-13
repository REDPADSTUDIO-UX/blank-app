"""Exact existing-worker job preparation. Never launches a worker or loads a model.
Unknown upstream interfaces stay contract-only; no hosted URL or download path.
"""
import hashlib,json
from pathlib import Path
from .agents import AgentError,encode
from .screenwriter import LocalUnavailable
from .no_gpu_staging import load,resolve_profile,fingerprint,LEGACY
from .offline_department_contracts import PARTIAL_ROLES,VISUAL_ROLES,inspection_spec

NATIVE={
 'vision7':('qwen25-vl-7b','config.json','redpad_pipeline.vision_worker'),
 'wan22_5':('wan-local','model_index.json','redpad_pipeline.offline_worker'),
 'svd_xt':('local-svd','model_index.json','redpad_pipeline.offline_worker'),
 'indic_parler':('bengali-tts','config.json','redpad_pipeline.speech_worker'),
 'stable_audio_small':('stable-audio-small','model_config.json','redpad_pipeline.audio_worker')}
INTERFACES={
 'wan_animate2':{'documented_local_entry':'infer/wan_animate_2_demo.py',
   'inputs':['prompt','refer-img-file','refer-video-file','config'],
   'blocker':'Native CLI/YAML/WanAnimate2MPIPipeline source reviewed at 3ad2fef7d61d6200c9c653e0fe47be7616b323f3; exact auxiliary .pth/component safety and local MPI execution bridge remain unverified. No Diffusers/old Animate substitution.'},
 'ltx25':{'documented_local_entry':'ltx_pipelines.distilled',
   'inputs':['transformer-path','text-encoder-path','video-vae-path','audio-vae-path','spatial-upsampler-path'],
   'blocker':'Split ModelPaths/DistilledPipeline source reviewed at f0f2f8607189c78a72420b2b63cb1975b5eca179; selected pinned BF16 recipe still lacks approved exact spatial upsampler/tokenizer dependencies and verified local execution bridge. No older LTX or repack.'},
 'indic_speak':{'documented_local_entry':'inference.TTS (current model card)',
   'inputs':['local directory','text','speaker'],
   'blocker':'Pinned card inaccessible; current example names preview-v2. Exact code/components/speaker mapping and upstream licenses unverified.'},
 'indicf5':{'documented_local_entry':'custom AutoModel callable (model card)',
   'inputs':['text','ref_audio_path','ref_text'],
   'blocker':'Requires reviewed custom code and local auxiliary dependencies; trust_remote_code=True is not authorized. Gated access and specific voice consent pending.'},
 'ace15':{'documented_local_entry':'ACE-Step 1.5 project local package',
   'inputs':['caption','instrumental generation','duration','seed'],
   'blocker':'Source pinned at ca1e85fe9430179831e6bc6be790c332190a3866; initialize_service auto-download/code-sync must be disabled by reviewed local bridge. weights_only=True observed but bounded auxiliary tensor checks/full model-code review remain. Never use ACE 3.5B.'}}
COMPLETED_ROLES={'qc','location','cinematographer','continuity','editing'}


def verify_existing_bundle(profile_id,folder,approval_path):
    """Future local file-hash verification only; never imports inference libraries.
    This assignment tests tiny labeled fixtures, never reads actual model weights.
    """
    if profile_id not in NATIVE:raise LocalUnavailable('No verified exact native worker binding; contract-only.')
    registry,_=load();p=resolve_profile(profile_id,registry)
    folder=Path(folder);approval_path=Path(approval_path)
    if not folder.is_dir() or not approval_path.is_file():raise LocalUnavailable('Approved local model bundle/receipt absent; no download or inference.')
    if any(x.is_symlink() for x in (folder,approval_path,*folder.parents,*approval_path.parents)):raise AgentError('Symlink bundle/receipt prohibited.')
    from .offline_media import checkpoint_manifest
    manifest=checkpoint_manifest(folder,NATIVE[profile_id][1])
    if profile_id=='indic_parler' and not (folder/'description_tokenizer').is_dir():raise AgentError('Complete local description tokenizer required; no auxiliary download.')
    for f in p['selected_weight_files']:
        row=manifest['files'].get(f['path'])
        if not row or row['bytes']!=f['bytes'] or row['sha256']!=f['sha256']:raise AgentError('Exact pinned weight recipe differs; no quantized/version substitution.')
    origin=folder/'redpad_model_origin.json'
    if not origin.is_file():raise AgentError('Exact model origin receipt required.')
    identity=json.loads(origin.read_text());approval=json.loads(approval_path.read_text())
    if identity.get('repo')!=p['repo'] or identity.get('revision')!=p['revision']:raise AgentError('Bundle model/revision differs from pinned profile.')
    if approval.get('approved') is not True or approval.get('model')!=p['repo'] or not all(isinstance(approval.get(k),str) and approval[k].strip() for k in ('owner','license_note')) or approval.get('manifest')!=manifest:
        raise AgentError('Existing owner/license approval does not match current complete bundle.')
    return {'profile':profile_id,'repo':p['repo'],'revision':p['revision'],'profile_sha256':fingerprint(p),
            'manifest_sha256':manifest['sha256'],'folder':str(folder.resolve()),
            'worker_module':NATIVE[profile_id][2],'actual_runtime_verified':False,'production_ready':False}


def prepare_native(staged,store,*,spec=None,verify_bundle=False):
    plan=staged['plan'];role=plan['role'];pid=plan['profile'];r=plan['request']
    if role not in PARTIAL_ROLES:raise AgentError('Only the eleven previously partial roles may use this extension.')
    if pid not in NATIVE:
        if pid not in INTERFACES:raise AgentError('Use the existing shared text/image worker; no duplicate engine.')
        if verify_bundle:raise LocalUnavailable('Native execution bridge/component recipe incomplete; bundle authentication cannot be claimed.')
        if spec is not None:
            from .offline_specialist_preparation import prepare_specialist
            job=prepare_specialist(staged,store,spec)
            job['preparer_source_sha256']=hashlib.sha256((Path(__file__).parent/'offline_specialist_preparation.py').read_bytes()).hexdigest()
            return job
        return {'stage_id':staged['id'],'profile':pid,'interface':INTERFACES[pid],
                'status':'RUNTIME BLOCKED','contract_only':True,'worker_module':None,
                'launch_authorized':False,'inference_completed':False,'human_reviewed':False}
    from .producer_references import References
    refs=References(store);pins={row['id']:row for row in staged['references']}
    def path(pin):
        row=pins.get(pin['id'])
        if not row or row['version']!=pin['version']:raise AgentError('Reference not bound to this staged request.')
        return str(refs.path(row))
    root=store.path.parent/'agent_media'/'prepared_offline'/fingerprint({'stage':staged['id'],'spec':spec})
    checkpoint_key,_,worker=NATIVE[pid]
    from .offline_media import MODEL_ROOT
    folder=MODEL_ROOT/checkpoint_key
    payload={'checkpoint':str(folder),'output':str(root/('output.mp4' if pid in ('wan22_5','svd_xt') else 'output.wav'))}
    if pid=='vision7':
        if spec is None:raise AgentError('Explicit departmental inspection specification required.')
        inspection_spec(role,spec,r['images'])
        schema={'findings':[{'category':'supplied dimension','reference_id':'supplied ID','region':[0,0,1,1],'observation':'visible evidence only','certainty':'visible/inferred/uncertain'}],'abstain':False}
        question=encode({'question':r['question'],'scope':spec,'response_contract':schema,
                         'rule':'No unsupported location, identity, lens or quality claims; no approvals. Abstain on insufficient evidence.'})
        payload.update(images=[{'path':path(pin),'sha256':pins[pin['id']]['sha256'],'relative':pin['id']} for pin in r['images']],
                       request={'question':question,'seed':r['seed']},output=str(root/'raw_response.txt'))
    elif pid in ('wan22_5','svd_xt'):
        native=dict(r);native.pop('reference');reference=path(r['reference']) if r['reference'] is not None else None
        if reference is not None:native['reference']=reference
        payload.update(engine=checkpoint_key,request=native,reference=reference)
    elif pid=='indic_parler':
        import unicodedata
        from .offline_speech import STYLES
        payload.update(text=unicodedata.normalize('NFC',r['text']),description=r['preset']+' speaks in Bengali. '+STYLES[r['style']],seed=r['seed'])
    else:payload.update(engine=checkpoint_key,request=r)
    bound=None
    if verify_bundle:bound=verify_existing_bundle(pid,folder,MODEL_ROOT/(checkpoint_key+'.approval.json'))
    result={'stage_id':staged['id'],'profile':pid,'status':'RUNTIME BLOCKED','contract_only':False,
            'worker_module':worker,'payload':payload,'payload_sha256':fingerprint(payload),'bundle_binding':bound,
            'worker_source_sha256':hashlib.sha256((Path(__file__).parent/(worker.rsplit('.',1)[-1]+'.py')).read_bytes()).hexdigest(),
            'offline_environment':{'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1'},
            'launch_authorized':False,'inference_completed':False,'human_reviewed':False,
            'limitations':'Existing worker schema mapped only. Actual package/API, device, dtype, numerical output and independent quality remain unverified.'}
    return result


class PreparedRequests:
    """Persistent preparation records; no execution entry point or authority transfer."""
    def __init__(self,store):
        self.store=store
        from .no_gpu_staging import StagingLedger
        self.staging=StagingLedger(store)
        with store.tx() as db:db.execute('CREATE TABLE IF NOT EXISTS offline_prepared_requests(id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT)')
    def prepare(self,stage_id,*,spec=None,verify_bundle=False):
        if type(verify_bundle) is not bool:raise AgentError('Explicit boolean bundle-check setting required.')
        stage=self.staging.get(stage_id);job=prepare_native(stage,self.store,spec=spec,verify_bundle=verify_bundle)
        record={'stage_id':stage_id,'spec':spec,'verify_bundle':verify_bundle,'job':job};token=fingerprint(record);raw=encode(record)
        with self.store.tx() as db:db.execute('INSERT OR IGNORE INTO offline_prepared_requests VALUES (?,?,?)',(token,raw,hashlib.sha256(raw.encode()).hexdigest()))
        return {'prepared_id':token,**job}
    def get(self,id):
        with self.store.tx() as db:row=db.execute('SELECT payload,sha256 FROM offline_prepared_requests WHERE id=?',(id,)).fetchone()
        if not row or hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Unknown or altered offline preparation.')
        record=json.loads(row['payload'])
        if fingerprint(record)!=id:raise AgentError('Offline preparation identity changed.')
        stage=self.staging.get(record['stage_id']);current=prepare_native(stage,self.store,spec=record['spec'],verify_bundle=record['verify_bundle'])
        if current!=record['job']:raise AgentError('Source, spec, worker or model binding changed; preparation is stale.')
        return {'prepared_id':id,**current}


def readiness_updates(rows):
    # Only the eleven targeted roles change. Rejected unsupported modes remain explicit.
    for role in PARTIAL_ROLES:
        r=rows[role]
        r['offline_native_preparation']='implemented; no runtime launch'
        r['runtime_status']='RUNTIME BLOCKED';r['human_status']='HUMAN REVIEW PENDING'
        if role in COMPLETED_ROLES and 'vision7' in r['operation_candidates'].get('image_inspection',[]):
            r['engineering_status']='NO-GPU ENGINEERING COMPLETE'
            r['execution_binding_pending']=[]
            r['runtime_validation_pending']=['vision7 exact installed bundle, local dependencies, device/API and actual critic accuracy']
            r['unsupported_mode_policy']='Reject unsupported audio/whole-video claims; actual listening and artistic acceptance require independent review.'
        else:
            r['engineering_status']='PARTIAL'
            r['missing_official_interface']=[INTERFACES[k]['blocker'] for k in r['execution_binding_pending'] if k in INTERFACES]
            if role in {'performance','motion','video','voice','music','casting'}:
                from .offline_specialist_preparation import PINS
                r['specialist_preparation']='source-reviewed native call and evidence preparation; no executable runtime bridge'
                r['native_source_revisions']={k:PINS[k] for k in r['execution_binding_pending'] if k in PINS}
                r['offline_preparation_evidence']='verification/offline_6/'
    return rows
