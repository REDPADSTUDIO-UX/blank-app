"""Twenty executable department preparation/validation workflows.

These functions operate on supplied creative data. They never pretend to invent
stories, inspect unseen footage, or generate media. Real inference is separate.
"""
import copy
import math
import json
from pathlib import Path
from .agents import AgentError, AGENTS, encode, nonempty
from .director import validate as validate_direction
from .screenwriter import validate as validate_screenplay, render as render_screenplay
from .storyboard import draft_board, validate_board

# Each record is a usable department artifact, not an unconstrained text blob.
FIELDS = {
 'story': ('beats', ['id','premise','cause','consequence','character_arc','episode']),
 'character': ('characters',['id','name','appearance','identity','reference','continuity']),
 'art': ('designs',['id','palette','set','props','style']),
 'location': ('locations',['id','architecture','geography','layout','reference']),
 'costume': ('wardrobe',['id','scene','character','outfit','reference','change_reason']),
 'performance': ('beats',['id','scene','character','emotion','intensity','blocking','micro_expression']),
 'cinematographer': ('shots',['id','scene','lens_mm','framing','movement','lighting','axis']),
 'motion': ('actions',['id','shot','body_motion','object_interaction','constraints','qa_criterion']),
 'video': ('requests',['id','shot','prompt','reference','seconds','fps','width','height']),
 'voice': ('lines',['id','scene','speaker','text','pronunciation','emotion','start','seconds']),
 'continuity': ('observations',['id','scene','entity','attribute','value','change_reason']),
 'music': ('cues',['id','scene','kind','start','seconds','purpose','asset','review_criterion']),
 'editing': ('clips',['id','shot','start','seconds','video','audio','subtitle','transition']),
 'growth': ('packages',['id','title','description','keywords','thumbnail_brief','campaign']),
 'youtube': ('releases',['id','channel_id','title','description','video_reference','approval_note']),
}
NUMERIC = {'seconds','fps','width','height','lens_mm','intensity','start'}


def require(value, fields):
    if not isinstance(value,dict) or set(value)!=set(fields):
        raise AgentError('Required fields: '+', '.join(fields))


def validate_records(key, data):
    label,fields=FIELDS[key]
    require(data,['project',label])
    if not nonempty(data['project']): raise AgentError('Project name required.')
    rows=data[label]
    if not isinstance(rows,list) or not 1 <= len(rows) <= 200:
        raise AgentError('Supply 1–200 department records.')
    ids=set()
    for row in rows:
        require(row,fields)
        for field in fields:
            v=row[field]
            if field in NUMERIC:
                if type(v) not in (int,float) or not math.isfinite(v) or v<0 or (field!='start' and v==0):
                    raise AgentError(field+' must be a finite valid number.')
            elif not nonempty(v): raise AgentError(field+' must be non-empty text; use "none" when intentionally absent.')
        if row['id'] in ids: raise AgentError('Duplicate record ID.')
        ids.add(row['id'])
        if key=='performance' and row['intensity']>10: raise AgentError('Intensity must be 1–10.')
        if key=='video' and (row['seconds']>30 or row['fps']>60 or max(row['width'],row['height'])>4096):
            raise AgentError('Video request exceeds safe test limits (30s, 60fps, 4096px).')
        if key=='video' and any(type(row[f]) is not int for f in ('fps','width','height')):
            raise AgentError('Frame rate and dimensions must be integers.')
        if key=='music' and row['kind'] not in ('music','sfx','ambience','foley'):
            raise AgentError('Unknown sound cue type.')
    return copy.deepcopy(rows)


