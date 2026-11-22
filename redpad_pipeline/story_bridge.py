"""Staged season-to-episode bridge on the existing Engine and approval ledger.

Compilation preserves approved prose; it never writes dialogue, grants approval,
or turns an authored fixture into model evidence.
"""
import copy,json
from pathlib import Path
from .agents import AgentError,encode
from .creative import digest,season_check,texts,hook_check,ending_check

FIELDS={
 'bible':['id','title','logline','premise','conflict','season_arc','ending_strategy','feasibility','characters','rules','initial_state'],
 'arcs':['id','character','want','need','turns'],
 'outline':['number','hook','ending','reveals','objective','cause','development','escalation','payoff','character_change','state_before','state_after','knowledge_changes','plants','payoffs'],
 'sequences':['id','scene_ids','seconds','objective','obstacle','turn','consequence']}

def validate_stage(role,data,sources,prior=None):
    if role!='story' or data.get('stage') not in FIELDS:raise AgentError('Story stage required.')
    stage=data['stage'];rows=copy.deepcopy(data.get('records'))
    if not isinstance(rows,list) or not 1<=len(rows)<=100:raise AgentError('Bounded story stage records required.')
    for row in rows:
        if not isinstance(row,dict) or not set(FIELDS[stage])<=set(row):raise AgentError('Missing '+stage+' fields: '+', '.join(FIELDS[stage]))
    if stage in ('bible','outline') and len(rows)!=1:raise AgentError('One bounded bible/episode per call.')
    if any(not isinstance(x,dict) for x in sources.values()):raise AgentError('Approved stage sources required.')
    actual={k:v['artifact'] for k,v in sources.items()}
    if data.get('sources')!=actual:raise AgentError('Story stage sources must match exact approved dependencies.')
    registry={}
    if stage=='bible':
        b=rows[0]
        texts(b,['id','title','logline','premise','conflict','season_arc','ending_strategy','feasibility'])
        if not isinstance(b['characters'],list) or not b['characters'] or not isinstance(b['initial_state'],dict) or not b['initial_state']:raise AgentError('Characters and explicit initial story state required.')
        for c in b['characters']:texts(c,['id','name','biography','want','need','internal_conflict','relationship_arc'])
        if len({c['id'] for c in b['characters']})!=len(b['characters']) or len({c['name'] for c in b['characters']})!=len(b['characters']):raise AgentError('Distinct stable character IDs/names required.')
        if not isinstance(b['rules'],list) or not all(isinstance(r,str) and r.strip() for r in b['rules']) or not all(isinstance(k,str) and isinstance(v,str) and k.strip() and v.strip() for k,v in b['initial_state'].items()):raise AgentError('Explicit textual world rules and state facts required.')
    elif stage=='arcs':
        for row in rows:texts(row,['id','character','want','need','turns'])
        bible=next((a['records'][0] for a in actual.values() if a.get('stage')=='bible'),None)
        if not bible or {r['character'] for r in rows}!={c['id'] for c in bible['characters']}:raise AgentError('Every bible character needs an arc; no unrelated identity.')
    elif stage=='outline':
        row=rows[0];number=data['episode']
        texts(row,['objective','cause','development','escalation','payoff','character_change']);hook_check(row['hook']);ending_check(row['ending'])
        if type(row['number']) is not int or not isinstance(row['reveals'],list) or not all(isinstance(x,str) and x.strip() for x in row['reveals']) or not isinstance(row['state_before'],dict) or not isinstance(row['state_after'],dict):raise AgentError('Typed episode ordinal, reveals and state maps required.')
        if not all(isinstance(v,str) and v.strip() for v in row['state_after'].values()):raise AgentError('State facts must be explicit nonempty text.')
        b=next((a['records'][0] for a in actual.values() if a.get('stage')=='bible'),None)
        previous=next((a['records'][0] for a in actual.values() if a.get('stage')=='outline' and a['episode']==number-1),None)
        predecessor=next((a for a in actual.values() if a.get('stage')=='outline' and a['episode']==number-1),{})
        registry=copy.deepcopy(predecessor.get('setup_registry',{}))
        before=previous['state_after'] if previous else b['initial_state'] if b else None
        if row['number']!=number or not before or row['state_before']!=before or set(row['state_after'])!=set(before):raise AgentError('Episode state or ordinal contradicts approved predecessor.')
        if number>1 and not previous:raise AgentError('Previous approved episode missing.')
        if row['state_after']==before:raise AgentError('An episode must change tracked state.')
        if not isinstance(row['knowledge_changes'],list):raise AgentError('Explicit knowledge transitions required.')
        for change in row['knowledge_changes']:
            if not isinstance(change,dict) or set(change)!={'character','fact','learned_by'} or not change['learned_by'] or change['character'] not in {c['id'] for c in b['characters']}:raise AgentError('Knowledge change requires known character and disclosure event.')
        if not isinstance(row['plants'],list) or not isinstance(row['payoffs'],list):raise AgentError('Explicit setup/payoff lists required.')
        for plant in row['plants']:
            if not isinstance(plant,dict) or set(plant)!={'id','question'} or not plant['id'] or not plant['question'] or plant['id'] in registry:raise AgentError('Setup must have a unique ID and explicit question.')
            registry[plant['id']]={'id':plant['id'],'plant':plant['question'],'plant_episode':number}
        for payoff in row['payoffs']:
            if not isinstance(payoff,dict) or set(payoff)!={'id','answer'} or not payoff['answer'] or payoff['id'] not in registry or registry[payoff['id']]['plant_episode']>=number or 'payoff_episode' in registry[payoff['id']]:raise AgentError('Payoff requires an earlier unresolved setup, not an invented or repeated reveal.')
            registry[payoff['id']].update(payoff=payoff['answer'],payoff_episode=number)
    elif stage=='sequences':
        for row in rows:
            texts(row,['id','objective','obstacle','turn','consequence'])
            if not isinstance(row['scene_ids'],list) or not all(isinstance(s,str) and s.strip() for s in row['scene_ids']):raise AgentError('Explicit scene IDs required.')
        ids=[sid for r in rows for sid in r['scene_ids']]
        if len(ids)!=len(set(ids)):raise AgentError('A scene cannot belong to multiple sequences.')
        if len({r['id'] for r in rows})!=len(rows) or any(type(r['seconds']) is not int or r['seconds']<=0 or not r['scene_ids'] for r in rows):raise AgentError('Unique timed sequence/scene references required.')
        if sum(r['seconds'] for r in rows)!=data['seconds']:raise AgentError('Sequences must cover the episode time budget.')
        if not any(a.get('episodes') for a in actual.values()):raise AgentError('Approved compiled season required before sequence breakdown.')
    if prior is not None:
        if data.get('base')!=prior:raise AgentError('Revision base must match this task’s exact previous artifact.')
        if prior.get('stage')!=stage or prior.get('episode')!=data['episode']:raise AgentError('Revision cannot switch a stage or episode identity.')
        old={r.get('id',str(r.get('number',0))):r for r in prior['records']};new={r.get('id',str(r.get('number',0))):r for r in rows}
        changed={k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
        if not changed<=set(data.get('targets',[])):raise AgentError('Stage revision changed locked records outside target IDs.')
    return {'agent':role,'artifact_type':'story_stage','artifact':{'stage':stage,'episode':data['episode'],'records':rows,'setup_registry':registry},'findings':[],
            'model_inference':False,'media_generated':False,'human_review_required':True,'creative_quality_verified':False}

class StoryBridge:
    def __init__(self,program):self.program=program
    def queue_benchmark(self,artifact=None,*,source_tasks=None,research=None,locks=None,task=None,targets=None):
        """The original bounded Story case on the existing project/Engine ledger.
        Missing real-runtime authorization blocks before model construction.
        Supplied artifacts remain software fixtures, never candidate evidence.
        """
        from .story_quality import request as benchmark_request
        p=self.program;deps=source_tasks or []
        if not p.summary()['project']:raise AgentError('Open the existing Studio project first.')
        base=None
        if task:
            with p.store.tx() as db:
                current=p.store._task(db,task);p.store._current(db,current)
                if current['agent']!='story' or current['state']!='Revision requested':raise AgentError('Owner-requested Story revision required.')
                row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,current['revision'])).fetchone()
                if not row:raise AgentError('Missing immutable Story revision base.')
                base=json.loads(json.loads(row[0])['summary'])['artifact']
                previous=db.execute('SELECT inputs FROM agent_runs WHERE task=? ORDER BY rowid DESC LIMIT 1',(task,)).fetchone()
                original=json.loads(previous[0]) if previous else {}
                if locks is None:locks=original.get('locks',[])
                if research is None:research=original.get('research',[])
                deps=list(dict.fromkeys([*deps,*[r['id'] for r in json.loads(current['refs'])]]))
        sources={tid:{'$from':tid,'path':['artifact']} for tid in deps}
        data=benchmark_request(artifact,sources=sources,research=research,locks=locks,base=base,targets=targets)
        return p.engine.enqueue('story',data,deps,mode='software' if artifact is not None else 'local',task=task,
                                idempotency_key='story-benchmark:'+digest([p.project_id,data,task]))
    def _linked(self,label):
        with self.program.store.tx() as db:r=db.execute('SELECT run FROM studio_links WHERE label=?',(label,)).fetchone()
        if not r:raise AgentError('Missing stage: '+label)
        run=next(rn for rn in self.program.engine.runs() if rn['id']==r[0]);self.program.current_output(run['task'])
        return run['task']
    def queue(self,stage,episode=1,records=None,*,task=None,targets=None):
        p=self.program;project=p.summary()['project']
        if not project:raise AgentError('Create or open the existing Studio project first.')
        if stage not in FIELDS or type(episode) is not int or not 1<=episode<=project['episodes']:raise AgentError('Valid staged episode required.')
        names=[]
        if stage!='bible':names=['bridge:bible']
        if stage in ('outline','sequences'):names+=['bridge:arcs']
        if stage=='outline' and episode>1:names+=['bridge:outline:'+str(episode-1)]
        if stage=='sequences':names+=['story','director_story']
        deps=[self._linked(n) for n in names]
        label='bridge:'+stage+(':'+str(episode) if stage in ('outline','sequences') else '')
        with p.store.tx() as db:old=db.execute('SELECT run FROM studio_links WHERE label=?',(label,)).fetchone()
        if old and task is not None:
            previous=next(r for r in p.engine.runs() if r['id']==old[0])
            if previous['task']!=task:raise AgentError('Stage revision must preserve the existing task identity.')
        data={'story_stage_v1':True,'stage':stage,'episode':episode,'seconds':project['seconds'],'brief':project['brief'],
              'records':records or [],'sources':{tid:{'$from':tid,'path':['artifact']} for tid in deps},'targets':targets or []}
        if task:
            with p.store.tx() as db:
                t=p.store._task(db,task);prior=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task,t['revision'])).fetchone()
            if t['state']!='Revision requested' or not prior:raise AgentError('Owner must request a revision on the existing stage first.')
            data['base']=json.loads(json.loads(prior[0])['summary'])['artifact']
        if old and task is None:
            previous=next(r for r in p.engine.runs() if r['id']==old[0])
            if json.loads(previous['inputs'])!=data:raise AgentError('Stage already exists; request a targeted revision on its task instead.')
            return old[0]
        if records is not None:
            validate_stage('story',dict(data,sources={tid:p.current_output(tid)['artifact'] for tid in deps}),{tid:p.current_output(tid) for tid in deps},data.get('base'))
        rid=p.engine.enqueue('story',data,deps,mode='software' if records is not None else 'local',task=task,
               idempotency_key='bridge:'+p.project_id+':'+digest([label,data,task]))
        with p.store.tx() as db:db.execute('INSERT OR REPLACE INTO studio_links VALUES (?,?)',(label,rid))
        return rid
    def compile_season(self):
        p=self.program;project=p.summary()['project'];deps=[self._linked('bridge:bible'),self._linked('bridge:arcs')]
        deps += [self._linked('bridge:outline:'+str(n)) for n in range(1,project['episodes']+1)]
        bible=p.current_output(deps[0])['artifact']['records'][0]
        episodes=[p.current_output(t)['artifact']['records'][0] for t in deps[2:]]
        artifact={k:copy.deepcopy(bible[k]) for k in ('logline','premise','conflict','season_arc','ending_strategy','feasibility','characters')}
        arcs={r['character']:r for r in p.current_output(deps[1])['artifact']['records']}
        for c in artifact['characters']:
            c.update(want=arcs[c['id']]['want'],need=arcs[c['id']]['need'],relationship_arc=arcs[c['id']]['turns'])
        registry=p.current_output(deps[-1])['artifact']['setup_registry']
        if any('payoff_episode' not in r for r in registry.values()):raise AgentError('Season has unresolved setup promises; complete the planned payoff or request a targeted architecture revision.')
        artifact.update(episodes=episodes,setups=list(registry.values()),continuity=[],research=[{'source_id':'original-staged-project','license':'original','note':'Approved versioned stages compiled without rewriting prose; artistic review still required.','status':'original'}])
        brief={'title':project['title'],'premise':project['brief'],'genre':'Bangladeshi family mystery','tone':'restrained natural drama','episodes':project['episodes'],'episode':1,'seconds':project['seconds']}
        season_check(artifact,brief)
        rid=p.engine.enqueue('story',{'creative_v1':True,'kind':'season','brief':brief,'artifact':artifact,'bridge_compilation':True},deps,mode='software',idempotency_key='compiled-season:'+digest([artifact,deps]))
        with p.store.tx() as db:db.execute('INSERT OR REPLACE INTO studio_links VALUES (?,?)',('story',rid))
        return rid

    def queue_critic(self,episode,role='director'):
        if role not in ('director','qc'):raise AgentError('Independent critic role required.')
        source=self._linked('bridge:outline:'+str(episode))
        rid=self.program.engine.enqueue(role,{'grounded_review_v1':True,'source':{'$from':source,'path':['artifact']},'findings':[]},[source],mode='local',idempotency_key='episode-critic:'+digest([role,source,self.program.current_output(source)]))
        with self.program.store.tx() as db:db.execute('INSERT OR REPLACE INTO studio_links VALUES (?,?)',('bridge:critic:'+role+':'+str(episode),rid))
        return rid

    def next_director_review(self):
        p=self.program;total=p.summary()['project']['episodes'];season=self._linked('story');critics=[]
        for n in range(1,total+1):
            label='bridge:critic:director:'+str(n)
            with p.store.tx() as db:row=db.execute('SELECT run FROM studio_links WHERE label=?',(label,)).fetchone()
            if not row:return self.queue_critic(n)
            run=next(r for r in p.engine.runs() if r['id']==row[0])
            with p.store.tx() as db:task=p.store._task(db,run['task'])
            if task['state']!='Approved':return run['id']
            p.current_output(task['id'],'director');critics.append(task['id'])
        rid=p.engine.enqueue('director',{'grounded_review_compilation_v1':True,'season_task':season,'critic_tasks':critics},[season,*critics],mode='software',idempotency_key='compiled-director:'+digest([season,critics]))
        with p.store.tx() as db:db.execute('INSERT OR REPLACE INTO studio_links VALUES (?,?)',('director_story',rid))
        return rid

    def import_ledger_outline(self,folder,number,plants,payoffs):
        """Reuse an existing validated archive without regenerating/relabeling it.
        Mapping is a software transform; original raw/result/evidence stay intact.
        """
        from .series_ledger import SeriesLedger
        from .offline_media import sha,ROOT
        folder=Path(folder)
        if any(p.is_symlink() for p in (folder,*folder.parents)) or not folder.resolve().is_relative_to((ROOT/'phase3_runs').resolve()):raise AgentError('Only an isolated staged development archive may be imported.')
        folder=folder.resolve()
        if any(p.is_symlink() for p in folder.glob('*.json')):raise AgentError('Linked archive files are prohibited.')
        ledger=SeriesLedger(folder);state=ledger.state();project=self.program.summary()['project']
        bible=self.program.current_output(self._linked('bridge:bible'))['artifact']['records'][0]
        if set(state['config']['actors'])!={c['name'] for c in bible['characters']}:raise AgentError('Archive characters differ from the approved bible.')
        if type(number) is not int or not 1<=number<=state['completed'] or state['config']['brief']!=project['brief']:raise AgentError('Archive episode/project brief mismatch; no unrelated draft import.')
        path=folder/f'ep{number:03}.json';record=json.loads(path.read_text());r=record['result']
        hook={'type':'character','image':r['emotion_action'],'question':r['hook_decision'],'promise':r['consequence']}
        ending={'type':'decision','payoff':r['consequence'],'question':r['hook_decision'],'next_connection':r['hook_decision'],'earned_by':r['choice']}
        row={'number':number,'hook':hook,'ending':ending,'reveals':[],'objective':r['want'],'cause':r['cause_id'],'development':r['choice'],'escalation':r['cost'],'payoff':r['consequence'],'character_change':r['emotion_action'],
             'state_before':r['state_before'],'state_after':r['state_after'],'knowledge_changes':[],'plants':plants,'payoffs':payoffs,
             'imported_ledger_evidence':{'relative_path':str(path.relative_to(ROOT)),'sha256':sha(path),'provenance':record.get('provenance'),'new_inference':False,'quality_verified':False}}
        return self.queue('outline',number,[row])
