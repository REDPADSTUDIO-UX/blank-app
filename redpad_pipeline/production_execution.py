"""Executable cross-department handoffs over approved existing Studio outputs."""
import copy,json,re,unicodedata
from uuid import uuid4
from .agents import AgentError,encode
from .creative import digest
from .offline_media import CATALOG,validate_request

class ProductionOps:
    def __init__(self,program):
        self.p=program
        with program.store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS production_packets(id TEXT PRIMARY KEY,kind TEXT,payload TEXT,sha TEXT);
          CREATE TABLE IF NOT EXISTS production_feedback(id TEXT PRIMARY KEY,payload TEXT,sha TEXT);
        ''')
    def sources(self,tasks):
        result={};pins=[]
        for role,tid in tasks.items():
            body=self.p.current_output(tid,role)
            with self.p.store.tx() as db:t=self.p.store._task(db,tid)
            result[role]=body;pins.append({'role':role,'task':tid,'revision':t['revision'],'artifact_sha256':digest(body['artifact'])})
        return result,pins
    def _save(self,kind,data):
        token=digest([kind,data]);id=token[:32]
        with self.p.store.tx() as db:db.execute('INSERT OR IGNORE INTO production_packets VALUES (?,?,?,?)',(id,kind,encode(data),token))
        return {'id':id,'kind':kind,**data}
    def packet(self,id):
        with self.p.store.tx() as db:r=db.execute('SELECT * FROM production_packets WHERE id=?',(id,)).fetchone()
        if not r:raise AgentError('Unknown production packet.')
        data=json.loads(r['payload'])
        if digest([r['kind'],data])!=r['sha']:raise AgentError('Packet integrity failed.')
        _,pins=self.sources({s['role']:s['task'] for s in data['sources']})
        if data.get('casting_locks'):
            from .casting import Casting
            current={r['character']:r['lock_id'] for r in Casting(self.p).current()}
            if any(current.get(c)!=lock for c,lock in data['casting_locks'].items()):raise AgentError('Recasting invalidated this shot packet.')
        if pins!=data['sources']:raise AgentError('Packet sources changed; regenerate only the affected packet.')
        return {'id':id,'kind':r['kind'],**data}
    def shot(self,tasks,shot_id):
        required={'script','character','art','location','costume','storyboard','performance','cinematographer','motion'}
        if set(tasks) not in (required,required|{'casting'}):raise AgentError('Approved screenplay and all eight shot departments required.')
        bodies,pins=self.sources(tasks)
        def rows(role):return bodies[role]['artifact']['records']
        def one(items,label):
            if len(items)!=1:raise AgentError('Exactly one unambiguous '+label+' required.')
            return copy.deepcopy(items[0])
        board=one([r for r in rows('storyboard') if r['id']==shot_id],'storyboard shot')
        scene=one([s for s in bodies['script']['artifact']['scenes'] if s['id']==board['scene']],'screenplay scene')
        chars={r['id']:r for r in rows('character')};location=one([r for r in rows('location') if r['id']==board['location']],'location')
        if not set(board['characters'])<=chars.keys():raise AgentError('Unknown character identity.')
        performance=[one([r for r in rows('performance') if r['scene']==board['scene'] and r['character']==c and r.get('shot',shot_id)==shot_id],'performance per character') for c in board['characters']]
        camera=one([r for r in rows('cinematographer') if r.get('shot',r['id'])==shot_id and r['scene']==board['scene']],'camera per shot')
        wardrobe=[one([r for r in rows('costume') if r['scene']==board['scene'] and r['character']==c],'costume per character') for c in board['characters']]
        art=one([r for r in rows('art') if board['scene'] in r['scene_ids']],'production design')
        motions=copy.deepcopy([r for r in rows('motion') if r['shot']==shot_id])
        offset=sum(r['seconds'] for r in rows('storyboard') if r['order']<board['order'])
        for motion in motions:motion['shot_local_start']=motion['start']-offset
        if not motions or any(m['character'] not in board['characters'] or not 0<=m['shot_local_start'] or m['shot_local_start']+m['seconds']>board['seconds'] for m in motions):raise AgentError('Motion has no shot, unknown actor, or exceeds shot timing.')
        for act in performance:
            if act['pause_seconds']>board['seconds']:raise AgentError('Performance pause exceeds shot.')
            if any(not isinstance(act.get(k),str) or not act[k].strip() for k in ('objective','tactic','partner_reaction')):raise AgentError('Playable acting objective, tactic and reaction required for shot execution.')
        conflicts=[f for role in required for f in bodies[role].get('findings',[]) if isinstance(f,dict) and f.get('severity') in ('error','blocker')]
        if conflicts:raise AgentError('Resolve approved metadata conflicts before shot execution: '+encode(conflicts))
        actor_refs=[];locks={}
        if 'casting' in tasks:
            from .casting import Casting
            casting=Casting(self.p)
            current={r['character']:r for r in casting.current()}
            for c in board['characters']:
                lock=current.get(c)
                if not lock or lock['task']!=tasks['casting']:raise AgentError('Current Producer casting lock per shot character required.')
                actors=json.loads(lock['payload'])['actors'];actor=one([r for r in actors if r['character']==c],'locked actor')
                actor_refs.append(actor);locks[c]=lock['lock_id']
            for role in ('costume','storyboard','performance','cinematographer','motion'):
                bound={p['character']:p['lock_id'] for p in bodies[role]['artifact'].get('derived',{}).get('casting_identity_locks',[])}
                if any(bound.get(c)!=lock for c,lock in locks.items()):raise AgentError('Shot department '+role+' must consume the exact locked casting identity; legacy metadata does not prove this.')
        return self._save('shot_execution',{'casting_locks':locks,'actors':actor_refs,'sources':pins,'shot':board,'scene':scene,'identities':[chars[c] for c in board['characters']],
           'location':location,'art':art,'costumes':wardrobe,'performance':performance,'camera':camera,'motion':motions,
           'reference_assets':sorted({v for c in board['characters'] for v in chars[c]['references']}|set(location['references'])),
           'technical_requirements':{'identity_lock':False,'lip_sync':False,'physics_simulation':False,'unsupported_controls':'Performance/camera/motion prose is editorial intent until actual model conditioning is verified.'},
           'actual_media_generated':False,'professional_quality_verified':False})
    def queue_video(self,packet_id,engine,request,required_controls=(),evaluation_window=None):
        packet=self.packet(packet_id)
        if packet['kind']!='shot_execution':raise AgentError('Shot execution packet required.')
        validate_request(engine,request)
        if any(CATALOG[engine].get(c) is not True for c in required_controls):raise AgentError('Required conditioning is unsupported; prose is not model control.')
        duration=request['frames']/request['fps']
        if evaluation_window is not None:
            from .specialists import number
            if not isinstance(evaluation_window,dict) or set(evaluation_window)!={'start','seconds'} or not number(evaluation_window['start']) or not number(evaluation_window['seconds'],.01,30) or evaluation_window['start']+evaluation_window['seconds']>packet['shot']['seconds'] or abs(evaluation_window['seconds']-duration)>.001:raise AgentError('Explicit in-shot benchmark window must match native generated duration; it is not a completed long take.')
        elif abs(duration-packet['shot']['seconds'])>1/request['fps']+.001:raise AgentError('Native video duration differs from approved shot; request a targeted timing revision or an explicit short evaluation window, do not stretch silently.')
        prompt=request.get('prompt','')
        if engine=='local-svd' and prompt:raise AgentError('SVD cannot execute text direction. Use an approved image; keep shot guidance outside prompt.')
        data={'operation':'offline_video','engine':engine,'request':dict(request,editorial_guidance={'packet':packet_id,'shot':packet['shot'],'performance':packet['performance'],'camera':packet['camera'],'motion':packet['motion'],'evaluation_window':evaluation_window,'full_shot_completed':False})}
        return self.p.engine.enqueue('video',data,[s['task'] for s in packet['sources']],mode='media',idempotency_key='shot-video:'+digest([packet_id,engine,request,evaluation_window]))
    def voice(self,tasks,mapping,lexicon,lexicon_version,style_map=None):
        if set(tasks)!={'script','voice','character'} or not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}',lexicon_version):raise AgentError('Approved voice/script/identity and versioned pronunciation rules required.')
        from .offline_speech import PRESETS,STYLES
        bodies,pins=self.sources(tasks);characters=bodies['character']['artifact']['records'];names={c['name']:c['id'] for c in characters};lines=[]
        if set(mapping)!={c['id'] for c in characters} or any(v not in PRESETS for v in mapping.values()):raise AgentError('Explicit character-to-documented synthetic preset map required.')
        if not isinstance(lexicon,dict) or any(not isinstance(k,str) or not k.strip() or not isinstance(v,str) or not v.strip() for k,v in lexicon.items()):raise AgentError('Bounded pronunciation dictionary required.')
        expected=[(s['id'],names.get(b['speaker']),b['text']) for s in bodies['script']['artifact']['scenes'] for b in s['beats'] if b['type']=='dialogue']
        supplied=bodies['voice']['artifact']['records']
        if [(r['scene'],r['character'],r['text']) for r in supplied]!=expected:raise AgentError('Voice dialogue/speaker/order differs from approved screenplay.')
        for row in supplied:
            normalized=unicodedata.normalize('NFC',' '.join(row['text'].split()))
            for word,value in sorted(lexicon.items(),key=lambda pair:-len(pair[0])):normalized=re.sub(r'(?<!\w)'+re.escape(word)+r'(?!\w)',lambda _:value,normalized)
            style=(style_map or {}).get(row['character'],row.get('synthesis_style'))
            if style not in STYLES:raise AgentError('Choose supported synthesis_style explicitly; do not pretend arbitrary emotion/pace/pause controls are supported.')
            if len(normalized)>300:raise AgentError('Split long dialogue at an approved sentence/beat boundary before synthesis.')
            lines.append({'id':row['id'],'scene':row['scene'],'character':row['character'],'original':row['text'],'request':{'preset':mapping[row['character']],'style':style,'text':normalized,'seed':42},
                'planned_start':row['start'],'planned_seconds':row['seconds'],'pauses':row['pauses'],'timing_status':'Editorial targets; measured speech and alignment pending. No speed/pause/lip-sync control claimed.'})
        return self._save('voice_execution',{'sources':pins,'lexicon_version':lexicon_version,'lexicon':lexicon,'lines':lines,'listening_review_completed':False,'reference_cloning':False})
    def queue_speech(self,packet_id,line_id):
        p=self.packet(packet_id)
        if p['kind']!='voice_execution':raise AgentError('Voice execution packet required.')
        line=next((r for r in p['lines'] if r['id']==line_id),None)
        if not line:raise AgentError('Unknown approved dialogue segment.')
        return self.p.engine.enqueue('voice',{'operation':'offline_speech','request':line['request']},[s['task'] for s in p['sources']],mode='media',idempotency_key='speech:'+digest([packet_id,line_id]))
    def bind_voice_audio(self,packet_id,line_runs,owner,rights,confirmed=False):
        from .delivery import Delivery
        from .offline_media import digest as media_digest
        p=self.packet(packet_id)
        if p['kind']!='voice_execution' or set(line_runs)!={r['id'] for r in p['lines']}:raise AgentError('Every approved voice segment needs its actual synthesis run.')
        source=next(s['task'] for s in p['sources'] if s['role']=='voice');body=self.p.current_output(source,'voice')
        rows=copy.deepcopy(body['artifact']['records']);deps=[s['task'] for s in p['sources']];delivery=Delivery(self.p)
        validated=[]
        for row in rows:
            spec=next(s for s in p['lines'] if s['id']==row['id']);rid=line_runs[row['id']]
            run=next((r for r in self.p.engine.runs() if r['id']==rid),None)
            if not run or run['mode']!='media':raise AgentError('Owned approved speech run required.')
            output=self.p.current_output(run['task'],'voice');meta=output['artifact'].get('metadata',{})
            if json.loads(run['inputs']).get('request')!=spec['request'] or not {s['task'] for s in p['sources']}<=set(json.loads(run['dependencies'])):raise AgentError('Synthesis settings or source dependencies differ from the approved voice packet.')
            if meta.get('actual_inference_verified') is not True or meta.get('text_sha256')!=media_digest(unicodedata.normalize('NFC',spec['request']['text'])) or meta.get('preset')!=spec['request']['preset']:raise AgentError('Synthesis transcript/preset/inference differs from the approved dialogue packet.')
            deps.append(run['task']);validated.append((row,rid,output['artifact']['path'],meta))
        for row,rid,path,meta in validated:
            row['audio_receipt']=delivery.register(path,owner,rights,confirmed,run_id=rid)
            row['measured_seconds']=delivery.asset(row['audio_receipt'])['inspection']['duration']
        data={'specialist_v1':True,'project':body['artifact']['project'],'records':rows,'sources':{'voice':{'$from':source,'path':['artifact']}},'base':{'$from':source,'path':['artifact']},'targets':[r['id'] for r in rows]}
        return self.p.engine.enqueue('voice',data,list(dict.fromkeys(deps)),mode='software',idempotency_key='measured-voice:'+digest([packet_id,line_runs]))
    def feedback(self,task,revision,reviewer,expertise,category,anchor,observation,decision,*,provenance='human',dataset_consent=False):
        if provenance not in ('human','simulation') or category not in ('creative','visual','listening','editing','technical') or decision not in ('prefer','reject','correct','uncertain'):raise AgentError('Attributed feedback classification required.')
        if not all(isinstance(x,str) and x.strip() for x in (reviewer,expertise,observation)):raise AgentError('Actual reviewer, relevant expertise and observation required.')
        with self.p.store.tx() as db:
            t=self.p.store._task(db,task);r=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,revision)).fetchone()
        if not r or revision!=t['revision']:raise AgentError('Feedback must identify a current output version; old notes remain archived.')
        body=json.loads(json.loads(r[0])['summary']);text=encode(body['artifact'])
        if not isinstance(anchor,dict):raise AgentError('Source-specific feedback anchor required.')
        if body['artifact'].get('path') and category in ('visual','listening','editing') and 'quote' in anchor:raise AgentError('Actual media feedback requires an asset hash and image region/media timestamp, not a quotation from metadata.')
        if 'quote' in anchor:
            if not isinstance(anchor['quote'],str) or len(anchor['quote'].strip())<4 or anchor['quote'] not in text:raise AgentError('Feedback quotation is absent from this exact source.')
        else:
            path=body['artifact'].get('path')
            if not path or anchor.get('asset')!=path:raise AgentError('Media feedback must bind the actual output path.')
            from .offline_media import media_path,sha
            asset=media_path(self.p.store.path,path)
            if anchor.get('sha256')!=sha(asset):raise AgentError('Media feedback hash differs.')
            if asset.suffix.lower() in ('.png','.jpg','.jpeg'):
                from PIL import Image
                with Image.open(asset) as im:im.verify()
                region=anchor.get('region')
                if not isinstance(region,list) or len(region)!=4 or any(type(x) not in (int,float) or not 0<=x<=1 for x in region) or not region[0]<region[2] or not region[1]<region[3]:raise AgentError('Image feedback requires a normalized nonempty region.')
            else:
                from .specialist_inspection import inspect_clip
                duration=inspect_clip(path,self.p.store.path)['duration']
                if type(anchor.get('seconds')) not in (int,float) or not 0<=anchor['seconds']<=duration:raise AgentError('Valid inspected media timestamp required.')
        value={'id':uuid4().hex,'task':task,'revision':revision,'source_sha256':digest(body),'reviewer':reviewer,'expertise':expertise,'category':category,'anchor':anchor,'observation':observation,'decision':decision,
               'provenance':provenance,'dataset_consent':dataset_consent is True,'training_performed':False,'grants_approval':False}
        with self.p.store.tx() as db:db.execute('INSERT INTO production_feedback VALUES (?,?,?)',(value['id'],encode(value),digest(value)))
        return value
    def feedback_export(self):
        with self.p.store.tx() as db:records=db.execute('SELECT * FROM production_feedback ORDER BY rowid').fetchall()
        rows=[]
        for r in records:
            p=json.loads(r['payload'])
            if digest(p)!=r['sha']:raise AgentError('Feedback integrity failed.')
            rows.append(p)
        return {'schema_version':1,'records':rows,'future_dataset_candidates':[r['id'] for r in rows if r['provenance']=='human' and r['dataset_consent']],
                'dataset_license_and_training_approval_pending':True,'weight_training_performed':False}
    def queue_promotion(self,script_task,delivery_task,qc_task,*,review_date):
        """Truthful source-derived package; no invented trailer/thumbnail/metrics."""
        from .offline_media import media_path,sha
        script=self.p.current_output(script_task,'script');delivery=self.p.current_output(delivery_task,'editing');qc=self.p.current_output(qc_task,'qc')
        with self.p.store.tx() as db:q=self.p.store._task(db,qc_task);d=self.p.store._task(db,delivery_task)
        if not any(r['id']==delivery_task and r['revision']==d['revision'] for r in json.loads(q['refs'])):raise AgentError('QC must bind this exact delivery version, not an old edit plan.')
        if any(f.get('severity') in ('error','blocker') for f in qc.get('findings',[]) if isinstance(f,dict)):raise AgentError('Resolve QC delivery blockers before promotional preparation.')
        a=delivery['artifact'];path=media_path(self.p.store.path,a.get('path'));metadata=a.get('metadata',{})
        if metadata.get('state')!='technical_output_validated' or metadata.get('output_sha256')!=sha(path):raise AgentError('Current technically inspected actual delivery required; no plan/test-pattern-as-film claim.')
        if metadata.get('evaluation_only') is True:raise AgentError('Evaluation fixtures cannot be promoted as a finished film.')
        s=script['artifact'];title=s['title'];opening=next(b['text'] for b in s['scenes'][0]['beats'] if b['type']=='action')
        row={'id':'source-promo','audience':'বাংলা নাটকের দর্শক — owner targeting review pending','genre':'Bangladeshi drama','title_bn':title,'title_en':title,
             'description_bn':opening,'description_en':opening,'keywords':['বাংলা নাটক'],'thumbnail':'Actual source frame selection and visual review pending; no generated image claimed',
             'campaign':'Original source-based preparation only','release_date':review_date,'trailer':'Actual delivery source: '+a['path']+'; trailer edit not generated','metrics':[],
             'delivery_sha256':sha(path),'creative_marketing_review_pending':True,'translation_pending':True}
        data={'specialist_v1':True,'project':self.p.project_id,'records':[row],
              'sources':{'screenplay':{'$from':script_task,'path':['artifact']},'editing':{'$from':delivery_task,'path':['artifact']},'qc':{'$from':qc_task,'path':['artifact']}},'base':None,'targets':[]}
        return self.p.engine.enqueue('growth',data,[script_task,delivery_task,qc_task],mode='software',idempotency_key='source-promotion:'+digest([script_task,delivery_task,qc_task,sha(path)]))
    def queue_readonly_release(self,growth_task,channel_id,channel_name):
        body=self.p.current_output(growth_task,'growth');rows=body['artifact']['records']
        if len(rows)!=1:raise AgentError('Select one approved source-bound promotional package.')
        from .youtube import channel_id as validate_channel
        validate_channel(channel_id)
        r=rows[0]
        if not r.get('delivery_sha256'):raise AgentError('Promotion has no actual delivery binding.')
        row={'id':'prepared-release','channel_id':channel_id,'channel_name':channel_name,'title':r['title_bn'],'description':r['description_bn'],'keywords':r['keywords'],
             'thumbnail':'pending','video':'pending','action':'prepare','oauth_scope':'https://www.googleapis.com/auth/youtube.readonly','connection':'unverified',
             'checks':{'media_qc':False,'rights':False,'owner_review':False},'source_delivery_sha256':r['delivery_sha256']}
        data={'specialist_v1':True,'project':self.p.project_id,'records':[row],'sources':{'growth':{'$from':growth_task,'path':['artifact']}},'base':None,'targets':[]}
        return self.p.engine.enqueue('youtube',data,[growth_task],mode='software',idempotency_key='readonly-release:'+digest([growth_task,channel_id]))
