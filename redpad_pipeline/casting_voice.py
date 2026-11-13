"""Casting-to-Voice audition handoff in the existing agent store, no second database.
Unavailable source is explicit abstention; no alternate model is silently selected.
"""
import hashlib,json
from .agents import AgentError,encode
from .no_gpu_staging import load,resolve_profile,fingerprint,prepare as model_prepare
from .producer_references import References
from .voice_source_policy import binding_status


class CastingVoice:
    def __init__(self,casting):
        self.casting=casting;self.store=casting.store;self.p=casting.p;self.refs=casting.refs
        with self.store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS casting_voice_drafts(id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT,voice_run TEXT,voice_task TEXT,prepared TEXT,native_run TEXT,source_task TEXT);
        ''')
    def _snapshot(self,task,candidate_id):
        t,body=self.casting.proposal(task);rows=body['artifact']['records']
        c=next((r for r in rows if r['id']==candidate_id),None)
        if not c:raise AgentError('Exact current casting candidate required.')
        character_source=None
        with self.store.tx() as db:
            for source_pin in json.loads(t['refs']):
                source=self.store._task(db,source_pin['id'])
                if source['agent']!='character':continue
                raw=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(source['id'],source['revision'])).fetchone()
                if source['state']!='Approved' or source['revision']!=source_pin['revision'] or not raw:raise AgentError('Current owner-approved Character Bible source required.')
                artifact=json.loads(json.loads(raw[0])['summary'])['artifact']
                character=next((r for r in artifact['records'] if r['id']==c['character']),None)
                if character:character_source={'task':source['id'],'revision':source['revision'],'record_sha256':fingerprint(character)}
        if character_source is None:raise AgentError('Casting voice trial must match an approved Character Bible identity.')
        refs=[]
        for pin in c['image_refs']+c['voice_refs']:
            row=self.refs.get(pin['id'])
            if row['version']!=pin['version'] or row['archived'] or row['rights'] not in ('fictional_ai','authorized_person') or not row['source'].strip():raise AgentError('Current sourced authorized casting reference required.')
            self.refs.path(row);refs.append(row)
        if not c['image_refs']:raise AgentError('Candidate portrait required for identity handoff.')
        return {'task':task,'revision':t['revision'],'candidate_id':candidate_id,'candidate_sha256':fingerprint(c),
                'actor_id':c['actor_id'],'character_id':c['character'],'proposal_sha256':fingerprint(body),
                'character_source':character_source,'sources_sha256':fingerprint(json.loads(t['refs'])),'references':refs}
    def _validate_request(self,snapshot,pid,r,spec,consent_review):
        from .offline_specialist_preparation import speech_spec,bind_pins
        registry,_=load();agent=registry['agents']['voice']
        if pid not in [agent['primary_candidate']]+agent['secondary_candidates']:raise AgentError('Use only an existing explicitly chosen Voice AI candidate, never fallback.')
        op='reference_voice' if pid=='indicf5' else 'text_to_audio'
        plan=model_prepare('voice',pid,op,r);pins=bind_pins(self.store,speech_spec(spec,r,pid))
        if pid=='indicf5':
            from .voice_consent import VoiceConsents
            if r['speaker_id']!=snapshot['actor_id'] or r['reference'] not in [{'id':x['id'],'version':x['version']} for x in snapshot['references'] if x['extension'] in ('.wav','.mp3','.m4a')]:raise AgentError('Reference voice belongs to a different/unlisted casting actor.')
            if consent_review is not None:VoiceConsents(self.store).require(consent_review,actor_id=snapshot['actor_id'],reference=r['reference'],document=r['consent_reference'],transcript=r['reference_transcript'],scope_task=snapshot['task'])
        elif consent_review is not None:raise AgentError('Preset synthesis is not reference voice cloning.')
        return plan,pins
    def assess(self,task,candidate_id,spec):
        from .offline_specialist_preparation import casting_assessment,bind_pins
        snapshot=self._snapshot(task,candidate_id);check=casting_assessment(spec)
        if (spec['actor_id'],spec['character_id'])!=(snapshot['actor_id'],snapshot['character_id']):raise AgentError('Assessment actor/character differs from Casting/Character source.')
        _,body=self.casting.proposal(task);candidate=next(r for r in body['artifact']['records'] if r['id']==candidate_id)
        if spec['portrait'] not in candidate['image_refs'] or (spec['voice'] is not None and spec['voice'] not in candidate['voice_refs']):raise AgentError('Assessment uses an unbound portrait/voice identity.')
        if spec['partner_actor_id'] is not None and spec['partner_actor_id'] not in {r['actor_id'] for r in body['artifact']['records']}:raise AgentError('Pair assessment partner is not a current casting candidate.')
        pins=bind_pins(self.store,check['reference_requirements'])
        if any(p['rights']=='authorized_person' and p['extension'] not in ('.txt','.pdf','.docx') for p in pins) and spec['identity_kind']!='authorized_person':raise AgentError('Real-person assessment cannot be declared fictional.')
        payload={'kind':'casting_assessment_draft_not_human_review','snapshot':snapshot,'spec':spec,'pins':pins,'check_result':check}
        id=fingerprint(payload)
        with self.store.tx() as db:db.execute('INSERT OR IGNORE INTO casting_evaluations(id,task,revision,payload) VALUES (?,?,?,?)',(id,task,snapshot['revision'],encode(payload)))
        return self.assessment(id)
    def assessment(self,id):
        from .offline_specialist_preparation import casting_assessment,bind_pins
        with self.store.tx() as db:r=db.execute('SELECT payload FROM casting_evaluations WHERE id=?',(id,)).fetchone()
        if not r:raise AgentError('Unknown assessment draft.')
        d=json.loads(r[0]);s=d.get('snapshot',{})
        if d.get('kind')!='casting_assessment_draft_not_human_review' or fingerprint(d)!=id or self._snapshot(s['task'],s['candidate_id'])!=s:raise AgentError('Assessment source changed or is a different review kind.')
        checked=casting_assessment(d['spec'])
        if checked!=d['check_result'] or bind_pins(self.store,checked['reference_requirements'])!=d['pins']:raise AgentError('Assessment media evidence changed.')
        return {'id':id,**d,'human_review_pending':True,'artistic_accepted':False}
    def prepare(self,task,candidate_id,profile,request,spec,*,consent_review=None,assessment_id=None):
        snapshot=self._snapshot(task,candidate_id);plan,pins=self._validate_request(snapshot,profile,request,spec,consent_review)
        if assessment_id is not None and self.assessment(assessment_id)['snapshot']!=snapshot:raise AgentError('Assessment belongs to another candidate/source.')
        binding=binding_status(profile)
        payload={'snapshot':snapshot,'plan':plan,'spec':spec,'extra_pins':pins,'binding':binding,'consent_review':consent_review,'assessment_id':assessment_id,
                 'kind':'casting_audition_only','candidate_origin':'existing Voice department shortlist; explicit choice, no Casting model replacement',
                 'human_review_pending':True,'artistic_accepted':False,'fallback':None}
        raw=encode(payload);id=fingerprint(payload)
        with self.store.tx() as db:db.execute('INSERT OR IGNORE INTO casting_voice_drafts(id,payload,sha256,source_task) VALUES (?,?,?,?)',(id,raw,hashlib.sha256(raw.encode()).hexdigest(),task))
        return self.get(id)
    def get(self,id):
        with self.store.tx() as db:r=db.execute('SELECT * FROM casting_voice_drafts WHERE id=?',(id,)).fetchone()
        if not r or hashlib.sha256(r['payload'].encode()).hexdigest()!=r['sha256']:raise AgentError('Unknown/altered casting voice draft.')
        d=json.loads(r['payload']);s=d['snapshot']
        if fingerprint(d)!=id or self._snapshot(s['task'],s['candidate_id'])!=s:raise AgentError('Casting identity, source, revision or references changed.')
        if d['assessment_id'] is not None and self.assessment(d['assessment_id'])['snapshot']!=s:raise AgentError('Casting assessment/source changed.')
        plan,pins=self._validate_request(s,d['plan']['profile'],d['plan']['request'],d['spec'],d['consent_review'])
        if plan!=d['plan'] or pins!=d['extra_pins'] or binding_status(plan['profile'])!=d['binding']:raise AgentError('Voice candidate/source/consent binding changed; draft stale.')
        if r['native_run']:
            with self.store.tx() as db:_assert_native_evidence(db,self.store,dict(r),d)
        return {'id':id,**d,'voice_run':r['voice_run'],'voice_task':r['voice_task'],'prepared_id':r['prepared'],'native_run':r['native_run'],
                'abstain':True,'professional_accepted':False,'runtime_status':'MODEL/GPU VALIDATION BLOCKED'}
    def handoff(self,id):
        draft=self.get(id)
        if draft['voice_run']:return draft
        context={'casting_voice_draft':id,'actor_id':draft['snapshot']['actor_id'],'character_id':draft['snapshot']['character_id'],
                 'casting_revision':draft['snapshot']['revision'],'source_sha256':draft['snapshot']['proposal_sha256'],
                 'instruction':'Read-only audition; no identity/voice/chemistry acceptance. Existing QC/Director/Producer controls apply.'}
        run=self.p.engine.enqueue('voice',{'casting_audition_v1':True,'context':context},mode='local',idempotency_key='casting-voice:'+id)
        task=next(r['task'] for r in self.p.engine.runs() if r['id']==run)
        with self.store.tx() as db:db.execute('UPDATE casting_voice_drafts SET voice_run=?,voice_task=? WHERE id=? AND voice_run IS NULL',(run,task,id))
        return self.get(id)
    def stage(self,id):
        from .shared_model_services import SharedServices
        d=self.handoff(id)
        if d['binding']['source_blocked']:raise AgentError('Selected voice source blocked; no inference/fallback. Casting abstains.')
        service=SharedServices(self.store);plan=d['plan'];stage=service.stage_request(d['voice_run'],plan['profile'],plan['operation'],plan['request'])
        prepared=service.prepare_offline_request(stage['id'],spec=d['spec'])
        with self.store.tx() as db:db.execute('UPDATE casting_voice_drafts SET prepared=? WHERE id=?',(prepared['prepared_id'],id))
        return prepared
    def attach_result(self,id,native_run):
        from .native_execution import NativeExecution
        from .native_local_bundle import local_path,digest_file
        from .native_voice_worker import validate_wav
        d=self.get(id);runtime=NativeExecution(self.store);state=runtime.status(native_run);row=runtime._row(native_run);record=json.loads(row['payload'])
        if not d['prepared_id'] or record.get('prepared_id')!=d['prepared_id'] or state['software_fixture'] or state['state']!='RETURNED FOR TECHNICAL REVIEW' or not state['result'].get('inference_completed'):raise AgentError('Exact real native audition evidence required; mock/unrelated outputs cannot prove voice quality.')
        result=state['result'];artifact=local_path(runtime.root/native_run,result['artifact'])
        if artifact.suffix!='.wav' or digest_file(artifact)!=result['artifact_sha256']:raise AgentError('Original voice artifact changed or missing; no evidence substitution.')
        validate_wav(artifact,result['sample_rate'])
        with self.store.tx() as db:db.execute('UPDATE casting_voice_drafts SET native_run=? WHERE id=?',(native_run,id))
        return self.get(id)  # Still not human accepted.
    def packets(self,task):
        with self.store.tx() as db:ids=[r[0] for r in db.execute('SELECT id FROM casting_voice_drafts WHERE source_task=?',(task,))]
        rows=[]
        for id in ids:
            d=self.get(id)
            if d['snapshot']['task']!=task:continue
            rows.append({'draft':id,'candidate':d['snapshot']['candidate_id'],'character':d['snapshot']['character_id'],'profile':d['plan']['profile'],
                         'voice_source_blocked':d['binding']['source_blocked'],'voice_run':d['voice_run'],'native_run':d['native_run'],
                         'assessment_id':d['assessment_id'],'abstain':True,'human_review_pending':True,'voice_accepted':False,'chemistry_accepted':False})
        return sorted(rows,key=lambda r:r['draft'])


def _assert_reference_rows(db,store,pins):
    for pin in pins:
        r=db.execute('SELECT r.payload FROM producer_refs r JOIN producer_ref_heads h ON r.id=h.id AND r.version=h.version WHERE r.id=?',(pin['id'],)).fetchone()
        if not r or json.loads(r[0])!=pin:raise AgentError('Casting voice evidence metadata changed.')
        path=store.path.parent/'agent_media'/'producer_references'/pin['id']/(str(pin['version'])+pin['extension'])
        if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=pin['sha256']:raise AgentError('Casting voice evidence bytes changed.')

def _assert_assessment(db,store,draft):
    if draft.get('assessment_id') is None:return
    r=db.execute('SELECT payload FROM casting_evaluations WHERE id=?',(draft['assessment_id'],)).fetchone()
    if not r:raise AgentError('Casting performance assessment missing.')
    assessment=json.loads(r[0])
    if fingerprint(assessment)!=draft['assessment_id'] or assessment['snapshot']!=draft['snapshot']:raise AgentError('Casting assessment identity/source changed.')
    _assert_reference_rows(db,store,assessment['pins'])

def _assert_character_source(db,store,snapshot):
    pin=snapshot['character_source'];source=store._task(db,pin['task'])
    if source['agent']!='character' or source['revision']!=pin['revision'] or source['state']!='Approved':raise AgentError('Character source approval/revision changed.')
    raw=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(source['id'],source['revision'])).fetchone()
    if not raw:raise AgentError('Character source output missing.')
    body=json.loads(json.loads(raw[0])['summary']);record=next((r for r in body['artifact']['records'] if r['id']==snapshot['character_id']),None)
    if record is None or fingerprint(record)!=pin['record_sha256']:raise AgentError('Casting character specification changed.')

def _assert_native_evidence(db,store,row,draft):
    import re
    from .native_local_bundle import local_path,digest_file
    from .native_voice_worker import validate_wav
    id=row['native_run']
    if not isinstance(id,str) or not re.fullmatch('[a-f0-9]{32}',id):raise AgentError('Invalid native audition ID.')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='native_research_runs'").fetchone():raise AgentError('Native audition record unavailable.')
    native=db.execute('SELECT payload,sha256,state,result FROM native_research_runs WHERE id=?',(id,)).fetchone()
    if not native or hashlib.sha256(native['payload'].encode()).hexdigest()!=native['sha256'] or native['state']!='RETURNED FOR TECHNICAL REVIEW':raise AgentError('Verified native audition record unavailable.')
    if not isinstance(native['result'],str):raise AgentError('Native audition evidence incomplete.')
    spec=json.loads(native['payload']);result=json.loads(native['result'])
    if spec.get('software_fixture') is not False or spec.get('prepared_id')!=row['prepared'] or result.get('inference_completed') is not True or result.get('profile')!=draft['plan']['profile']:raise AgentError('Mock or unrelated voice result is not casting evidence.')
    artifact=local_path(store.path.parent/'agent_media'/'native_research_runs'/id,result['artifact'])
    if artifact.suffix!='.wav' or digest_file(artifact)!=result['artifact_sha256']:raise AgentError('Native voice artifact changed after attachment.')
    validate_wav(artifact,result['sample_rate'])

def packet_fingerprint(db,task,store=None):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='casting_voice_drafts'").fetchone():return fingerprint([])
    rows=[]
    for row in db.execute('SELECT id,payload,sha256,voice_run,native_run,prepared FROM casting_voice_drafts WHERE source_task=? ORDER BY id',(task,)):
        if hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Casting voice evidence altered.')
        if store is not None:
            d=json.loads(row['payload'])
            _assert_character_source(db,store,d['snapshot'])
            _assert_reference_rows(db,store,d['snapshot']['references']+d['extra_pins'])
            _assert_assessment(db,store,d)
            if row['native_run']:_assert_native_evidence(db,store,row,d)
        rows.append(dict(row))
    return fingerprint(rows)


def check_voice_handoff(db,store,task):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='casting_voice_drafts'").fetchone():return
    row=db.execute('SELECT payload,sha256 FROM casting_voice_drafts WHERE voice_task=?',(task['id'],)).fetchone()
    if not row:return
    if hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Casting voice handoff altered.')
    d=json.loads(row['payload']);s=d['snapshot'];source=store._task(db,s['task']);store._current(db,source)
    if source['revision']!=s['revision']:raise AgentError('Casting audition source revision changed.')
    if fingerprint(json.loads(source['refs']))!=s['sources_sha256']:raise AgentError('Casting audition source dependency pins changed.')
    _assert_character_source(db,store,s)
    raw=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(s['task'],s['revision'])).fetchone()
    if not raw or fingerprint(json.loads(json.loads(raw[0])['summary']))!=s['proposal_sha256']:raise AgentError('Casting audition source identity changed.')
    _assert_reference_rows(db,store,s['references']+d['extra_pins'])
    _assert_assessment(db,store,d)
    if d['binding']['source_blocked']:raise AgentError('Exact selected voice source blocked; no automatic model fallback.')
    if d['plan']['profile']=='indicf5':
        # The full scope/audio/transcript check ran when producing/getting the draft.
        # Execution also requires the same immutable, non-revoked review record.
        if not d['consent_review'] or not db.execute("SELECT 1 FROM sqlite_master WHERE name='voice_consent_reviews'").fetchone():raise AgentError('Explicit human consent review required before any cloning.')
        receipt=db.execute('SELECT payload,sha256 FROM voice_consent_reviews WHERE id=?',(d['consent_review'],)).fetchone()
        if not receipt or hashlib.sha256(receipt['payload'].encode()).hexdigest()!=receipt['sha256'] or fingerprint(json.loads(receipt['payload']))!=d['consent_review'] or db.execute('SELECT 1 FROM voice_consent_revocations WHERE id=?',(d['consent_review'],)).fetchone():raise AgentError('Voice consent revoked or altered.')
