"""Department-specific derivations over supplied production data."""
from .specialists import need,text,number,records,finding


def process(key,rows,data):
    derived={};findings=[]
    if key=='storyboard':
        from .storyboard import draft_board,validate_board,script_hash
        records(rows,['id','scene','order','action','purpose','composition','characters','location','camera','performance','seconds'])
        need([r['order'] for r in rows]==list(range(1,len(rows)+1)),'Shot order must be consecutive.')
        for r in rows:
            need(number(r['seconds'],2,20) and type(r['seconds']) is int,'Shot duration must be 2–20 whole seconds.')
            need(isinstance(r['characters'],list) and r['characters'],'Shot characters required.')
        script=data['sources'].get('screenplay')
        if script:
            scenes=script.get('scenes',script.get('screenplay',{}).get('scenes',[]))
            ids={str(s.get('id',s.get('number'))) for s in scenes}
            need(all(str(r['scene']) in ids for r in rows),'Shot references unknown screenplay scene.')
        board=draft_board(1,data['project'],'Manual coverage draft.','16:9')
        board['script_hash']=script_hash('\n'.join(r['action'] for r in rows))
        # Preserve the existing Studio schema while using explicit supplied shot decisions.
        template=board['shots'][0];board['shots']=[]
        for r in rows:
            shot=dict(template,number=r['order'],narration=r['action'],visual=r['composition'],seconds=r['seconds'],notes=r['purpose'],reference_path='')
            board['shots'].append(shot)
        validate_board(board)
        derived.update(studio_board=board,reference_status='Not generated',video_requests=[dict(shot=r['id'],scene=r['scene'],prompt=r['action'],seconds=r['seconds'],characters=r['characters'],location=r['location']) for r in rows])
    elif key=='performance':
        records(rows,['id','scene','character','emotion_from','emotion_to','transition_reason','intensity','subtext','gaze','body_language','pause_seconds','blocking','micro_expression'])
        states={}
        for r in rows:
            need(number(r['intensity'],1,10) and number(r['pause_seconds'],0,30),'Invalid acting intensity/pause.')
            if r['character'] in states and states[r['character']]!=r['emotion_from']:
                findings.append(finding(r['id'],'emotional_transition',states[r['character']],r['emotion_from'],key))
            states[r['character']]=r['emotion_to']
            if r['intensity']>7:findings.append(finding(r['id'],'review_restraint','naturalistic restraint',r['intensity'],key,'warning'))
        derived['final_emotions']=states
    elif key=='cinematographer':
        records(rows,['id','scene','lens_mm','height_m','angle','movement','lighting','exposure','color','framing','axis_side','screen_direction','axis_reset','purpose'])
        axes={}
        for r in rows:
            need(number(r['lens_mm'],8,300) and number(r['height_m'],0,30),'Invalid lens/camera height.')
            need(r['axis_side'] in ('A','B','neutral') and type(r['axis_reset']) is bool,'Invalid axis specification.')
            prev=axes.get(r['scene'])
            if prev and r['axis_side'] not in (prev,'neutral') and not r['axis_reset']:
                findings.append(finding(r['id'],'axis_crossing',prev,r['axis_side'],key,'warning'))
            if r['axis_side']!='neutral':axes[r['scene']]=r['axis_side']
        derived['scene_axes']=axes
    elif key=='motion':
        records(rows,['id','shot','character','from_pose','to_pose','start','seconds','contact','object','object_before','object_after','gravity','collision','change_reason'])
        poses={};objects={};ends={}
        transitions={'standing':{'standing','walking','sitting'},'walking':{'walking','standing','sitting'},'sitting':{'sitting','standing'}}
        for r in rows:
            need(number(r['start']) and number(r['seconds'],0.01,30),'Invalid motion timing.')
            need(r['from_pose'] in transitions and r['to_pose'] in transitions,'Unknown posture.')
            if r['to_pose'] not in transitions[r['from_pose']]:findings.append(finding(r['id'],'impossible_pose_transition',sorted(transitions[r['from_pose']]),r['to_pose'],key))
            if r['character'] in poses and poses[r['character']]!=r['from_pose']:findings.append(finding(r['id'],'pose_continuity',poses[r['character']],r['from_pose'],key))
            if r['start']<ends.get(r['character'],0):findings.append(finding(r['id'],'overlapping_body_actions',ends[r['character']],r['start'],key))
            if r['to_pose']=='sitting' and r['contact']=='none':findings.append(finding(r['id'],'missing_support','seat contact',r['contact'],key))
            if r['object'] in objects and objects[r['object']]!=r['object_before']:findings.append(finding(r['id'],'object_permanence',objects[r['object']],r['object_before'],key))
            if r['object_before']!=r['object_after'] and r['change_reason']=='none':findings.append(finding(r['id'],'unexplained_object_change',r['object_before'],r['object_after'],key))
            if r['gravity']!='normal' or r['collision']!='no_penetration':findings.append(finding(r['id'],'physical_constraint','normal gravity/no penetration',[r['gravity'],r['collision']],key,'warning'))
            poses[r['character']]=r['to_pose'];objects[r['object']]=r['object_after'];ends[r['character']]=r['start']+r['seconds']
        derived.update(final_poses=poses,physics_simulated=False)
    elif key=='continuity':
        records(rows,['id','episode','scene','entity','attribute','value','change_reason','affected_shots'])
        state={};last_episode=0
        for r in rows:
            need(type(r['episode']) is int and r['episode']>=last_episode,'Continuity records must be in episode order.')
            need(isinstance(r['affected_shots'],list),'Affected shots list required.')
            token=(r['entity'],r['attribute']);old=state.get(token)
            if old is not None and old!=r['value'] and r['change_reason']=='none':findings.append(finding(r['id'],'unexplained_'+r['attribute'],old,r['value'],key))
            state[token]=r['value'];last_episode=r['episode']
        derived.update(state=[dict(entity=k[0],attribute=k[1],value=v) for k,v in state.items()],affected_shots=sorted({s for r in rows if any(f['record']==r['id'] for f in findings) for s in r['affected_shots']}))
    else:
        from .specialist_media import process as media_process
        return media_process(key,rows,data)
    return derived,findings


