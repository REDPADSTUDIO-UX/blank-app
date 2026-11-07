"""Bounded scene generation → unchanged screenplay assembly → existing approval.
Uses the existing raw-response StagedDraft ledger; no model downloads/fallback.
"""
import copy,json,re
from .agents import AgentError
from .creative import digest,prepare_creative
from .production_execution import ProductionOps
from .staged_writing import StagedDraft,scene_schema,digest as stage_digest
from .screenwriter import WritingError

class EpisodeScenes:
    def __init__(self,program,episode,version='v1'):
        if type(episode) is not int or not 1<=episode<=100:raise AgentError('Valid episode required.')
        if not isinstance(version,str) or not re.fullmatch(r'[a-z0-9_-]{1,40}',version):raise AgentError('Safe immutable episode draft version required.')
        self.p=program;self.episode=episode;self.folder=program.root/'episode_drafts'/('ep'+str(episode))/version
        if any(p.is_symlink() for p in (self.folder,*self.folder.parents)):raise AgentError('Unsafe episode draft path.')
        self.folder.mkdir(parents=True,exist_ok=True)
    def create(self,tasks,scene_specs,characters,ending_setup_scenes):
        if set(tasks)!={'story','director'}:raise AgentError('Approved compiled season and Director review required.')
        from .story_bridge import StoryBridge
        sequence_task=StoryBridge(self.p)._linked('bridge:sequences:'+str(self.episode))
        bodies,pins=ProductionOps(self.p).sources(tasks)
        sequence=self.p.current_output(sequence_task,'story');rows=sequence['artifact']['records']
        with self.p.store.tx() as db:seq=self.p.store._task(db,sequence_task)
        pins.append({'role':'sequence','task':sequence_task,'revision':seq['revision'],'artifact_sha256':digest(sequence['artifact'])})
        expected=[sid for r in rows for sid in r['scene_ids']]
        if not isinstance(scene_specs,list) or [s.get('id') for s in scene_specs]!=expected or len(set(expected))!=len(expected):raise AgentError('Approved ordered sequence scene coverage required.')
        if any('beats' in s or not re.fullmatch(r'[a-z0-9_-]{1,45}',s['id']) for s in scene_specs):raise AgentError('Scene metadata only; safe IDs and no prewritten beats in model task.')
        from .creative import texts
        for i,s in enumerate(scene_specs,1):
            texts(s,['heading','location','time','objective','obstacle','turn','consequence','subtext','performance','transition'])
            texts(s.get('sound'),['music','sfx'])
            if s.get('number')!=i or not s['heading'].startswith(('INT.','EXT.','INT./EXT.')) or type(s.get('seconds')) is not int or not 1<=s['seconds']<=600:raise AgentError('Valid numbered/timed scene metadata required before saving the immutable plan.')
        duration={s['id']:s['seconds'] for s in scene_specs}
        if any(sum(duration[sid] for sid in r['scene_ids'])!=r['seconds'] for r in rows):raise AgentError('Scene specs must preserve approved sequence timing.')
        season=bodies['story']['artifact'];ep=season['episodes'][self.episode-1]
        if not characters or {c['name'] for c in characters}!={c['name'] for c in season['characters'] if c['name'] in {x['name'] for x in characters}} or any(not c.get('voice') for c in characters):raise AgentError('Known season characters and explicit distinct voice specifications required.')
        if not ending_setup_scenes or not set(ending_setup_scenes)<=set(expected):raise AgentError('Explicit ending setup scene references required.')
        data={'sources':pins,'sequence_task':sequence_task,'sequence_source':sequence['artifact'],'scene_specs':scene_specs,'characters':characters,
              'episode_source':ep,'title':self.p.summary()['project']['title'],'ending_setup_scenes':ending_setup_scenes,'professional_quality_verified':False,'plan_provenance':'owner-supplied structural scene specs; not model-generated screenplay'}
        path=self.folder/'plan.json'
        if path.exists():
            if json.loads(path.read_text())!=data:raise AgentError('Draft plan is immutable; use a new project/version after targeted upstream revision.')
        else:path.write_text(json.dumps(data,ensure_ascii=False,indent=2))
        return data
    def plan(self):
        path=self.folder/'plan.json'
        if path.is_symlink():raise AgentError('Unsafe episode plan.')
        data=json.loads(path.read_text())
        for pin in data['sources']:
            body=self.p.current_output(pin['task'])
            with self.p.store.tx() as db:t=self.p.store._task(db,pin['task'])
            if t['revision']!=pin['revision'] or digest(body['artifact'])!=pin['artifact_sha256']:raise AgentError('Episode draft source is stale; preserve files and start a revised source-bound draft.')
        return data
    def run_scene(self,scene_id,*,model,complete=None,think=None):
        plan=self.plan();spec=next((s for s in plan['scene_specs'] if s['id']==scene_id),None)
        if not spec:raise AgentError('Unknown approved scene.')
        if complete is None:
            from .model_routing import ModelRoutes,inventory
            approved=next((m for m in ModelRoutes(self.p.store).models() if m['name']==model and m['approved']),None)
            if not approved or inventory().get(model)!=approved['digest']:raise AgentError('Exact installed/approved local model required; no automatic restore/download.')
            if model.startswith(('qwen3:4b','qwen3.5:4b','gemma3:4b')):raise AgentError('Unchanged weak 4B full-scene repetitions blocked. Use an explicitly justified isolated fix experiment or an approved stronger candidate.')
            policy=ModelRoutes(self.p.store).policy('script')
            candidate=next((r for r in (policy or {}).get('models',[]) if r['name']==model),{})
            if 'think' in candidate:
                if think is not None and think!=candidate['think']:raise AgentError('Scene thinking mode contradicts the pinned route.')
                think=candidate['think']
            if model.startswith('qwen3.5:') and think is None:raise AgentError('Pin an explicit reviewed Qwen3.5 thinking mode before a bounded scene; do not repeat the known default-thinking truncation.')
        names=[c['name'] for c in plan['characters']];schema=scene_schema(names);schema['properties']['heading']={'type':'string','enum':[spec['heading']]}
        # The old micro-pilot's 90-character action cap rejected a legitimate
        # complete visual beat. Keep a bounded scene budget without truncating
        # or manually editing the preserved model response.
        for branch in schema['properties']['beats']['items']['oneOf']:
            branch['properties']['text']['maxLength']=400 if branch['properties']['type']['enum']==['action'] else 200
        index=next(i for i,s in enumerate(plan['scene_specs']) if s['id']==scene_id)
        prior=['scene_'+s['id'] for s in plan['scene_specs'][:index]]
        data={'plan_sha256':digest(plan),'scene':spec,'characters':plan['characters'],'episode_source':plan['episode_source'],'prior_scene_outcomes':[]}
        for key in prior:
            p=json.loads((self.folder/(key+'.json')).read_text());data['prior_scene_outcomes'].append({'key':key,'final_beat':p['result']['beats'][-1] if p.get('result') else None})
        def check(r):
            self.plan()
            if r['heading']!=spec['heading'] or r['beats'][0]['type']!='action':raise WritingError('Scene heading/action-first contract changed.')
        record=StagedDraft(self.folder).run('scene_'+scene_id,'script',data,'Write only this scene, with responsive Bangladeshi Bengali dialogue and visible action. Preserve approved scene objective, knowledge, props and sequence budget. Distinct voice, restrained emotion, character humor; do not summarize the whole season or repeat instructions. Short complete sentences, no inner-state narration.',schema,
            dependencies=prior,model=model,tokens=1536,complete=complete,check=check,think=think)
        if complete is None:
            try:identity=inventory().get(model)==approved['digest']
            except Exception:identity=False
            record['identity_verified']=identity;record['evidence']['model_digest']=approved['digest']
            if not identity:record.update(status='failed',error='Scene model identity changed after inference.')
            (self.folder/('scene_'+scene_id+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
        return record
    def compile(self):
        plan=self.plan();scenes=[];evidence=[]
        from jsonschema import Draft202012Validator
        for spec in plan['scene_specs']:
            p=self.folder/('scene_'+spec['id']+'.json')
            if p.is_symlink():raise AgentError('Unsafe scene evidence path.')
            r=json.loads(p.read_text())
            if r['status']!='validated_stage' or stage_digest(r['request'])!=r['request_sha256'] or json.loads(r['raw'])!=r['result'] or r['request']['data']['plan_sha256']!=digest(plan):raise AgentError('Incomplete, changed or stale scene evidence; no automatic regeneration.')
            if r['provenance']=='local_inference' and r.get('identity_verified') is not True:raise AgentError('Scene inference identity verification missing.')
            if not Draft202012Validator(r['request']['schema']).is_valid(r['result']):raise AgentError('Saved scene schema failed.')
            for key,expected in r['request']['dependencies'].items():
                if stage_digest(json.loads((self.folder/(key+'.json')).read_text()))!=expected:raise AgentError('Prior scene dependency changed.')
            scenes.append(dict(copy.deepcopy(spec),beats=copy.deepcopy(r['result']['beats'])))
            evidence.append({'scene':spec['id'],'record_sha256':digest(r),'provenance':r['provenance'],'raw_unchanged':True})
        artifact={'title':plan['title'],'characters':plan['characters'],'hook':plan['episode_source']['hook'],
            'ending':dict(plan['episode_source']['ending'],setup_scene_ids=plan['ending_setup_scenes']),'scenes':scenes}
        project=self.p.summary()['project'];brief={'title':project['title'],'premise':project['brief'],'genre':'Bangladeshi drama','tone':'restrained character drama','episodes':project['episodes'],'episode':self.episode,'seconds':project['seconds']}
        deps=[p['task'] for p in plan['sources']];source=next(p['task'] for p in plan['sources'] if p['role']=='story')
        data={'creative_v1':True,'kind':'screenplay','brief':brief,'artifact':artifact,'source':{'$from':source,'path':['artifact']},'sequence_source':{'$from':plan['sequence_task'],'path':['artifact']},'scene_evidence':evidence}
        prepare_creative('script',dict(data,source=self.p.current_output(source)['artifact'],sequence_source=plan['sequence_source']))
        rid=self.p.engine.enqueue('script',data,deps,mode='software',idempotency_key='compiled-scenes:'+digest([plan,evidence]))
        with self.p.store.tx() as db:db.execute('INSERT OR REPLACE INTO studio_links VALUES (?,?)',('script:episode'+str(self.episode),rid))
        return rid
