"""Existing Studio's no-code realistic-drama workbench; never invents media or reviews."""
from pathlib import Path
import json,threading
import streamlit as st
from .drama_quality import Studio,QualityError,DIMENSIONS,STAGES
_threads={}
FIELDS={
'research':{'claim':'গবেষণার তথ্য / সৃজনশীল সিদ্ধান্ত','application':'স্ক্রিপ্টে কোথায় কাজে লাগবে','source_url':'মূল উৎসের HTTPS লিংক','source_summary':'উৎস যা সমর্থন করে','retrieved_at':'যাচাইয়ের তারিখ'},
'season':{'premise':'গল্পের ভিত্তি','arc':'মৌসুমের চরিত্র ও রহস্যের যাত্রা'},
'bible':{'identity':'চরিত্র / লোকেশনের পরিচয়','continuity':'চেহারা, পোশাক, অবস্থান ও স্থায়ী বৈশিষ্ট্য','motivation':'উদ্দেশ্য ও ব্যক্তিগত দ্বন্দ্ব','voice_speaker':'নির্দিষ্ট কণ্ঠের পরিচয়','voice_direction':'কণ্ঠ পরিচালনা'},
'scene':{'setting':'স্থান ও সময়','objective':'চরিত্র কী চায়','obstacle':'বাধা / সংঘাত','turn':'দৃশ্যের শেষে কী বদলায়','consequence':'পরের দৃশ্যে এর ফল','action':'দৃশ্যমান অভিনয় ও ঘটনা','start':'শুরুর সেকেন্ড','end':'শেষের সেকেন্ড'},
'line':{'speaker':'বক্তা ID','addressee':'কাকে বলছে','scene_id':'দৃশ্য ID','text':'শুধু কথ্য বাংলা সংলাপ','intention':'কেন বলছে','emotion':'আবেগ ও তার সংযম','pace':'গতি','pauses':'বিরতি','emphasis':'গুরুত্বের শব্দ / অভিপ্রায়','breathing':'শ্বাসের নির্দেশ','start':'শুরুর সেকেন্ড','end':'শেষের সেকেন্ড'},
'lexicon':{'written':'লিখিত শব্দ','spoken':'উচ্চারণের জন্য বিকল্প লেখা','reason':'কেন সংশোধন প্রয়োজন'},
'shot':{'scene_id':'দৃশ্য ID','order':'শটের ক্রম','seconds':'দৈর্ঘ্য','action':'অভিনয় ও অর্থপূর্ণ নড়াচড়া','framing':'ফ্রেমিং','camera_reason':'ক্যামেরা কেন নড়বে / স্থির থাকবে'},
'music':{'start':'সংগীত শুরুর সেকেন্ড','end':'সংগীত শেষের সেকেন্ড','purpose':'এই দৃশ্যে সংগীতের কাজ','progression':'আবেগ কীভাবে বদলাবে','instrumentation':'বাদ্যযন্ত্র / সাউন্ড','motif':'মূল সুরের ধারণা','harmony':'হারমনি ও তার পরিবর্তন'},
'sfx':{'event_id':'শটের নির্দিষ্ট action event ID','shot_id':'শট ID','offset':'শটের মধ্যে শব্দের মুহূর্ত','global_start':'এপিসোডে শব্দের সেকেন্ড','duration':'শব্দের দৈর্ঘ্য','event':'কোন বাস্তব ঘটনায় শব্দ হচ্ছে','sound':'উৎস শব্দের ধরন','distance':'কত দূরে','room':'ঘর / reverberation','perspective':'কার অবস্থান থেকে শুনছি'}}
NUMBERS={'start','end','seconds','offset','global_start','duration','order'}

def _worker(studio,pid,operation,*args):
 from .drama_free import probe,visual_sample,voice_sample,produce_missing
 from .drama_finish import render
 try:
  {'probe':probe,'visual':visual_sample,'voice':voice_sample,'render':render,'produce':produce_missing}[operation](studio,pid,*args)
 except Exception as exc:
  # Only locally generated safe errors are stored; no raw provider/credential error.
  folder=studio.root/pid;folder.mkdir(exist_ok=True)
  message=str(exc) if isinstance(exc,QualityError) else 'Operation failed; inspect its checkpoint. No paid fallback was used.'
  (folder/'last_ui_status.json').write_text(json.dumps({'operation':operation,'status':'blocked','detail':message}))

