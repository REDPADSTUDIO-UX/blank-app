"""Owner-authorized two-model download and identical CPU benchmark.
Only pinned Gemma3 and Qwen3.5 manifests from the recorded approval request.
No extra model, hosted fallback, GPU job or production approval.
"""
import hashlib,json,subprocess,threading,time,urllib.request
from pathlib import Path
from redpad_pipeline.local_ollama_session import local_cpu_session,ROOT
from redpad_pipeline.agents import AgentStore
from redpad_pipeline.model_routing import ModelRoutes,inventory
from redpad_pipeline.model_benchmark import run_case,cases

NAMES=['gemma3:4b-it-q4_K_M','qwen3.5:4b-q4_K_M']
OUT=ROOT/'verification/approved_comparison'
ROWS={r['model']:r for r in json.loads((ROOT/'verification/model_comparison/registry_metadata.json').read_text())}

def save(name,data):OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':
    store=AgentStore(ROOT/'phase3_runs/approved_comparison/agent_control.sqlite3')
    save('owner_authorization.json',{'owner_message':'porer porikha ar onumoti dilam','scope':'Explicit response to the request for exact two model downloads, Gemma terms consent, same six CPU tasks, and read-only existing free-GPU readiness. No new GPU/cloud/account/paid resource authorized.','models':NAMES,'gemma_terms_consented':True,'gemma_terms_source':'https://ai.google.dev/gemma/terms','baseline_reused':'verification/master_studio/qwen_control','independent_human_review_completed':False})
    with local_cpu_session() as env:
        for name in NAMES:
            row=ROWS[name]
            with urllib.request.urlopen(row['source'],timeout=45) as r:raw=r.read(100000)
            if 'sha256:'+hashlib.sha256(raw).hexdigest()!=row['manifest_digest']:raise RuntimeError('Approved candidate manifest changed; no substituted download.')
            binary=ROOT/'phase3_models/ollama-runtime/bin/ollama'
            print('Downloading approved pinned model',name,flush=True)
            with (OUT/(name.split(':')[0]+'-download.log')).open('w') as log:
                subprocess.run([str(binary),'pull',name],env=env,stdout=log,stderr=log,timeout=1200,check=True)
            if inventory().get(name)!=row['manifest_digest']:raise RuntimeError('Downloaded model digest mismatch.')
            manifest=json.loads(raw);blob_checks=[]
            for layer in [manifest['config'],*manifest['layers']]:
                path=ROOT/'phase3_models/ollama-weights/blobs'/layer['digest'].replace(':','-');h=hashlib.sha256()
                with path.open('rb') as f:
                    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
                if 'sha256:'+h.hexdigest()!=layer['digest'] or path.stat().st_size!=layer['size']:raise RuntimeError('Model blob verification failed.')
                blob_checks.append({'digest':layer['digest'],'bytes':layer['size'],'verified':True})
            save(name.split(':')[0]+'-installation.json',{'model':name,'manifest_digest':row['manifest_digest'],'verified_blobs':blob_checks,'fresh_pull_layer_bytes':row['fresh_pull_layer_bytes'],'GPU_used':False,'model_download_authorized':True,'production_approved':False})
            ModelRoutes(store).approve_installed(name,row['manifest_digest'],'Owner-consented Gemma terms' if name.startswith('gemma') else 'Apache-2.0; exact owner-approved candidate','owner authorization in current conversation',True)
            for case in cases():
                started=time.monotonic();stop=threading.Event();samples=[]
                def monitor():
                    import psutil
                    while not stop.is_set():
                        processes=[psutil.Process(),*psutil.Process().children(recursive=True)]
                        rss=0
                        for p in processes:
                            try:rss+=p.memory_info().rss
                            except psutil.Error:pass
                        samples.append(rss);stop.wait(.5)
                thread=threading.Thread(target=monitor,daemon=True);thread.start()
                try:result=run_case(store,ROOT/'phase3_runs/approved_comparison/cases',name,case['id'])
                finally:stop.set();thread.join(timeout=2)
                peak=max(samples,default=0)
                print(name,case['id'],result['status'],result.get('error',''),'RSS',peak,flush=True)
                for manifest_path in (ROOT/'phase3_runs/approved_comparison/cases').glob('*/manifest.json'):
                    m=json.loads(manifest_path.read_text())
                    if m['model']!=name:continue
                    dest=OUT/name.split(':')[0];dest.mkdir(parents=True,exist_ok=True)
                    for p in manifest_path.parent.glob('*.json'):(dest/p.name).write_bytes(p.read_bytes())
                    (dest/(case['id']+'-resource.json')).write_text(json.dumps({'peak_sampled_aggregate_rss_bytes':peak,'sample_interval_seconds':.5,'measurement':'Sum RSS of this Python process and owned Ollama descendants; shared pages may be counted more than once; not PSS','wall_seconds_including_postchecks':round(time.monotonic()-started,3)},indent=2))
            subprocess.run([str(binary),'stop',name],env=env,capture_output=True,timeout=30,check=True)
            print('Unloaded',name,flush=True)
