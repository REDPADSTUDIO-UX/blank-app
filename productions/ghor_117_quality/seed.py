"""Authored original realism revision. No paid screenplay/model API is invoked.
This is a production checkpoint, not a claim that the episode was generated.
"""
from pathlib import Path
import json,sys,sqlite3,time,base64
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from redpad_pipeline.drama_quality import Studio,QualityError
from redpad_pipeline.drama_finish import compose_cue,sound_event
P=Path(__file__).parent;REPO=P.parents[1];DB=REPO/'redpad_studio.db';MEDIA=REPO/'redpad_media';studio=Studio(DB,MEDIA)
SCENES=[
 dict(id='S01',start=0,end=24,setting='বাবার কাজের ঘর · রাত · cold open',objective='রাফি অচেনা রেকর্ডিং বন্ধ করে নিজের গলা কোথা থেকে আসছে বুঝতে চায়।',obstacle='টেপ থেকে তার নিজের এমন কথা শোনা যায় যা সে এখনো বলেনি।',turn='রেকর্ডিংয়ে চাবি রাখার শব্দ; বাইরে হাজেরার হাতে সত্যিকারের চাবি।',consequence='ঘটনাটি কাকতালীয় কি না পরীক্ষা করার প্রয়োজন তৈরি হয়।',action='ক্লোজ শটে টেপ চলছে। রাফির হাত STOP-এর ওপর থামে। সে ঘাড় ঘোরায়; দরজার পাশে চাবি হাতে হাজেরা। প্রথম কথাটি টেপে, দ্বিতীয়বার মুখে। কোনো ভূতের মুখ দেখানো নয়।',durations=[3,4,5,3,4,5],lines=[(2,7,'rafi_echo','hazera','খালা, চাবিটা টেবিলে রাখেন।','anticipate an ordinary request','neutral'),(12,17,'hazera','rafi','কী হলো? আমাকে ওভাবে দেখছিস কেন?','understand his sudden stare','uneasy'),(18,23,'rafi','hazera','আমি কি... কথাটা একটু আগে বলেছি?','confirm whether his memory is wrong','restrained fear')]),
 dict(id='S02',start=24,end=76,setting='একই বাড়ি · কিছুক্ষণ আগে',objective='বাড়ি বিক্রির কাগজ নিয়ে রাতেই চলে যাওয়া।',obstacle='হাজেরা চাবি দিতে চান না; বিক্রির কথা শুনে ব্যক্তিগত আঘাত পান।',turn='রাফি স্বীকার করে বাড়িটি ধরে রাখার সামর্থ্য নেই।',consequence='চাবির লেনদেন পারিবারিক বিশ্বাসের সংঘাতে পরিণত হয়।',action='ভেজা জুতা বাইরে খুলে রাফি খাম বের করে। হাজেরা দুই কাপের বদলে একটি কাপ রাখেন। খালি কাপের জায়গায় রাফির চোখ যায়। দরজার নিচে তখন মেঝে শুকনো।',durations=[4,5,3,5,4,5,4,5,3,5,4,5],lines=[(1,6,'hazera','rafi','কাল সকালে আসলে হতো না?','keep him for a proper visit','hurt but welcoming'),(8,14,'rafi','hazera','কাল লোক আসবে, খালা। দলিলটা নিয়ে যাই।','avoid discussing the sale','businesslike'),(16,22,'hazera','rafi','লোক মানে? বাড়ি দেখার লোক?','make him say it aloud','controlled hurt'),(24,32,'rafi','hazera','খালি পড়ে আছে। দেখাশোনার টাকাটাও তো আমার নাই।','defend a practical decision','defensive'),(35,42,'hazera','rafi','আমাকে একবার বলতি। চাবি রাখি, এটুকু জানার অধিকারও নাই?','ask to be treated as family','wounded'),(44,51,'rafi','hazera','আপনাকে বললে... আপনি আটকাতেন।','admit that he avoided her','embarrassed')]),
 dict(id='S03',start=76,end=121,setting='কাজের টেবিল / তালাবদ্ধ দরজার সামনে',objective='বাবার রেখে যাওয়া কাগজ উদ্ধার করে আলোচনা শেষ করা।',obstacle='হাজেরা এমন এক শেষ ফোনের কথা বলেন যা রাফি ইচ্ছা করে ধরেনি।',turn='টেপের লেবেলে বাবার হাতে রাফির নাম দেখা যায়।',consequence='রাফি চলে যাওয়ার বদলে বাবার গলা শোনার সিদ্ধান্ত নেয়।',action='কাপ ছুঁয়েও রাফি চা খায় না। হাজেরা আলমারি থেকে টেপ দেন; কোনো অদ্ভুত ভবিষ্যদ্বাণী করেন না। চাবি আঁচলে বেঁধে রেখেছেন। রাফি পুরোনো কল-লিস্ট খুলে আবার বন্ধ করে।',durations=[5,4,3,5,4,5,4,5,5,5],lines=[(1,7,'hazera','rafi','শেষ রাতে তোকে ফোন দিতে বলেছিল।','deliver an unfinished obligation','quiet'),(9,14,'rafi','hazera','জানি। পরে ফোন করতাম।','end an uncomfortable subject','closed'),(17,25,'hazera','rafi','পরে তো আর কথা হয়নি। এইটা তোর জন্য রেখেছিল।','hand over the tape without accusing him','gentle'),(28,34,'rafi','hazera','কী আছে এতে?','hope for something he will not admit','guarded'),(36,43,'hazera','rafi','শুনিনি। নামটা দেখেই রেখে দিয়েছিলাম।','respect a private message','plain')]),
 dict(id='S04',start=121,end=172,setting='টেবিল / ফোনে মীনা অন্য বাসায়',objective='মীনার সাহায্যে টেপটি নিরাপদে বাজিয়ে বাবার বার্তা শোনা।',obstacle='পুরোনো যন্ত্র আটকে যায়; রাফি নিজের অপরাধবোধ নিয়ে কথা বলতে চায় না।',turn='টেপ চলার পর বাবার বদলে তাদের বর্তমান কথার অংশ শোনা যায়।',consequence='টেপটি স্মৃতিচিহ্ন থেকে পরীক্ষার বস্তু হয়ে ওঠে।',action='রাফি ঢিলে ফিতে দেখে পেন্সিলে রিল সামান্য ঘুরিয়ে নেয়। ফোন স্পিকারে নয়, কানের কাছে। মীনার সংলাপ off-camera; তাকে ওই বাড়িতে দেখানো যাবে না। রাফি প্লে চাপলে আগে ক্লিক, পরে ফিতের hiss।',durations=[4,5,4,3,5,4,5,4,5,4,4,4],lines=[(1,7,'mina','rafi','বাড়ি বিক্রি করছিস, আমাকে অন্যের কাছে শুনতে হবে?','ask why he shut her out','familiar annoyance'),(9,16,'rafi','mina','আজ এই কথা না। বাবার একটা টেপ পেয়েছি।','ask for help without asking for comfort','tired'),(18,24,'mina','rafi','আচ্ছা। ফোনটা রাখ। আগে যন্ত্রটা চালু কর।','put the argument aside','practical'),(27,34,'rafi','mina','এখনো যদি ওই জমির হিসাব শোনায়, আমি কিন্তু উঠব।','cover grief with a small joke','dry warmth'),(36,42,'mina','rafi','তাহলে উঠে যাস। আগে শুনে তো দেখ।','give him permission to listen','warm but direct'),(45,50,'rafi','mina','একটু দাঁড়া... এটা তোর গলা?','identify an unexpected sound','uncertain')]),
 dict(id='S05',start=172,end=226,setting='কাজের ঘর / দরজার পাশে হাজেরা',objective='রাফি শব্দটি ফোনের echo না পুরোনো টেপ তা আলাদা করতে চায়।',obstacle='হাজেরা ঘটনাটি বুঝছেন না; মীনা ফোনে সব শব্দ স্পষ্ট শুনতে পান না।',turn='হাজেরা টেবিলে চাবি রাখার আগেই টেপে একই ধাতব শব্দ বাজে। Cold open-এর মুহূর্ত ফিরে আসে।',consequence='রাফির বাস্তব ব্যাখ্যা দুর্বল হয়; সে বাইরে থেকে বন্ধ ঘরের তালা পরীক্ষা করে।',action='রাফি ফোন mute করে। মীনার মুখ নয়, রাফির শোনার প্রতিক্রিয়া। হাজেরা চাবি খুলছেন; রাফি টেপ বন্ধ করতে গিয়ে থামেন। বাস্তব চাবির আঘাতের সঙ্গে আগের রেকর্ডের আলাদা timing স্পষ্ট থাকবে।',durations=[5,3,4,5,4,5,4,3,5,4,5,3,4],lines=[(1,7,'rafi','mina','তুই দশ সেকেন্ড কিছু বলিস না। শুধু লাইনে থাক।','isolate the sound source','focused'),(10,17,'hazera','rafi','এত রাতে ভাঙা জিনিসটা নিয়ে বসতে হবে?','get him to stop and rest','irritated concern'),(20,25,'rafi_echo','hazera','খালা, চাবিটা টেবিলে রাখেন।','repeat the anticipatory line','neutral'),(28,34,'hazera','rafi','কী হলো? আমাকে ওভাবে দেখছিস কেন?','read his expression','uneasy'),(37,44,'rafi','hazera','ওটা এখনো হাতে রাখেন। নামাবেন না।','prevent the recorded sound from happening','urgent but quiet'),(47,53,'hazera','rafi','চাবি নিয়ে কী হয়েছে তোর?','ask for an explanation','afraid for him')]),
 dict(id='S06',start=226,end=265,setting='তালাবদ্ধ ঘরের বাইরের করিডর',objective='রাফি দরজা না খুলে অস্বাভাবিক শব্দের উৎস খুঁজতে চায়।',obstacle='বৃষ্টি থেমেছে, কিন্তু দরজার নিচ থেকে পানি এগিয়ে আসে।',turn='চাবি তালায় ঢোকে না; হাজেরা জানান বাবা তালা বদলেছিলেন।',consequence='রাফি বিক্রির কাগজ ছেড়ে প্রমাণ রেকর্ড করতে চায়।',action='রাফি মেঝেতে বসে টর্চ ফেলেন। দরজার নিচের পানি ছুঁয়ে আঙুল দেখেন। হাজেরা এক পা পিছিয়ে যান। বাইরে বৃষ্টির বদলে জানালার কার্নিশে শেষ কয়েক ফোঁটা; ভেতরে waterline sound নয় গড়িয়ে পড়ার আলাদা ক্ষুদ্র শব্দ।',durations=[4,5,3,5,4,5,4,5,4],lines=[(1,7,'rafi','hazera','এই চাবি তো ঢুকছে না। অন্য চাবিটা কোথায়?','find a physical explanation','tense'),(10,17,'hazera','rafi','শেষ দিকে তালা বদলেছিল। আমাকে দেয়নি।','admit she cannot help','shaken'),(20,26,'rafi','mina','মীনা, বৃষ্টি থেমেছে। কিন্তু ভেতর থেকে পানি আসছে।','describe only what he can observe','controlled panic'),(29,37,'mina','rafi','দরজায় হাত দিস না। আগে একটু সরে দাঁড়া। আমি আসছি।','keep him safe without explaining the mystery','firm concern')]),
 dict(id='S07',start=265,end=300,setting='কাজের ঘর থেকে বেরোনোর পথ / বন্ধ দরজা',objective='রাফি দরজা না খুলে হাজেরাকে নিয়ে বেরিয়ে যেতে চায়।',obstacle='টেপে তার নিজের ভবিষ্যৎ প্রতিক্রিয়া বাজে; বন্ধ ঘরের ভেতরে ফোন বেজে ওঠে।',turn='টেপের লাইন এখনো বলা হয়নি; রাফি সিদ্ধান্ত বদলে দরজার সামনে থেমে যায়।',consequence='পর্ব ২-এ ঘরের ভেতরের ফোন কার এবং রাফির হারানো স্মৃতির সঙ্গে এর সম্পর্ক কী—তার অনুসন্ধান শুরু হবে।',action='রাফি কাঁধে ব্যাগ তোলেন, হাজেরাকে আগে যেতে বলেন। ক্যাসেটের কণ্ঠ তাকে থামায়। তার নিজের ফোন silent; অন্য ringtone বন্ধ দরজার ভেতর। তালা অক্ষত। দরজার নিচে ফোনের ক্ষীণ আলো সরে যায়; কোনো মুখ বা cheap jump-scare নয়।',durations=[5,4,3,5,4,5,4,5],lines=[(1,7,'rafi','hazera','চলেন। সকালে লোক এনে দেখব। এখন থাক।','choose to leave rather than behave foolishly','resolute'),(11,18,'rafi_echo','mina','আমি খুলিনি, মীনা। শব্দটা ভেতর থেকে আসছে।','anticipate his next explanation','low'),(21,27,'mina','rafi','রাফি? ওটা কার ফোন বাজছে?','seek a response through the still-open call','alarmed'),(29,34,'rafi','mina','আমি তো... ফোনটা সাইলেন্ট করেছি।','realize the sound is not his device','almost a whisper')])]
