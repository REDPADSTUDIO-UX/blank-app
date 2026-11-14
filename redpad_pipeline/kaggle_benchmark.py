"""Resumable comparable real-output trials; no hosted endpoint or automatic selection."""
import json,math,re,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError,encode
from .offline_media import digest,sha
from .shared_model_services import SharedServices,profile,catalog,resource_preflight,ROOT
from .kaggle_runtime import probe
from .screenwriter import model_json

CASE_FILE=ROOT/'assets/professional/kaggle_bengali_cases.json'
def hashlib_sha(raw):
    import hashlib
    return hashlib.sha256(raw.encode()).hexdigest()

def cases():return json.loads(CASE_FILE.read_text())

def technical_validation(case,raw,worker):
    result={'json_valid':False,'technical_pass':False,'generation_complete':not worker.get('truncated',True),'quote_findings':[], 'artistic_scores':None,'human_review':'pending','professional_accepted':False}
    try:data=model_json(raw);result['json_valid']=isinstance(data,dict)
    except ValueError:return result
    result['contract_fields_valid']=isinstance(data,dict) and set(data)==set(case['required_keys'])
    if not isinstance(data,dict):return result
    # Real GPU output used an array where the task explicitly requests a scene string.
    result['contract_field_types_valid']=('scene' not in case['required_keys'] or isinstance(data.get('scene'),str) and bool(data['scene'].strip()))
    expected=case.get('expected_objective_defects')
    if expected is not None:
        findings=data.get('findings')
        if not isinstance(findings,list):result['json_valid']=False;return result
        tp=set();fp=0;unsupported=0
        for f in findings:
            if not isinstance(f,dict):unsupported+=1;continue
            quote=f.get('quote');grounded=isinstance(quote,str) and bool(quote.strip()) and quote in case['source']
            if not grounded:unsupported+=1
            if f.get('category')=='contract' and f.get('decision')=='revise':
                if grounded and f.get('code') in expected:tp.add(f['code'])
                else:fp+=1
        result.update(critic_control_pass=(unsupported==0 and fp==0 and len(tp)==len(set(expected))),true_positive_defects=len(tp),false_positive_findings=fp,missed_expected_defects=len(set(expected)-tp),unsupported_quotes=unsupported,quote_findings=findings)
    result['technical_pass']=result['json_valid'] and result['generation_complete'] and result['contract_fields_valid'] and result['contract_field_types_valid'] and result.get('unsupported_quotes',0)==0 and result.get('critic_control_pass',True)
    return result