def screenplay_breakdown(screenplay):
    """Deterministic coverage draft from actual approved scene content, no image claims.

    Long scenes receive bounded coverage slots carrying the original action. Shot
    composition still needs Director review; generated reference IDs are placeholders
    to map to the approved Character/Location Bibles before production.
    """
    import hashlib,math
    need(isinstance(screenplay,dict) and isinstance(screenplay.get('scenes'),list),'Structured screenplay scenes required.')
    rows=[]
    for scene in screenplay['scenes']:
        need(isinstance(scene,dict) and text(scene.get('id')) and number(scene.get('seconds'),2,1600),'Scene ID and bounded timing required.')
        seconds=scene['seconds'];need(type(seconds) is int,'Whole scene seconds required.')
        count=math.ceil(seconds/20);quotient,remainder=divmod(seconds,count)
        actions=[b['text'] for b in scene.get('beats',[]) if b.get('type')=='action' and text(b.get('text'))]
        need(actions,'Visual action required for shot breakdown.')
        names=[b['speaker'] for b in scene.get('beats',[]) if b.get('type')=='dialogue' and text(b.get('speaker'))]
        if not names:names=[c['name'] for c in screenplay.get('characters',[]) if text(c.get('name'))]
        need(names,'Scene character identities required.')
        ids=list(dict.fromkeys('char_'+hashlib.sha256(name.encode()).hexdigest()[:10] for name in names))
        location='loc_'+hashlib.sha256(scene['location'].encode()).hexdigest()[:10]
        for n in range(count):
            rows.append(dict(id=scene['id']+'-shot'+str(n+1),scene=scene['id'],order=len(rows)+1,
               action=actions[min(n,len(actions)-1)],purpose=scene.get('objective','Review scene objective'),
               composition='Director composition review required',characters=ids,location=location,camera='Static',
               performance=scene.get('performance','Naturalistic performance review required'),seconds=quotient+(n<remainder)))
    need(1<=len(rows)<=80,'Split screenplay into at most 80 shot slots per board.')
    return rows