# Totals are performance-designed, with varied 3–5s coverage and longer dialogue across cuts.
assert all(abs(sum(s['durations'])-(s['end']-s['start']))<.01 for s in SCENES),[(s['id'],sum(s['durations']),s['end']-s['start']) for s in SCENES]

def finish_checkpoint(pid):
 from shot_coverage import apply_coverage,bind_sound_events
 apply_coverage(studio,pid);bind_sound_events(studio,pid)
 if not any(a['kind']=='reference' and a['target']=='rafi' and a['current'] for a in studio.assets(pid)):
  old=next((a for a in studio.assets(pid) if a['kind']=='reference' and a['target']=='rafi'),None)
  if old:studio.register_asset(pid,'reference','rafi',old['path'],old['metadata'])
 e=studio.entries(pid);folder=studio.root/pid/'score_sketches';folder.mkdir(exist_ok=True)
 present={(a['kind'],a['target']) for a in studio.assets(pid) if a['current']}
 for key,r in e.items():
  component,target=key.split('/');p=r['payload']
  if component=='music' and p['treatment']=='composed' and ('music',target) not in present:
   f=folder/(target+'.wav');meta=compose_cue(f,p);studio.register_asset(pid,'music',target,f,meta)
  if component=='sfx' and p['sound']!='custom_original_phone' and (p['kind'],target) not in present:
   f=folder/(target+'.wav');meta=sound_event(f,p);studio.register_asset(pid,p['kind'],target,f,meta)
 script='# ঘর ১:১৭ — না-বলা কথা · বাস্তবধর্মী সংশোধন\n\nমৌলিক গল্প। কোনো গল্পকথক নেই। লক্ষ্য ৩০০ সেকেন্ড।\n\n'
 for scene in SCENES:
  p=e['scene/'+scene['id']]['payload'];script+=f"## {p['start']}–{p['end']} সেকেন্ড · {p['setting']}\n\n{p['action']}\n\n"
  for _,r in sorted(((k,v) for k,v in e.items() if k.startswith('line/')),key=lambda x:x[1]['payload']['start']):
   line=r['payload']
   if line['scene_id']==scene['id']:script+=f"{line['start']}–{line['end']} · {line['speaker']}: {line['text']}\n\n"
  script+=f"দৃশ্যের পরিবর্তন: {p['turn']}\nপরিণতি: {p['consequence']}\n\n"
 script=studio.sync_content_script(pid)
 (P/'screenplay_v3.md').write_text(script.rstrip()+'\n')
 with sqlite3.connect(DB) as db:db.execute('UPDATE content SET script=? WHERE id=?',(script,studio.project(pid)['content_id']))
 from shot_coverage import apply_coverage,bind_sound_events
 apply_coverage(studio,pid)
 bind_sound_events(studio,pid)
 (P/'authored_project.json').write_text(json.dumps(studio.snapshot(pid),ensure_ascii=False,indent=2))
 print('Recovered authored project checkpoint; no repeated generation request.',flush=True)

