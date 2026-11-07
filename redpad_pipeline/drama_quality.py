"""Strict realistic-drama workflow: versioned inputs, selective invalidation and gates.
No generation/provider/billing call occurs in this module. Reviews are explicit evidence,
not an invented quality score. Legacy productions are not reclassified as realistic.
"""
from __future__ import annotations
import hashlib,json,math,re,shutil,sqlite3,subprocess,time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

class QualityError(ValueError):pass
COMPONENTS={'research','season','bible','scene','line','lexicon','shot','music','sfx','capability'}
KINDS={'reference','shot','voice','music','foley','ambience','designed'}
DIMENSIONS={'reference':{'identity','rights'},'shot':{'realism','continuity','movement'},'voice':{'pronunciation','performance','clarity'},'music':{'musicality','story_fit','mix'},'foley':{'timing','perspective','story_fit'},'ambience':{'continuity','perspective','mix'},'designed':{'timing','story_fit','mix'}}
STAGES=('development','first_draft','script_edit','dialogue_polish')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def text_hash(value):return hashlib.sha256(value.encode()).hexdigest()
def file_hash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def ident(v):
 if not isinstance(v,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',v):raise QualityError('Use a short alphanumeric identifier.')
 return v
def text(v):return isinstance(v,str) and bool(v.strip())
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def url(v):return isinstance(v,str) and bool(re.fullmatch(r'https://[^\s]+',v))
def media_info(path):
 try:
  p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,timeout=25,check=True)
  info=json.loads(p.stdout);seconds=float(info['format']['duration'])
  if not math.isfinite(seconds) or seconds<=0:raise ValueError()
  return {'seconds':seconds,'streams':[{k:s[k] for k in ('codec_type','codec_name','width','height','sample_rate','channels') if k in s} for s in info['streams']]}
 except (OSError,ValueError,KeyError,subprocess.SubprocessError):raise QualityError('Media probe failed; no output was registered.') from None

