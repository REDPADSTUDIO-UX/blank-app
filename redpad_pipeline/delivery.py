"""Genuine isolated asset import, source-bound EDL assembly and delivery receipts.

No placeholder generator, network transport, source replacement or artistic pass.
"""
from .resource_guard import serialized

import json,math,subprocess,time
from pathlib import Path
from uuid import uuid4
from .agents import AgentError,encode
from .creative import digest
from .offline_media import media_path,sha
from .specialist_inspection import inspect_clip

class Delivery:
    def __init__(self,program):
        self.p=program
        with program.store.tx() as db:db.execute('CREATE TABLE IF NOT EXISTS delivery_assets(id TEXT PRIMARY KEY,payload TEXT,sha TEXT)')
    def register(self,path,owner,rights,confirmed=False,*,run_id=None,origin='owner_import'):
        if confirmed is not True or not all(isinstance(s,str) and s.strip() for s in (owner,rights)):raise AgentError('Explicit rights attestation and owner identity required for isolated assets.')
        if origin not in ('owner_import','manually_authored_fixture'):raise AgentError('Cannot claim unverified imports are neural model outputs.')
        source=None;metadata={}
        if run_id:
            run=next((r for r in self.p.engine.runs() if r['id']==run_id),None)
            if not run:raise AgentError('Unknown source run.')
            body=self.p.current_output(run['task']);artifact=body['artifact']
            if artifact.get('path')!=path:raise AgentError('Imported path differs from source output.')
            with self.p.store.tx() as db:task=self.p.store._task(db,run['task'])
            source={'task':run['task'],'revision':task['revision'],'body_sha256':digest(body)}
            metadata=artifact.get('metadata',{})
            origin='verified_local_inference' if metadata.get('actual_inference_verified') is True and metadata.get('model_identity_verified') is True and metadata.get('worker_inference',{}).get('inference_completed') is True else 'source_output_unverified_neural_origin'
            if metadata.get('evaluation_only') is True or metadata.get('contains_fixture_inputs') is True:origin='manually_authored_fixture'
        info=inspect_clip(path,self.p.store.path);p=media_path(self.p.store.path,path)
        value={'path':path,'sha256':sha(p),'inspection':info,'owner':owner,'rights':rights,'origin':origin,'source':source,
               'model_metadata':metadata,'professional_quality_verified':False,'human_artistic_review_completed':False}
        id=digest(value)
        with self.p.store.tx() as db:db.execute('INSERT OR IGNORE INTO delivery_assets VALUES (?,?,?)',(id,encode(value),digest(value)))
        return id
    def asset(self,id):
        with self.p.store.tx() as db:r=db.execute('SELECT * FROM delivery_assets WHERE id=?',(id,)).fetchone()
        if not r:raise AgentError('Unknown delivery asset receipt.')
        value=json.loads(r['payload'])
        if digest(value)!=r['sha'] or sha(media_path(self.p.store.path,value['path']))!=value['sha256']:raise AgentError('Delivery source asset changed; reimport and review required.')
        if value['source']:
            s=value['source'];body=self.p.current_output(s['task'])
            with self.p.store.tx() as db:task=self.p.store._task(db,s['task'])
            if task['revision']!=s['revision'] or digest(body)!=s['body_sha256']:raise AgentError('Delivery source approval/revision changed.')
        return value
    def queue_edl(self,plan_task,bindings,durations=None):
        """Bind real assets to an approved plan; new output needs fresh QC/owner review."""
        body=self.p.current_output(plan_task,'editing');rows=json.loads(encode(body['artifact']['records']));deps=[plan_task];timecode=0
        if not isinstance(bindings,dict) or set(bindings)!={r['shot'] for r in rows}:raise AgentError('Bind every approved shot, without adding unrelated shots.')
        durations=durations or {}
        if set(durations)-set(bindings):raise AgentError('Unknown explicit duration revision.')
        for r in rows:
            b=bindings[r['shot']]
            if not isinstance(b,dict) or set(b)!={'video','audio'}:raise AgentError('Actual video/audio receipts required per shot.')
            for field,id in b.items():
                a=self.asset(id);r[field]=a['path']
                if a['source']:deps.append(a['source']['task'])
            seconds=durations.get(r['shot'],r['seconds'])
            if type(seconds) not in (int,float) or not math.isfinite(seconds) or not .01<=seconds<=300:raise AgentError('Valid explicit revised clip duration required.')
            r.update(start=timecode,seconds=seconds,source_in=0,source_seconds=self.asset(b['video'])['inspection']['duration'],subtitle_start=timecode,subtitle_end=timecode+seconds,asset_receipts=b)
            if any(seconds>self.asset(id)['inspection']['duration']+.04 for id in b.values()):raise AgentError('Actual media too short for requested cut; no stretching.')
            timecode+=seconds
        data={'specialist_v1':True,'project':body['artifact']['project'],'records':rows,'sources':{'editing':{'$from':plan_task,'path':['artifact']}},'base':{'$from':plan_task,'path':['artifact']},'targets':[r['id'] for r in rows]}
        return self.p.engine.enqueue('editing',data,list(dict.fromkeys(deps)),mode='software',idempotency_key='receipt-edl:'+digest([plan_task,data]))
    @serialized
    def render(self,editing_task,receipts,*,evaluation_only=False,timeout=300):
        if type(evaluation_only) is not bool:raise AgentError('Evaluation-only flag must be an explicit boolean.')
        if type(timeout) is not int or not 30<=timeout<=900:raise AgentError('Bounded assembly timeout required.')
        body=self.p.current_output(editing_task,'editing');rows=body['artifact']['records']
        if not isinstance(receipts,dict) or not 1<=len(rows)<=80:raise AgentError('Bounded approved EDL and receipt map required.')
        ids={p for r in rows for p in (r['video'],r['audio'])}
        if set(receipts)!=ids or 'pending' in ids:raise AgentError('Every actual EDL asset must have an explicit receipt; no generated substitute.')
        assets={path:self.asset(receipts[path]) for path in ids}
        if any(a['path']!=path for path,a in assets.items()):raise AgentError('Receipt/path mismatch.')
        if not evaluation_only and any(a['origin']=='manually_authored_fixture' for a in assets.values()):raise AgentError('Test fixtures cannot become production delivery.')
        from .specialists import prepare
        # Revalidate EDL using the same current approved records, before rendering.
        prepare('editing',{'specialist_v1':True,'project':body['artifact']['project'],'records':rows,'sources':{},'base':None,'targets':[]})
        profile=rows[0]['export_profile']
        if any(r['export_profile']!=profile or r['transition']!='cut' or r['vfx']!='none' or r['color'] not in ('source','none') for r in rows):raise AgentError('This assembly implements hard cuts/source color only; effects/fades/grading must not be silently ignored.')
        width,height,fps={'1080p24':(1920,1080,24),'720p24':(1280,720,24),'test256p8':(256,144,8)}[profile]
        total=sum(r['seconds'] for r in rows)
        if total>300:raise AgentError('Split long delivery into approved scenes of at most five minutes.')
        for r in rows:
            for field,kind in (('video','video'),('audio','audio')):
                a=assets[r[field]]
                if not any(s.get('codec_type')==kind for s in a['inspection']['streams']):raise AgentError('EDL input lacks required '+kind+' stream.')
                if r['source_in']+r['seconds']>a['inspection']['duration']+.04:raise AgentError('EDL overruns actual source media, regardless of declared source_seconds.')
        root=self.p.root/'agent_media/deliveries'
        if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe delivery workspace.')
        job=root/uuid4().hex;job.mkdir(parents=True);out=job/'review.mp4'
        state={'state':'running','editing_task':editing_task,'editing_body_sha256':digest(body),'receipts':receipts,'input_hashes':{p:a['sha256'] for p,a in assets.items()},
               'evaluation_only':evaluation_only is True,'actual_neural_inference':False,'professional_quality_verified':False,'human_review_completed':False}
        def save():(job/'receipt.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
        save();started=time.monotonic()
        try:
            parts=[]
            for i,r in enumerate(rows):
                if abs(r['seconds']*fps-round(r['seconds']*fps))>.001:raise AgentError('Cut duration must fit the approved export frame grid; request an explicit rebudget.')
                # Normalize sequentially: at most two decoders, rather than
                # opening up to 160 source streams at once on a small CPU host.
                cmd=['ffmpeg','-nostdin','-v','error'];filters=[]
                vp=media_path(self.p.store.path,r['video']);ap=media_path(self.p.store.path,r['audio'])
                for path in (vp,ap):
                    with path.open('rb') as f:header=f.read(12)
                    fmt='mov' if header[4:8]==b'ftyp' else 'wav'
                    cmd+=['-protocol_whitelist','file,pipe','-f',fmt,'-i',str(path)]
                filters += [f'[0:v]trim=start={r["source_in"]}:duration={r["seconds"]},setpts=PTS-STARTPTS,scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v]',
                            f'[1:a]atrim=start={r["source_in"]}:duration={r["seconds"]},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a]']
                part=job/f'part-{i:03}.mkv';parts.append(part)
                cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-threads','1','-pix_fmt','yuv420p','-c:a','pcm_s16le',str(part)]
                remaining=timeout-(time.monotonic()-started)
                if remaining<=0:raise AgentError('Total assembly deadline exceeded; completed parts retained.')
                with (job/'worker.log').open('a') as log:subprocess.run(cmd,stdout=log,stderr=log,timeout=remaining,check=True)
            playlist=job/'owned-parts.txt';playlist.write_text('\n'.join("file '"+p.name+"'" for p in parts))
            remaining=timeout-(time.monotonic()-started)
            if remaining<=0:raise AgentError('Total assembly deadline exceeded.')
            cmd=['ffmpeg','-nostdin','-v','error','-protocol_whitelist','file,pipe','-f','concat','-safe','1','-i',str(playlist),'-c:v','copy','-c:a','aac','-movflags','+faststart',str(out)]
            with (job/'worker.log').open('a') as log:subprocess.run(cmd,stdout=log,stderr=log,timeout=remaining,check=True)
            for id in receipts.values():self.asset(id)
            if digest(self.p.current_output(editing_task,'editing'))!=digest(body):raise AgentError('EDL changed during assembly.')
            relative=str(out.relative_to(self.p.root/'agent_media'));inspection=inspect_clip(relative,self.p.store.path)
            if abs(inspection['duration']-total)>.2:raise AgentError('Delivery duration differs from approved EDL.')
            subprocess.run(['ffmpeg','-v','error','-protocol_whitelist','file,pipe','-i',str(out),'-f','null','-'],capture_output=True,timeout=60,check=True)
            def tc(t):
                n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
            (job/'dialogue.srt').write_text('\n\n'.join(f'{i}\n{tc(r["subtitle_start"])} --> {tc(r["subtitle_end"])}\n{r["subtitle"]}' for i,r in enumerate(rows,1) if r['subtitle'].strip()))
            state.update(state='technical_output_validated',output=relative,output_sha256=sha(out),inspection=inspection,subtitles='dialogue.srt',subtitle_embedding=False)
            return {'path':relative,'model':'none — receipt-bound FFmpeg assembly','actual_generation':True,'metadata':state}
        except Exception:
            state.update(state='failed',error='Assembly/validation failed; original inputs and partial output retained.')
            raise
        finally:state['wall_seconds']=round(time.monotonic()-started,3);save()

def from_sidecar(sidecar):
    from types import SimpleNamespace
    from .agents import AgentStore
    from .agent_engine import Engine
    from .studio_program import StudioProgram
    program=SimpleNamespace(store=AgentStore(sidecar),root=Path(sidecar).parent)
    program.engine=Engine(program.store)
    program.current_output=lambda tid,role=None:StudioProgram.current_output(program,tid,role)
    return Delivery(program)