def _launch(studio,pid,operation,*args):
 key=(str(studio.db.resolve()),pid)
 if key in _threads and _threads[key].is_alive():raise QualityError('This project already has an operation running.')
 worker=threading.Thread(target=_worker,args=(studio,pid,operation,*args),daemon=True);_threads[key]=worker;worker.start()

def edit(studio,pid,component):
 e=studio.entries(pid);items=[k.split('/')[1] for k in e if k.startswith(component+'/')]
 choice=st.selectbox('বিদ্যমান '+component,items+['নতুন আইটেম'],key='dq_choose_'+component)
 item=st.text_input('আইটেম ID',value='' if choice=='নতুন আইটেম' else choice,key='dq_id_'+component+'_'+choice)
 previous=e.get(component+'/'+item,{});payload=previous.get('payload',{}).copy();rev=previous.get('revision',0)
 with st.form('dq_edit_'+component+'_'+choice):
  for field,label in FIELDS[component].items():
   value=payload.get(field,0 if field in NUMBERS else '')
   if field in NUMBERS:
    value=st.number_input(label,value=float(value),step=1.0 if field=='order' else .25,key='dq_field_'+component+'_'+choice+'_'+field);payload[field]=int(value) if field=='order' else value
   else:payload[field]=st.text_area(label,value=str(value),height=80,key='dq_field_'+component+'_'+choice+'_'+field)
  if component=='research':payload['classification']=st.selectbox('তথ্য / কল্পনা / craft reference',['verified_fact','fictional_choice','craft_reference'],index=['verified_fact','fictional_choice','craft_reference'].index(payload.get('classification','fictional_choice')))
  for field,source in ({'research_ids':'research'} if component=='scene' else {'lexicon_ids':'lexicon'} if component=='line' else {'reference_ids':'bible','line_ids':'line'} if component=='shot' else {'scene_ids':'scene'} if component=='music' else {}).items():
   options=[k.split('/')[1] for k in e if k.startswith(source+'/')];payload[field]=st.multiselect(field,options,default=[x for x in payload.get(field,[]) if x in options])
  if component=='shot':
   payload['events']=st.data_editor(payload.get('events',[]),num_rows='dynamic',key='dq_shot_events_'+choice)
   payload['style']='photorealistic';coverage=['on_camera','off_camera','reaction','over_shoulder','insert','establishing'];payload['coverage']=st.selectbox('সংলাপের coverage',coverage,index=coverage.index(payload.get('coverage','reaction')));st.caption('এই workflow-তে cartoon, still animatic বা mock fallback নেই।')
  if component=='bible':payload['reference_required']=st.checkbox('ভিজ্যুয়াল রেফারেন্স লাগবে',value=payload.get('reference_required',True))
  if component=='music':
   options=['composed','ambience_only','silence'];payload['treatment']=st.selectbox('সংগীত / ambience / silence',options,index=options.index(payload.get('treatment','ambience_only')))
  if component=='sfx':
   options=['foley','ambience','designed'];payload['kind']=st.selectbox('আলাদা শব্দের layer',options,index=options.index(payload.get('kind','foley')))
  if component=='season':
   st.caption('Episode table: premise, clue, reveal and consequence remain editable project data.')
   rows=payload.get('episodes',[])
   if isinstance(rows,list) and all(isinstance(x,dict) for x in rows):payload['episodes']=st.data_editor(rows,num_rows='dynamic',key='dq_episode_table_'+choice)
  save=st.form_submit_button('নতুন revision সংরক্ষণ')
 if save:
  try:studio.save(pid,component,item,payload,rev);studio.sync_content_script(pid) if component in {'research','season','bible','scene','line','lexicon'} else None;st.success('Revision saved. Affected assets and approvals are checked against the new source.');st.rerun()
  except (QualityError,ValueError) as ex:st.error(str(ex))
 if previous:
  with st.expander('Revision history'):st.json(studio.history(pid,component,item),expanded=False)