def seed():
 marker=P/'project_pointer.json'
 if marker.exists():
  pid=json.loads(marker.read_text())['project_id'];studio.project(pid);finish_checkpoint(pid);return pid
 now=datetime.now(timezone.utc).isoformat()
 with sqlite3.connect(DB) as db:
  channel=db.execute("SELECT id FROM channels WHERE name='নিশিকথা'").fetchone()
  if not channel:raise QualityError('Existing isolated channel profile is required; do not touch Render.')
  cid=db.execute("INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",(channel[0],'ঘর ১:১৭ — না-বলা কথা · realistic revision','Strict realistic drama; not the old cartoon export','','Draft',now,now)).lastrowid
 pid=studio.create('ঘর ১:১৭ — পর্ব ১ · বাস্তবধর্মী সংশোধন',300,cid);marker.write_text(json.dumps({'project_id':pid,'content_id':cid}))
 def put(c,i,p):return studio.save(pid,c,i,p,studio.entries(pid).get(c+'/'+i,{}).get('revision',0))
 research=[
 ('R01',dict(claim='Ordinary cassette playback depends on the tape and transport condition. Slack tape can be taken up by turning a reel with a pencil.',classification='verified_fact',application='Rafi checks and tightens slack before playback; the pencil action grounds his profession and gives motivated close coverage.',source_url='https://www.sony.com/electronics/support/audio-video-boomboxes/cfs-9000/articles/00028567',source_summary='Manufacturer troubleshooting describes tape-slack and tape-player head/drive checks. It does not explain or support supernatural playback.',retrieved_at=now)),
 ('R02',dict(claim='The house, rainfall on this fictional night, sale deadline and the characters’ family history are invented.',classification='fictional_choice',application='Set the story in a worn family house in Wari, Dhaka. Do not claim this is a documented haunting or an actual weather event.')),
 ('R03',dict(claim='Suspense should be built from a testable sound event, a character decision and its consequence, while grief shapes the reason to stay.',classification='fictional_choice',application='Repeat the key-drop event with clearly separated timing. Rafi tries muting the phone and later chooses to leave. No supernatural rule is presented as scientific fact.')),
 ('R04',dict(claim='Current emotional Bangla TTS candidate has production restrictions; another promising Bengali voice model has gated weight access.',classification='verified_fact',application='Reject ehzawad emotional TTS for this production without permission; test the existing public Indic Parler demo separately and do not bypass gated downloads.',source_url='https://huggingface.co/ehzawad/orpheus-bangla-emotional-tts',source_summary='The current model page identifies a research-only noncommercial licence and requires written permission for production use.',retrieved_at=now))]
 for i,r in research:put('research',i,r)
 season=json.loads((REPO/'productions/ghor_117/season.json').read_text())
 put('season','main',dict(premise='ফোন না ধরা নিয়ে অপরাধবোধে ভোগা এক সাউন্ড এডিটর বাবার বাড়ির টেপে না-বলা কথার শব্দ পায়।',arc='পারিবারিক অস্বীকার → শব্দের পরীক্ষা → নিখোঁজ মানুষের অনুসন্ধান → শৈশবের মুছে যাওয়া স্মৃতি → সত্য জানার নৈতিক মূল্য।',episodes=season,clue_rules=['টেপের পূর্বাভাস সীমিত ও পরীক্ষা-সাপেক্ষ; নিয়ম পরে অকারণে বদলাবে না।','হাজেরা কিছু জানেন কিন্তু সর্বজ্ঞ নন।','মীনা গবেষক বন্ধু; বন্ধ ঘরের কণ্ঠ বলে ধরে নেওয়া যাবে না।'],rights='Original REDPAD fiction; no adaptation of a Humayun Ahmed work.'))
 bibles={
 'rafi':dict(identity='রাফি, ৩২, ঢাকার সাউন্ড এডিটর। কাজ সামলায়; শোকের কথা এড়িয়ে চলে।',continuity='মাঝারি বাদামি ত্বক, ছোট এলোমেলো কালো চুল, হালকা দাড়ি; charcoal long-sleeve shirt, dark trousers. Keep reference 003 face and clothing.',motivation='বাড়ি বিক্রি করে দায়িত্বের চাপ কমাতে চায়; আসলে বাবার শেষ কথা না শোনার অপরাধবোধ এড়ায়।',voice_speaker='Arjun',voice_direction='Bangladeshi conversational register, low and dry, restrained; not announcer speech.',reference_required=True),
 'hazera':dict(identity='হাজেরা, ৬১, প্রতিবেশী; পরিবারের মতো দেখাশোনা করেছেন।',continuity='বয়সের রেখা, ধূসর চুল ঢাকা muted plum cotton sari; একই চাবির গোছা ও সাধারণ স্টিলের কাপ.',motivation='বাড়ি রক্ষা নয়, রাফির কাছে আপনজনের স্বীকৃতি চান।',voice_speaker='Aditi',voice_direction='Mature, warm, matter-of-fact; hurt stays below the words.',reference_required=True),
 'mina':dict(identity='মীনা, ৩০, অডিও গবেষক ও পুরোনো বন্ধু; অন্য বাসা থেকে ফোনে কথা বলে।',continuity='Episode 1 uses off-camera telephone dialogue; do not fabricate an appearance or put her inside Rafi’s house.',voice_speaker='Aditi',voice_direction='Clear conversational Bangla, practical and intimate, urgency without screaming.',reference_required=False),
 'rafi_echo':dict(identity='টেপে রাফিরই কণ্ঠ; পৃথক ভূত চরিত্র নয়।',continuity='Same selected Rafi voice identity with a cassette bandwidth treatment; no dramatic monster pitch.',voice_speaker='Arjun',voice_direction='Same delivery as Rafi, neutral enough that the repeated line can be recognised.',reference_required=False),
 'house':dict(identity='পুরান ঢাকার ওয়ারীর কাল্পনিক পুরোনো পারিবারিক বাড়ির কাজের ঘর ও ছোট করিডর।',continuity='Window left; wooden desk and cassette beside it; locked room reached through the right-hand doorway. Warm desk lamp, cool wet night. Floor dry until S06. No floating props, ghost faces or changing doors.',reference_required=True)}
 for i,b in bibles.items():put('bible',i,b)
 put('lexicon','clock',dict(written='১:১৭',spoken='একটা সতেরো',reason='Read a clock time in natural Bangladeshi Bangla, not isolated digits.'))
 for s in SCENES:
  p={k:v for k,v in s.items() if k not in ('id','lines','durations')};p['research_ids']=['R01'] if s['id']=='S04' else ['R02','R03'];p['season_id']='main';put('scene',s['id'],p)
 studio.record_stage(pid,'development','Original season and seven-scene objectives/conflicts developed; research and fictional decisions are separately labelled.','REDPAD agent — authored development')
 lines=[];shot_specs=[];li=0
 for s in SCENES:
  for begin,end,speaker,to,words,intention,emotion in s['lines']:
   li+=1;line_id=f'L{li:03}';p=dict(scene_id=s['id'],speaker=speaker,addressee=to,text=words,start=s['start']+begin,end=s['start']+end,intention=intention,emotion=emotion,pace='Conversational, allow the hesitation written in the line',pauses='Use punctuation and the action beat; do not fill all silence',emphasis='Emphasise the intention, not every word',breathing='Only motivated breath; no added gasp on each line',lexicon_ids=[]);put('line',line_id,p);lines.append((line_id,p))
 studio.record_stage(pid,'first_draft','Complete dialogue/action draft authored. No model API call or automatic research success is implied.','REDPAD agent — first draft')
 # A real structural revision: tie key-drop timing and the decision to leave to consequences.
 p=studio.entries(pid)['scene/S05']['payload'];p['continuity_note']='The anticipatory key sound precedes the real drop; Hazera must still be holding the keys during Rafi’s objection. Do not show her dropping them early.';put('scene','S05',p)
 p=studio.entries(pid)['scene/S07']['payload'];p['continuity_note']='Rafi actively chooses to leave; the second phone stops him. The locked door stays shut through Episode 1.';put('scene','S07',p)
 studio.record_stage(pid,'script_edit','Revised S05 physical key continuity and S07 decision/consequence. Removed explanatory supernatural dialogue and face-reveal jump scares.','REDPAD agent — script edit')
 # Dialogue polish is localized, not a claim of a voice performance already generated.
 for key,p in lines:
  if p['speaker']=='rafi':p['performance_note']='Avoid declamatory delivery. Short clauses, swallow uncertainty rather than adding a dramatic pause to every word.';put('line',key,p)
 studio.record_stage(pid,'dialogue_polish','Checked conversational register and subtext; separated spoken text from stage directions. Real pronunciation/acting auditions remain unverified.','REDPAD agent — dialogue polish')
 order=0
 for s in SCENES:
  clock=s['start']
  for i,seconds in enumerate(s['durations']):
   order+=1;sid=f'Q{order:03}';overlap=[key for key,p in lines if p['start']<clock+seconds and p['end']>clock]
   coverage=['reaction','over_shoulder','insert','on_camera','reaction'][i%5]
   reference_ids=['rafi','house']
   if s['id'] in ('S02','S03','S05') and i%5 in (1,3):reference_ids.append('hazera')
   action=s['action']+' Coverage beat '+str(i+1)+': '+['listen before responding','hand/prop action with clear contact','reaction held through the unheard line','a small head turn toward the other person','reframe only after the character decides'][i%5]+'.'
   shot=dict(order=order,scene_id=s['id'],start=clock,seconds=seconds,style='photorealistic',action=action,framing=['Close-up','Over-shoulder medium','Insert','Medium two-shot','Reaction close-up'][i%5],camera_reason='Restrained locked camera or a small motivated push to isolate the reaction; no decorative orbit.',reference_ids=reference_ids,line_ids=overlap,coverage=coverage,notes='Dialogue may continue across the cut. Never stretch or loop an undersized clip into this shot.');put('shot',sid,shot);shot_specs.append((sid,shot));clock+=seconds
 # Cue boundaries are dramatic decisions, not one automatic score for the whole episode.
 cues={
 'M01':dict(scene_ids=['S01'],start=7,end=20,purpose='Introduce the anticipatory sound after the hook, then leave the question exposed.',progression='Sparse two-note uncertainty; thin out before the spoken question.',treatment='composed',instrumentation='Soft felt-piano-like plucks and a brief bowed-string voicing',motif='D–A–E–F with rests; a question, not an impact on every cut.',harmony='D minor add9 to B-flat add9, unresolved.',tempo=54,level_db=-11),
 'M02':dict(scene_ids=['S02'],start=24,end=76,purpose='Let the strained family conversation and cup action carry the scene.',progression='No score; room and rain perspective only.',treatment='ambience_only'),
 'M03':dict(scene_ids=['S03'],start=90,end=118,purpose='Support the missed-call grief without announcing a ghost.',progression='A warm version of the motif grows once, then withdraws when the tape is handed over.',treatment='composed',instrumentation='Low felt piano voicings, restrained soft strings',motif='Opening D–A contour returns with longer rests.',harmony='D minor add9, B-flat, C suspended, A without resolution.',tempo=48,level_db=-13),
 'M04':dict(scene_ids=['S04','S05'],start=121,end=226,purpose='The mechanical and voice test must be audible and believable.',progression='No musical score under the sound experiment.',treatment='ambience_only'),
 'M05':dict(scene_ids=['S06','S07'],start=238,end=279,purpose='Turn family unease into uncertainty as the water appears.',progression='A restrained descending answer to the earlier motif; stop before the second phone.',treatment='composed',instrumentation='Separated low piano notes and soft unstable string intervals',motif='E–D–A–C sharp; do not copy a film theme.',harmony='D minor to A altered colour, with silence between phrases.',tempo=58,level_db=-12,notes=[64,62,57,61]),
 'M06':dict(scene_ids=['S07'],start=279,end=300,purpose='Let the unseen phone and final response become the ending.',progression='No score; retain quiet room tone and the phone perspective.',treatment='ambience_only')}
 for k,p in cues.items():put('music',k,p)
 def sound(key,global_start,duration,event,sound,kind='foley',distance='near',level=-9):
  q,shot=next((k,p) for k,p in shot_specs if p['start']<=global_start<p['start']+p['seconds']);spec=dict(shot_id=q,offset=global_start-shot['start'],global_start=global_start,duration=duration,event=event,sound=sound,kind=kind,distance=distance,room='Small furnished room, short reflections' if distance=='near' else 'Corridor beyond a closed wooden door',perspective='Match the camera/listener side of the door',level_db=level);put('sfx',key,spec)
 sound('A_room',0,300,'Quiet indoor room tone, no music claim','room_tone','ambience',level=-15)
 sound('A_rain',24,202,'Rain through the window; explicitly ends at S06, not a full-episode loop','rain','ambience','far',-9)
 sound('F_cup',39,.65,'Hazera puts one steel cup on the wooden table','cup')
 sound('F_play',166,.6,'Rafi depresses PLAY; click precedes tape hiss','tape_play')
 sound('A_tape',166,113,'Tape transport hiss from desk; ends when the final phone becomes the focus','tape_hiss','ambience',level=-12)
 sound('F_key_future',197,.8,'The recorded key impact precedes the real-world gesture','keys','designed',level=-10)
 sound('F_key_real',219,.8,'Actual key impact occurs only when Hazera eventually lowers her hand','keys',level=-7)
 sound('F_step',234,1.4,'Rafi steps into the corridor before crouching','footstep','foley','medium')
 sound('F_water',242,.35,'A drop joins water from under the locked door; no running-tap shortcut','drip','foley','near',-6)
 # Phone requires an imported/created reviewed original ringtone, not a generic impact.
 sound('D_phone',281,6,'Unseen second phone rings behind the locked door, Rafi phone remains silent','custom_original_phone','designed','far',-7)
 # No global quality pass is fabricated: project review stays pending until assessed.
 asset_path=studio.import_bytes(pid,'rafi.jpg',base64.b64decode((REPO/'assets/demos/ghor_refs/003.b64').read_text()))
 studio.register_asset(pid,'reference','rafi',asset_path,dict(engine='Existing REDPAD AI reference asset 003; original generator provenance not independently reverified',output_kind='photorealistic_reference',rights_url='https://github.com/REDPADSTUDIO-UX/blank-app',rights_note='User-authorized reuse of existing fictional project reference for an internal representative test. Public output rights still need provenance review.',rights_scope='internal_test',cost_usd=0,paid_api=False))
 # Store actual musical sketches, with reviews left pending rather than label them finished.
 folder=studio.root/pid/'score_sketches';folder.mkdir(exist_ok=True)
 for k,cue in cues.items():
  if cue['treatment']!='composed':continue
  path=folder/(k+'.wav');meta=compose_cue(path,cue);studio.register_asset(pid,'music',k,path,meta)
 for key,r in studio.entries(pid).items():
  if key.startswith('sfx/') and r['payload']['sound']!='custom_original_phone':
   target=key.split('/')[1];path=folder/(target+'.wav');meta=sound_event(path,r['payload']);studio.register_asset(pid,r['payload']['kind'],target,path,meta)
 # Save the current revised screenplay to the existing isolated content row.
 e=studio.entries(pid);script='# ঘর ১:১৭ — না-বলা কথা · বাস্তবধর্মী সংশোধন\n\nমৌলিক গল্প। কোনো গল্পকথক নেই। লক্ষ্য ৩০০ সেকেন্ড।\n\n'
 for s in SCENES:
  p=e['scene/'+s['id']]['payload'];script+=f"## {s['start']}–{s['end']} সেকেন্ড · {s['setting']}\n\n{p['action']}\n\n"
  for k,line in lines:
   if line['scene_id']==s['id']:script+=f"{line['start']}–{line['end']} · {line['speaker']}: {line['text']}\n\n"
  script+=f"দৃশ্যের পরিবর্তন: {p['turn']}\nপরিণতি: {p['consequence']}\n\n"
 script=studio.sync_content_script(pid)
 (P/'screenplay_v3.md').write_text(script.rstrip()+'\n')
 with sqlite3.connect(DB) as db:db.execute('UPDATE content SET script=? WHERE id=?',(script,cid))
 from shot_coverage import apply_coverage,bind_sound_events
 apply_coverage(studio,pid)
 bind_sound_events(studio,pid)
 (P/'authored_project.json').write_text(json.dumps(studio.snapshot(pid),ensure_ascii=False,indent=2))
 print('Authored',len(SCENES),'scenes',len(lines),'dialogue lines',len(shot_specs),'varied shots; no generated episode claimed.',flush=True)
 return pid
if __name__=='__main__':print(seed())
