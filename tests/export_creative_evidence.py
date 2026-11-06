"""Reproducible software evidence; explicitly not real model writing samples."""
import copy,json,tempfile,hashlib
from pathlib import Path
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.creative import prepare_creative,render
from redpad_pipeline.readiness import inspect_resources
from tests.test_creative import samples,request


def main():
 root=Path(__file__).resolve().parents[1]/'verification/creative';root.mkdir(parents=True,exist_ok=True)
 d=samples();reports={}
 for tag,key,req in [('A','story',request('season',d['romance_season'],d['romance_brief'])),
                     ('B','story',request('season',d['season'])),('C','script',request('screenplay',d['screenplay'])),
                     ('E','story',request('season',d['continuity_season'],dict(d['brief'],episodes=3)))]:
  result=prepare_creative(key,req);reports[tag]={'status':'software_fixture_pass','findings':result['findings'],'artifact_sha256':result['artifact_sha256'],'creative_score':None,'provenance':'manually authored original fixture'}
 try:prepare_creative('script',request('screenplay',d['weak_script']))
 except AgentError as exc:before=str(exc)
 repaired=prepare_creative('script',request('rewrite',{'scenes':[d['screenplay']['scenes'][1]],'ending':d['screenplay']['ending']},source=d['weak_script'],targets=['s2','__ending__']))
 reports['D']={'status':'structural_repair_pass','before':before,'after_findings':repaired['findings'],'unchanged_scenes':['s1','s3'],'creative_score':None,'provenance':'manual replacement fixture; no model judgment'}
 with tempfile.TemporaryDirectory() as directory:
  store=AgentStore(Path(directory)/'agent_control.sqlite3');engine=Engine(store)
  def run(key,req,deps):
   rid=engine.enqueue(key,req,deps);assert engine.execute(rid)=='Awaiting QC'
   tid=next(r['task'] for r in engine.runs() if r['id']==rid)
   store.review(tid,1,'Recommend','Synthetic independent review for software test','qc')
   store.review(tid,1,'Approve','Synthetic owner action in isolated test only','owner')
   return tid
  story=run('story',request('season',d['season']),[])
  review=run('director',request('direction',d['direction_story'],source={'$from':story,'path':['artifact']}),[story])
  script=run('script',request('screenplay',d['screenplay'],source={'$from':story,'path':['artifact']}),[story,review])
  review2=run('director',request('direction',d['direction_script'],source={'$from':script,'path':['artifact']}),[script])
  revision=run('script',request('rewrite',[d['screenplay']['scenes'][1]],source={'$from':script,'path':['artifact']},targets=['s2']),[script,review2])
  blocked=[]
  for key,req,deps in [('story',request('season',d['season']),[]),('director',request('direction',d['direction_story'],source={'$from':story,'path':['artifact']}),[story]),('script',request('screenplay',d['screenplay'],source={'$from':story,'path':['artifact']}),[story,review])]:
   rid=engine.enqueue(key,req,deps,'local');assert engine.execute(rid)=='Blocked';blocked.append(next(r for r in engine.runs() if r['id']==rid))
  def compact(run):
   return {**{k:v for k,v in run.items() if k!='inputs'},'input_sha256':hashlib.sha256(run['inputs'].encode()).hexdigest()}
  evidence={'scope':'Original manually authored Bengali software fixtures, simulated human approvals; not real AI outputs',
   'scenarios':reports,'runs':[compact(r) for r in engine.runs()],'audit':store.history(),'model_attempts_blocked':[compact(r) for r in blocked],
   'real_inference_count':0,'human_reviewed_creative_results':0,'production_quality_verified':False,'weight_training':False,
   'readiness':inspect_resources(probe=True)}
  (root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 lines=['# Original manual Bengali examples — NOT model-generated','', 'These examples exercise software contracts only. Five-minute timing is an estimate, not a validated finished episode or premium quality claim.','', '## A — Family romantic drama, five-episode outline','']
 for e in d['romance_season']['episodes']:lines.append(f"{e['number']}. **{e['objective']}** — {e['cause']} {e['payoff']}")
 lines+=['','## B — Thirty-episode horror architecture','']
 for e in d['season']['episodes']:lines.append(f"{e['number']}. **{e['objective']}** — {e['cause']} {e['payoff']}")
 lines+=['','## C — Episode 1 / five-minute timing fixture','',render(d['screenplay'],'screenplay'),'', '## D — Structural repair', '',before,'', 'Only s2 and the ending metadata were replaced; s1 and s3 were preserved. Emotional/comedic improvement is not independently verified.','', '## E — Continuity fixture','',json.dumps(reports['E']['findings'],ensure_ascii=False,indent=2)]
 (root/'MANUAL_BENGALI_EXAMPLES.md').write_text('\n'.join(lines)+'\n')
 print('PASS: A–E software examples and collaboration evidence exported; 3 model calls blocked; real inference 0')
if __name__=='__main__':main()
