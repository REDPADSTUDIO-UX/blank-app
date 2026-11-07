"""Real-output benchmark registry, distinct from software tests and production.
No download, model launch, external reviewer contact or automatic approval.
Human expertise/independence is explicitly owner-attested, never inferred.
"""
import hashlib,json,re,time
from pathlib import Path
from uuid import uuid4
from .agents import AGENTS,AgentError,encode

ROOT=Path(__file__).resolve().parents[1]
def sha(value):return hashlib.sha256(encode(value).encode()).hexdigest()
def suite():return json.loads((ROOT/'assets/professional/suite.json').read_text())
def models():return json.loads((ROOT/'assets/professional/models.json').read_text())['models']
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()

def trial_context(store,run):
    with store.tx() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='professional_bindings'").fetchone():return None
        row=db.execute('SELECT context,sha256 FROM professional_bindings WHERE run=?',(run,)).fetchone()
    if not row:return None
    context=json.loads(row['context'])
    if sha(context)!=row['sha256']:raise AgentError('Professional trial context changed.')
    with store.tx() as db:
        used=db.execute('SELECT sum(CASE WHEN r.attempt<1 THEN 1 ELSE r.attempt END) FROM professional_bindings b JOIN agent_runs r ON r.id=b.run WHERE b.trial=?',(context['trial'],)).fetchone()[0] or 0
    if used>context['max_calls']:raise AgentError('Professional trial retry/call budget exhausted; do not repeat weak generations.')
    return context

