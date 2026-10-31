"""Studio-owned, checkpointed free image/voice -> edited episode workflow.

No billed providers, no publishing and no automatic retry of uncertain calls.
An image animatic is labelled as such; it is never described as neural video.
"""
import hashlib,json,math,sqlite3,threading,wave,shutil
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
from PIL import Image,ImageOps
from .remote_gpu import free_account_token,GPUError
from .free_voice import generate_google_bangla,VoiceError
from .media import ff,duration,timestamp

IMAGE_SPACE='black-forest-labs/FLUX.1-schnell'
_threads={}
_guard=threading.Lock()

def write(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2));tmp.replace(path)

def validate(plan):
    if not isinstance(plan,dict) or not isinstance(plan.get('title'),str) or not plan['title'].strip():
        raise ValueError('A named episode plan is required.')
    shots=plan.get('shots',[])
    if not isinstance(shots,list) or not 1<=len(shots)<=60:raise ValueError('Use 1–60 shots.')
    if len({s.get('prompt') for s in shots})!=len(shots):raise ValueError('Repeated visual prompts are blocked.')
    for s in shots:
        if not isinstance(s.get('seconds'),int) or not 3<=s['seconds']<=15:raise ValueError('Each shot must be 3–15 seconds.')
        if not isinstance(s.get('text'),str) or not 1<=len(s['text'])<=500:raise ValueError('Each shot needs short spoken Bangla.')
        if not isinstance(s.get('prompt'),str) or not 10<=len(s['prompt'])<=2000:raise ValueError('Each shot needs a distinct image prompt.')
    if sum(s['seconds'] for s in shots)>600:raise ValueError('Split episodes longer than ten minutes.')
    return plan

def new_job(db_path,media_dir,channel_id,plan):
    validate(plan)
    from .engine import initialize
    initialize(db_path)
    root=(Path(media_dir)/'free_episodes'/uuid4().hex).resolve();root.mkdir(parents=True)
    write(root/'plan.json',plan)
    script='\n'.join(s['text'] for s in plan['shots'])
    now=datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as db:
        if not db.execute('SELECT id FROM channels WHERE id=?',(channel_id,)).fetchone():raise ValueError('Select an existing channel.')
        cid=db.execute("INSERT INTO content(channel_id,title,topic,script,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
            (channel_id,plan['title'],'FREE AI IMAGE ANIMATIC — '+plan.get('source_note',''),script,'Draft',now,now)).lastrowid
    write(root/'state.json',dict(phase='queued',content_id=cid,done=0,total=len(plan['shots']),plan_sha256=hashlib.sha256((root/'plan.json').read_bytes()).hexdigest(),error='',output_kind='AI-generated images with editorial camera animation',paid_calls=0))
    return root

def perceptual(path):
    with Image.open(path) as im:
        vals=list(ImageOps.grayscale(im).resize((9,8)).getdata())
    return sum((vals[y*9+x]>vals[y*9+x+1])<<(y*8+x) for y in range(8) for x in range(8))

def image(prompt,dest,seed):
    from gradio_client import Client
    token=free_account_token()
    if not token:raise GPUError('A verified free account is required for episode generation.')
    client=Client(IMAGE_SPACE,hf_token=token,verbose=False,analytics_enabled=False,
                  download_files=str(dest.parent/'download'),httpx_kwargs={'timeout':60})
    try:
        result=client.submit(prompt,seed,False,832,480,4,api_name='/infer').result(timeout=240)
        path=Path(result[0]).resolve()
        if not path.is_relative_to(dest.parent.resolve()) or not path.is_file() or path.stat().st_size>15*1024*1024:
            raise GPUError('Image result could not be accepted.')
        with Image.open(path) as im:
            if im.width*im.height>4_000_000:raise GPUError('Image is too large.')
            im.convert('RGB').save(dest,quality=94)
    except GPUError:raise
    except Exception:
        raise GPUError('Free image generation did not complete. No automatic retry or paid fallback was used.') from None