def prepare(key, data, upstream=None):
    """Pure deterministic execution: validate, normalize, derive useful metadata."""
    if key not in AGENTS: raise AgentError('Unknown department.')
    encode(data)
    upstream=upstream or []
    output={'agent':key,'artifact_type':AGENTS[key]['output_contract']['kind'],
            'provenance':'software','model_inference':False,'media_generated':False,
            'human_review_required':True,'findings':[],'upstream':upstream}
    if key=='director':
        require(data,['plan','seconds'])
        output['artifact']=validate_direction(copy.deepcopy(data['plan']),data['seconds'])
    elif key=='script':
        require(data,['screenplay','seconds'])
        problems=validate_screenplay(data['screenplay'],data['seconds'])
        if problems: raise AgentError('; '.join(problems))
        output['artifact']={'screenplay':copy.deepcopy(data['screenplay']),'formatted':render_screenplay(data['screenplay'])}
    elif key=='storyboard':
        require(data,['content_id','title','script','ratio'])
        if type(data['content_id']) is not int or data['content_id']<=0 or not nonempty(data['title']) or not nonempty(data['script']):
            raise AgentError('Storyboard content, title and script required.')
        if data['ratio'] not in ('16:9','9:16'): raise AgentError('Unsupported storyboard ratio.')
        board=draft_board(data['content_id'],data['title'],data['script'],data['ratio'])
        validate_board(board)
        output['artifact']=board
        output['findings'].append('Deterministic shot draft; Director must review composition and pacing.')
    elif key=='qc':
        require(data,['subject_agent','checks'])
        if data['subject_agent'] not in AGENTS or data['subject_agent']=='qc': raise AgentError('QC cannot review itself.')
        if not isinstance(data['checks'],list) or not data['checks']: raise AgentError('Evidence checks required.')
        findings=[]
        for check in data['checks']:
            require(check,['criterion','result','evidence','revision'])
            if check['result'] not in ('pass','fail','unverified') or not all(nonempty(check[k]) for k in ('criterion','evidence','revision')):
                raise AgentError('Checks require evidence and actionable revision instructions.')
            if check['result']!='pass': findings.append(copy.deepcopy(check))
        output['artifact']={'checks':copy.deepcopy(data['checks']),'recommendation':'Revision Required' if findings else 'Recommend owner review',
                            'creative_quality_verified':False}
        output['findings']=findings
    elif key=='production_manager':
        require(data,['project','jobs'])
        if not nonempty(data['project']) or not isinstance(data['jobs'],list): raise AgentError('Production project/jobs required.')
        from .readiness import inspect_resources
        states={}
        for job in data['jobs']:
            require(job,['id','state'])
            if not all(nonempty(v) for v in job.values()): raise AgentError('Invalid production job.')
            states[job['state']]=states.get(job['state'],0)+1
        output['artifact']={'project':data['project'],'job_counts':states,'resources':inspect_resources(probe=False)}
    else:
        rows=validate_records(key,data)
        output['artifact']={'project':data['project'],FIELDS[key][0]:rows}
        if key in ('voice','music','editing'):
            rows.sort(key=lambda r:(r['start'],r['id']))
            output['artifact']['duration_seconds']=max(r['start']+r['seconds'] for r in rows)
        if key=='editing':
            for left,right in zip(rows,rows[1:]):
                if right['start']<left['start']+left['seconds']:
                    output['findings'].append({'clip':right['id'],'issue':'Overlapping edit clips; review intended transition.'})
            output['artifact']['render_status']='Not rendered; validated asset ingestion and existing drama_finish required.'
        if key=='continuity':
            seen={}
            for row in rows:
                token=(row['entity'],row['attribute'])
                if token in seen and seen[token]!=row['value'] and row['change_reason'].lower() in ('none','unknown','নেই'):
                    output['findings'].append({'record':row['id'],'issue':'Unexplained continuity change','previous':seen[token],'current':row['value']})
                seen[token]=row['value']
        if key in ('video','voice'):
            output['artifact']['generation_status']='Request prepared only; no media generated.'
        if key=='youtube':
            import re
            if any(not re.fullmatch(r'UC[A-Za-z0-9_-]{22}',r['channel_id']) for r in rows):
                raise AgentError('Valid YouTube channel ID required.')
            output['artifact']['release_status']='Preparation only — no upload, scheduling, publishing or channel mutation.'
            output['artifact']['oauth_scope']='https://www.googleapis.com/auth/youtube.readonly'
    return output


def contract(key):
    examples=Path(__file__).with_name('department_examples.json')
    if examples.is_file():
        return json.loads(examples.read_text())[key]
    if key in FIELDS:
        label,fields=FIELDS[key]
        return {'project':'Project name',label:[{f:(1 if f in NUMERIC else 'none') for f in fields}]}
    return {'director':{'plan':{},'seconds':30},'script':{'screenplay':{},'seconds':30},
            'storyboard':{'content_id':1,'title':'দরজা','script':'রাফি দরজার সামনে দাঁড়ায়।','ratio':'16:9'},
            'qc':{'subject_agent':'script','checks':[{'criterion':'Visual action first','result':'unverified','evidence':'Needs screenplay review','revision':'Inspect opening beat'}]},
            'production_manager':{'project':'দরজা','jobs':[]}}[key]