def assets(studio,pid):
 available=studio.assets(pid)
 if not available:st.info('কোনো বাস্তব media asset এখনো যোগ হয়নি।');return
 aid=st.selectbox('শুনুন / দেখুন / take নির্বাচন করুন',[a['id'] for a in available],format_func=lambda i:next(f"{a['kind']} / {a['target']} · {'current' if a['current'] else 'STALE'} · {a['id'][:8]}" for a in available if a['id']==i),key='dq_asset')
 a=next(a for a in available if a['id']==aid)
 if a['kind']=='reference':st.image(a['path'],width=400)
 elif a['kind']=='shot':st.video(a['path'])
 else:st.audio(a['path'])
 st.caption('Selected' if a['selected'] else 'Not selected');st.json(a['metadata'],expanded=False)
 with st.form('dq_review_'+aid):
  dimension=st.selectbox('সম্পাদকীয় পরীক্ষা',sorted(DIMENSIONS[a['kind']]))
  verdict=st.selectbox('ফল',['needs_review','fail','pass']);reviewer=st.text_input('কে মূল্যায়ন করেছেন');rtype=st.selectbox('Reviewer type',['agent','human']);evidence=st.text_area('যা সত্যিই দেখা / শোনা হয়েছে; নির্দিষ্ট সমস্যা বা প্রমাণ লিখুন')
  submit=st.form_submit_button('এই take-এর মূল্যায়ন সংরক্ষণ')
 if submit:
  try:studio.review(pid,aid,dimension,verdict,reviewer,rtype,evidence);st.success('Evidence saved; no human review was invented.')
  except QualityError as ex:st.error(str(ex))
 if st.button('সব মূল্যায়ন পাস হলে এই take ব্যবহার করুন'):
  try:studio.select(pid,aid);st.success('Selected current take.');st.rerun()
  except QualityError as ex:st.error(str(ex))

