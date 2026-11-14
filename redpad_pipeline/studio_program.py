"""Unified, resumable development/production ledger over the existing 20 agents.

No production database, model downloads, approvals or automatic media generation.
Project notes and hierarchy are planning data; generated artifacts live in the
existing Engine with unchanged source-version and owner/QC gates.
"""
import copy,hashlib,json,re,sqlite3
from pathlib import Path
from uuid import uuid4
from .agents import AGENTS,AgentStore,AgentError,encode
from .agent_engine import Engine

ROOT=Path(__file__).resolve().parents[1]
PROGRAM_ROOT=ROOT/'phase3_runs/studio_program'
WORKSTREAMS={
 'A':('Writing model comparison',[],'Approved Gemma/Qwen3.5 CPU comparison exists at f71e282; no candidate passed independent creative acceptance. Runtime availability must be rechecked on this host.'),
 'B':('Creative intelligence',['A'],'Independent Bengali creative acceptance remains missing.'),
 'C':('Character and production design',['B'],'Real approved identity/location references required.'),
 'D':('Storyboard performance camera motion',['C'],'Plans exist; actual acting/physics quality unverified.'),
 'E':('Wan LTX SVD offline generation',['D'],'Approved checkpoints, exact licenses and compatible GPU required.'),
 'F':('Bengali speech and audio',['B'],'Approved offline TTS weights, listening review and lip-sync dependencies missing.'),
 'G':('Continuity QC orchestration',[],'No AI may approve its own output; current source gates remain.'),
 'H':('Growth and YouTube preparation',[],'Read-only/preparation only; publishing is prohibited.'),
 'I':('Unified Dashboard',[],'Software interface is separate from actual creative/media readiness.'),
 'J':('Cinematic acceptance',['B','C','D','E','F','G'],'Real media, technical validation, human review and owner acceptance required.')}
CHILD={'series':'season','season':'episode','episode':'sequence','sequence':'scene','scene':'shot','shot':'asset'}


