"""Failure-boundary tests; generated codec fixtures are not realistic drama evidence."""
import json,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from redpad_pipeline.drama_quality import Studio,QualityError,assert_content_publishable
from redpad_pipeline.drama_finish import render,compose_cue,sound_event
from redpad_pipeline.drama_free import visual_sample,voice_sample,probe

class DramaQualityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.studio=Studio(self.root/'demo.db',self.root/'media');self.pid=self.studio.create('Original test project',20)
  for component,item,p in [
   ('research','R',{'classification':'fictional_choice','claim':'Fictional night','application':'Invented setting'}),
   ('season','main',{'premise':'A test premise','arc':'Conflict to consequence','episodes':[{'n':1,'summary':'Fiction'}]}),
   ('bible','rafi',{'identity':'Fictional Bangladeshi man','continuity':'Black shirt','reference_required':True}),
   ('scene','S',{'start':0,'end':20,'objective':'Find document','obstacle':'Locked door','turn':'Chooses to leave','consequence':'Sound stops him','setting':'Fictional house','action':'He turns','research_ids':['R']}),
   ('line','L',{'start':0,'end':5,'scene_id':'S','speaker':'rafi','addressee':'friend','text':'আমি ফিরব।','intention':'reassure','emotion':'restrained','pace':'natural','pauses':'one breath','emphasis':'intent','lexicon_ids':[]}),
   ('shot','Q',{'order':1,'start':0,'scene_id':'S','seconds':20,'action':'He turns','framing':'Close','camera_reason':'See reaction','reference_ids':['rafi'],'line_ids':['L'],'coverage':'reaction','style':'photorealistic'})]:self.save(component,item,p)
 def save(self,component,item,p):return self.studio.save(self.pid,component,item,p,self.studio.entries(self.pid).get(component+'/'+item,{}).get('revision',0))
 def voice(self,line='L'):
  p=self.studio.root/self.pid/'voice.wav';p.parent.mkdir(exist_ok=True);rate=24000;t=np.arange(rate)/rate
  with wave.open(str(p),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes((np.sin(t*2*np.pi*220)*8000).astype('<i2').tobytes())
  return self.studio.register_asset(self.pid,'voice',line,p,dict(engine='offline codec fixture, not an actor',output_kind='neural_dialogue',rights_url='https://example.org/original',rights_note='Test-only original synthesis; not performance evidence',rights_scope='internal_test',cost_usd=0,paid_api=False))
 def test_revision_history_and_concurrent_editor_protection(self):
  p=self.studio.entries(self.pid)['scene/S']['payload'];p['turn']='New consequence';self.save('scene','S',p)
  self.assertEqual(len(self.studio.history(self.pid,'scene','S')),2)
  with self.assertRaisesRegex(QualityError,'changed elsewhere'):self.studio.save(self.pid,'scene','S',p,1)
 def test_spoken_line_correction_changes_only_relevant_assets(self):
  self.save('lexicon','time',{'written':'১:১৭','spoken':'একটা সতেরো','reason':'clock time'})
  p=self.studio.entries(self.pid)['line/L']['payload'];p['text']='এখন ১:১৭।';p['lexicon_ids']=['time'];self.save('line','L',p)
  aid=self.voice();self.assertIn('একটা সতেরো',self.studio.spoken_line(self.pid,'L'))
  self.save('lexicon','unused',{'written':'অন্য','spoken':'অন্য','reason':'separate word'})
  self.assertTrue(next(a for a in self.studio.assets(self.pid) if a['id']==aid)['current'])
  self.save('lexicon','time',{'written':'১:১৭','spoken':'রাত একটা সতেরো','reason':'clarify the scene'})
  self.assertFalse(next(a for a in self.studio.assets(self.pid) if a['id']==aid)['current'])
 def test_line_edit_invalidates_its_shot_but_not_other_scene(self):
  q=self.studio.fingerprint(self.pid,'shot/Q')
  self.save('scene','other',{'objective':'Other','obstacle':'Other','turn':'Other','consequence':'Other','setting':'Elsewhere','action':'Wait','research_ids':['R']})
  before=self.studio.fingerprint(self.pid,'scene/other');p=self.studio.entries(self.pid)['line/L']['payload'];p['text']='আমি এখন যাব।';self.save('line','L',p)
  self.assertNotEqual(q,self.studio.fingerprint(self.pid,'shot/Q'));self.assertEqual(before,self.studio.fingerprint(self.pid,'scene/other'))
 def test_uncertainty_never_selects_a_take_and_fail_revokes_acceptance(self):
  aid=self.voice()
  for d in ('pronunciation','performance','clarity'):self.studio.review(self.pid,aid,d,'needs_review','agent','agent','Codec activity only, no actual listening assessment.')
  with self.assertRaisesRegex(QualityError,'editorial'):self.studio.select(self.pid,aid)
  # These are explicitly contract-test reviews, not model-generated quality evidence.
  for d in ('pronunciation','performance','clarity'):self.studio.review(self.pid,aid,d,'pass','test reviewer','agent','Test fixture review to exercise the selection boundary.')
  self.studio.select(self.pid,aid)
  self.studio.review(self.pid,aid,'clarity','fail','test reviewer','agent','Later review finds the fixture is not speech.')
  with self.assertRaises(QualityError):self.studio.select(self.pid,aid)
  self.assertTrue(any('line/L' in x for x in self.studio.gates(self.pid)['full_render']['issues']))
 def test_asset_bytes_changed_invalidates_reviews(self):
  aid=self.voice();a=next(a for a in self.studio.assets(self.pid) if a['id']==aid);Path(a['path']).chmod(0o644);Path(a['path']).write_bytes(b'not the reviewed media')
  self.assertFalse(next(a for a in self.studio.assets(self.pid) if a['id']==aid)['current'])
  with self.assertRaises(QualityError):self.studio.review(self.pid,aid,'clarity','pass','agent','agent','Cannot certify changed file contents.')
 def test_cartoon_and_nonzero_cost_are_rejected_before_media_processing(self):
  p=self.studio.root/self.pid/'bad.mp4';p.parent.mkdir(exist_ok=True);p.write_bytes(b'bad')
  for kind in ('cartoon','procedural_2d','still_animatic','mock'):
   with self.assertRaisesRegex(QualityError,'no cartoon'):self.studio.register_asset(self.pid,'shot','Q',p,{'output_kind':kind})
  with self.assertRaisesRegex(QualityError,'zero-cost'):self.studio.register_asset(self.pid,'voice','L',p,dict(output_kind='neural_dialogue',engine='test',rights_url='https://example.org',rights_note='test',cost_usd=.01,paid_api=True))
 def test_wrong_stream_cannot_be_imported_as_real_footage(self):
  aid=self.voice();a=next(a for a in self.studio.assets(self.pid) if a['id']==aid)
  with self.assertRaisesRegex(QualityError,'no video stream'):self.studio.register_asset(self.pid,'shot','Q',a['path'],dict(output_kind='photorealistic_neural_video',engine='test',rights_url='https://example.org',rights_note='Test',cost_usd=0,paid_api=False))
 def test_path_traversal_and_foreign_media_are_blocked(self):
  p=self.root/'outside.wav';p.write_bytes(b'not imported')
  with self.assertRaisesRegex(QualityError,'Import media'):self.studio.register_asset(self.pid,'voice','L',p,{})
  with self.assertRaises(QualityError):self.studio.save(self.pid,'line','../bad',{},0)
 def test_render_blocked_before_ffmpeg_and_no_fallback(self):
  with patch('redpad_pipeline.drama_finish.ff') as ff:
   with self.assertRaisesRegex(QualityError,'Full render blocked'):render(self.studio,self.pid)
   ff.assert_not_called()
  self.assertFalse(self.studio.gates(self.pid)['full_render']['passed'])
 def test_timeline_and_research_evidence_required(self):
  p=self.studio.entries(self.pid)['research/R']['payload'];p['classification']='verified_fact';self.save('research','R',p)
  self.assertTrue(any('source evidence' in x for x in self.studio.structural_issues(self.pid)))
  p=self.studio.entries(self.pid)['shot/Q']['payload'];p['seconds']=3;self.save('shot','Q',p)
  self.assertTrue(any('target' in x for x in self.studio.structural_issues(self.pid)))
 def test_stage_order_and_changed_script_polish(self):
  with self.assertRaises(QualityError):self.studio.record_stage(self.pid,'dialogue_polish','Not yet developed','test')
  for stage in ('development','first_draft','script_edit','dialogue_polish'):self.studio.record_stage(self.pid,stage,'Actual contract-test stage observation','test')
  self.assertTrue(self.studio.gates(self.pid)['development']['passed'])
  p=self.studio.entries(self.pid)['line/L']['payload'];p['text']='আমি যাব না।';self.save('line','L',p)
  self.assertFalse(self.studio.gates(self.pid)['development']['passed'])
 def test_pending_job_blocks_duplicate_or_uncertain_submission(self):
  jid=self.studio.start_job(self.pid,'shot','Q')
  with self.assertRaisesRegex(QualityError,'uncertain'):self.studio.start_job(self.pid,'shot','Q')
  self.studio.job_state(jid,'blocked','Free quota unavailable')
  with self.assertRaises(QualityError):self.studio.start_job(self.pid,'shot','Q')
 def test_research_and_sound_plan_not_equivalent_to_real_sample(self):
  self.assertFalse(self.studio.gates(self.pid)['representative_scene']['passed'])
  with self.assertRaises(QualityError):voice_sample(self.studio,self.pid,'L')
 def test_reachable_endpoint_is_not_verified_quota_or_production_rights(self):
  class Response:
   status_code=200
   def json(self):return {'named_endpoints':{'/generate_video':{}}}
  with patch('requests.get',return_value=Response()):probe(self.studio,self.pid)
  gates=self.studio.gates(self.pid);self.assertFalse(gates['capability']['passed'])
  cap=self.studio.entries(self.pid)['capability/video']['payload'];self.assertEqual(cap['access'],'endpoint_reachable');self.assertIsNone(cap['remaining_gpu_seconds'])
 def test_sound_events_have_story_boundaries_and_no_transition_fallback(self):
  self.save('sfx','rain',dict(shot_id='Q',offset=0,global_start=0,duration=20,event='Rain ends at 10s',sound='rain',kind='ambience',distance='far',room='window',perspective='inside',must_stop_by=10))
  self.assertTrue(any('stop event' in x for x in self.studio.structural_issues(self.pid)))
  with self.assertRaisesRegex(QualityError,'No generic transition'):sound_event(self.root/'event.wav',{'sound':'generic_whoosh','duration':1})
 def test_music_requires_a_composition_plan_and_cannot_fill_silence(self):
  p=dict(scene_ids=['S'],start=0,end=10,purpose='Grief',progression='Recede',treatment='composed')
  self.save('music','M',p);self.assertTrue(any('harmonic development' in x for x in self.studio.structural_issues(self.pid)))
  self.save('music','quiet',dict(scene_ids=['S'],start=5,end=15,purpose='Listen',progression='Room only',treatment='silence'))
  self.assertTrue(any('overlaps' in x for x in self.studio.structural_issues(self.pid)))
 def test_original_music_sketch_is_a_real_audio_component_not_auto_approved(self):
  cue=dict(start=0,end=4,treatment='composed',instrumentation='Plucks and strings',motif='D A E F',harmony='D minor add9')
  p=self.root/'music.wav';meta=compose_cue(p,cue)
  with wave.open(str(p)) as w:self.assertEqual(w.getnchannels(),2);self.assertEqual(w.getnframes(),192000)
  self.assertEqual(meta['output_kind'],'composed_music');self.assertNotIn('approved',meta)
 def test_existing_approval_and_youtube_paths_cannot_bypass_strict_project(self):
  with self.studio.tx() as db:
   db.executescript("CREATE TABLE content(id INTEGER PRIMARY KEY,script TEXT,status TEXT);INSERT INTO content VALUES(1,'script','Approved');UPDATE dq_projects SET content_id=1;")
  with self.assertRaisesRegex(QualityError,'no quality-approved'):assert_content_publishable(self.studio.db,self.studio.root.parent,1)
  from redpad_pipeline.review_guard import ensure_current_source
  from redpad_pipeline.models import ProductionError
  from redpad_pipeline.youtube import snapshot,YouTubeError
  with self.assertRaises(ProductionError):ensure_current_source(self.studio.db,self.studio.root.parent,1)
  with self.assertRaises(YouTubeError):snapshot(self.studio.db,self.studio.root.parent,1)
 def test_legacy_row_is_not_relabelled_or_deleted(self):
  assert_content_publishable(self.studio.db,self.studio.root.parent,99)
  self.assertEqual(len(self.studio.projects()),1)
 def test_direct_studio_script_edit_breaks_binding(self):
  with self.studio.tx() as db:
   db.executescript("CREATE TABLE content(id INTEGER PRIMARY KEY,script TEXT,status TEXT,updated_at TEXT);INSERT INTO content VALUES(1,'draft','Draft','now');UPDATE dq_projects SET content_id=1;")
  self.studio.sync_content_script(self.pid)
  self.assertFalse(any('draft and versioned' in x for x in self.studio.structural_issues(self.pid)))
  with self.studio.tx() as db:db.execute("UPDATE content SET script='untracked replacement' WHERE id=1")
  self.assertTrue(any('draft and versioned' in x for x in self.studio.structural_issues(self.pid)))
 def test_cycles_and_credentials_are_not_persisted_as_valid_inputs(self):
  with self.assertRaises(QualityError):self.save('capability','bad',{'api_key':'never-store'})
  p=self.studio.entries(self.pid)['scene/S']['payload'];p['depends_on']=['line/L'];self.save('scene','S',p)
  self.assertTrue(any('Circular' in x for x in self.studio.structural_issues(self.pid)))
 def test_voice_assignment_changes_voice_without_invalidating_picture(self):
  before_shot=self.studio.fingerprint(self.pid,'shot/Q');before_line=self.studio.fingerprint(self.pid,'line/L')
  p=self.studio.entries(self.pid)['bible/rafi']['payload'];p['voice_speaker']='A different approved speaker';self.save('bible','rafi',p)
  self.assertEqual(before_shot,self.studio.fingerprint(self.pid,'shot/Q'));self.assertNotEqual(before_line,self.studio.fingerprint(self.pid,'line/L'))
 def test_appearance_change_does_not_regenerate_unrelated_voice(self):
  before=self.studio.fingerprint(self.pid,'line/L');p=self.studio.entries(self.pid)['bible/rafi']['payload'];p['continuity']='A revised jacket';self.save('bible','rafi',p)
  self.assertEqual(before,self.studio.fingerprint(self.pid,'line/L'))
 def test_external_disclosure_requires_recorded_destination_and_revision(self):
  endpoint='https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space'
  with self.assertRaises(QualityError):self.studio.require_disclosure(self.pid,endpoint)
  self.studio.allow_disclosure(self.pid,endpoint,'Owner-authorized actual test fixture disclosure for this revision.')
  self.studio.require_disclosure(self.pid,endpoint)
  p=self.studio.entries(self.pid)['scene/S']['payload'];p['action']='A new unpublished action';self.save('scene','S',p)
  with self.assertRaises(QualityError):self.studio.require_disclosure(self.pid,endpoint)
 def test_discovery_refresh_does_not_change_creative_source(self):
  before=self.studio.source_hash(self.pid);self.save('capability','video',{'quota':'unknown','cost_usd':0,'paid_api':False})
  self.assertEqual(before,self.studio.source_hash(self.pid))
 def test_new_selected_take_marks_final_export_stale(self):
  aid=self.voice();a=next(a for a in self.studio.assets(self.pid) if a['id']==aid)
  path=self.root/'fake_final.mp4';path.write_bytes(b'test-only export manifest fixture')
  from redpad_pipeline.drama_quality import file_hash
  export={'path':str(path),'sha':file_hash(path),'source_hash':self.studio.source_hash(self.pid),'manifest':json.dumps({'assets':{}})}
  self.assertTrue(self.studio.export_current(self.pid,export))
  for dim in ('pronunciation','performance','clarity'):self.studio.review(self.pid,aid,dim,'pass','contract test','agent','Fixture review only to exercise selected-take invalidation.')
  self.studio.select(self.pid,aid)
  self.assertFalse(self.studio.export_current(self.pid,export))
 def test_imported_take_is_frozen_before_source_path_is_reused(self):
  aid=self.voice();a=next(a for a in self.studio.assets(self.pid) if a['id']==aid)
  mutable=self.studio.root/self.pid/'voice.wav';mutable.write_bytes(b'producer replaced its temporary output')
  self.assertIn('/objects/',a['path']);self.assertTrue(next(a for a in self.studio.assets(self.pid) if a['id']==aid)['current'])
 def test_false_human_and_empty_evidence_are_not_invented(self):
  with self.assertRaises(QualityError):self.studio.review(self.pid,'project','drama','pass','','human','')
  with self.assertRaises(QualityError):self.studio.review(self.pid,'project','final_picture','pass','agent','agent','No export yet; cannot review final picture.')

if __name__=='__main__':unittest.main()