def show(db_path,media_dir):
 studio=Studio(db_path,media_dir);st.subheader('🎬 Realistic Drama — Quality Workbench')
 st.caption('Research → screenplay revisions → continuity → performed dialogue → realistic footage → scene-specific sound → technical + editorial review. Zero paid APIs.')
 projects=studio.projects()
 if not projects:
  st.info('কোনো strict realistic-drama project নেই। পুরোনো cartoon/demo এই workflow-এর completed output নয়।')
 with st.expander('নতুন drama project'):
  with st.form('dq_new'):
   with studio.tx() as db:channels=db.execute('SELECT id,name FROM channels ORDER BY id').fetchall()
   channel=st.selectbox('Existing Studio channel',[r[0] for r in channels],format_func=lambda cid:next(r[1] for r in channels if r[0]==cid))
   title=st.text_input('প্রজেক্টের নাম');seconds=st.number_input('এপিসোডের লক্ষ্য সেকেন্ড',value=300,min_value=15,max_value=3600);create=st.form_submit_button('প্রজেক্ট তৈরি',disabled=not channels)
  if create:
   try:studio.create(title,seconds,channel_id=channel);st.rerun()
   except QualityError as ex:st.error(str(ex))
 if not projects:return
 pid=st.selectbox('Drama project',[p['id'] for p in projects],format_func=lambda i:next(p['title'] for p in projects if p['id']==i),key='dq_project')
 gates=studio.gates(pid)
 cols=st.columns(4)
 for col,key,label in zip(cols,['development','editorial','capability','representative_scene'],['Script / research','Editorial review','Free resources','Realism + dialogue test']):col.metric(label,'PASS' if gates[key]['passed'] else 'BLOCKED / REVIEW')
 with st.expander('যে বাধাগুলো ঠিক করতে হবে',expanded=True):
  for issue in gates['full_render']['issues']:st.write('• '+issue)
 tab1,tab2,tab3,tab4,tab5=st.tabs(['Research / season','Script / continuity','Voice / footage','Music / SFX','QA / checkpoints'])
 with tab1:
  which=st.radio('Development',['research','season'],horizontal=True,key='dq_development');edit(studio,pid,which)
 with tab2:
  which=st.radio('Script department',['scene','line','bible','lexicon','shot'],horizontal=True,key='dq_script');edit(studio,pid,which)
  with st.expander('স্ক্রিপ্ট revision stage সংরক্ষণ'):
   with st.form('dq_stage'):
    stage=st.selectbox('Stage',STAGES);note=st.text_area('আসল পরিবর্তন / মূল্যায়নের প্রমাণ');reviewer=st.text_input('সম্পাদক / agent পরিচয়');save=st.form_submit_button('Stage record')
   if save:
    try:studio.record_stage(pid,stage,note,reviewer);st.rerun()
    except QualityError as ex:st.error(str(ex))
 with tab3:
  st.info('শুধু existing free endpoint-এর bounded test। HTTP 200 মানেই generation বা পর্যাপ্ত quota নয়। ব্যর্থ job স্বয়ংক্রিয়ভাবে আবার জমা হবে না।')
  if st.button('বিনামূল্যের access ও resource যাচাই'):
   try:_launch(studio,pid,'probe');st.success('Read-only resource check started. Refresh below.')
   except QualityError as ex:st.error(str(ex))
  e=studio.entries(pid);shots=[k.split('/')[1] for k in e if k.startswith('shot/')];lines=[k.split('/')[1] for k in e if k.startswith('line/')];refs=[a for a in studio.assets(pid) if a['kind']=='reference' and a['current']]
  consent=st.checkbox('এই revision-এর reference ও action prompt → zerogpu-aoti Wan2.2; সংলাপ ও অভিনয় নির্দেশ → ai4bharat Indic Parler public HF Space-এ পাঠানোর অনুমতি',key='dq_free_consent')
  if shots and refs:
   shot=st.selectbox('Representative shot',shots);ref=st.selectbox('এই শটের actual reference',[a['id'] for a in refs],format_func=lambda aid:next(a['target'] for a in refs if a['id']==aid))
   if st.button('একটি realistic shot test',disabled=not consent):
    try:studio.allow_disclosure(pid,'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space','Owner used the explicit project reference/action disclosure checkbox for this revision.');_launch(studio,pid,'visual',shot,ref);st.success('Single sample job started; no paid fallback.')
    except QualityError as ex:st.error(str(ex))
  if lines:
   line=st.selectbox('অভিনয় ও উচ্চারণের audition line',lines,format_func=lambda i:e['line/'+i]['payload']['text'])
   st.caption('উচ্চারণ-সংশোধিত text: '+studio.spoken_line(pid,line))
   if st.button('একটি expressive dialogue audition',disabled=not consent):
    try:studio.allow_disclosure(pid,'https://ai4bharat-indic-parler-tts.hf.space','Owner used the explicit project dialogue disclosure checkbox for this revision.');_launch(studio,pid,'voice',line);st.success('Single audition started; review the actual audio before selection.')
    except QualityError as ex:st.error(str(ex))
  if st.button('Preflight পাস হলে missing footage / dialogue তৈরি',disabled=not consent or not gates['production_start']['passed']):
   try:
    for destination in ['https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space','https://ai4bharat-indic-parler-tts.hf.space']:studio.allow_disclosure(pid,destination,'Owner requested this production batch with the explicit revision-scoped disclosure checkbox.')
    _launch(studio,pid,'produce');st.success('Bounded zero-cost batch started; editorial review remains required.')
   except QualityError as ex:st.error(str(ex))
  with st.expander('নিজস্ব / অনুমতিপ্রাপ্ত বাস্তব media import'):
   with st.form('dq_upload'):
    kind=st.selectbox('Asset kind',['reference','shot','voice','music','foley','ambience','designed']);target=st.text_input('Source item ID');upload=st.file_uploader('PNG / JPEG / MP4 / WAV / MP3 / FLAC',type=['png','jpg','jpeg','mp4','wav','mp3','flac']);engine=st.text_input('প্রকৃত model / recording source');rights_url=st.text_input('ব্যবহারের অনুমতির উৎস');rights_note=st.text_area('অনুমতি / মালিকানার বিবরণ');public=st.checkbox('Public production-use rights যাচাই হয়েছে');add=st.form_submit_button('বাস্তব asset যুক্ত করুন')
   if add:
    try:
     if upload is None:raise QualityError('Choose a real file.')
     path=studio.import_bytes(pid,upload.name,upload.getvalue());studio.register_asset(pid,kind,target,path,dict(engine=engine,rights_url=rights_url,rights_note=rights_note,rights_scope='publication' if public else 'internal_test',cost_usd=0,paid_api=False,output_kind={'reference':'photorealistic_reference','shot':'photorealistic_neural_video','voice':'neural_dialogue','music':'composed_music'}.get(kind,kind)));st.success('Imported, not automatically reviewed or selected.');st.rerun()
    except QualityError as ex:st.error(str(ex))
  assets(studio,pid)
 with tab4:
  which=st.radio('Sound department',['music','sfx'],horizontal=True,key='dq_sound');edit(studio,pid,which)
  sound_entries=studio.entries(pid);targets=[k.split('/')[1] for k in sound_entries if k.startswith(which+'/') and (which!='music' or sound_entries[k]['payload'].get('treatment')=='composed')]
  if targets:
   target=st.selectbox('Local sound sketch source',targets,key='dq_local_sound')
   if st.button('এই cue-এর original local audio sketch তৈরি'):
    try:
     from .drama_finish import local_cue
     aid=local_cue(studio,pid,which,target);st.success('Original audio component created or recovered from cache. Editorial review is still required.')
    except (QualityError,KeyError) as ex:st.error(str(ex))
   matched=next((a for a in studio.assets(pid) if a['target']==target and a['current']),None)
   if matched:st.audio(matched['path'])
  st.caption('Music, ambience, Foley and designed effects are separate timed layers. Original composer sketches still need musicality/story-fit review.')
 with tab5:
  st.json(gates,expanded=False);st.dataframe(studio.jobs(pid),hide_index=True)
  status=studio.root/pid/'last_ui_status.json'
  if status.exists():st.json(json.loads(status.read_text()))
  st.button('Refresh production status')
  with st.form('dq_project_review'):
   dimension=st.selectbox('Project / final editorial check',['drama','dialogue','continuity','sound_plan','final_picture','final_sound']);decision=st.selectbox('Actual assessment',['needs_review','fail','pass']);who=st.text_input('Reviewer identity');rtype=st.selectbox('Actual reviewer type',['agent','human']);note=st.text_area('Concrete observations');save=st.form_submit_button('সংরক্ষণ করুন')
  if save:
   try:studio.review(pid,'final' if dimension.startswith('final_') else 'project',dimension,decision,who,rtype,note);st.rerun()
   except QualityError as ex:st.error(str(ex))
  if st.button('সব gate পাস হলে final MP4 render',disabled=not gates['full_render']['passed']):
   try:_launch(studio,pid,'render');st.success('Finishing started from selected real media only.')
   except QualityError as ex:st.error(str(ex))
  with studio.tx() as db:export=db.execute('SELECT * FROM dq_exports WHERE project=?',(pid,)).fetchone()
  if export:
   if studio.export_current(pid,export):
    st.video(export['path']);st.json(json.loads(export['qa']),expanded=False)
    with Path(export['path']).open('rb') as f:st.download_button('Download actual realistic-drama render',f,file_name='episode.mp4',mime='video/mp4')
    if st.button('Final review পাস হলে existing Approval Dashboard-এ যুক্ত করুন'):
     try:studio.attach_export(pid);st.success('Attached for owner approval; not published.')
     except QualityError as ex:st.error(str(ex))
   else:st.warning('Previous render is stale; source changed.')
  else:st.warning('কোনো নতুন realistic episode render হয়নি। পুরোনো cartoon ভিডিও এখানে final হিসেবে দেখানো হবে না।')
  st.download_button('Download production checkpoint JSON',json.dumps(studio.snapshot(pid),ensure_ascii=False,indent=2),file_name='realistic_drama_checkpoint.json',mime='application/json')
