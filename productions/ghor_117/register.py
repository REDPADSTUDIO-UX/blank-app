"""Register verified output and storyboard in this checkout's isolated SQLite only."""
import json,sqlite3,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from redpad_pipeline.engine import initialize
from redpad_pipeline.storyboard import save_board,script_hash,load_board
from redpad_pipeline.drama_animation import frame
P=Path(__file__).parent;REPO=P.parents[1];R=REPO/'redpad_media'/'drama'/'ghor117_ep01';DB=REPO/'redpad_studio.db'
plan=json.loads((P/'plan.json').read_text());qa=json.loads((R/'qa_report.json').read_text());video=R/qa['file']
if not qa['passed'] or hashlib.sha256(video.read_bytes()).hexdigest()!=qa['sha256']:raise ValueError('Unverified output')
if not DB.exists():raise ValueError('Run isolated Studio first to initialize its schema')
initialize(DB);now=datetime.now(timezone.utc).isoformat();script=(P/'screenplay.md').read_text()
with sqlite3.connect(DB) as db:
 db.execute('CREATE TABLE IF NOT EXISTS drama_projects(project_key TEXT PRIMARY KEY,content_id INTEGER NOT NULL,media_root TEXT NOT NULL,sha256 TEXT NOT NULL,metadata TEXT NOT NULL)')
 row=db.execute('SELECT content_id FROM drama_projects WHERE project_key=?',('ghor117_ep01',)).fetchone()
 if row:cid=row[0]
 else:
  ch=db.execute('SELECT id FROM channels WHERE name=?',('নিশিকথা',)).fetchone()
  channel=ch[0] if ch else db.execute("INSERT INTO channels(name,platform,niche,videos_per_day,publish_time,active) VALUES (?,?,?,0,'18:00',1)",('নিশিকথা','YouTube','Original Bangla animated drama')).lastrowid
  cid=db.execute("INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",(channel,plan['title'],'Original 2D animated drama — owner-authorized Episode 1 demonstration',script,'Approved',now,now)).lastrowid
 db.execute('INSERT OR REPLACE INTO content_video VALUES (?,?,?,?,?)',(cid,str(video.resolve()),qa['seconds'],1,now))
 review=dict(authorization='User explicitly authorized agent approval and public publication of only this completed Episode 1.',reviewer='Automated production QA under owner instruction',human_watched=False,media_sha256=qa['sha256'],qa_passed=True,approved_at=now,channel_id=plan['channel_id'],content_id=cid,scope='Only final verified Episode 1; no other upload or schedule')
 db.execute('INSERT OR REPLACE INTO drama_projects VALUES (?,?,?,?,?)',('ghor117_ep01',cid,str(R.resolve()),qa['sha256'],json.dumps(review,ensure_ascii=False)))
(R/'review_record.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
board=dict(content_id=cid,title=plan['title'],script_hash=script_hash(script),ratio='16:9',character_bible='Rafi: short black hair, stubble, ochre shirt. Mina: long black hair, teal. Hazera: purple scarf and grey streaks. Same rigs throughout. See production_bible.md.',location_bible='Rafi house: window left, portrait centre, locked door right, desk left. Mina apartment is separate with bookcase. Night.',look_bible='Original stylized graphic-novel 2D animation, 1280x720. Warm ochre against blue night.',shots=[])
refs=R/'shot_references';refs.mkdir(exist_ok=True)
for i,s in enumerate(plan['shots']):
 f=refs/(s['id']+'.png');frame(s,1,.25).save(f)
 board['shots'].append(dict(number=i+1,narration=s['text'] or 'দৃশ্য ও শব্দ; কোনো সংলাপ নেই।',visual=s['view']+' / '+s['action'],shot_type='Close-up' if 'close' in s['view'] else 'Insert' if s['view']=='tape' else 'Medium',camera='Slow push-in',seconds=7 if i%2==0 else 8,notes=f'Exact production timing: {s["start"]}–{s["start"]+7.5}s; integer storyboard slots round alternating 7/8s. Foley: {s["sfx"]}.',reference_path=str(f.resolve()),english='',sfx='none'))
current=load_board(DB,cid)
save_board(DB,board,expected_revision=current['revision'] if current else 0)
# Record authorized approval, never assert a person watched this output.
with sqlite3.connect(DB) as db:db.execute("UPDATE storyboards SET review_status='Approved' WHERE content_id=?",(cid,))
(R/'storyboard.json').write_text(json.dumps(board,ensure_ascii=False,indent=2));print('Registered isolated Studio project',cid,'with 40 storyboard references and hash-bound review')
