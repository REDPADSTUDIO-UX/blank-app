"""Media request contracts, not generated film/audio."""
import re
import unicodedata
from pathlib import PurePosixPath
from .specialists import need,text,number,records,finding

PROVIDERS={
 'local-svd':dict(modes=['image_to_video'],installed_adapter=True,requires=['local checkpoint','torch/diffusers','CUDA GPU'],reference_control='single_image'),
 'wan-local':dict(modes=['text_to_video','image_to_video'],installed_adapter=True,requires=['approved Wan2.2 TI2V 5B local adapter','checkpoint','compatible GPU'],reference_control='unverified'),
 'ltx-local':dict(modes=['text_to_video','image_to_video'],installed_adapter=True,requires=['approved LTX 0.9.5 local adapter','checkpoint','compatible GPU'],reference_control='unverified'),
 'bengali-tts-local':dict(modes=['speech'],installed_adapter=True,requires=['approved local Indic Parler-TTS backend','voice rights/reference'],reference_control='unverified')}


def asset(value, pending=True):
    need(text(value),'Asset reference required.')
    if pending and value=='pending':return
    path=PurePosixPath(value)
    need(not path.is_absolute() and '..' not in path.parts and ':' not in value and '\\' not in value,'Only isolated relative asset references accepted.')


def process(key,rows,data):
    derived={};findings=[]
    if key=='video':
        records(rows,['id','shot','provider','mode','prompt','reference','characters','seconds','fps','width','height','seed'])
        for r in rows:
            need(r['provider'] in PROVIDERS and r['provider']!='bengali-tts-local','Unknown video provider.')
            provider=PROVIDERS[r['provider']];need(r['mode'] in provider['modes'],'Unsupported provider capability.')
            need(number(r['seconds'],0.1,30) and type(r['fps']) is int and 1<=r['fps']<=60,'Invalid video duration/fps.')
            need(all(type(r[k]) is int and 64<=r[k]<=4096 and r[k]%2==0 for k in ('width','height')),'Even video dimensions 64–4096 required.')
            need(type(r['seed']) is int and 0<=r['seed']<=2147483647 and isinstance(r['characters'],list),'Seed/character references invalid.')
            asset(r['reference'])
            if r['mode']=='image_to_video' and r['reference']=='pending':findings.append(finding(r['id'],'missing_reference','approved reference image','pending',key,'blocker'))
        derived.update(provider_capabilities={r['provider']:PROVIDERS[r['provider']] for r in rows},job_state='Prepared — not generated',
                       execution_interface='SVD retains its legacy native adapter; Wan/LTX use digest-pinned owned local inference jobs. Availability/actual inference are separate.',qc_required=True)
    elif key=='voice':
        records(rows,['id','scene','speaker','character','text','lexicon','emotion','pace_wpm','start','seconds','pauses','reference'])
        speakers={};cues=[]
        for r in rows:
            need(text(r['text']) and isinstance(r['lexicon'],dict),'Dialogue and pronunciation dictionary required.')
            need(number(r['pace_wpm'],50,250) and number(r['start']) and number(r['seconds'],0.1,300),'Invalid speech pacing/timing.')
            need(isinstance(r['pauses'],list) and all(number(p,0,30) for p in r['pauses']) and sum(r['pauses'])<r['seconds'],'Pauses exceed dialogue duration.')
            need(r['speaker'] not in speakers or speakers[r['speaker']]==r['character'],'Speaker identity remapped.')
            speakers[r['speaker']]=r['character'];asset(r['reference'])
            normalized=unicodedata.normalize('NFC',' '.join(r['text'].split()))
            spoken=normalized
            for word,replacement in sorted(r['lexicon'].items(),key=lambda item:-len(item[0])):
                need(text(word) and text(replacement),'Pronunciation entries must be nonempty text.')
                spoken=re.sub(r'(?<!\w)'+re.escape(word)+r'(?!\w)',lambda m:replacement,spoken)
            cues.append(dict(id=r['id'],speaker=r['speaker'],original=normalized,synthesis_text=spoken,start=r['start'],end=r['start']+r['seconds'],alignment_status='Estimated timing only; no phoneme alignment'))
        derived.update(speaker_map=speakers,lip_sync_cues=cues,backend=PROVIDERS['bengali-tts-local'],generation_status='No audio generated')
    elif key=='music':
        records(rows,['id','scene','kind','start','seconds','emotion','motif','purpose','asset','license','gain_db','duck_db','dialogue_present','review'])
        for r in rows:
            need(r['kind'] in ('music','sfx','foley','ambience'),'Unknown cue kind.')
            need(number(r['start']) and number(r['seconds'],0.01,3600),'Invalid cue timing.')
            need(number(r['gain_db'],-60,0) and number(r['duck_db'],-30,0) and type(r['dialogue_present']) is bool,'Invalid mixing constraints.')
            asset(r['asset']);need(r['license'] in ('original','public_domain','licensed','unknown'),'License classification required.')
            if r['license']=='unknown':findings.append(finding(r['id'],'license_unverified','verified usage rights','unknown',key,'blocker'))
            if r['dialogue_present'] and r['kind']=='music' and r['duck_db']==0:findings.append(finding(r['id'],'dialogue_masking','review ducking','no ducking',key,'warning'))
        derived.update(cue_sheet=sorted(rows,key=lambda r:r['start']),duration=max(r['start']+r['seconds'] for r in rows),composition_status='Cue metadata only')
    elif key=='editing':
        records(rows,['id','shot','order','start','seconds','source_in','source_seconds','video','audio','subtitle','subtitle_start','subtitle_end','transition','color','vfx','export_profile'])
        need([r['order'] for r in rows]==list(range(1,len(rows)+1)),'Edit order must be consecutive.')
        end=0
        for r in rows:
            need(all(number(r[k]) for k in ('start','source_in','source_seconds','subtitle_start','subtitle_end')) and number(r['seconds'],0.01,3600),'Invalid timeline number.')
            need(abs(r['start']-end)<.001,'Timeline must be contiguous without overlapping cuts.')
            need(r['source_in']+r['seconds']<=r['source_seconds']+.001,'Clip exceeds source duration.')
            need(r['start']<=r['subtitle_start']<=r['subtitle_end']<=r['start']+r['seconds'],'Subtitle outside clip.')
            need(r['transition'] in ('cut','fade') and r['export_profile'] in ('1080p24','720p24','test256p8'),'Unsupported export/transition.')
            asset(r['video']);asset(r['audio']);end=r['start']+r['seconds']
            if 'pending' in (r['video'],r['audio']):findings.append(finding(r['id'],'missing_media','validated local media','pending',key,'blocker'))
        derived.update(duration_seconds=end,edl=[dict(shot=r['shot'],start=r['start'],end=r['start']+r['seconds'],source_in=r['source_in']) for r in rows],
                       render_operation='render_quality_project',export_path=None,render_status='Plan only — approved isolated quality project required')
    else:
        from .specialist_operations import process as operations
        return operations(key,rows,data)
    return derived,findings