class StudioProgram:
    def __init__(self,project_id):
        if not isinstance(project_id,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',project_id):raise AgentError('Safe project ID required.')
        self.root=PROGRAM_ROOT/project_id
        if any(p.is_symlink() for p in (self.root,*self.root.parents)):raise AgentError('Project symlinks prohibited.')
        self.root.mkdir(parents=True,exist_ok=True);self.project_id=project_id
        self.store=AgentStore(self.root/'agent_control.sqlite3');self.engine=Engine(self.store)
        with self.store.tx() as db:db.executescript('''
            CREATE TABLE IF NOT EXISTS studio_project(id TEXT PRIMARY KEY,title TEXT,brief TEXT,episodes INTEGER,seconds INTEGER);
            CREATE TABLE IF NOT EXISTS studio_nodes(id TEXT PRIMARY KEY,parent TEXT,kind TEXT,ordinal INTEGER,data TEXT,UNIQUE(parent,kind,ordinal));
            CREATE TABLE IF NOT EXISTS studio_messages(id INTEGER PRIMARY KEY,role TEXT,text TEXT,provenance TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS studio_links(label TEXT PRIMARY KEY,run TEXT);
            CREATE TABLE IF NOT EXISTS studio_workstreams(id TEXT PRIMARY KEY,state TEXT,evidence TEXT,blocker TEXT);
            CREATE TABLE IF NOT EXISTS studio_checkpoints(id INTEGER PRIMARY KEY,payload TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')

    def create(self,title,brief,episodes=30,seconds=300):
        if not isinstance(title,str) or not title.strip() or len(title)>200 or not isinstance(brief,str) or not 1<=len(brief)<=16000:raise AgentError('Bounded title and original brief required.')
        if type(episodes) is not int or not 1<=episodes<=100 or type(seconds) is not int or not 180<=seconds<=4200:raise AgentError('Supported project: 1–100 episodes, each 180–4200 seconds.')
        with self.store.tx() as db:
            row=db.execute('SELECT * FROM studio_project WHERE id=?',(self.project_id,)).fetchone()
            values=(self.project_id,title,brief,episodes,seconds)
            if row:
                if tuple(row)!=values:raise AgentError('Project exists; do not overwrite its locked creative brief.')
                return self.summary()
            db.execute('INSERT INTO studio_project VALUES (?,?,?,?,?)',values)
            db.execute('INSERT INTO studio_nodes VALUES (?,?,?,?,?)',('series',None,'series',1,encode({'title':title,'status':'planned'})))
            db.execute('INSERT INTO studio_nodes VALUES (?,?,?,?,?)',('season1','series','season',1,encode({'status':'planned'})))
            for i in range(1,episodes+1):db.execute('INSERT INTO studio_nodes VALUES (?,?,?,?,?)',('episode'+str(i),'season1','episode',i,encode({'target_seconds':seconds,'status':'planned_not_generated'})))
            for key,(_,_,blocker) in WORKSTREAMS.items():db.execute('INSERT INTO studio_workstreams VALUES (?,?,?,?)',(key,'tracked',encode([]),blocker))
        return self.summary()

    def note(self,role,text):
        if role not in ('director','story','script') or not isinstance(text,str) or not 1<=len(text)<=12000:raise AgentError('Primary creative role and bounded owner note required.')
        with self.store.tx() as db:db.execute('INSERT INTO studio_messages(role,text,provenance) VALUES (?,?,?)',(role,text,'owner_note_not_AI_output'))

    def add_node(self,parent,kind,ordinal,data):
        if type(ordinal) is not int or ordinal<1 or not isinstance(data,dict):raise AgentError('Valid hierarchy node required.')
        with self.store.tx() as db:
            p=db.execute('SELECT kind FROM studio_nodes WHERE id=?',(parent,)).fetchone()
            if not p or CHILD.get(p[0])!=kind:raise AgentError('Invalid Series→Season→Episode→Sequence→Scene→Shot→Asset relationship.')
            old=db.execute('SELECT id,data FROM studio_nodes WHERE parent=? AND kind=? AND ordinal=?',(parent,kind,ordinal)).fetchone()
            if old:
                if json.loads(old['data'])!=data:raise AgentError('Existing node is immutable; create a versioned task revision.')
                return old['id']
            key=uuid4().hex;db.execute('INSERT INTO studio_nodes VALUES (?,?,?,?,?)',(key,parent,kind,ordinal,encode(data)))
        return key

    def current_output(self,task_id,role=None):
        with self.store.tx() as db:
            t=self.store._task(db,task_id)
            if t['state']!='Approved' or (role and t['agent']!=role):raise AgentError('Current approved output required.')
            self.store._current(db,t)
            row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(task_id,t['revision'])).fetchone()
            body=json.loads(json.loads(row[0])['summary'])
        return body

    def queue_creative(self,stage,episode=1):
        from .phase3 import shape
        with self.store.tx() as db:
            p=db.execute('SELECT * FROM studio_project WHERE id=?',(self.project_id,)).fetchone()
            links={r['label']:r['run'] for r in db.execute('SELECT * FROM studio_links')}
        if p is None:raise AgentError('Create the project first.')
        runs={r['id']:r for r in self.engine.runs()}
        label=stage if stage in ('story','director_story') else stage+':episode'+str(episode)
        if label in links:return links[label]
        if type(episode) is not int or not 1<=episode<=p['episodes']:raise AgentError('Invalid episode.')
        if stage=='story' and p['episodes']>5:raise AgentError('Long series requires per-episode staged architecture and review; a single giant season call is blocked. Use hierarchy/short staged research until a qualified model is available.')
        if stage=='director_story' and 'story' in links and json.loads(runs[links['story']]['inputs']).get('bridge_compilation') is True:
            from .story_bridge import StoryBridge
            return StoryBridge(self).next_director_review()
        seed=json.loads((ROOT/'assets/writing/creative/scenarios.json').read_text());deps=[]
        brief={'title':p['title'],'premise':p['brief'],'genre':'Bangladeshi drama','tone':'natural Bangladeshi Bengali, restrained emotion, character wit','episodes':p['episodes'],'episode':episode,'seconds':p['seconds']}
        if stage=='story':role='story';kind='season';template=seed['season'];template['episodes']=template['episodes'][:p['episodes']]
        else:
            parent={'director_story':'story','script':'story','director_script':'script:episode'+str(episode)}.get(stage)
            if not parent or parent not in links:raise AgentError('Required creative stage is not queued.')
            parent_task=runs[links[parent]]['task'];source=self.current_output(parent_task,'script' if stage=='director_script' else 'story')
            deps=[parent_task]
            if stage=='script':
                if 'director_story' not in links:raise AgentError('Approved season Director review required.')
                review_task=runs[links['director_story']]['task'];self.current_output(review_task,'director');deps.append(review_task)
                role='script';kind='screenplay';template=seed['screenplay']
            else:role='director';kind='direction';template=seed['direction_script' if stage=='director_script' else 'direction_story']
        data={'creative_v1':True,'kind':kind,'brief':brief,'artifact':shape(template)}
        if stage!='story':data['source']={'$from':deps[0],'path':['artifact']}
        if stage=='script':
            source_run=runs[links['story']]
            if json.loads(source_run['inputs']).get('bridge_compilation') is True:
                from .story_bridge import StoryBridge
                sequences=StoryBridge(self)._linked('bridge:sequences:'+str(episode));deps.append(sequences)
                data['sequence_source']={'$from':sequences,'path':['artifact']}
        rid=self.engine.enqueue(role,data,deps,mode='local',idempotency_key='studio:'+self.project_id+':'+stage+':'+str(episode))
        with self.store.tx() as db:db.execute('INSERT INTO studio_links VALUES (?,?)',(label,rid))
        return rid

    def queue_specialists(self,episode=1):
        from .specialist_project import queue_generated_project
        with self.store.tx() as db:links={r['label']:r['run'] for r in db.execute('SELECT * FROM studio_links')}
        runs={r['id']:r for r in self.engine.runs()}
        needed=[]
        for label in ('script:episode'+str(episode),'director_script:episode'+str(episode)):
            if label not in links:raise AgentError('Approved screenplay and its Director review required.')
            task=runs[links[label]]['task'];self.current_output(task);needed.append(task)
        plan=queue_generated_project(self.engine,self.project_id+':episode'+str(episode),needed)
        with self.store.tx() as db:
            for role,rid in plan['runs'].items():db.execute('INSERT OR IGNORE INTO studio_links VALUES (?,?)',('internal:'+role+':episode'+str(episode),rid))
        return plan

    def tick(self,max_runs=1):
        if type(max_runs) is not int or not 1<=max_runs<=3:raise AgentError('One to three bounded runs per owner action.')
        # Existing Engine performs dependency and current-version checks; never auto-approve.
        out={}
        for run in self.engine.runs():
            if run['state']=='Blocked' and run['blocker']=='Approval/dependency':
                with self.store.tx() as db:
                    try:self.engine._sources(db,run)
                    except AgentError:continue
                self.engine.retry(run['id'])
        for _ in range(max_runs):
            ready=next((r for r in reversed(self.engine.runs()) if r['state']=='Ready for Input'),None)
            if not ready:break
            out[ready['id']]=self.engine.execute(ready['id'],local_options={'num_ctx':4096,'num_predict':1024,'timeout_seconds':180,'stream':True})
        return out

    def summary(self):
        with self.store.tx() as db:
            project=db.execute('SELECT * FROM studio_project WHERE id=?',(self.project_id,)).fetchone()
            nodes=[dict(r) for r in db.execute('SELECT * FROM studio_nodes')]
            streams=[dict(r) for r in db.execute('SELECT * FROM studio_workstreams')]
            notes=[dict(r) for r in db.execute('SELECT * FROM studio_messages')]
        return {'project':dict(project) if project else None,'hierarchy':nodes,'workstreams':streams,'owner_notes':notes,
                'runs':self.engine.runs(),'tasks':self.store.tasks(),'registered_agents':len(AGENTS),'production_ready':False,
                'auto_publish':False,'quality':'Software/planning state only; no artistic approval inferred.'}

    def production_overview(self):
        """One current overview; task approval never implies artistic acceptance."""
        summary=self.summary();tasks={t['id']:t for t in summary['tasks']};runs={r['id']:r for r in summary['runs']};outputs=self.store.outputs()
        with self.store.tx() as db:links={r['label']:r['run'] for r in db.execute('SELECT * FROM studio_links')}
        def state(rid):
            run=runs.get(rid)
            if not run:return 'Not queued'
            task=tasks[run['task']]
            try:
                with self.store.tx() as db:self.store._current(db,task)
            except AgentError:return 'Stale source — targeted recovery required'
            return task['state'] if task['revision'] else run['state']
        agents=[]
        for role in AGENTS:
            latest=next((r for r in summary['runs'] if tasks[r['task']]['agent']==role),None)
            item={'agent':role,'owner_facing':role in ('director','story','script'),'state':state(latest['id']) if latest else 'Not queued',
                  'model':latest['model'] if latest else '', 'blocker':latest['error'] if latest else 'No current department output',
                  'artistic_quality':'Not verified','task':latest['task'] if latest else None}
            if latest:
                output=next((o for o in outputs if o['task']==latest['task'] and o['revision']==tasks[latest['task']]['revision']),None)
                body=json.loads(json.loads(output['payload'])['summary']) if output else {}
                item.update(provenance=body.get('provenance','not executed'),findings=body.get('findings',[]))
            agents.append(item)
        episodes=[{'episode':n,'outline':state(links.get('bridge:outline:'+str(n))),'sequences':state(links.get('bridge:sequences:'+str(n))),
                   'script':state(links.get('script:episode'+str(n))),'director':state(links.get('director_script:episode'+str(n)))} for n in range(1,(summary['project'] or {}).get('episodes',0)+1)]
        return {'agents':agents,'episodes':episodes,'primary_owner_agents':['director','story','script'],'professional_quality_verified':False,'auto_publish':False}

    def checkpoint(self,source_commit,evidence):
        if not re.fullmatch(r'[a-f0-9]{40}',source_commit) or not isinstance(evidence,dict):raise AgentError('Exact source commit and attributed evidence required.')
        summary=self.summary()
        compact={k:summary[k] for k in ('project','workstreams','registered_agents','production_ready')}
        compact['runs']=[{**{k:r[k] for k in ('id','task','state','attempt','expected_revision','model')},'input_sha256':hashlib.sha256(r['inputs'].encode()).hexdigest()} for r in summary['runs']]
        compact['nodes']=[{k:n[k] for k in ('id','parent','kind','ordinal')} for n in summary['hierarchy']]
        payload={'source_commit':source_commit,'summary':compact,'evidence':evidence,'next_action':'Resolve pending source approval/runtime blockers; resume existing run IDs, do not regenerate approved outputs.'}
        with self.store.tx() as db:db.execute('INSERT INTO studio_checkpoints(payload) VALUES (?)',(encode(payload),))
        return payload

    def recover(self,run_id,worker_stopped=False):
        if worker_stopped is not True:raise AgentError('Confirm the previous worker has stopped.')
        new_id=self.engine.recover(run_id)
        with self.store.tx() as db:db.execute('UPDATE studio_links SET run=? WHERE run=?',(new_id,run_id))
        return new_id