class Studio:
 def __init__(self,db_path,media_root):
  self.db=Path(db_path);self.root=Path(media_root).resolve()/'quality_drama';self.root.mkdir(parents=True,exist_ok=True)
  self.db.parent.mkdir(parents=True,exist_ok=True)
  with self.tx() as db:
   db.executescript('''CREATE TABLE IF NOT EXISTS dq_projects(id TEXT PRIMARY KEY,title TEXT NOT NULL,content_id INTEGER UNIQUE,target_seconds REAL NOT NULL,created REAL NOT NULL);
   CREATE TABLE IF NOT EXISTS dq_revisions(project TEXT,component TEXT,item TEXT,revision INTEGER,payload TEXT,sha TEXT,created REAL,PRIMARY KEY(project,component,item,revision));
   CREATE TABLE IF NOT EXISTS dq_heads(project TEXT,component TEXT,item TEXT,revision INTEGER,PRIMARY KEY(project,component,item));
   CREATE TABLE IF NOT EXISTS dq_assets(id TEXT PRIMARY KEY,project TEXT,kind TEXT,target TEXT,path TEXT,sha TEXT,inputs TEXT,metadata TEXT,selected INTEGER DEFAULT 0,created REAL);
   CREATE TABLE IF NOT EXISTS dq_reviews(id INTEGER PRIMARY KEY,project TEXT,subject TEXT,subject_hash TEXT,dimension TEXT,decision TEXT,reviewer TEXT,reviewer_type TEXT,evidence TEXT,created REAL);
   CREATE TABLE IF NOT EXISTS dq_stages(project TEXT,stage TEXT,source_hash TEXT,evidence TEXT,reviewer TEXT,created REAL,PRIMARY KEY(project,stage,source_hash));
   CREATE TABLE IF NOT EXISTS dq_jobs(id TEXT PRIMARY KEY,project TEXT,kind TEXT,target TEXT,input_hash TEXT,state TEXT,detail TEXT,created REAL,updated REAL);
   CREATE TABLE IF NOT EXISTS dq_disclosures(project TEXT,destination TEXT,source_hash TEXT,note TEXT,created REAL,PRIMARY KEY(project,destination,source_hash));
   CREATE TABLE IF NOT EXISTS dq_script_links(project TEXT PRIMARY KEY,source_hash TEXT,script_sha TEXT);
   CREATE TABLE IF NOT EXISTS dq_exports(project TEXT PRIMARY KEY,path TEXT,sha TEXT,source_hash TEXT,manifest TEXT,qa TEXT,created REAL);''')
 @contextmanager
 def tx(self):
  with sqlite3.connect(self.db,timeout=15) as db:
   db.row_factory=sqlite3.Row
   yield db
 def projects(self):
  with self.tx() as db:return [dict(x) for x in db.execute('SELECT * FROM dq_projects ORDER BY created DESC')]
 def create(self,title,target_seconds=300,content_id=None,*,channel_id=None):
  if not text(title) or not finite(target_seconds) or not 15<=target_seconds<=3600:raise QualityError('Provide a title and duration of 15–3600 seconds.')
  pid=uuid4().hex
  with self.tx() as db:
   if content_id is None and channel_id is not None:
    if not db.execute('SELECT id FROM channels WHERE id=?',(channel_id,)).fetchone():raise QualityError('Choose an existing Studio channel.')
    now=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
    content_id=db.execute("INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",(channel_id,title,'Strict realistic drama','','Draft',now,now)).lastrowid
   db.execute('INSERT INTO dq_projects VALUES (?,?,?,?,?)',(pid,title,content_id,target_seconds,time.time()))
  return pid
 def project(self,pid):
  with self.tx() as db:r=db.execute('SELECT * FROM dq_projects WHERE id=?',(pid,)).fetchone()
  if not r:raise QualityError('Unknown drama project.')
  return dict(r)
 def entries(self,pid):
  self.project(pid)
  with self.tx() as db:
   rows=db.execute('SELECT r.* FROM dq_revisions r JOIN dq_heads h ON r.project=h.project AND r.component=h.component AND r.item=h.item AND r.revision=h.revision WHERE r.project=? ORDER BY r.component,r.item',(pid,)).fetchall()
  return {r['component']+'/'+r['item']:{'revision':r['revision'],'sha':r['sha'],'payload':json.loads(r['payload'])} for r in rows}
 def history(self,pid,component,item):
  with self.tx() as db:return [dict(r) for r in db.execute('SELECT revision,payload,sha,created FROM dq_revisions WHERE project=? AND component=? AND item=? ORDER BY revision DESC',(pid,component,item))]
 def save(self,pid,component,item,payload,expected_revision=0):
  self.project(pid);ident(item)
  if component not in COMPONENTS or not isinstance(payload,dict):raise QualityError('Unknown component or invalid JSON object.')
  encoded=canonical(payload)
  if len(encoded)>150_000:raise QualityError('Split oversized project notes.')
  # Do not allow embedded credentials in versioned project data.
  if any(re.search(r'(api[_-]?key|access[_-]?token|client[_-]?secret|password)',k,re.I) for k in payload):raise QualityError('Credentials belong in secret storage, not project records.')
  with self.tx() as db:
   db.execute('BEGIN IMMEDIATE')
   row=db.execute('SELECT revision FROM dq_heads WHERE project=? AND component=? AND item=?',(pid,component,item)).fetchone();actual=row[0] if row else 0
   if actual!=expected_revision:raise QualityError('This item changed elsewhere; refresh before saving.')
   db.execute('INSERT INTO dq_revisions VALUES (?,?,?,?,?,?,?)',(pid,component,item,actual+1,encoded,digest(payload),time.time()))
   db.execute('INSERT OR REPLACE INTO dq_heads VALUES (?,?,?,?)',(pid,component,item,actual+1))
   # Final review/render can never remain current after any source revision.
   # Existing assets stay on disk and are invalidated by their own dependency hashes.
   return actual+1
 def dependencies(self,key,p):
  component=key.split('/')[0];deps=set(p.get('depends_on',[]))
  if component=='scene':deps.update('research/'+x for x in p.get('research_ids',[]));deps.add('season/'+p.get('season_id','main'))
  if component=='line':
   deps.update(['scene/'+str(p.get('scene_id','')), 'bible/'+str(p.get('speaker',''))]);deps.update('lexicon/'+x for x in p.get('lexicon_ids',[]))
  if component=='shot':
   deps.add('scene/'+str(p.get('scene_id','')));deps.update('bible/'+x for x in p.get('reference_ids',[]));deps.update('line/'+x for x in p.get('line_ids',[]))
  if component=='music':deps.update('scene/'+x for x in p.get('scene_ids',[]))
  if component=='sfx':deps.add('shot/'+str(p.get('shot_id','')))
  if any(not isinstance(x,str) or not re.fullmatch(r'[a-z]+/[a-zA-Z0-9_-]{1,80}',x) for x in deps):raise QualityError('A dependency identifier is invalid.')
  return sorted(deps)
 def fingerprint(self,pid,key,entries=None,trail=()):
  entries=entries if entries is not None else self.entries(pid)
  if key in trail:raise QualityError('Circular project dependencies.')
  if key not in entries:raise QualityError('Missing dependency: '+key)
  p=entries[key]['payload'];deps=self.dependencies(key,p)
  component=key.split('/')[0]
  own=entries[key]['sha']
  if component=='bible':own=digest({k:v for k,v in p.items() if k not in {'voice_speaker','voice_direction','motivation'}})
  dependency_hashes={}
  for dep in deps:
   dep_p=entries.get(dep,{}).get('payload',{})
   if component=='line' and dep.startswith('bible/'):
    if dep not in entries:raise QualityError('Missing dependency: '+dep)
    dependency_hashes[dep]=digest({k:dep_p.get(k) for k in ('identity','motivation','voice_speaker','voice_direction')})
   elif component=='shot' and dep.startswith('line/'):
    if dep not in entries:raise QualityError('Missing dependency: '+dep)
    dependency_hashes[dep]=digest({k:dep_p.get(k) for k in ('text','start','end','scene_id','speaker','addressee','intention','emotion')})
   else:dependency_hashes[dep]=self.fingerprint(pid,dep,entries,trail+(key,))
  # The actual selected face/location reference bytes, not just prose, bind footage.
  references={}
  if component=='shot':
   with self.tx() as db:
    for ref in p.get('reference_ids',[]):
     row=db.execute("SELECT sha FROM dq_assets WHERE project=? AND kind='reference' AND target=? AND selected=1 ORDER BY created DESC LIMIT 1",(pid,ref)).fetchone()
     if row:references[ref]=row[0]
  return digest({'source':own,'dependencies':dependency_hashes,'reference_bytes':references})
 def script_hash(self,pid):
  e=self.entries(pid);return digest({k:v['sha'] for k,v in e.items() if k.split('/')[0] in {'research','season','bible','scene','line','lexicon'}})
 def allow_disclosure(self,pid,destination,note):
  allowed={'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space','https://ai4bharat-indic-parler-tts.hf.space'}
  if destination not in allowed or len(note.strip())<20:raise QualityError('Specify the existing free destination and actual owner authorization.')
  with self.tx() as db:db.execute('INSERT OR REPLACE INTO dq_disclosures VALUES (?,?,?,?,?)',(pid,destination,self.source_hash(pid),note,time.time()))
 def require_disclosure(self,pid,destination):
  with self.tx() as db:row=db.execute('SELECT 1 FROM dq_disclosures WHERE project=? AND destination=? AND source_hash=?',(pid,destination,self.source_hash(pid))).fetchone()
  if not row:raise QualityError('Owner authorization to send this revision’s reference/dialogue to the named public service is not recorded. No private project media was sent.')
 def source_hash(self,pid):return digest({k:v['sha'] for k,v in self.entries(pid).items() if not k.startswith('capability/')})
 def record_stage(self,pid,stage,evidence,reviewer):
  if stage not in STAGES or not text(evidence) or not text(reviewer):raise QualityError('Record an actual revision stage and its evidence.')
  # Development must precede drafts; same snapshot can be inspected at later stages,
  # but the history records who assessed it and never claims a model ran.
  with self.tx() as db:
   if stage!=STAGES[0] and not db.execute('SELECT 1 FROM dq_stages WHERE project=? AND stage=?',(pid,STAGES[STAGES.index(stage)-1])).fetchone():raise QualityError('Complete the preceding script stage first.')
   db.execute('INSERT OR REPLACE INTO dq_stages VALUES (?,?,?,?,?,?)',(pid,stage,self.script_hash(pid),evidence,reviewer,time.time()))
 def structural_issues(self,pid):
  e=self.entries(pid);issues=[]
  needed={'research':False,'season':False,'scene':False,'line':False,'shot':False}
  for key,r in e.items():
   comp,item=key.split('/');p=r['payload'];needed[comp]=True
   required={'research':['claim','classification','application'], 'season':['premise','arc','episodes'], 'bible':['identity','continuity'], 'scene':['start','end','objective','obstacle','turn','consequence','setting','action'], 'line':['start','end','scene_id','speaker','addressee','text','intention','emotion','pace','pauses','emphasis'], 'shot':['order','scene_id','seconds','action','framing','camera_reason','reference_ids','coverage'], 'music':['scene_ids','start','end','purpose','progression','treatment'], 'sfx':['event_id','global_start','duration','shot_id','offset','event','kind','distance','room','perspective']} .get(comp,[])
   for field in required:
    if field not in p or p[field] is None or p[field]=='' or p[field]==[]:issues.append(key+': missing '+field)
   if comp=='research':
    if p.get('classification') not in ('verified_fact','fictional_choice','craft_reference'):issues.append(key+': classify fact, fiction or craft reference')
    if p.get('classification')!='fictional_choice' and not (url(p.get('source_url')) and text(p.get('source_summary')) and text(p.get('retrieved_at'))):issues.append(key+': source evidence missing')
   if comp=='season' and not isinstance(p.get('episodes'),list):issues.append(key+': episode architecture must be a list')
   if comp in ('line','scene') and (not all(finite(p.get(k)) for k in ('start','end')) or not 0<=p.get('start',-1)<p.get('end',-1)<=self.project(pid)['target_seconds']):issues.append(key+': invalid dramatic timeline interval')
   if comp=='line':
    if not re.search('[\u0980-\u09ff]',p.get('text','')):issues.append(key+': Bangla dialogue required')
    for lex in p.get('lexicon_ids',[]):
     lp=e.get('lexicon/'+lex,{}).get('payload',{})
     if lp.get('written') not in p.get('text',''):issues.append(key+': listed pronunciation word is not in this line')
   if comp=='lexicon' and not all(text(p.get(k)) for k in ('written','spoken','reason')):issues.append(key+': pronunciation entry needs written/spoken/reason')
   if comp=='shot':
    if not isinstance(p.get('order'),int) or isinstance(p.get('order'),bool):issues.append(key+': shot order must be an integer')
    if not finite(p.get('seconds')) or not .5<=p['seconds']<=30:issues.append(key+': shot duration must be 0.5–30 seconds')
    if p.get('style')!='photorealistic':issues.append(key+': realistic drama cannot use cartoons, still animatics or mocks')
    if not p.get('reference_ids'):issues.append(key+': continuity references required')
    if p.get('coverage') not in ('on_camera','off_camera','reaction','over_shoulder','insert','establishing'):issues.append(key+': unsupported dialogue coverage')
   if comp=='music':
    if not all(finite(p.get(k)) for k in ('start','end')) or p.get('end',0)<=p.get('start',0):issues.append(key+': invalid cue interval')
    if p.get('treatment') not in ('composed','ambience_only','silence'):issues.append(key+': select composed music, ambience or silence')
    if p.get('treatment')=='composed' and not all(text(p.get(k)) for k in ('instrumentation','motif','harmony')):issues.append(key+': composition needs instrumentation, motif and harmonic development')
   if comp=='sfx':
    if not finite(p.get('duration')) or p.get('duration',0)<=0 or not finite(p.get('global_start')) or not 0<=p.get('global_start',-1)<p.get('global_start',0)+p.get('duration',0)<=self.project(pid)['target_seconds']:issues.append(key+': sound duration outside episode')
    shot=e.get('shot/'+str(p.get('shot_id','')),{}).get('payload',{})
    if not finite(p.get('offset')) or not 0<=p.get('offset',-1)<shot.get('seconds',0):issues.append(key+': event outside shot')
    event=next((x for x in shot.get('events',[]) if x.get('id')==p.get('event_id')),None)
    if not event or not finite(event.get('offset')) or not finite(p.get('offset')) or abs(event['offset']-p['offset'])>.02:issues.append(key+': SFX is not bound to the planned on-screen/off-screen event')
    if p.get('kind') not in ('foley','ambience','designed'):issues.append(key+': sound layer must be explicit')
   try:self.fingerprint(pid,key,e)
   except QualityError as ex:issues.append(str(ex))
  project=self.project(pid)
  if project['content_id'] is not None:
   with self.tx() as db:
    link=db.execute('SELECT source_hash,script_sha FROM dq_script_links WHERE project=?',(pid,)).fetchone()
    row=db.execute('SELECT script FROM content WHERE id=?',(project['content_id'],)).fetchone()
   if not link or not row or link[0]!=self.script_hash(pid) or link[1]!=text_hash(row[0]):issues.append('Existing Studio draft and versioned screenplay differ; reconcile the screenplay before production')
  issues.extend('Missing '+k+' development' for k in ('research','season','scene','line','shot') if not needed.get(k))
  shot_rows=[r['payload'] for k,r in e.items() if k.startswith('shot/')]
  orders=[s.get('order') for s in shot_rows]
  if all(isinstance(x,int) for x in orders) and sorted(orders)!=list(range(1,len(orders)+1)):issues.append('Shot orders must be unique and continuous')
  for k,r in e.items():
   p=r['payload']
   if k.startswith('sfx/') and finite(p.get('global_start')) and finite(p.get('offset')):
    shot=e.get('shot/'+str(p.get('shot_id','')),{}).get('payload',{})
    if finite(shot.get('start')) and abs(p['global_start']-shot['start']-p['offset'])>.02:issues.append(k+': sound event and shot offsets disagree')
    stop=p.get('must_stop_by')
    if finite(stop) and p.get('global_start',0)+p.get('duration',0)>stop+.02:issues.append(k+': ambience violates a story stop event')
   if k.startswith('music/') and p.get('treatment')=='silence':
    for kk,rr in e.items():
     c=rr['payload']
     if kk.startswith('music/') and c.get('treatment')=='composed' and all(finite(v) for v in (p.get('start'),p.get('end'),c.get('start'),c.get('end'))) and max(p['start'],c['start'])<min(p['end'],c['end']):issues.append(k+': composed cue overlaps an intentional silence interval')
  total=sum(r['payload'].get('seconds',0) for k,r in e.items() if k.startswith('shot/') and finite(r['payload'].get('seconds')))
  if abs(total-self.project(pid)['target_seconds'])>1:issues.append(f'Shot timeline is {total:.2f}s; target is {self.project(pid)["target_seconds"]:.2f}s')
  return list(dict.fromkeys(issues))
 def register_asset(self,pid,kind,target,path,metadata):
  if kind not in KINDS:raise QualityError('Unknown asset kind.')
  component={'reference':'bible','shot':'shot','voice':'line','music':'music','foley':'sfx','ambience':'sfx','designed':'sfx'}[kind]
  self.project(pid);ident(target);path=Path(path).resolve();allowed=(self.root/pid).resolve()
  if not path.is_relative_to(allowed) or not path.is_file() or path.stat().st_size>500*1024*1024:raise QualityError('Import media into this project before registering it.')
  if kind=='shot' and metadata.get('output_kind')!='photorealistic_neural_video':raise QualityError('A realistic shot requires actual photorealistic neural footage; no cartoon/still/mock fallback.')
  if kind=='voice' and metadata.get('output_kind') not in ('neural_dialogue','recorded_dialogue'):raise QualityError('Spoken character dialogue is required.')
  if kind=='reference' and metadata.get('output_kind')!='photorealistic_reference':raise QualityError('Realistic-drama references must be photorealistic, not drawn rigs.')
  if kind=='music' and metadata.get('output_kind')!='composed_music':raise QualityError('A tone/noise bed cannot be registered as a musical composition.')
  if not (text(metadata.get('engine')) and url(metadata.get('rights_url')) and text(metadata.get('rights_note'))):raise QualityError('Engine and usage-rights evidence required.')
  if metadata.get('cost_usd')!=0 or metadata.get('paid_api') is not False:raise QualityError('Only explicitly zero-cost, no-paid-API assets are accepted.')
  if kind!='reference':
   info=media_info(path)
   if kind=='shot' and not any(s['codec_type']=='video' for s in info['streams']):raise QualityError('The shot has no video stream.')
   if kind in {'voice','music','foley','ambience','designed'} and not any(s['codec_type']=='audio' for s in info['streams']):raise QualityError('The take has no audio stream.')
   metadata={**metadata,'probe':info}
  else:
   from PIL import Image
   try:
    with Image.open(path) as im:im.verify()
   except Exception:raise QualityError('Invalid reference image.') from None
  content_sha=file_hash(path);objects=allowed/'objects';objects.mkdir(parents=True,exist_ok=True);frozen=objects/(content_sha+path.suffix.lower())
  if frozen.exists():
   if file_hash(frozen)!=content_sha:raise QualityError('A stored media object changed; restore its verified checkpoint before reuse.')
  else:
   shutil.copyfile(path,frozen);frozen.chmod(0o444)
  path=frozen
  aid=uuid4().hex;inputs=self.fingerprint(pid,component+'/'+target)
  with self.tx() as db:db.execute('INSERT INTO dq_assets VALUES (?,?,?,?,?,?,?,?,0,?)',(aid,pid,kind,target,str(path),file_hash(path),inputs,canonical(metadata),time.time()))
  return aid
 def import_bytes(self,pid,name,data):
  self.project(pid)
  if not isinstance(data,bytes) or not data or len(data)>500*1024*1024:raise QualityError('Invalid or oversized media upload.')
  suffix=Path(name).suffix.lower()
  if suffix not in ('.png','.jpg','.jpeg','.wav','.mp3','.mp4','.flac'):raise QualityError('Unsupported media extension.')
  folder=self.root/pid/'assets';folder.mkdir(parents=True,exist_ok=True);p=folder/(uuid4().hex+suffix);p.write_bytes(data);return p
 def assets(self,pid):
  with self.tx() as db:rows=db.execute('SELECT * FROM dq_assets WHERE project=? ORDER BY created DESC',(pid,)).fetchall()
  out=[]
  for r in rows:
   a=dict(r);a['metadata']=json.loads(a['metadata']);a['current']=self.asset_current(a);out.append(a)
  return out
 def asset_current(self,a):
  component={'reference':'bible','shot':'shot','voice':'line','music':'music','foley':'sfx','ambience':'sfx','designed':'sfx'}[a['kind']]
  try:return self.fingerprint(a['project'],component+'/'+a['target'])==a['inputs'] and Path(a['path']).is_file() and file_hash(a['path'])==a['sha']
  except (QualityError,OSError):return False
 def review(self,pid,subject,dimension,decision,reviewer,reviewer_type,evidence):
  if decision not in ('pass','fail','needs_review') or reviewer_type not in ('agent','human') or not text(reviewer) or len(evidence.strip())<15:raise QualityError('Record reviewer identity, type and concrete evidence; uncertainty is not a pass.')
  if subject=='project':
   if dimension not in {'drama','dialogue','continuity','sound_plan'}:raise QualityError('Use final export reviews for final picture/sound.')
   expected=self.source_hash(pid)
  elif subject=='final':
   if dimension not in {'final_picture','final_sound'}:raise QualityError('Unsupported final review dimension.')
   with self.tx() as db:export=db.execute('SELECT sha,source_hash,path FROM dq_exports WHERE project=?',(pid,)).fetchone()
   if not export or export[1]!=self.source_hash(pid) or not Path(export[2]).is_file() or file_hash(export[2])!=export[0]:raise QualityError('No current export bytes to review.')
   expected=export[1]+':'+export[0]
  else:
   a=next((a for a in self.assets(pid) if a['id']==subject),None)
   if not a or not a['current']:raise QualityError('Review only a current existing media asset.')
   if dimension not in DIMENSIONS[a['kind']]:raise QualityError('Review dimension does not match this asset.')
   expected=a['sha']+':'+a['inputs']
  with self.tx() as db:db.execute('INSERT INTO dq_reviews(project,subject,subject_hash,dimension,decision,reviewer,reviewer_type,evidence,created) VALUES (?,?,?,?,?,?,?,?,?)',(pid,subject,expected,dimension,decision,reviewer,reviewer_type,evidence,time.time()))
 def reviews_pass(self,pid,subject,expected,dimensions):
  with self.tx() as db:
   for dimension in dimensions:
    r=db.execute('SELECT decision FROM dq_reviews WHERE project=? AND subject=? AND subject_hash=? AND dimension=? ORDER BY id DESC LIMIT 1',(pid,subject,expected,dimension)).fetchone()
    if not r or r[0]!='pass':return False
  return True
 def select(self,pid,aid):
  a=next((a for a in self.assets(pid) if a['id']==aid),None)
  if not a or not a['current']:raise QualityError('Media is absent or stale.')
  if not self.reviews_pass(pid,aid,a['sha']+':'+a['inputs'],DIMENSIONS[a['kind']]):raise QualityError('Complete asset editorial review before selecting this take.')
  with self.tx() as db:
   db.execute('UPDATE dq_assets SET selected=0 WHERE project=? AND kind=? AND target=?',(pid,a['kind'],a['target']))
   db.execute('UPDATE dq_assets SET selected=1 WHERE id=?',(aid,))
 def jobs(self,pid):
  with self.tx() as db:return [dict(r) for r in db.execute('SELECT * FROM dq_jobs WHERE project=? ORDER BY created DESC',(pid,))]
 def start_job(self,pid,kind,target,allow_reconciled_retry=False):
  if kind not in ('shot','voice','music','foley','ambience','designed','render'):raise QualityError('Unsupported job.')
  ident(target);key={'shot':'shot','voice':'line','music':'music','foley':'sfx','ambience':'sfx','designed':'sfx'}.get(kind)
  fp=self.fingerprint(pid,key+'/'+target) if key else self.source_hash(pid)
  with self.tx() as db:
   db.execute('BEGIN IMMEDIATE')
   pending=db.execute("SELECT id,state FROM dq_jobs WHERE project=? AND kind=? AND target=? AND input_hash=? ORDER BY created DESC LIMIT 1",(pid,kind,target,fp)).fetchone()
   if pending and (pending['state']!='failed_reconciled' or not allow_reconciled_retry):raise QualityError('A cached, blocked or uncertain job exists; inspect its checkpoint instead of resubmitting.')
   jid=uuid4().hex;now=time.time();db.execute('INSERT INTO dq_jobs VALUES (?,?,?,?,?,?,?,?,?)',(jid,pid,kind,target,fp,'submission_uncertain','No automatic retry',now,now))
  return jid
 def job_state(self,jid,state,detail):
  if state not in ('running','complete','blocked','submission_uncertain','failed_reconciled'):raise QualityError('Invalid checkpoint state.')
  with self.tx() as db:db.execute('UPDATE dq_jobs SET state=?,detail=?,updated=? WHERE id=?',(state,detail[:2000],time.time(),jid))
 def gates(self,pid):
  e=self.entries(pid);struct=self.structural_issues(pid);source=self.source_hash(pid);script=self.script_hash(pid)
  with self.tx() as db:polish=db.execute("SELECT 1 FROM dq_stages WHERE project=? AND stage='dialogue_polish' AND source_hash=?",(pid,script)).fetchone()
  development=struct+([] if polish else ['Current screenplay needs a recorded dialogue-polish assessment'])
  editor=[] if self.reviews_pass(pid,'project',source,{'drama','dialogue','continuity','sound_plan'}) else ['Current project editorial review is incomplete or requires correction']
  capabilities=[]
  for kind in ('video','voice'):
   p=e.get('capability/'+kind,{}).get('payload',{})
   if not (p.get('cost_usd')==0 and p.get('paid_api') is False and p.get('access')=='verified' and p.get('production_rights')=='verified' and p.get('quota')=='available' and finite(p.get('checked_at')) and 0<=time.time()-p['checked_at']<86400):capabilities.append(kind+': free access, quota, rights and fresh evidence are not all verified')
   if kind=='video' and (not finite(p.get('estimated_job_gpu_seconds')) or not finite(p.get('remaining_gpu_seconds')) or p.get('remaining_gpu_seconds',0)<p.get('estimated_job_gpu_seconds',float('inf'))):capabilities.append('video: sufficient GPU quota for this project is unproven')
  selected=[a for a in self.assets(pid) if a['selected'] and a['current'] and self.reviews_pass(pid,a['id'],a['sha']+':'+a['inputs'],DIMENSIONS[a['kind']])]
  required=[]
  for key,r in e.items():
   comp,target=key.split('/');p=r['payload']
   kind={'bible':'reference','line':'voice','shot':'shot','sfx':p.get('kind'),'music':'music' if p.get('treatment')=='composed' else None}.get(comp)
   if comp=='bible' and p.get('reference_required') is False:kind=None
   if kind and not any(a['kind']==kind and a['target']==target for a in selected):required.append(key+': no current selected and editorially accepted asset')
  required.extend(a['kind']+'/'+a['target']+': public output rights are not verified' for a in selected if a['metadata'].get('rights_scope')!='publication')
  sample=e.get('capability/sample',{}).get('payload',{})
  sample_assets=[next((a for a in selected if a['id']==sample.get(k)),None) for k in ('video_asset','voice_asset')]
  sample_ok=all(sample_assets) and sample_assets[0]['kind']=='shot' and sample_assets[1]['kind']=='voice'
  preflight=development+editor+capabilities+([] if sample_ok else ['Representative photorealistic scene and performed dialogue have not both passed review'])
  finishing=development+editor+([] if sample_ok else ['Representative photorealistic scene and performed dialogue have not both passed review'])+required
  return {'production_start':{'passed':not preflight,'issues':list(dict.fromkeys(preflight))},'development':{'passed':not development,'issues':development},'editorial':{'passed':not editor,'issues':editor},'capability':{'passed':not capabilities,'issues':capabilities},'representative_scene':{'passed':bool(sample_ok),'issues':[] if sample_ok else ['No accepted paired realism-and-dialogue sample']},'full_render':{'passed':not finishing,'issues':list(dict.fromkeys(finishing))},'source_hash':source,'selected_assets':len(selected),'paid_api_calls':0}
 def sync_content_script(self,pid):
  e=self.entries(pid);project=self.project(pid)
  script='# '+project['title']+'\n\nOriginal fictional drama; character dialogue only.\n\n'
  scenes=sorted([(k,v['payload']) for k,v in e.items() if k.startswith('scene/')],key=lambda x:x[1].get('start',0))
  lines=sorted([(k,v['payload']) for k,v in e.items() if k.startswith('line/')],key=lambda x:x[1].get('start',0))
  for key,p in scenes:
   script+=f"## {key}: {p.get('start')}–{p.get('end')}s · {p.get('setting','')}\n\n{p.get('action','')}\n\n"
   for _,line in lines:
    if line.get('scene_id')==key.split('/')[1]:script+=f"{line.get('start')}–{line.get('end')} · {line.get('speaker')}: {line.get('text','')}\n\n"
  with self.tx() as db:
   if project['content_id'] is not None:db.execute("UPDATE content SET script=?,status='Draft',updated_at=? WHERE id=?",(script,__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),project['content_id']))
   db.execute('INSERT OR REPLACE INTO dq_script_links VALUES (?,?,?)',(pid,self.script_hash(pid),text_hash(script)))
  return script
 def spoken_line(self,pid,line_id):
  e=self.entries(pid);p=e['line/'+line_id]['payload'];spoken=p['text']
  for key in p.get('lexicon_ids',[]):
   entry=e['lexicon/'+key]['payload'];spoken=spoken.replace(entry['written'],entry['spoken'])
  return spoken
 def export_current(self,pid,export):
  if export is None:return False
  # Accept SQLite Row or a dict; call sites request named columns.
  source=export['source_hash'];manifest=json.loads(export['manifest'])
  selected={a['id']:a['sha'] for a in self.assets(pid) if a['selected'] and a['current']}
  return source==self.source_hash(pid) and manifest.get('assets')==selected and Path(export['path']).is_file() and file_hash(export['path'])==export['sha']
 def attach_export(self,pid):
  project=self.project(pid)
  if project['content_id'] is None:raise QualityError('No existing Studio content row is linked.')
  media_root=self.root.parent
  assert_content_publishable(self.db,media_root,project['content_id'])
  with self.tx() as db:
   export=db.execute('SELECT path,qa FROM dq_exports WHERE project=?',(pid,)).fetchone()
   script=db.execute('SELECT script FROM content WHERE id=?',(project['content_id'],)).fetchone()
   if not script:raise QualityError('Linked Studio draft is missing.')
   db.execute('CREATE TABLE IF NOT EXISTS content_video(content_id INTEGER PRIMARY KEY,video_path TEXT,seconds REAL,voice_included INTEGER,created_at TEXT)')
   db.execute('INSERT OR REPLACE INTO content_video VALUES (?,?,?,?,?)',(project['content_id'],export[0],json.loads(export[1])['duration'],1,__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()))
   # Remains awaiting review at the existing owner approval boundary.
   db.execute("UPDATE content SET status='Awaiting review' WHERE id=?",(project['content_id'],))
 def snapshot(self,pid):
  return {'project':self.project(pid),'entries':self.entries(pid),'gates':self.gates(pid),'assets':[{k:v for k,v in a.items() if k!='path'} for a in self.assets(pid)],'jobs':self.jobs(pid)}

