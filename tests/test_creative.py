import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from redpad_pipeline.agents import AgentStore,AgentError
from redpad_pipeline.agent_engine import Engine
from redpad_pipeline.creative import prepare_creative,evaluate,WEIGHTS,rewrite,creative_prompt

ROOT=Path(__file__).resolve().parents[1]
def samples():return json.loads((ROOT/'assets/writing/creative/scenarios.json').read_text())
def request(kind,artifact,brief=None,**extra):
 return dict(creative_v1=True,kind=kind,brief=brief or samples()['brief'],artifact=artifact,**extra)

class CreativeTests(unittest.TestCase):
 def setUp(self):
  self.data=samples();self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.s=AgentStore(Path(self.tmp.name)/'agent_control.sqlite3');self.e=Engine(self.s)
 def approve(self,tid):
  t=next(t for t in self.s.tasks() if t['id']==tid)
  self.s.review(tid,t['revision'],'Recommend','Independent manual test review','qc')
  self.s.review(tid,t['revision'],'Approve','Simulated owner test approval','owner')
 def run_task(self,key,req,deps=None,complete=None):
  rid=self.e.enqueue(key,req,deps,mode='local' if complete else 'software')
  state=self.e.execute(rid,complete=complete);r=next(r for r in self.e.runs() if r['id']==rid)
  self.assertEqual(state,'Awaiting QC',r['error']);return r['task']
 def test_a_family_romance_architecture(self):
  out=prepare_creative('story',request('season',self.data['romance_season'],self.data['romance_brief']))
  self.assertEqual(len(out['artifact']['episodes']),5);self.assertFalse(out['creative_quality_verified'])
 def test_b_30_episode_architecture(self):
  a=self.data['season'];prepare_creative('story',request('season',a))
  a['episodes'].pop()
  with self.assertRaises(AgentError):prepare_creative('story',request('season',a))
 def test_c_five_minute_visual_first_screenplay(self):
  out=prepare_creative('script',request('screenplay',self.data['screenplay']))
  self.assertIn('estimated',out['formatted']);self.assertEqual(sum(s['seconds'] for s in out['artifact']['scenes']),300)
 def test_d_weak_repair_is_targeted_and_not_quality_proof(self):
  weak=self.data['weak_script']
  with self.assertRaises(AgentError):prepare_creative('script',request('screenplay',weak))
  replacement={'scenes':[self.data['screenplay']['scenes'][1]],'ending':self.data['screenplay']['ending']}
  out=prepare_creative('script',request('rewrite',replacement,source=weak,targets=['s2','__ending__']))
  self.assertEqual(out['artifact']['scenes'][0],weak['scenes'][0]);self.assertEqual(out['artifact']['scenes'][2],weak['scenes'][2])
  self.assertFalse(out['creative_quality_verified'])
 def test_e_cross_episode_continuity(self):
  brief=dict(self.data['brief'],episodes=3)
  out=prepare_creative('story',request('season',self.data['continuity_season'],brief))
  self.assertTrue(any(f['code']=='continuity_change' and f['episode']==3 for f in out['findings']))
 def test_treatment_and_long_formats(self):
  a=copy.deepcopy(self.data['screenplay'])
  with self.assertRaises(AgentError):prepare_creative('script',request('treatment',a))
  for s in a['scenes']:s['beats']=[b for b in s['beats'] if b['type']=='action']
  for duration in (300,900,1800,4200):
   test=copy.deepcopy(a);test['scenes']=[]
   remaining=duration;i=1
   while remaining:
    s=copy.deepcopy(a['scenes'][0]);secs=min(300,remaining);s.update(id='s'+str(i),number=i,seconds=secs,action_seconds=secs-10,pause_seconds=5)
    test['scenes'].append(s);remaining-=secs;i+=1
   test['ending']['setup_scene_ids']=['s1']
   out=prepare_creative('script',request('treatment',test,dict(self.data['brief'],seconds=duration)))
   self.assertEqual(sum(s['seconds'] for s in out['artifact']['scenes']),duration)
 def test_full_collaboration_and_independent_approval(self):
  with patch('socket.socket',side_effect=AssertionError('No network')):
   story=self.run_task('story',request('season',self.data['season']));self.approve(story)
   review=self.run_task('director',request('direction',self.data['direction_story'],source={'$from':story,'path':['artifact']}),[story]);self.approve(review)
   script=self.run_task('script',request('screenplay',self.data['screenplay'],source={'$from':story,'path':['artifact']}),[story,review]);self.approve(script)
   second=self.run_task('director',request('direction',self.data['direction_script'],source={'$from':script,'path':['artifact']}),[script]);self.approve(second)
   for actor in ('director','script'):
    with self.assertRaises(AgentError):self.s.review(script,1,'Approve','self',actor)
   revised=self.run_task('script',request('rewrite',[self.data['screenplay']['scenes'][1]],source={'$from':script,'path':['artifact']},targets=['s2']),[script,second])
   self.assertEqual(len(self.s.outputs()),5)
 def test_forged_source_and_missing_director_blocked(self):
  rid=self.e.enqueue('script',request('screenplay',self.data['screenplay'],source=self.data['season']))
  self.assertEqual(self.e.execute(rid),'Failed')
 def test_director_evidence_and_complete_coverage(self):
  a=self.data['direction_script'];prepare_creative('director',request('direction',a,source=self.data['screenplay']))
  a['scenes'][0]['evidence']='fabricated quote'
  with self.assertRaises(AgentError):prepare_creative('director',request('direction',a,source=self.data['screenplay']))
 def test_ending_links_to_real_scenes(self):
  a=self.data['screenplay'];a['ending']['setup_scene_ids']=['missing']
  with self.assertRaises(AgentError):prepare_creative('script',request('screenplay',a))
 def test_scores_require_evidence_and_provenance(self):
  a=self.data['screenplay'];quote=a['title']
  ratings={d:dict(score=5,strength='fixture strength',weakness='fixture weakness',evidence=quote,revision='fixture revision') for d in WEIGHTS}
  report=evaluate(a,ratings,'test evaluator','simulation');self.assertEqual(report['score'],50)
  self.assertFalse(report['production_quality_verified']);self.assertFalse(report['owner_approval'])
  new=evaluate(a,ratings,'test evaluator','simulation',report);self.assertEqual(new['score_delta'],0)
  ratings['emotion_psychology']['evidence']='invented'
  with self.assertRaises(AgentError):evaluate(a,ratings,'test evaluator','simulation')
 def test_local_block_and_raw_simulation_record(self):
  req=request('season',self.data['season']);rid=self.e.enqueue('story',req,mode='local')
  self.assertEqual(self.e.execute(rid),'Blocked')
  self.e.retry(rid);self.assertEqual(self.e.execute(rid,complete=lambda *_:self.data['season']),'Awaiting QC')
  with self.s.tx() as db:r=db.execute('SELECT provenance,raw_output FROM creative_model_attempts').fetchone()
  self.assertEqual(r[0],'simulation');self.assertEqual(json.loads(r[1]),self.data['season'])
 def test_rewrite_scope_and_payoff_order(self):
  with self.assertRaises(AgentError):rewrite(self.data['screenplay'],[self.data['screenplay']['scenes'][0]],['s2'])
  a=self.data['season'];a['setups'][0]['payoff_episode']=0
  with self.assertRaises(AgentError):prepare_creative('story',request('season',a))
 def test_prompts_reuse_licensed_guidance_not_training(self):
  system,prompt=creative_prompt('story',request('season',self.data['season']),{})
  self.assertIn('CC-BY-3.0',prompt);self.assertIn('NOT weight training',prompt);self.assertIn('organic wit',system)
if __name__=='__main__':unittest.main()