def soundtrack(path,seconds,cuts):
    import numpy as np
    rate=24000
    with wave.open(str(path),'wb') as out:
        out.setparams((1,2,rate,0,'NONE','not compressed'))
        for start in range(seconds):
            t=(np.arange(rate)+start*rate)/rate
            build=.45+.5*t/seconds
            signal=(np.sin(2*np.pi*48*t)+.23*np.sin(2*np.pi*72.7*t))*1500*build
            # Half-second pulses permit second-aligned cuts on the score grid.
            beat=np.mod(t,.5);signal+=np.sin(2*np.pi*62*t)*np.exp(-beat*23)*650*build
            rng=np.random.default_rng(117+start)
            noise=rng.standard_normal(rate)
            signal+=noise*95*build  # steady rain/air texture, never a mute gap
            for cut in cuts:
                dt=t-cut
                signal+=np.where((dt>=0)&(dt<.7),np.sin(2*np.pi*42*dt)*np.exp(-np.maximum(dt,0)*8)*1700,0)
                rise=(dt>-.65)&(dt<0)
                signal+=np.where(rise,np.sin(2*np.pi*(250*t+100*t*t))*(dt+.65)*600,0)
            fade=np.minimum(1,np.minimum(t/.25,(seconds-t)/1.8))
            out.writeframes((np.clip(signal*fade,-26000,26000).astype('<i2')).tobytes())

def render_shot(still,voice,output,seconds,index):
    actual=duration(voice)
    pace=max(1.,actual/(seconds-.25))
    if pace>1.5:raise ValueError(f'Spoken audio is {actual:.2f}s and exceeds the {seconds}s shot at the supported pace. Speech was not truncated.')
    z='1.025+0.00014*on' if index%2==0 else '1.075-0.00014*on'
    vf=f"scale=1280:740:force_original_aspect_ratio=increase,crop=1280:740,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={seconds*24}:s=960x540:fps=24,format=yuv420p"
    ff(['-i',still,'-i',voice,'-vf',vf,'-af',f'atempo={pace:.6f},apad,atrim=duration={seconds}',
        '-t',seconds,'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','21',
        '-c:a','aac','-ar','24000','-ac','1','-movflags','+faststart',output],timeout=240)

def qa(path,seconds):
    import subprocess,re
    from redpad_video_studio import ffmpeg_binary
    if abs(duration(path)-seconds)>.15:raise ValueError('Final duration failed validation.')
    p=subprocess.run([ffmpeg_binary(),'-hide_banner','-i',str(path),'-vf','blackdetect=d=0.15:pix_th=0.025',
        '-af','silencedetect=n=-65dB:d=0.15','-f','null','-'],capture_output=True,text=True,timeout=240)
    if p.returncode:raise ValueError('Final MP4 failed full decode.')
    if 'black_start:' in p.stderr:raise ValueError('Black section detected; final review was blocked.')
    if 'silence_start:' in p.stderr:raise ValueError('Unintended silent section detected; final review was blocked.')
    return dict(full_decode=True,black_gap=False,silent_gap=False,seconds=duration(path))