def assert_content_publishable(db_path,media_root,content_id):
 """Called by existing approval and YouTube boundaries; legacy rows remain legacy."""
 with sqlite3.connect(db_path) as db:
  if not db.execute("SELECT 1 FROM sqlite_master WHERE name='dq_projects'").fetchone():return
  r=db.execute('SELECT id FROM dq_projects WHERE content_id=?',(content_id,)).fetchone()
  if not r:return
  db.row_factory=sqlite3.Row
  row=db.execute('SELECT * FROM dq_exports WHERE project=?',(r[0],)).fetchone();export=dict(row) if row else None
 if not export:raise QualityError('Realistic drama has no quality-approved final export; legacy/cartoon footage cannot substitute.')
 studio=Studio(db_path,media_root);gate=studio.gates(r[0])
 if not gate['full_render']['passed'] or not studio.export_current(r[0],export):raise QualityError('Realistic drama source or quality gates changed; final approval is blocked.')
 if not Path(export['path']).is_file() or file_hash(export['path'])!=export['sha']:raise QualityError('Final realistic-drama bytes changed or are missing.')
 if not json.loads(export['qa']).get('passed'):raise QualityError('Technical final QA has not passed.')
 if not studio.reviews_pass(r[0],'final',export['source_hash']+':'+export['sha'],{'final_picture','final_sound'}):raise QualityError('Final picture and sound editorial review required before publication approval.')
