"""Export executed software fixtures and actual inference without conflating them."""
import copy,hashlib,importlib.metadata,json,os,platform,re,tempfile
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator
from redpad_pipeline.agents import AGENTS,AgentStore
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.filmmaking_knowledge import readiness,retrieve,load,digest
from redpad_pipeline.screenwriter import render
from redpad_pipeline.offline_media import CATALOG,preflight
from redpad_pipeline.offline_speech import preflight as speech_preflight
from redpad_pipeline.series_ledger import SeriesLedger
from redpad_pipeline.staged_writing import blind_package
from tests.test_agent_foundation import fixture
from tests.test_screenwriter import sample

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/filmmaking_intelligence'
def save(name,value):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def export():
    modules=load()['modules'];matrix=[]
    with tempfile.TemporaryDirectory() as d:
        store=AgentStore(Path(d)/'agent_control.sqlite3');engine=Engine(store)
        for role in AGENTS:
            data=fixture(role)
            if role=='storyboard':data['script']=render(sample())
            calls=[]
            def provider(system,prompt):calls.append({'system':system,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()});return copy.deepcopy(data)
            run=engine.enqueue(role,data,mode='local')
            with patch('socket.socket',side_effect=AssertionError('External request forbidden for software fixture')):
                state=engine.execute(run,complete=provider)
            assert state=='Awaiting QC' and len(calls)==1,(role,state)
            task=next(r['task'] for r in engine.runs() if r['id']==run)
            output=next(o for o in store.outputs() if o['task']==task)
            body=json.loads(json.loads(output['payload'])['summary'])
            assert body['provenance']=='simulation' and body['knowledge_evidence']['conditioning_applied']
            assert 'CURATED CRAFT GUIDANCE' in calls[0]['system']
            row={'agent':role,'name':AGENTS[role]['name'],'new_knowledge_version':readiness()['version'],
                 'lesson_ids':[x['id'] for x in retrieve(role)['lessons']],
                 'rubric':modules[role]['rubric'],'authored_practical_scenario':modules[role]['scenario'],
                 'executed_new_knowledge_contract_probe':'simulation; injected response; no actual inference',
                 'probe_state':state,'knowledge_evidence':body['knowledge_evidence'],
                 'real_inference_this_milestone':role in ('story','script','director','qc'),
                 'new_real_media':False,'human_review_completed':False,'production_ready':False,
                 'remaining_blocker':'Bengali creative accuracy and independent review' if role in ('story','script','director','qc') else 'Actual specialist model/media capability not demonstrated; human review pending'}
            matrix.append(row)
            save('software_scenarios/'+role+'.json',{'scenario_scope':'Original teaching scenario is separate from the reused structural contract fixture below; neither is model-generated.',
                 'knowledge_scenario':modules[role]['scenario'],'contract_fixture':data,'actual_fixture_execution_output':body,
                 'captured_conditioning_system':calls[0]['system'],'human_review_completed':False})
    save('agents_matrix.json',matrix);save('knowledge_readiness.json',readiness())
    versions={}
    for name in ('streamlit','jsonschema','psutil','numpy','zstandard','torch','transformers','diffusers'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    save('environment.json',{'platform':platform.platform(),'logical_cpus':os.cpu_count(),'ram_bytes':os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'),
                           'versions':versions,'GPU_job_started':False,'media':{k:preflight(k) for k in CATALOG},'speech':speech_preflight()})
    records={p.stem:json.loads(p.read_text()) for p in (OUT/'inference').glob('*.json') if 'request_sha256' in json.loads(p.read_text())}
    for p in (OUT/'inference/series').glob('ep*.json'):records['series-'+p.stem]=json.loads(p.read_text())
    rows=[]
    for key,r in records.items():
        e=r['evidence'];assert r['provenance']=='local_inference' and e['model_digest']=='sha256:0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0'
        # StagedDraft and craft digest intentionally use the same canonical encoding.
        assert r['request_sha256']==digest(r['request'])
        assert r['raw_sha256']==hashlib.sha256(r['raw'].encode()).hexdigest()
        if e.get('raw_sha256'):assert e['raw_sha256']==r['raw_sha256']
        valid=bool(r['result'] is not None and Draft202012Validator(r['request']['schema']).is_valid(r['result']))
        if r['status']=='validated_stage':assert valid and e['inference_completed']
        row={'case':key,'role':r['request']['role'],'model':e['model'],'model_digest':e['model_digest'],
             'runtime_complete':e.get('inference_completed',False),'schema_valid':valid,'status':r['status'],'error':r.get('error',''),
             'wall_seconds':e.get('wall_seconds'),'eval_count':e.get('eval_count'),'raw_sha256':r['raw_sha256'],
             'knowledge_context_sha256':r['request'].get('knowledge_context_sha256'),'artistic_accepted':False}
        if key.startswith(('director-','qc-')) and r.get('result') is not None:
            got={f['line_id'] for f in r['result']['findings']};wanted=set() if key.endswith('clean') else {'L3'}
            row['strict_line_localization']={'expected':sorted(wanted),'observed':sorted(got),'matches':got==wanted,'scope':'Line localization only; issue/repair semantic accuracy is unreviewed.'}
        rows.append(row)
    if (OUT/'inference/series/series.json').exists():
        state=SeriesLedger(OUT/'inference/series').state();save('series_state.json',state)
    save('inference_summary.json',{'actual_calls':len(rows),'runtime_complete':sum(r['runtime_complete'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),
         'protocol_pass':sum(r['status']=='validated_stage' for r in rows),'wall_seconds':round(sum(r['wall_seconds'] or 0 for r in rows),3),
         'rows':rows,'human_reviews':0,'media_inference':0,'production_winners':[],
         'limitations':['One sample per task/arm; no statistical artistic ranking.',
                       'Only breakfast and wit have paired same-task controls; all other briefs differ from historical benchmarks.',
                       'Early development prompts retain .1 knowledge snapshots; final curated bundle is .2. Script lesson text is unchanged; hashes/version differences remain visible in original requests.',
                       'Strict line localization is not independent semantic criticism accuracy.',
                       'Software tests may overlap CPU inference; speed is observed, not an isolated performance benchmark.']})
    blind=OUT/'inference/blind-package.json';fingerprint=OUT/'inference/blind-input-sha256.txt'
    signature=digest(records)
    if not fingerprint.exists() or fingerprint.read_text().strip()!=signature:
        package,key=blind_package({k:{'role':r['request']['role'],'data':r['request']['data'],'task':r['request']['task'],'output':r['result'],'raw':r['raw'],'status':r['status']} for k,r in records.items()})
        save('inference/blind-package.json',package);save('inference/blind-admin-key.json',key);fingerprint.write_text(signature+'\n')
    if blind.exists():
        b=json.loads(blind.read_text());lines=['# Blind Bengali editorial package — unreviewed','No reviewer, ratings or artistic acceptance recorded. Withhold blind-admin-key.json from the reviewer.',
          'Read each original brief and unchanged output. Compare only candidates with identical tasks. Evaluate causality, natural dialogue, emotion, humor, filmable action, earned hook, continuity, targeted revision and evidence-grounded criticism.']
        for c in b['candidates']:lines+=['## '+c['id'],'```json',json.dumps(c['text'],ensure_ascii=False,indent=2),'```']
        lines+=['Reviewer: __________  Independence: __________  Date: __________','For each candidate: exact excerpt, observed issue, finding, score or insufficient evidence, accept/reject/defer. Leave blank until actual review.']
        (OUT/'BLIND_REVIEW.md').write_text('\n\n'.join(lines)+'\n')
    save('scope_checkpoint.json',{'parent':'f71e282a7274da850bab51c9848de925fe718e9a','scope_sha256':hashlib.sha256((ROOT/'assets/phase3/professional_scope.md').read_bytes()).hexdigest(),
         'agents_preserved':len(AGENTS),'knowledge_conditioning_not_weight_training':True,'new_model_variants':0,'new_cloud_resources':0,'paid_calls':0,'youtube_writes':0,
         'production_data_accessed':False,'Kaggle_or_Google_revisited':False,'knowledge_snapshots_preserved':True,
         'next_action':'Resume existing stages after blockers; independent editorial review and stronger-model approval remain separate. Do not regenerate completed cases.'})
    print('Verified software probes:',len(matrix),'Actual inference records:',len(rows))

if __name__=='__main__':export()