def run(db_path,root):
    import fcntl
    root=Path(root)
    with (root/'worker.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        state=json.loads((root/'state.json').read_text());plan=validate(json.loads((root/'plan.json').read_text()))
        if state['phase']=='complete':return
        if hashlib.sha256((root/'plan.json').read_bytes()).hexdigest()!=state['plan_sha256']:raise ValueError('Plan changed.')
        try:
            state.update(phase='running',error='');write(root/'state.json',state)
            hashes=[];clips=[];clock=0;cuts=[];subs=[]
            for i,s in enumerate(plan['shots']):
                folder=root/f'{i+1:03}';folder.mkdir(exist_ok=True)
                still=folder/'image.jpg';voice=folder/'voice.mp3';clip=folder/'shot.mp4'
                marker=folder/'pending.json'
                if marker.exists():raise ValueError('An external submission is uncertain; automatic retry is blocked.')
                if not voice.exists():
                    write(marker,{'stage':'voice-submission'})
                    made=generate_google_bangla(s['text'],folder);shutil.copyfile(made,voice);marker.unlink()
                actual=duration(voice)
                if actual/(s['seconds']-.25)>1.5:raise ValueError(f'Shot {i+1} voice duration {actual:.2f}s exceeds its slot. No image request was made for it.')
                if not still.exists():
                    write(marker,{'stage':'image-submission'})
                    image(s['prompt'],still,117+i*31);marker.unlink()
                h=perceptual(still)
                if any((h^x).bit_count()<5 for x in hashes):raise ValueError('Duplicate-looking image detected. No replacement was automatically submitted.')
                hashes.append(h)
                if not clip.exists():
                    temp=folder/'shot.partial.mp4';render_shot(still,voice,temp,s['seconds'],i);temp.replace(clip)
                clips.append(clip);cuts.append(clock)
                subs.append(f'{i+1}\n{timestamp(clock)} --> {timestamp(clock+s["seconds"])}\n{s["text"]}\n')
                clock+=s['seconds'];state['done']=i+1;write(root/'state.json',state)
                print(f'REDPAD_FREE_EPISODE shot {i+1}/{len(plan["shots"])} complete',flush=True)
            (root/'subtitles.bn.srt').write_text('\n'.join(subs))
            soundtrack(root/'score.wav',clock,cuts)
            (root/'concat.txt').write_text(''.join(f"file '{p.relative_to(root)}'\n" for p in clips))
            final=root/'episode.partial.mp4'
            ff(['-f','concat','-safe','0','-i',root/'concat.txt','-i',root/'score.wav','-i',root/'subtitles.bn.srt',
                '-filter_complex','[0:a]asplit=2[v][side];[1:a][side]sidechaincompress=threshold=0.03:ratio=5:attack=10:release=300[b];[v][b]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92[a]',
                '-map','0:v','-map','[a]','-map','2:0','-t',clock,'-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-c:s','mov_text','-metadata:s:s:0','language=ben','-movflags','+faststart',final],timeout=300)
            report=qa(final,clock);write(root/'qa.json',report)
            final.replace(root/'episode.mp4')
            script='\n'.join(s['text'] for s in plan['shots'])
            with sqlite3.connect(db_path) as db:
                row=db.execute('SELECT script FROM content WHERE id=?',(state['content_id'],)).fetchone()
                if not row or row[0]!=script:raise ValueError('Source script changed; final registration blocked.')
                db.execute('INSERT OR REPLACE INTO content_video VALUES (?,?,?,?,?)',(state['content_id'],str(root/'episode.mp4'),clock,1,datetime.now(timezone.utc).isoformat()))
                db.execute("UPDATE content SET status='Awaiting review' WHERE id=?",(state['content_id'],))
            state.update(phase='complete',qa=report);write(root/'state.json',state)
            print('REDPAD_FREE_EPISODE complete; decoded MP4 registered for human review',flush=True)
        except Exception as e:
            state.update(phase='blocked',error=str(e) if isinstance(e,(ValueError,GPUError,VoiceError)) else 'Free episode processing failed; no paid fallback or substitute video was used.')
            write(root/'state.json',state);print('REDPAD_FREE_EPISODE blocked: '+state['error'],flush=True)

def start(db_path,root):
    with _guard:
        key=str(root)
        if key in _threads and _threads[key].is_alive():return
        worker=threading.Thread(target=run,args=(db_path,root),daemon=True)
        _threads[key]=worker;worker.start()

def show(db_path,media_dir):
    import streamlit as st
    st.subheader('Free Episode Builder — AI image animatic')
    st.caption('FLUX.1 schnell images + Google Bengali speech + editorial camera animation + continuous procedural score/SFX. Not neural moving footage. No paid APIs or publishing.')
    with sqlite3.connect(db_path) as db:channels=db.execute('SELECT id,name FROM channels ORDER BY id DESC').fetchall()
    if not channels:st.info('Add an internal channel profile first.');return
    builtin=st.checkbox('Load original Ghor 1:17 five-minute demo plan',key='free_episode_builtin')
    initial=''
    if builtin:
        initial=(Path(__file__).resolve().parents[1]/'assets/demos/ghor_117_ep01.json').read_text()
        st.info('Original REDPAD story; not a work by Humayun Ahmed. 30 distinct shots, 300 seconds. This demo uses AI stills with camera animation.')
    plan_text=st.text_area('Episode shot plan JSON',value=initial,height=180,key='free_episode_plan_builtin' if builtin else 'free_episode_plan')
    channel=st.selectbox('Episode channel',channels,format_func=lambda r:r[1],key='free_episode_channel')
    consent=st.checkbox('I approve sending this shot plan to the named free image and voice services. Final video still requires review.',key='free_episode_consent')
    if st.button('Build free episode',disabled=not consent or not plan_text.strip()):
        try:
            root=new_job(db_path,media_dir,channel[0],json.loads(plan_text));start(db_path,root);st.success('Studio job started. Refresh status below.')
        except (ValueError,TypeError,KeyError):st.error('Plan is invalid; no generation was submitted.')
    st.button('Refresh episode jobs')
    for statefile in sorted((Path(media_dir)/'free_episodes').glob('*/state.json'),reverse=True):
        root=statefile.parent;state=json.loads(statefile.read_text());plan=json.loads((root/'plan.json').read_text())
        st.write(f"{plan['title']} · {state['phase']} · {state['done']}/{state['total']} shots")
        if state['error']:st.error(state['error'])
        if state['phase']=='complete':
            st.video(str(root/'episode.mp4'))
            with (root/'episode.mp4').open('rb') as data:st.download_button('Download completed episode',data,file_name='episode.mp4',mime='video/mp4',key=str(root))
            st.caption('Awaiting your review in Approval Dashboard. Server media is temporary; download the finished file.')
