"""Explicit mode-controlled arm; no download, altered brief or silent retry."""
import json
import threading
import time
import psutil
from experiments.run_approved_candidates import OUT, ROOT
from redpad_pipeline.local_ollama_session import local_cpu_session
from redpad_pipeline.agents import AgentStore
from redpad_pipeline.model_benchmark import cases, run_case

if __name__=='__main__':
    name='qwen3.5:4b-q4_K_M'
    store=AgentStore(ROOT/'phase3_runs/approved_comparison/agent_control.sqlite3')
    dest=OUT/'qwen3.5-nonthinking';dest.mkdir(parents=True,exist_ok=True)
    with local_cpu_session():
        for case in cases():
            stop=threading.Event();samples=[];start=time.monotonic()
            def monitor():
                while not stop.is_set():
                    rss=0
                    for p in [psutil.Process(),*psutil.Process().children(recursive=True)]:
                        try:rss+=p.memory_info().rss
                        except psutil.Error:pass
                    samples.append(rss);stop.wait(.5)
            thread=threading.Thread(target=monitor,daemon=True);thread.start()
            try:r=run_case(store,ROOT/'phase3_runs/approved_comparison/cases',name,case['id'],think=False)
            finally:stop.set();thread.join(timeout=2)
            for manifest in (ROOT/'phase3_runs/approved_comparison/cases').glob('*/manifest.json'):
                m=json.loads(manifest.read_text())
                if m['model']==name and m.get('think') is False:
                    for p in manifest.parent.glob('*.json'):(dest/p.name).write_bytes(p.read_bytes())
            (dest/(case['id']+'-resource.json')).write_text(json.dumps({'peak_sampled_aggregate_rss_bytes':max(samples,default=0),'sample_interval_seconds':.5,'measurement':'Sum RSS, including shared pages; not PSS','wall_seconds_including_postchecks':round(time.monotonic()-start,3)},indent=2))
            print(case['id'],r['status'],r.get('error',''),flush=True)