class ProfessionalLab:
    def __init__(self,store):
        self.store=store
        with store.tx() as db:db.executescript('''
            CREATE TABLE IF NOT EXISTS professional_trials(id TEXT PRIMARY KEY,role TEXT,payload TEXT,fingerprint TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS professional_bindings(run TEXT PRIMARY KEY,trial TEXT,sample_key TEXT,context TEXT,sha256 TEXT,UNIQUE(trial,sample_key));
            CREATE TABLE IF NOT EXISTS professional_samples(id TEXT PRIMARY KEY,trial TEXT,payload TEXT);
            CREATE TABLE IF NOT EXISTS professional_reviews(id TEXT PRIMARY KEY,trial TEXT,payload TEXT);
        ''')

    def plan(self,role,model_ids,hypothesis,expected_change,*,change_type='model_candidate',fix_ref=None,max_calls=3):
        specs=suite()['agents'];catalog=models()
        if role not in specs or not isinstance(model_ids,list) or not 1<=len(model_ids)<=5 or len(set(model_ids))!=len(model_ids):raise AgentError('Choose a department and one to five specialist model/tool profiles.')
        if any(m not in specs[role]['candidate_models']+['legacy4'] for m in model_ids):raise AgentError('Model profile is not researched for this specialist task.')
        if not isinstance(hypothesis,str) or len(hypothesis.strip())<30 or not isinstance(expected_change,str) or len(expected_change.strip())<20:raise AgentError('Record a specific capability hypothesis and observable improvement target before another call.')
        if change_type not in ('model_candidate','schema_fix','state_fix','adapter_fix','conditioning_control'):raise AgentError('Unsupported improvement hypothesis type.')
        if type(max_calls) is not int or not 1<=max_calls<=24:raise AgentError('A trial has a one to twenty-four call budget, including required supporting media.')
        if 'legacy4' in model_ids:
            if max_calls>2:raise AgentError('A specific weak-model fix may use at most two bounded diagnostic calls.')
            if change_type in ('model_candidate','conditioning_control') or not isinstance(fix_ref,dict):raise AgentError('Weak 4B repetition blocked; a demonstrated code/state/adapter fix is required.')
            path=fix_ref.get('path','')
            if not isinstance(path,str) or not path.startswith('redpad_pipeline/') or '..' in Path(path).parts:raise AgentError('A source-controlled component path is required.')
            p=ROOT/path
            if any(x.is_symlink() for x in (p,*p.parents)) or not p.is_file() or file_sha(p)!=fix_ref.get('sha256'):raise AgentError('Fix hypothesis must reference the actual source-controlled component hash.')
        spec=specs[role];id=uuid4().hex
        payload={'id':id,'role':role,'model_profiles':{m:catalog[m] for m in model_ids},'hypothesis':hypothesis,
                 'expected_change':expected_change,'change_type':change_type,'fix_ref':fix_ref,'max_calls':max_calls,
                 'case':spec,'case_sha256':sha(spec),'source_brief':suite()['shared_original_brief'],
                 'state':'planned_not_executed','professional_ready':False,'production_ready':False,'created':time.time()}
        fingerprint=sha({k:v for k,v in payload.items() if k not in ('id','created')})
        with self.store.tx() as db:
            if db.execute('SELECT 1 FROM professional_trials WHERE fingerprint=?',(fingerprint,)).fetchone():raise AgentError('Identical experiment already exists; resume it rather than reset its call budget.')
            db.execute('INSERT INTO professional_trials VALUES (?,?,?,?)',(id,role,encode(payload),fingerprint))
        return payload

    def trial(self,id):
        with self.store.tx() as db:r=db.execute('SELECT payload FROM professional_trials WHERE id=?',(id,)).fetchone()
        if not r:raise AgentError('Unknown professional trial.')
        data=json.loads(r[0])
        if sha(data['case'])!=data['case_sha256']:raise AgentError('Trial case snapshot modified.')
        return data

    def bind(self,id,run,sample_key):
        """Bind an existing queued Engine run; never change its model route or approvals."""
        from .model_routing import ModelRoutes,inventory
        t=self.trial(id)
        if not isinstance(sample_key,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',sample_key):raise AgentError('Distinct safe sample key required.')
        with self.store.tx() as db:
            r=db.execute('SELECT r.*,t.agent FROM agent_runs r JOIN tasks t ON t.id=r.task WHERE r.id=?',(run,)).fetchone()
            count=db.execute('SELECT count(*) FROM professional_bindings WHERE trial=?',(id,)).fetchone()[0]
        if not r or r['state']!='Ready for Input' or r['mode']=='local' and r['agent']!=t['role']:raise AgentError('Bind only a queued specialist run, before execution.')
        if count>=t['max_calls']:raise AgentError('Trial call budget exhausted; no repeated success or hidden retry.')
        if r['mode']=='local':
            policy=ModelRoutes(self.store).policy(t['role']);name=policy['models'][0]['name'] if policy else r['model'] or self.store.status(t['role'])['model']
            profiles=[p for p in t['model_profiles'].values() if p.get('runtime_tag')==name]
            if not profiles:raise AgentError('Current run route differs from the trial model; configure a separate approved research route explicitly.')
            approved=next((m for m in ModelRoutes(self.store).models() if m['approved'] and m['name']==name),None)
            if not approved or inventory().get(name)!=approved['digest']:raise AgentError('Exact model is not installed and explicitly approved; no download or paid fallback.')
            model_digest=approved['digest']
        elif r['mode']=='media':
            inputs=json.loads(r['inputs']);operation=inputs.get('operation')
            if operation=='offline_video':
                from .offline_media import approved,CATALOG
                engine=inputs.get('engine');approval=approved(engine,True);name=CATALOG[engine]['model']
            elif operation=='offline_speech':
                from .offline_speech import speech_approval,MODEL
                approval=speech_approval(True);name=MODEL
            elif operation=='offline_image':
                from .offline_image import approval as image_approval,MODEL
                approval=image_approval(True);name=MODEL
            else:raise AgentError('Only approved owned generative workers may produce benchmark media; procedural sketches are excluded.')
            if name not in [p.get('repo') for p in t['model_profiles'].values()]:raise AgentError('Owned media model differs from trial profiles.')
            model_digest=approval['manifest']['sha256']
        else:raise AgentError('A software/contract fixture cannot be bound as generative model evidence.')
        context={'trial':id,'role':t['role'],'sample_key':sample_key,'case_sha256':t['case_sha256'],
                 'task':t['case']['real_world_task'],'brief':t['source_brief'],'hypothesis':t['hypothesis'],
                 'expected_change':t['expected_change'],'expected_model':name,'expected_digest':model_digest,
                 'max_calls':t['max_calls'],
                 'input_sha256':hashlib.sha256(r['inputs'].encode()).hexdigest(),
                 'instruction':'Create actual original specialist output in the existing output contract. Preserve approved source facts; no fabricated media, scores, review or approvals.'}
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            used=db.execute('SELECT sum(CASE WHEN r.attempt<1 THEN 1 ELSE r.attempt END) FROM professional_bindings b JOIN agent_runs r ON r.id=b.run WHERE b.trial=?',(id,)).fetchone()[0] or 0
            if used>=t['max_calls']:raise AgentError('Trial reserved call budget exhausted.')
            try:db.execute('INSERT INTO professional_bindings VALUES (?,?,?,?,?)',(run,id,sample_key,encode(context),sha(context)))
            except Exception:raise AgentError('Run or sample is already bound; do not repeat it.') from None
        return context

    def capture_text(self,id,run):
        t=self.trial(id);context=trial_context(self.store,run)
        if not context or context['trial']!=id:raise AgentError('A prior trial/run binding is required; historical outputs cannot be relabeled as this new benchmark.')
        with self.store.tx() as db:
            r=db.execute('SELECT * FROM agent_runs WHERE id=?',(run,)).fetchone()
            e=db.execute('SELECT * FROM local_inference_evidence WHERE run=? AND attempt=?',(run,r['attempt'])).fetchone() if r else None
            if not r or not e:raise AgentError('No original real local-inference evidence; simulation/knowledge/tests are not creative capability.')
            evidence=json.loads(e['evidence']);raw=e['raw_text'];task=self.store._task(db,r['task']);self.store._current(db,task)
            current=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(r['task'],task['revision'])).fetchone()
        identity_match=e['model']==context['expected_model'] and evidence.get('model_digest')==context['expected_digest']
        completed=evidence.get('inference_completed') is True
        if completed and evidence.get('raw_sha256')!=hashlib.sha256(raw.encode()).hexdigest():raise AgentError('Raw response integrity check failed.')
        technical=r['state']=='Awaiting QC' and completed and bool(current) and identity_match
        body=json.loads(json.loads(current[0])['summary']) if current else None
        if technical and body.get('provenance')!='local_inference':raise AgentError('Injected provider output cannot count as real model evidence.')
        item={'id':run+':'+str(r['attempt']),'kind':'text','run':run,'role':t['role'],'model':e['model'],'model_digest':evidence.get('model_digest'),
              'attempt':r['attempt'],
              'run_state_at_capture':r['state'],'task_state_at_capture':task['state'],'identity_match':identity_match,
              'raw':raw,'sha256':hashlib.sha256(raw.encode()).hexdigest(),'runtime_evidence':evidence,
              'source_refs':json.loads(task['refs']),'output_revision':task['revision'],
              'input_sha256':context['input_sha256'],'technical_pass':technical,'actual_model_output':completed or bool(raw),
              'output_envelope_sha256':hashlib.sha256(current[0].encode()).hexdigest() if current else None,
              'failure':r['error'],'provenance':'owned_local_inference','case_sha256':t['case_sha256']}
        return self._save_sample(id,item)

    def capture_media(self,id,run):
        """Attach actual owned-worker output to its specialist trial. No fixture import."""
        from .offline_media import media_path
        t=self.trial(id)
        context=trial_context(self.store,run)
        if not context or context['trial']!=id:raise AgentError('Media run must be bound before inference; no relabeling historical output.')
        with self.store.tx() as db:
            r=db.execute('SELECT * FROM agent_runs WHERE id=?',(run,)).fetchone()
            if not r or r['state']!='Awaiting QC' or r['mode']!='media':raise AgentError('A completed owned media run is required.')
            task=self.store._task(db,r['task']);self.store._current(db,task)
            out=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(r['task'],task['revision'])).fetchone()
        body=json.loads(json.loads(out[0])['summary']);artifact=body['artifact'];meta=artifact.get('metadata',{})
        if not artifact.get('actual_generation') or not meta.get('actual_inference_verified') or not meta.get('model_identity_verified') or meta.get('worker_inference',{}).get('inference_completed') is not True:raise AgentError('A plan, fixture or procedural sketch is not verified generative-media inference.')
        if artifact['model'] not in [p.get('repo') for p in t['model_profiles'].values()]:raise AgentError('Media model was not declared in this trial.')
        if artifact['model']!=context['expected_model'] or meta.get('model_manifest_sha256',meta.get('manifest_sha256'))!=context['expected_digest']:raise AgentError('Generated media checkpoint differs from the pre-bound model.')
        p=media_path(self.store.path,artifact['path'])
        if file_sha(p)!=meta.get('output_sha256'):raise AgentError('Generated media changed after inference.')
        kind='image' if p.suffix.lower() in ('.png','.jpg','.jpeg') else 'audio' if p.suffix.lower()=='.wav' else 'video'
        if kind not in t['case']['required_output_kinds']:raise AgentError('This trial does not evaluate this output modality.')
        item={'id':run+':media','kind':kind,'run':run,'role':t['role'],'model':artifact['model'],
              'attempt':r['attempt'],'output_revision':task['revision'],
              'input_sha256':context['input_sha256'],'output_envelope_sha256':hashlib.sha256(out[0].encode()).hexdigest(),
              'run_state_at_capture':r['state'],'task_state_at_capture':task['state'],
              'model_digest':meta.get('model_manifest_sha256',meta.get('manifest_sha256')),'path':artifact['path'],
              'sha256':file_sha(p),'runtime_evidence':meta,'source_refs':json.loads(task['refs']),
              'technical_pass':meta.get('technical_output_validated',meta.get('state')=='technical_output_validated') is True,
              'actual_model_output':True,'provenance':'owned_local_media_worker','case_sha256':t['case_sha256']}
        if kind=='audio':
            from .audio_evaluation import measure
            item['objective_signal_metrics']=measure(artifact['path'],self.store.path)
        # Related specialist roles must share an approved screenplay/source with
        # the text plan. A random video cannot validate acting/camera/character.
        if task['agent']!=t['role']:
            known={encode(x) for s in self.samples(id) for x in s.get('source_refs',[])}
            if not known.intersection(encode(x) for x in item['source_refs']):raise AgentError('Supporting media has no common approved source with this specialist plan.')
        return self._save_sample(id,item)

    def _save_sample(self,id,item):
        with self.store.tx() as db:
            old=db.execute('SELECT trial,payload FROM professional_samples WHERE id=?',(item['id'],)).fetchone()
            if old:
                if old['trial']!=id or json.loads(old['payload'])!=item:raise AgentError('Evidence snapshot is immutable.')
                return item
            db.execute('INSERT INTO professional_samples VALUES (?,?,?)',(item['id'],id,encode(item)))
        return item

    def samples(self,id):
        with self.store.tx() as db:return [json.loads(r[0]) for r in db.execute('SELECT payload FROM professional_samples WHERE trial=? ORDER BY id',(id,))]

    def capture_trace(self,id,run):
        t=self.trial(id)
        if 'trace' not in t['case']['required_output_kinds']:raise AgentError('Execution trace is not a deliverable for this case.')
        text=next((s for s in self.samples(id) if s['run']==run and s['kind']=='text' and s['technical_pass']),None)
        if not text:raise AgentError('First capture the genuine specialist model plan for this exact run.')
        with self.store.tx() as db:
            r=db.execute('SELECT task FROM agent_runs WHERE id=?',(run,)).fetchone()
        events=[dict(e) for e in self.store.history() if e.get('task')==r['task']]
        if not events:raise AgentError('Actual execution history unavailable.')
        raw=encode(events)
        return self._save_sample(id,{'id':run+':trace','kind':'trace','run':run,'role':t['role'],'raw':raw,'sha256':hashlib.sha256(raw.encode()).hexdigest(),
            'attempt':text['attempt'],'output_revision':text['output_revision'],
            'input_sha256':text['input_sha256'],'output_envelope_sha256':text['output_envelope_sha256'],
            'run_state_at_capture':text['run_state_at_capture'],'task_state_at_capture':text['task_state_at_capture'],
            'actual_model_output':False,'actual_execution_trace':True,'technical_pass':True,'source_refs':text['source_refs'],'provenance':'actual_engine_history_not_model_fiction'})

    def _check_current_samples(self,id):
        from .offline_media import media_path
        samples=self.samples(id)
        with self.store.tx() as db:
            for item in samples:
                if item.get('path') and file_sha(media_path(self.store.path,item['path']))!=item['sha256']:raise AgentError('Reviewed asset changed; previous evaluation is stale.')
                if item['kind'] in ('text','trace') and hashlib.sha256(item['raw'].encode()).hexdigest()!=item['sha256']:raise AgentError('Reviewed text changed.')
                r=db.execute('SELECT task,attempt,state,inputs FROM agent_runs WHERE id=?',(item['run'],)).fetchone()
                if not r:raise AgentError('Evidence run disappeared.')
                task=self.store._task(db,r['task']);self.store._current(db,task)
                allowed_states=('Awaiting QC','Approved') if item['task_state_at_capture'] in ('Awaiting QC','Approved') else (item['task_state_at_capture'],)
                if r['state']!=item['run_state_at_capture'] or r['attempt']!=item['attempt'] or task['revision']!=item['output_revision'] or task['state'] not in allowed_states:raise AgentError('Reviewed run/output version changed; evaluation is stale.')
                if hashlib.sha256(r['inputs'].encode()).hexdigest()!=item['input_sha256']:raise AgentError('Original evaluated input changed.')
                if item.get('output_envelope_sha256'):
                    output=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(r['task'],item['output_revision'])).fetchone()
                    if not output or hashlib.sha256(output[0].encode()).hexdigest()!=item['output_envelope_sha256']:raise AgentError('Original output envelope changed.')
                if item['kind']=='text':
                    original=db.execute('SELECT raw_text FROM local_inference_evidence WHERE run=? AND attempt=?',(item['run'],item['attempt'])).fetchone()
                    if not original or original[0]!=item['raw']:raise AgentError('Captured text differs from the original inference ledger.')
                if json.loads(task['refs'])!=item['source_refs']:raise AgentError('Evidence sources changed.')
        return samples

    def expert_review(self,id,review,confirmed=False):
        if not isinstance(review,dict):raise AgentError('Structured actual human evaluation required.')
        t=self.trial(id);samples=self._check_current_samples(id);table={s['id']:s for s in samples}
        if confirmed is not True or review.get('reviewer_type')!='human' or review.get('independent') is not True or review.get('qualified_for_role') is not True or not str(review.get('reviewer','')).strip() or not str(review.get('expertise','')).strip():raise AgentError('Owner must attest a real independent, role-qualified human reviewer and their expertise; no model self-review.')
        if set(review.get('examined_samples',[]))!=set(table):raise AgentError('Reviewer must attest examining every actual sample in this evidence set.')
        if set(review.get('modes',[]))!=set(t['case']['review_modes']):raise AgentError('All required actual text/visual/listening evaluation modes must be completed.')
        if set(review.get('criteria',{}))!=set(t['case']['criteria']):raise AgentError('Review every specialist criterion; no prefilled scores.')
        observed_modes=set()
        for finding in review['criteria'].values():
            if not isinstance(finding,dict) or type(finding.get('passed')) is not bool or not str(finding.get('finding','')).strip() or not isinstance(finding.get('evidence'),list) or not finding['evidence']:raise AgentError('Each criterion requires a judgment, actual finding and source anchors.')
            for a in finding['evidence']:
                if not isinstance(a,dict):raise AgentError('Each evidence anchor must be structured.')
                s=table.get(a.get('sample'))
                if not s:raise AgentError('Review cites an unknown sample.')
                if s['kind'] in ('text','trace'):
                    observed_modes.add('text')
                    if not isinstance(a.get('quote'),str) or not a['quote'] or a['quote'] not in s['raw']:raise AgentError('Text review must cite unchanged actual model text.')
                elif s['kind']=='image':
                    observed_modes.add('visual')
                    region=a.get('region',[])
                    if not isinstance(region,list) or len(region)!=4 or any(type(v) not in (int,float) or not 0<=v<=1 for v in region) or not (region[0]<region[2] and region[1]<region[3]):raise AgentError('Image review requires a normalized observed region.')
                else:
                    observed_modes.add('listening' if s['kind']=='audio' else 'visual')
                    duration=s['runtime_evidence'].get('inspection',{}).get('duration',0)
                    if type(a.get('start')) not in (int,float) or type(a.get('end')) not in (int,float) or not 0<=a['start']<a['end']<=duration:raise AgentError('Listening/visual notes must reference an actual bounded time range.')
        if not set(t['case']['review_modes'])<=observed_modes:raise AgentError('Missing actual visual/listening/text evidence anchors for required review modes.')
        payload={'review':review,'sample_set_sha256':sha(samples),'attestation':'owner_attested_independent_expert; identity/qualification not independently verified by software','created':time.time()}
        with self.store.tx() as db:db.execute('INSERT INTO professional_reviews VALUES (?,?,?)',(uuid4().hex,id,encode(payload)))
        return self.status(id)

    def status(self,id):
        t=self.trial(id);samples=self._check_current_samples(id)
        counts={kind:len({s['sha256'] for s in samples if s['kind']==kind and s['technical_pass'] and (s['actual_model_output'] or kind=='trace' and s.get('actual_execution_trace'))}) for kind in t['case']['required_output_kinds']}
        per_engine={p['repo']:len({s['sha256'] for s in samples if s['kind']=='video' and s.get('model')==p['repo'] and s['technical_pass']}) for p in t['model_profiles'].values() if p.get('repo') in [models()[m].get('repo') for m in ('wan','ltx','svd')]}
        engine_coverage=True
        if t['role']=='video':engine_coverage=len(per_engine)==3 and all(n>=t['case']['per_model_video_minimum'] for n in per_engine.values())
        enough=all(counts[k]>=n for k,n in t['case']['minimum_counts'].items()) and all(s['technical_pass'] for s in samples) and engine_coverage
        with self.store.tx() as db:reviews=[json.loads(r[0]) for r in db.execute('SELECT payload FROM professional_reviews WHERE trial=? ORDER BY rowid',(id,))]
        latest=reviews[-1] if reviews else None
        accepted=bool(enough and latest and latest['sample_set_sha256']==sha(samples) and all(f['passed'] for f in latest['review']['criteria'].values()))
        return {'trial':id,'role':t['role'],'real_output_counts':counts,'required_counts':t['case']['minimum_counts'],'per_video_model_counts':per_engine,'engine_coverage_complete':engine_coverage,'failed_captured_outputs':sum(not s['technical_pass'] for s in samples),
                'representative_outputs_complete':enough,'independent_expert_review_recorded':bool(latest),
                'expert_accepted_this_benchmark_only':accepted,'professional_ready':False,'production_ready':False,
                'state':'benchmark_expert_accepted_owner_production_approval_pending' if accepted else 'expert_review_pending_or_failed' if enough else 'real_outputs_and_compute_pending',
                'scope':'No test/KB/prompt/schema success proves professional intelligence; existing QC/owner production gates remain mandatory.'}

    def blind_packet(self,id):
        t=self.trial(id);items=[];key={}
        for s in self._check_current_samples(id):
            code=hashlib.sha256((id+s['id']).encode()).hexdigest()[:12];key[code]={'sample':s['id'],'model':s.get('model'),'sha256':s['sha256']}
            items.append({'id':code,'kind':s['kind'],'original_raw':s.get('raw'),'asset':s.get('path'),'sha256':s['sha256'],'technical_pass':s['technical_pass']})
        return {'case':t['case'],'source_brief':t['source_brief'],'samples':items,'human_review_completed':False,
                'limitations':'Metadata blind only; prose/style can disclose identity. Do not share administrator key with the reviewer.'},key