class KaggleLab:
    def __init__(self,store):
        self.store=store;self.services=SharedServices(store)
        with store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS kaggle_trial_jobs(id TEXT PRIMARY KEY,payload TEXT,state TEXT,output TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS kaggle_editorial_reviews(id TEXT PRIMARY KEY,payload TEXT);
          CREATE TABLE IF NOT EXISTS kaggle_provisional_selections(role TEXT PRIMARY KEY,payload TEXT);
          CREATE TABLE IF NOT EXISTS kaggle_canaries(id TEXT PRIMARY KEY,payload TEXT);
          CREATE TABLE IF NOT EXISTS kaggle_trial_context(id INTEGER PRIMARY KEY CHECK(id=1),payload TEXT);
        ''')
    def record_settings(self,observations,observer,source,confirmed=False):
        required={'free_tier_verified','remaining_gpu_quota_hours','maximum_session_hours','internet_download_available','session_remaining_hours'}
        if confirmed is not True or not observer.strip() or not isinstance(source,str) or not source.startswith('https://www.kaggle.com/code/') or set(observations)!=required:raise AgentError('Actual private Notebook settings observation, observer and Kaggle source URL required.')
        if observations['free_tier_verified'] is not True or type(observations['internet_download_available']) is not bool:raise AgentError('Free Kaggle resource must be verified; no paid fallback.')
        for k in ('remaining_gpu_quota_hours','maximum_session_hours','session_remaining_hours'):
            if type(observations[k]) not in (int,float) or not math.isfinite(observations[k]) or not 0<observations[k]<=1000:raise AgentError('Positive actual observed quota/session budget required, never an invented default.')
        if observations['session_remaining_hours']>observations['maximum_session_hours']:raise AgentError('Observed remaining session cannot exceed its actual maximum.')
        data={**observations,'observer':observer,'source':source,'observed_at':time.time(),'scope':'Operator-recorded actual Notebook settings; runtime probe separately measures hardware. No credentials.'}
        with self.store.tx() as db:db.execute('INSERT OR REPLACE INTO kaggle_trial_context VALUES (1,?)',(encode(data),))
        return data
    def plan(self,profile_ids,case_ids,hypothesis,max_seconds_per_case=240):
        suite=cases();allcases={c['id']:c for c in suite['cases']}
        if not isinstance(hypothesis,str) or len(hypothesis.strip())<30 or type(max_seconds_per_case) is not int or not 30<=max_seconds_per_case<=600:raise AgentError('Specific measurable hypothesis and bounded call budget required.')
        if not isinstance(profile_ids,list) or not 1<=len(profile_ids)<=4 or len(set(profile_ids))!=len(profile_ids) or not isinstance(case_ids,list) or not case_ids or not set(case_ids)<=set(allcases) or len(case_ids)!=len(set(case_ids)):raise AgentError('Exact candidate and comparable case lists required.')
        ids=[]
        for model in profile_ids:
            p=profile(model)
            if p['adapter']!='hf_text_nf4':raise AgentError('This writing comparison requires the exact text adapter; do not silently use legacy alternatives.')
            for id in case_ids:
                c=allcases[id];payload={'profile':model,'repo':p['repo'],'revision':p['revision'],'case':c,'settings':suite['settings'],'suite_sha256':digest(suite),'hypothesis':hypothesis,'timeout_seconds':max_seconds_per_case,'automatic_retries':0,'production_approved':False}
                token=digest(payload)
                with self.store.tx() as db:db.execute('INSERT OR IGNORE INTO kaggle_trial_jobs(id,payload,state) VALUES (?,?,?)',(token,encode(payload),'Planned — Not Executed'))
                ids.append(token)
        return ids
    def jobs(self):
        with self.store.tx() as db:return [dict(r) for r in db.execute('SELECT * FROM kaggle_trial_jobs ORDER BY rowid')]
    def verify_runtime(self):
        runtime=probe()
        if runtime['provider']!='kaggle_environment_marker':raise AgentError('Runtime canary requires an already running Kaggle session; no GPU activated.')
        with self.store.tx() as db:context=db.execute('SELECT payload FROM kaggle_trial_context WHERE id=1').fetchone()
        if not context or time.time()-json.loads(context[0])['observed_at']>1800:raise AgentError('Fresh actual free-tier/quota observation required first.')
        from .kaggle_runtime import tensor_canary
        result={'runtime':runtime,'canary':tensor_canary(),'captured_at':time.time(),'model_inference':False}
        with self.store.tx() as db:db.execute('INSERT OR REPLACE INTO kaggle_canaries VALUES (?,?)',('runtime',encode(result)))
        return result
    def model_canary(self,id):
        p=profile(id);installed=self.services.installed(id,True);runtime=probe()
        if runtime['provider']!='kaggle_environment_marker':raise AgentError('Model canary restricted to actual Kaggle runtime.')
        with self.store.tx() as db:r=db.execute('SELECT payload FROM kaggle_canaries WHERE id=?',('runtime',)).fetchone()
        if not r or time.time()-json.loads(r[0])['captured_at']>3600:raise AgentError('Complete/persist a fresh tiny tensor runtime canary first.')
        token=digest([id,installed['manifest']['sha256'],runtime['gpus'],runtime['libraries']])
        # Free memory changes naturally, so persistent duplicate protection keys use stable identity only.
        token=digest([id,installed['manifest']['sha256'],[{k:g[k] for k in ('name','total_bytes','driver','compute_capability')} for g in runtime['gpus']],runtime['libraries']])
        with self.store.tx() as db:old=db.execute('SELECT payload FROM kaggle_canaries WHERE id=?',(token,)).fetchone()
        if old:
            result=json.loads(old[0])
            if result.get('genuine_inference') is True:return result
            raise AgentError('Canary already attempted/interrupted for this exact installation/hardware; inspect preserved failure before a new explicit hypothesis.')
        if p['adapter']!='hf_text_nf4':raise AgentError('This model canary currently supports the text arm only; media canaries need their exact approved adapter.')
        request={'system':'Reply in one short Bengali sentence. No score or approval.','prompt':'বৃষ্টি শেষে ঢাকার সকালকে এক বাক্যে বর্ণনা করুন।','max_new_tokens':32,'context_tokens':512,'temperature':0,'seed':117,'thinking':False}
        # Observe quota once more, including preservation margin, before the first model load.
        with self.store.tx() as db:context=db.execute('SELECT payload FROM kaggle_trial_context WHERE id=1').fetchone()
        if not context:raise AgentError('Quota observation missing.')
        context=json.loads(context[0]);elapsed=(time.time()-context['observed_at'])/3600
        if elapsed>0.5 or (min(context['remaining_gpu_quota_hours'],context['session_remaining_hours'])-elapsed)*3600<360:raise AgentError('Insufficient/fresh quota for bounded model canary and preservation.')
        with self.store.tx() as db:db.execute('INSERT INTO kaggle_canaries VALUES (?,?)',(token,encode({'profile':id,'state':'Running','genuine_inference':False})))
        try:folder,evidence=self.services.execute(id,request,timeout=240)
        except Exception as exc:
            failure={'profile':id,'state':'Failed or interrupted','genuine_inference':False,'error_type':type(exc).__name__,'artifact_folder':str(getattr(self.services,'last_folder',''))}
            with self.store.tx() as db:db.execute('UPDATE kaggle_canaries SET payload=? WHERE id=?',(encode(failure),token))
            raise
        raw=(folder/'raw_response.txt').read_text()
        result={'profile':id,'manifest_sha256':installed['manifest']['sha256'],'runtime':runtime,'raw':raw,'raw_sha256':sha(folder/'raw_response.txt'),'evidence':evidence,'captured_at':time.time(),'genuine_inference':evidence.get('actual_inference_verified') is True,'creative_acceptance':False}
        with self.store.tx() as db:db.execute('UPDATE kaggle_canaries SET payload=? WHERE id=?',(encode(result),token))
        return result

    def confirm_canary_export(self,id,retrieved_raw,private_version_url,confirmed=False):
        if confirmed is not True or not isinstance(private_version_url,str) or not private_version_url.startswith('https://www.kaggle.com/code/') or 'scriptVersionId=' not in private_version_url:raise AgentError('A saved private Kaggle version and verified retrieval are required, not temporary working storage.')
        file=Path(retrieved_raw)
        if any(p.is_symlink() for p in (file,*file.parents)) or not file.is_file() or file.stat().st_size>1024*1024:raise AgentError('Bounded retrieved canary output file required.')
        with self.store.tx() as db:
            rows=[dict(r) for r in db.execute("SELECT * FROM kaggle_canaries WHERE id<>'runtime'")]
            matches=[r for r in rows if json.loads(r['payload']).get('profile')==id and json.loads(r['payload']).get('genuine_inference') is True and json.loads(r['payload']).get('raw_sha256')==sha(file)]
            if not matches:raise AgentError('Retrieved output does not match a real captured canary hash.')
            for row in matches:
                value=json.loads(row['payload']);value['persistence_verified']={'source':private_version_url,'retrieved_raw_sha256':sha(file),'confirmed_at':time.time()}
                db.execute('UPDATE kaggle_canaries SET payload=? WHERE id=?',(encode(value),row['id']))
        return {'verified_exports':len(matches),'human_artistic_review':False}

    def run_one(self,id):
        with self.store.tx() as db:
            r=db.execute('SELECT * FROM kaggle_trial_jobs WHERE id=?',(id,)).fetchone();context=db.execute('SELECT payload FROM kaggle_trial_context WHERE id=1').fetchone()
        if not r:raise AgentError('Unknown benchmark job.')
        if r['state']=='Completed':return json.loads(r['output'])
        if r['state']!='Planned — Not Executed':raise AgentError('Interrupted/failed trials require explicit investigation and new hypothesis; no blind retry.')
        if not context:raise AgentError('Kaggle account/settings/quota unverified; no GPU job submitted.')
        context=json.loads(context[0]);j=json.loads(r['payload']);runtime=probe()
        if runtime['provider']!='kaggle_environment_marker':raise AgentError('This is not a verified running Kaggle environment; no other GPU/cloud allowed.')
        if time.time()-context['observed_at']>1800:raise AgentError('Refresh actual Kaggle quota/session settings before this workload.')
        elapsed=(time.time()-context['observed_at'])/3600
        budget=min(context['remaining_gpu_quota_hours'],context['session_remaining_hours'])-elapsed
        if budget*3600<j['timeout_seconds']+120:raise AgentError('Insufficient remaining observed budget plus preservation margin; stop safely.')
        if j['suite_sha256']!=digest(cases()):raise AgentError('Benchmark suite changed; preserve old experiment without implicit rerun.')
        p=profile(j['profile']);installed=self.services.installed(j['profile'],True)
        with self.store.tx() as db:canaries=[json.loads(x[0]) for x in db.execute("SELECT payload FROM kaggle_canaries WHERE id<>'runtime'")]
        if not any(c.get('profile')==j['profile'] and c.get('manifest_sha256')==installed['manifest']['sha256'] and c.get('genuine_inference') is True and c.get('persistence_verified') for c in canaries):raise AgentError('Persist a real model canary and verify retrieval from saved private output before a larger benchmark.')
        readiness=resource_preflight(p,runtime)
        if readiness['blockers']:raise AgentError('; '.join(readiness['blockers']))
        c=j['case'];request={**j['settings'],'system':c['system'],'prompt':c['prompt']+'\n\nSOURCE MATERIAL:\n'+c['source']}
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT state FROM kaggle_trial_jobs WHERE id=?',(id,)).fetchone()[0]!='Planned — Not Executed':raise AgentError('Trial state changed.')
            db.execute("UPDATE kaggle_trial_jobs SET state='Running' WHERE id=?",(id,))
        try:
            folder,evidence=self.services.execute(j['profile'],request,timeout=j['timeout_seconds'])
            raw=(folder/'raw_response.txt').read_text();validation=technical_validation(c,raw,evidence['worker'])
            output={'profile':j['profile'],'repo':j['repo'],'revision':j['revision'],'case_id':c['id'],'raw':raw,'raw_sha256':sha(folder/'raw_response.txt'),'evidence':evidence,'runtime':runtime,'validation':validation,'provenance':'local_inference','artifact_folder':str(folder),'human_review_completed':False,'professional_accepted':False}
            with self.store.tx() as db:db.execute("UPDATE kaggle_trial_jobs SET state='Completed',output=? WHERE id=?",(encode(output),id))
            return output
        except Exception as exc:
            with self.store.tx() as db:db.execute("UPDATE kaggle_trial_jobs SET state='Failed — Evidence Preserved',output=? WHERE id=?",(encode({'error_type':type(exc).__name__,'provenance':'failure_not_a_model_output','artifact_folder':str(getattr(self.services,'last_folder','')),'human_review_completed':False}),id))
            raise
    def blind_packet(self):
        samples=[];key={}
        for job in self.jobs():
            if job['state']!='Completed':continue
            output=json.loads(job['output']);code=digest([job['id'],'blind-v1'])[:12]
            samples.append({'id':code,'case':json.loads(job['payload'])['case'],'raw':output['raw'],'raw_sha256':output['raw_sha256'],'technical_validation':output['validation']})
            key[code]={k:output[k] for k in ('profile','repo','revision','case_id')}
        samples.sort(key=lambda x:x['id'])
        return {'samples':samples,'human_review_completed':False,'instructions':'Review Bengali dialogue, psychology, subtext, causality, humor, pacing and grounded criticism independently. Give evidence with exact quote/scene. Rate writing separately from protocol validity. No model identities or administrator key for reviewer. Empty packet means no real samples exist.'},key
    def comparative_sources(self,role,models):
        if role not in catalog()['agents'] or not isinstance(models,list) or len(models)<2 or len(set(models))!=len(models):raise AgentError('A registered role and at least two distinct tested candidates are required.')
        required=[c for c in cases()['cases'] if role in c['roles']]
        if not required:raise AgentError('This department needs actual specialist/media samples through ProfessionalLab; writing tests cannot approve its artistic capability.')
        table={}
        for job in self.jobs():
            if job['state']!='Completed':continue
            spec=json.loads(job['payload']);output=json.loads(job['output'])
            if spec['profile'] not in models or spec['case']['id'] not in {c['id'] for c in required}:continue
            current=profile(spec['profile'])
            if spec['repo']!=current['repo'] or spec['revision']!=current['revision'] or output.get('repo')!=current['repo'] or output.get('revision')!=current['revision'] or output['evidence'].get('worker',{}).get('repo')!=current['repo'] or output['evidence'].get('worker',{}).get('revision')!=current['revision']:raise AgentError('Model revision or actual worker identity differs from the compared candidate.')
            if spec['suite_sha256']!=digest(cases()) or spec['case']!=next(c for c in required if c['id']==spec['case']['id']) or spec['settings']!=cases()['settings']:raise AgentError('Comparable case/source/settings changed; no selection allowed.')
            if output.get('provenance')!='local_inference' or output['evidence'].get('actual_inference_verified') is not True or output['evidence'].get('worker',{}).get('inference_completed') is not True or hashlib_sha(output['raw'])!=output['raw_sha256']:raise AgentError('Complete, unmodified actual model outputs required for comparison.')
            if not output['validation'].get('technical_pass') or output['validation'].get('critic_control_pass') is False:raise AgentError('Technical or grounded-critic acceptance gate failed; no weak model promotion.')
            token=(spec['profile'],spec['case']['id'])
            if token in table:raise AgentError('Multiple hypotheses exist for a comparison case; isolate the intended evidence set before selection.')
            table[token]={'job':job['id'],'raw':output['raw'],'raw_sha256':output['raw_sha256'],'revision':output['revision']}
        if set(table)!={(m,c['id']) for m in models for c in required}:raise AgentError('All identical role-specific cases must finish for every compared candidate.')
        return required,table
    def record_editorial_comparison(self,role,models,review,confirmed=False):
        required,table=self.comparative_sources(role,models)
        if confirmed is not True or not isinstance(review,dict) or review.get('reviewer_type')!='human' or review.get('independent') is not True or review.get('qualified_for_role') is not True or not str(review.get('reviewer','')).strip() or not str(review.get('expertise','')).strip():raise AgentError('Actual independent qualified human review and explicit owner attestation required; no AI-generated expert scores.')
        dimensions={d for c in required for d in c['dimensions']}
        if set(review.get('models',{}))!=set(models):raise AgentError('Review every compared model, not just the preferred one.')
        for model in models:
            ratings=review['models'][model]
            if set(ratings)!=dimensions:raise AgentError('All role-specific editorial dimensions require actual findings.')
            for value in ratings.values():
                if type(value.get('score')) is not int or not 1<=value['score']<=5 or type(value.get('accepted')) is not bool or not str(value.get('finding','')).strip() or not value.get('evidence'):raise AgentError('Human score, explicit acceptance, finding and exact evidence required.')
                for anchor in value['evidence']:
                    sample=next((v for (m,c),v in table.items() if m==model and v['job']==anchor.get('job')),None)
                    if not sample or not isinstance(anchor.get('quote'),str) or not anchor['quote'] or anchor['quote'] not in sample['raw']:raise AgentError('Human review must quote this model’s actual unchanged output.')
        id=uuid4().hex;payload={'role':role,'models':models,'review':review,'sample_set_sha256':digest(sorted((m,c,v['raw_sha256']) for (m,c),v in table.items())),'attestation':'Owner-attested actual independent human; software does not authenticate identity/qualifications','created':time.time()}
        with self.store.tx() as db:db.execute('INSERT INTO kaggle_editorial_reviews VALUES (?,?)',(id,encode(payload)))
        return id
    def select_provisional(self,role,id,preferred,reason,confirmed=False):
        if confirmed is not True or not isinstance(reason,str) or len(reason.strip())<30:raise AgentError('Explicit Producer selection with comparative justification required.')
        with self.store.tx() as db:row=db.execute('SELECT payload FROM kaggle_editorial_reviews WHERE id=?',(id,)).fetchone()
        if not row:raise AgentError('Actual comparative editorial review missing.')
        review=json.loads(row[0]);required,table=self.comparative_sources(role,review['models'])
        if review['role']!=role or digest(sorted((m,c,v['raw_sha256']) for (m,c),v in table.items()))!=review['sample_set_sha256']:raise AgentError('Editorial comparison source set changed.')
        route=catalog()['agents'][role]
        if preferred not in [route['primary_candidate']]+route['secondary_candidates'] or preferred not in review['models']:raise AgentError('Preferred candidate is not explicitly shortlisted/tested for this role; request an explicit substitution first.')
        if any(not v['accepted'] or v['score']<4 for v in review['review']['models'][preferred].values()):raise AgentError('Preferred candidate did not meet explicit human creative acceptance; best of weak outputs is not production-ready.')
        result={'role':role,'profile':preferred,'review':id,'reason':reason,'status':'Provisional Primary Selected','sample_set_sha256':review['sample_set_sha256'],'production_approved':False,'professional_ready':False,'scope':'This benchmark only; actual specialist/media/production acceptance gates remain. Existing live routes unchanged.'}
        with self.store.tx() as db:db.execute('INSERT OR REPLACE INTO kaggle_provisional_selections VALUES (?,?)',(role,encode(result)))
        return result

    def comparison(self):
        groups={}
        for job in self.jobs():
            j=json.loads(job['payload']);g=groups.setdefault(j['profile'],{'completed':0,'failed':0,'pending':0,'runtime_seconds':[],'cases':[],'artistic_scores':None,'provisional_primary':False,'status':'Blocked — Genuine comparable inference and independent review pending'})
            if job['state']=='Completed':
                o=json.loads(job['output']);g['completed']+=1;g['cases'].append(o['case_id']);g['runtime_seconds'].append(o['evidence']['runtime_seconds'])
            elif job['state'].startswith('Failed'):g['failed']+=1
            else:g['pending']+=1
        with self.store.tx() as db:selections=[json.loads(r[0]) for r in db.execute('SELECT payload FROM kaggle_provisional_selections')]
        for selection in selections:
            with self.store.tx() as db:review=json.loads(db.execute('SELECT payload FROM kaggle_editorial_reviews WHERE id=?',(selection['review'],)).fetchone()[0])
            self.comparative_sources(selection['role'],review['models'])
        return {'models':groups,'provisional_selections':selections,'winner_selected':bool(selections),'professional_ready_agents':0,'human_review_completed':False}
