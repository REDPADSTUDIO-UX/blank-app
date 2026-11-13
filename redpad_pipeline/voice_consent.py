"""Explicit scoped human consent records, distinct from uploaded documents.
No speech recognition, legal validity claim, inference, or automatic approval.
"""
import hashlib,json
from .agents import AgentError,encode
from .no_gpu_staging import fields,text,ref,fingerprint
from .producer_references import References


class VoiceConsents:
    def __init__(self,store):
        self.store=store;self.refs=References(store)
        with store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS voice_consent_reviews(id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT);
          CREATE TABLE IF NOT EXISTS voice_consent_revocations(id TEXT PRIMARY KEY,reason TEXT,owner TEXT);
        ''')
    def _pins(self,spec):
        result=[]
        for key,extensions in [('reference',{'.wav','.mp3','.m4a'}),('document',{'.txt','.pdf','.docx'})]:
            pin=spec[key];ref(pin);row=self.refs.get(pin['id'])
            if row['version']!=pin['version'] or row['archived'] or row['extension'] not in extensions or not row['source'].strip():raise AgentError('Current exact consent/reference evidence required.')
            if key=='reference' and row['rights'] not in ('fictional_ai','authorized_person'):raise AgentError('Voice source rights unavailable.')
            self.refs.path(row);result.append(row)
        return result
    def confirm(self,spec,*,confirmed=False):
        fields(spec,('actor_id','reference','document','transcript_sha256','uses','reviewer','scope_task','note'))
        if confirmed is not True:raise AgentError('Human consent review requires explicit owner confirmation; document upload is insufficient.')
        for key in ('actor_id','reviewer','scope_task','note'):text(spec[key],1000)
        if spec['uses']!=['voice_clone'] or not isinstance(spec['transcript_sha256'],str) or len(spec['transcript_sha256'])!=64 or any(c not in '0123456789abcdef' for c in spec['transcript_sha256']):raise AgentError('Exact transcript hash and voice-clone scope required.')
        with self.store.tx() as db:scope=self.store._task(db,spec['scope_task'])
        pins=self._pins(spec);record={'spec':spec,'scope_revision':scope['revision'],'evidence':pins,'kind':'explicit_human_review_declaration_not_automatic_document_verification','legal_authenticity_verified':False}
        raw=encode(record);id=fingerprint(record)
        with self.store.tx() as db:
            db.execute('INSERT OR IGNORE INTO voice_consent_reviews VALUES (?,?,?)',(id,raw,hashlib.sha256(raw.encode()).hexdigest()))
            self.store.event(db,spec['scope_task'],'owner','voice_consent_review',{'receipt':id,'automatic_identity_or_artistic_acceptance':False})
        return id
    def revoke(self,id,owner,reason,*,confirmed=False):
        if confirmed is not True:raise AgentError('Explicit owner revocation required.')
        text(owner,100);text(reason,1000)
        with self.store.tx() as db:
            if not db.execute('SELECT 1 FROM voice_consent_reviews WHERE id=?',(id,)).fetchone():raise AgentError('Unknown consent review.')
            db.execute('INSERT OR REPLACE INTO voice_consent_revocations VALUES (?,?,?)',(id,reason,owner))
    def require(self,id,*,actor_id,reference,document,transcript,scope_task):
        with self.store.tx() as db:
            row=db.execute('SELECT payload,sha256 FROM voice_consent_reviews WHERE id=?',(id,)).fetchone()
            revoked=db.execute('SELECT 1 FROM voice_consent_revocations WHERE id=?',(id,)).fetchone()
        if not row or revoked or hashlib.sha256(row['payload'].encode()).hexdigest()!=row['sha256']:raise AgentError('Specific non-revoked human consent review required.')
        record=json.loads(row['payload']);spec=record['spec']
        with self.store.tx() as db:current_scope=self.store._task(db,scope_task)
        if current_scope['revision']!=record['scope_revision']:raise AgentError('Voice consent task revision changed.')
        if fingerprint(record)!=id or (spec['actor_id'],spec['reference'],spec['document'],spec['scope_task'],spec['transcript_sha256'])!=(actor_id,reference,document,scope_task,hashlib.sha256(transcript.encode()).hexdigest()) or spec['uses']!=['voice_clone']:
            raise AgentError('Consent actor/audio/transcript/task/scope differs; no consent reuse.')
        if self._pins(spec)!=record['evidence']:raise AgentError('Voice/consent evidence changed after review.')
        return {'receipt_id':id,'explicit_human_review_recorded':True,'legal_authenticity_verified':False,'artistic_accepted':False}