def audit():
    """Current repository evidence, not a claim about all future model capability."""
    specs=suite()['agents'];profiles=models();rows=[]
    for role,case in specs.items():
        rows.append({'agent':role,'name':AGENTS[role]['name'],
          'software_scope':'Existing contracts, source/approval coordination and knowledge conditioning; model/media adapters vary.',
          'end_to_end_software_complete':False,
          'historical_real_model_attempts':'Observed but professionally inadequate' if role in ('story','script','director','qc') else 'No validated specialist model/media capability demonstrated',
          'professional_intelligence_verified':False,'production_capable':False,
          'capability_required':case['capability_required'],'model_candidates':case['candidate_models'],
          'compute':{m:{k:profiles[m].get(k) for k in ('host_ram_gib_planning','gpu_vram_gib_planning_range','memory_evidence')} for m in case['candidate_models']},
          'real_world_test':case['real_world_task'],'required_outputs':case['minimum_counts'],
          'expertise_required':case['expertise_required'],'review_modes':case['review_modes'],
          'specialist_development_needed':case['specialist_development_needed']})
    return {'strategy':'Model capability + real output + independent expert evaluation','agents':rows,
            'professional_ready_count':0,'human_reviews_this_audit':0,'new_inference_calls':0,
            'status_scope':'Repository evidence at b0d37be audited; no new model capability or human review fabricated.'}
