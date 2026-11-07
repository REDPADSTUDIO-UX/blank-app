"""Actual isolated cue/voice mix, with receipt-bound rights and explicit ducking.
Sound quality, pronunciation and emotional fit still need listening review.
"""
from .resource_guard import serialized

import json,subprocess,time
from uuid import uuid4
from .agents import AgentError
from .creative import digest
from .delivery import Delivery
from .offline_media import media_path,sha
from .specialists import number

@serialized
def mix(program,music_task,voice_task,receipts,seconds,timeout=180):
    if not number(seconds,.1,300) or type(timeout) is not int or not 30<=timeout<=600:raise AgentError('Bounded scene mix duration/timeout required.')
    delivery=Delivery(program);music=program.current_output(music_task,'music');voice=program.current_output(voice_task,'voice')
    cues=music['artifact']['records'];lines=voice['artifact']['records'];assets={};sources=[];intervals=[]
    from .specialists import prepare
    for role,body in (('music',music),('voice',voice)):
        prepare(role,{'specialist_v1':True,'project':body['artifact']['project'],'records':body['artifact']['records'],'sources':{},'base':None,'targets':[]})
    for line in lines:
        id=line.get('audio_receipt')
        if not id:raise AgentError('Actual approved dialogue audio receipt missing; a voice plan is not synthesized speech.')
        a=delivery.asset(id)
        if not number(line['start']) or line['start']+a['inspection']['duration']>seconds+.04:raise AgentError('Measured dialogue exceeds scene mix timing.')
        assets[id]=a;sources.append({'receipt':id,'start':line['start'],'duration':a['inspection']['duration'],'gain':0.,'duck':False})
        intervals.append((line['start'],line['start']+a['inspection']['duration']))
    merged=[]
    for begin,end in sorted(intervals):
        if merged and begin<=merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
        else:merged.append((begin,end))
    intervals=merged
    for cue in cues:
        if cue['license']=='unknown' or cue['asset']=='pending' or cue['asset'] not in receipts:raise AgentError('Cue rights and genuine audio receipt required; no substitute signal is composed.')
        id=receipts[cue['asset']];a=delivery.asset(id)
        if a['path']!=cue['asset'] or not any(s['codec_type']=='audio' for s in a['inspection']['streams']):raise AgentError('Cue receipt is not the declared audio asset.')
        if cue['start']+cue['seconds']>seconds or cue['seconds']>a['inspection']['duration']+.04:raise AgentError('Cue exceeds actual asset or scene duration; no silent loop/stretch.')
        assets[id]=a;sources.append({'receipt':id,'start':cue['start'],'duration':cue['seconds'],'gain':cue['gain_db'],'duck':cue['duck_db'] if cue['kind']=='music' and cue['dialogue_present'] else False})
    if not sources:raise AgentError('No genuine source audio to mix.')
    root=program.root/'agent_media/mixes'
    if any(p.is_symlink() for p in (root,*root.parents)):raise AgentError('Unsafe audio mix folder.')
    job=root/uuid4().hex;job.mkdir(parents=True);output=job/'mix.wav';state={'state':'running','music_task':music_task,'voice_task':voice_task,'music_sha256':digest(music),'voice_sha256':digest(voice),'receipts':list(assets),'actual_neural_inference':False,'listening_review_completed':False}
    def save():(job/'receipt.json').write_text(json.dumps(state,indent=2))
    save();start=time.monotonic()
    try:
        cmd=['ffmpeg','-nostdin','-v','error'];filters=[]
        for i,s in enumerate(sources):
            a=assets[s['receipt']];p=media_path(program.store.path,a['path'])
            with p.open('rb') as f:head=f.read(12)
            cmd+=['-protocol_whitelist','file,pipe','-f','mov' if head[4:8]==b'ftyp' else 'wav','-i',str(p)]
            chain=f'[{i}:a]atrim=duration={s["duration"]},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={s["gain"]}dB,adelay={round(s["start"]*1000)}:all=1'
            if s['duck'] is not False:
                for begin,end in intervals:chain+=f",volume={s['duck']}dB:enable='between(t,{begin},{end})'"
            filters.append(chain+f'[a{i}]')
        filters.append(''.join(f'[a{i}]' for i in range(len(sources)))+f'amix=inputs={len(sources)}:normalize=0,apad,atrim=duration={seconds},alimiter=limit=0.95[out]')
        cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le',str(output)]
        with (job/'worker.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,timeout=timeout,check=True)
        for id in assets:delivery.asset(id)
        if digest(program.current_output(music_task,'music'))!=digest(music) or digest(program.current_output(voice_task,'voice'))!=digest(voice):raise AgentError('Cue/voice source changed during mix.')
        from .audio_evaluation import measure
        relative=str(output.relative_to(program.root/'agent_media'));metrics=measure(relative,program.store.path)
        state.update(state='technical_output_validated',output_sha256=sha(output),pcm_metrics=metrics,limiter_applied=True,ducking='Fixed gain reduction during measured dialogue intervals; no claimed artistic mastering or LUFS target.')
        return {'path':relative,'actual_generation':True,'model':'none — receipt-bound FFmpeg audio mix','metadata':state}
    except Exception:state.update(state='failed',error='Scene audio mixing failed; source receipts/partial output retained.');raise
    finally:state['wall_seconds']=round(time.monotonic()-start,3);save()
