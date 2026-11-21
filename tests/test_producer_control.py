"""Phase 1 software evidence. All generated fixture responses are SIMULATION."""
import copy,io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from redpad_pipeline.agents import AGENTS,AgentError
from redpad_pipeline.studio_program import StudioProgram
from redpad_pipeline.producer_control import Producer,response
from redpad_pipeline.producer_references import inspect_file,MAX_FILE
from redpad_pipeline.specialists import example,prepare
from tests.test_agent_foundation import fixture

class ProducerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.patch=patch('redpad_pipeline.studio_program.PROGRAM_ROOT',Path(self.tmp.name));self.patch.start();self.addCleanup(self.patch.stop)
  self.p=StudioProgram('fictional-test');self.p.create('Phase 1 fixture','Original fictional technical fixture; not generated art',1,300)
  self.c=Producer(self.p);self.s=self.p.store;self.e=self.p.engine
 def task(self,role,data=None,deps=None,complete=None):
  rid=self.e.enqueue(role,data if data is not None else fixture(role),deps,mode='local' if complete else 'software')
  state=self.e.execute(rid,complete=complete)
  self.assertEqual(state,'Awaiting QC',next(r['error'] for r in self.e.runs() if r['id']==rid))
  return next(r['task'] for r in self.e.runs() if r['id']==rid)
 def approve(self,tid):
  t=next(t for t in self.s.tasks() if t['id']==tid)
  if t['agent']!='qc':self.s.review(tid,t['revision'],'Recommend','Independent test fixture inspection, not artistic review','qc')
  self.c.approve_batch([(tid,t['revision'])],'Explicit fixture owner action')
 def body(self,tid):
  return json.loads(json.loads([o for o in self.s.outputs() if o['task']==tid][-1]['payload'])['summary'])
 def image(self,name='fictional.png',rights='fictional_ai'):
  b=io.BytesIO();Image.new('RGB',(32,32),'gray').save(b,format='PNG')
  return self.c.refs.put(name,b.getvalue(),'casting','Manual synthetic test square; not an AI actor','Owner-authored technical fixture',rights)
 def casting(self):
  character=self.task('character',example('character'));self.approve(character)
  script=self.task('script');self.approve(script)
  direction=self.task('director');self.approve(direction)
  data=example('casting');data['records']=[]
  for char in ('rafi','hazera'):
   r=copy.deepcopy(example('casting')['records'][0]);a=self.image(char+'.png');r.update(id='candidate-'+char,character=char,actor_id='actor-'+char,image_refs=[{'id':a['id'],'version':a['version']}]);data['records'].append(r)
  data['sources']={role:{'$from':tid,'path':['artifact']} for role,tid in [('character',character),('screenplay',script),('director',direction)]}
  cast=self.task('casting',data,[character,script,direction]);return cast,character,data
 def lock(self,cast,confirm=False):
  self.s.review(cast,1,'Recommend','Independent metadata fixture assessment','qc')
  rid=self.c.casting.queue_review(cast)
  self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='ছবি acting-এর প্রমাণ নয়; media review pending.',delegations=[],risks=['No performance test'])),'Awaiting QC')
  tid=next(r['task'] for r in self.e.runs() if r['id']==rid)
  self.s.review(tid,1,'Recommend','Independent Director report inspection fixture','qc')
  return self.c.casting.lock(cast,tid,['candidate-rafi','candidate-hazera'],'Producer fixture identity approval only',confirm)
 def test_exactly_twenty_one_and_no_hair_makeup_agent(self):
  self.assertEqual(len(AGENTS),21);self.assertIn('casting',AGENTS)
  self.assertFalse(any('makeup' in k or 'hair' in k for k in AGENTS));self.assertIn('Hair styling and makeup',AGENTS['costume']['responsibilities'])
 def test_reference_parse_version_history_and_pin_invalidation(self):
  r=self.c.refs.put('story.txt','বাসের টিকিট লাল বাক্সে।'.encode(),'story',source='original')
  self.assertEqual(r['text'],'বাসের টিকিট লাল বাক্সে।')
  rid=self.c.say('রেফারেন্সের ভিত্তিতে পরামর্শ দিন।');task=next(r['task'] for r in self.e.runs() if r['id']==rid)
  with self.assertRaises(AgentError):self.c.refs.update(r['id'],1,category='character')
  new=self.c.refs.update(r['id'],1,True,category='character');self.assertEqual(new['version'],2)
  self.assertEqual(len(self.c.refs.rows(True)),2);self.assertTrue(self.c.refs.path(r).is_file())
  self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='stale',delegations=[],risks=[])),'Blocked')
 def test_media_not_understood_and_malformed_files_rejected(self):
  r=inspect_file('clip.mp4',b'\0\0\0\x18ftypisom'+b'0'*20)
  self.assertEqual(r['status'],'stored_uninspected');self.assertEqual(r['text'],'')
  for name,content in [('bad.png',b'fake'),('bad.mp4',b'fake'),('x.exe',b'fake'),('bad.txt',b'\xff')]:
   with self.subTest(name=name),self.assertRaises(AgentError):inspect_file(name,content)
  z=io.BytesIO()
  with zipfile.ZipFile(z,'w') as f:f.writestr('word/document.xml','<!DOCTYPE x [<!ENTITY a "x">]><x/>')
  with self.assertRaises(AgentError):inspect_file('unsafe.docx',z.getvalue())
 def test_docx_actual_text_and_pdf_limitations(self):
  z=io.BytesIO()
  with zipfile.ZipFile(z,'w') as f:f.writestr('word/document.xml','<w:document xmlns:w="word"><w:p><w:t>রাফির গল্প</w:t></w:p></w:document>')
  self.assertEqual(inspect_file('story.docx',z.getvalue())['text'],'রাফির গল্প')
  self.assertEqual(inspect_file('broken.pdf',b'%PDF-1.4\nnot a readable pdf')['status'],'parser_unavailable_or_failed')
 def test_persistent_real_engine_conversation_and_no_software_echo(self):
  rid=self.c.say('ঢাকায় পারিবারিক গল্পের পরিকল্পনা করুন।')
  self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='গল্পের আগে চরিত্রের লক্ষ্য ঠিক করি।',delegations=[],risks=['Unreviewed'])),'Awaiting QC')
  self.c.collect();self.c.collect();fresh=Producer(StudioProgram('fictional-test'))
  self.assertEqual(len(fresh.conversation()),2);self.assertIn('simulation',fresh.conversation()[-1]['text'])
  bad=self.e.enqueue('director',dict(producer_director_v1=True,message='echo',context={},reply=dict(reply='fake',delegations=[],risks=[])))
  self.assertEqual(self.e.execute(bad),'Failed')
 def test_missing_model_is_blocker_not_fabricated_director_reply(self):
  rid=self.c.say('বাস্তব উত্তর দিন।')
  with patch('socket.socket',side_effect=AssertionError('No external fallback')):self.assertEqual(self.e.execute(rid),'Blocked')
  self.c.collect();self.assertEqual(self.c.conversation()[-1]['speaker'],'status')
 def test_real_delegation_requires_approved_director_then_is_idempotent(self):
  rid=self.c.say('গল্প শুরু করুন।')
  raw=dict(reply='Story বিভাগে brief পাঠাই।',delegations=[dict(action='develop_story',episode=1,target_task='',targets=[],instruction='Original Bengali story')],risks=[])
  self.assertEqual(self.e.execute(rid,complete=lambda *_:raw),'Awaiting QC')
  tid=next(r['task'] for r in self.e.runs() if r['id']==rid)
  with self.assertRaises(AgentError):self.c.dispatch(tid)
  self.approve(tid);first=self.c.dispatch(tid);self.assertEqual(self.c.dispatch(tid),first)
  self.assertTrue(any(t['agent']=='story' for t in self.s.tasks()));self.assertFalse(self.p.summary()['auto_publish'])
 def test_batch_approval_atomic_with_independent_qc(self):
  a=self.task('art',example('art'));b=self.task('location',example('location'))
  self.s.review(a,1,'Recommend','Independent fixture metadata','qc')
  with self.assertRaises(AgentError):self.c.approve_batch([(a,1),(b,1)],'Owner batch')
  self.assertEqual(next(t['state'] for t in self.s.tasks() if t['id']==a),'QC recommended')
  self.s.review(b,1,'Recommend','Independent fixture metadata','qc');self.c.approve_batch([(a,1),(b,1)],'Owner batch')
  self.assertTrue(all(t['state']=='Approved' for t in self.s.tasks()))
 def test_feedback_goes_to_director_and_keeps_source_until_authorized(self):
  tid=self.task('art',example('art'));self.approve(tid)
  rid=self.c.feedback(tid,1,'Request Changes','Make set1 less ornate.')
  run=next(r for r in self.e.runs() if r['id']==rid)
  self.assertEqual(next(t['agent'] for t in self.s.tasks() if t['id']==run['task']),'director')
  self.assertEqual(next(t['state'] for t in self.s.tasks() if t['id']==tid),'Approved')
  with self.assertRaises(AgentError):self.c.revise(tid,['set1'],'Simplify',False)
  with self.assertRaises(AgentError):self.c.revise(tid,['missing'],'Simplify',True)
  self.c.revise(tid,['set1'],'Simplify',True)
  self.assertEqual(next(t['state'] for t in self.s.tasks() if t['id']==tid),'Revision requested')
 def test_casting_cannot_bypass_director_qc_or_identity_rights(self):
  cast,_,_=self.casting()
  self.s.review(cast,1,'Recommend','Independent candidate metadata review','qc')
  with self.assertRaises(AgentError):self.s.review(cast,1,'Approve','generic bypass','owner')
  with self.assertRaises(AgentError):self.c.approve_batch([(cast,1)],'bypass')
  with self.assertRaises(AgentError):self.c.casting.lock(cast,'missing',['candidate-rafi'],'bad')
 def test_casting_lock_costume_consumption_and_reference_replacement_stales(self):
  cast,char,data=self.casting();lock=self.lock(cast)
  costume=example('costume');costume['sources']={'casting':{'$from':cast,'path':['artifact']},'character':{'$from':char,'path':['artifact']}}
  for i,r in enumerate(costume['records']):r.update(actor_id='actor-rafi',hair='short black',makeup='natural',apparent_age=33,chronology=i,scene_state=dict(injury='none',sweat='none',rain='none',dirt='none'))
  tid=self.task('costume',costume,[cast,char]);body=self.body(tid)
  self.assertEqual(body['artifact']['derived']['casting_identity_locks'][0]['lock_id'],lock)
  self.assertFalse(body['creative_quality_verified']);self.approve(tid)
  ref=data['records'][0]['image_refs'][0];self.c.refs.update(ref['id'],1,True,notes='replacement observation')
  with self.s.tx() as db:
   with self.assertRaises(AgentError):self.s._current(db,self.s._task(db,tid))
 def test_wrong_actor_unexplained_hair_change_and_portrait_acting_rejected(self):
  cast,char,data=self.casting();self.lock(cast)
  r=data['records'][0]['image_refs'][0]
  with self.assertRaises(AgentError):self.c.casting.evaluate(cast,'performance',[r],'Portrait proves acting','Test reviewer')
  self.c.casting.evaluate(cast,'appearance',[r],'Technical square only, no artistic acceptance','Test reviewer')
  costume=example('costume');costume['sources']={'casting':self.body(cast)['artifact']}
  for i,row in enumerate(costume['records']):row.update(actor_id='actor-rafi',hair='short',makeup='natural',apparent_age=33,chronology=i,scene_state=dict(injury='none',sweat='none',rain='none',dirt='none'))
  costume['records'][1]['hair']='long'
  with self.assertRaises(AgentError):prepare('costume',costume)
 def test_recast_invalidates_consumers_and_preserves_old_outputs(self):
  cast,char,data=self.casting();first=self.lock(cast)
  run=self.e.enqueue('performance',dict(example('performance'),sources={'casting':{'$from':cast,'path':['artifact']}}),[cast])
  self.assertEqual(self.e.execute(run),'Awaiting QC');tid=next(r['task'] for r in self.e.runs() if r['id']==run)
  old=self.body(tid)
  second=self.task('casting',data,[char]+[r['id'] for r in json.loads(next(t['refs'] for t in self.s.tasks() if t['id']==cast)) if r['id']!=char])
  with self.assertRaises(AgentError):self.lock(second,False)
  # The failed attempt preserved the pending QC and Director review, so use its exact review.
  with self.s.tx() as db:review=db.execute('SELECT task FROM casting_inspections WHERE source=?',(second,)).fetchone()[0]
  new=self.c.casting.lock(second,review,['candidate-rafi','candidate-hazera'],'Explicit recast fixture',True)
  self.assertNotEqual(first,new);self.assertEqual(self.body(tid),old)
  with self.s.tx() as db:
   with self.assertRaises(AgentError):self.s._current(db,self.s._task(db,tid))
 def test_generated_graph_contains_casting_before_consumers_legacy_graph_untouched(self):
  from redpad_pipeline.specialist_project import DEPENDENCIES,CASTING_DEPENDENCIES,queue_generated_project
  self.assertEqual(len(DEPENDENCIES),17);self.assertEqual(len(CASTING_DEPENDENCIES),18)
  script=self.task('script');self.approve(script);director=self.task('director');self.approve(director)
  plan=queue_generated_project(self.e,'test',[script,director]);self.assertIn('casting',plan['tasks'])
  for role in ('costume','performance','video','voice','continuity'):
   run=next(r for r in self.e.runs() if r['id']==plan['runs'][role]);self.assertIn(plan['tasks']['casting'],json.loads(run['dependencies']))
 def test_targeted_script_revision_preserves_other_scenes_and_unrelated_approval(self):
  from tests.test_creative import samples,request
  d=samples();story=self.task('story',request('season',d['season']));self.approve(story)
  direction=self.task('director',request('direction',d['direction_story'],source={'$from':story,'path':['artifact']}),[story]);self.approve(direction)
  script=self.task('script',request('screenplay',d['screenplay'],source={'$from':story,'path':['artifact']}),[story,direction]);self.approve(script)
  unrelated=self.task('art',example('art'));self.approve(unrelated)
  old=self.body(script)['artifact'];target=old['scenes'][1]['id']
  rid=self.c.revise(script,[target],'Keep emotion understated; preserve other scenes.',True)
  replacement=copy.deepcopy(old['scenes'][1])
  # Preserve the valid fixture scene while proving scope enforcement; no creative improvement claimed.
  seen=[]
  def provider(system,prompt):seen.append(system);return [replacement]
  self.assertEqual(self.e.execute(rid,complete=provider),'Awaiting QC')
  new=self.body(script);self.assertEqual(new['provenance'],'simulation')
  self.assertEqual(new['artifact']['scenes'][0],old['scenes'][0]);self.assertIn('Keep emotion understated',seen[0])
  self.assertEqual(next(t['state'] for t in self.s.tasks() if t['id']==unrelated),'Approved')
 def test_rejected_pending_version_cannot_be_approved_without_revision(self):
  tid=self.task('art',example('art'));self.s.review(tid,1,'Recommend','Independent fixture QC','qc')
  self.c.feedback(tid,1,'Reject','Wrong production look; revise set1.')
  with self.assertRaises(AgentError):self.c.approve_batch([(tid,1)],'Accidental approval')
 def test_story_episode_revision_uses_real_number_and_blocks_other_episode_changes(self):
  from tests.test_creative import samples,request
  d=samples();tid=self.task('story',request('season',d['season']));self.approve(tid)
  old=self.body(tid)['artifact'];number=str(old['episodes'][0]['number'])
  rid=self.c.revise(tid,[number],'Only revise this episode causal beat.',True)
  changed=copy.deepcopy(old);changed['premise']='Changed outside episode target'
  self.assertEqual(self.e.execute(rid,complete=lambda *_:changed),'Failed')
  self.assertEqual(len([o for o in self.s.outputs() if o['task']==tid]),1)
 def test_director_plan_feedback_cannot_outlive_reviewed_revision(self):
  tid=self.task('art',example('art'));self.approve(tid)
  rid=self.c.feedback(tid,1,'Request Changes','Revise set1.')
  revision=self.c.revise(tid,['set1'],'Simplify set1.',True)
  self.assertEqual(self.e.execute(revision,complete=lambda *_:{'records':example('art')['records']}),'Awaiting QC')
  self.assertEqual(self.e.execute(rid,complete=lambda *_:dict(reply='old feedback',delegations=[],risks=[])),'Blocked')
 def test_generic_advanced_approval_cannot_bypass_producer_rejection(self):
  tid=self.task('art',example('art'));self.s.review(tid,1,'Recommend','Independent fixture QC','qc')
  self.c.feedback(tid,1,'Reject','Wrong look.')
  with self.assertRaises(AgentError):self.s.review(tid,1,'Approve','Bypass','owner')

 def test_reference_tamper_blocks_inference_before_provider_call(self):
  r=self.image();rid=self.c.say('Use the actual reference.')
  self.c.refs.path(r).write_bytes(b'tampered')
  def provider(*_):raise AssertionError('Must not infer with tampered source')
  self.assertEqual(self.e.execute(rid,complete=provider),'Blocked')

 def test_model_cannot_create_approval_or_unknown_actions(self):
  with self.assertRaises(AgentError):response(dict(reply='publish',delegations=[dict(action='publish',episode=1,target_task='',targets=[],instruction='upload')],risks=[]))
  x=example('casting');x['records'][0]['performance_passed']=True
  with self.assertRaises(AgentError):prepare('casting',x)

if __name__=='__main__':unittest.main()
