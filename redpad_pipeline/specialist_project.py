"""Create a branched, approval-gated software production graph using existing agents."""
import copy,hashlib
from .agents import AgentError,encode
from .specialists import IMPLEMENTED

# Every node uses an existing department. QC appears once here; owners can queue
# additional independent QC tasks at any earlier handoff with the same contracts.
DEPENDENCIES={
 'character':[], 'art':[], 'location':[], 'costume':['character','art'],
 'storyboard':['character','art','location','costume'],
 'performance':['character','storyboard'],
 'cinematographer':['storyboard','location','performance'],
 'motion':['storyboard','performance'],
 'video':['storyboard','character','cinematographer','motion'],
 'voice':['character','performance'], 'music':[],
 'editing':['video','voice','music'],
 'continuity':['character','costume','location','storyboard','cinematographer'],
 'qc':['editing','continuity','video','character'],
 'production_manager':[], 'growth':['editing','qc'], 'youtube':['growth','qc']}


def queue_project(engine,inputs,creative_tasks):
    if not isinstance(inputs,dict) or set(inputs)!=IMPLEMENTED:raise AgentError('Supply one validated specialist input per existing department.')
    if not isinstance(creative_tasks,list) or not creative_tasks:raise AgentError('Approved creative task references required.')
    # Preflight every supplied contract and creative reference before mutations.
    from .specialists import prepare
    for key,data in inputs.items():
        prepare(key,data)
        if any(source in data['sources'] for source in DEPENDENCIES[key]):raise AgentError('Graph source alias already supplied.')
    with engine.store.tx() as db:
        roles=set();versions=[];creative_sources={}
        for tid in creative_tasks:
            t=engine.store._task(db,tid)
            if t['state']!='Approved':raise AgentError('Creative source approval required.')
            engine.store._current(db,t)
            if t['agent'] in roles:raise AgentError('Select one current output per creative department.')
            roles.add(t['agent']);versions.append([tid,t['revision']])
            alias='screenplay' if t['agent']=='script' else t['agent']
            if any(alias in data['sources'] for data in inputs.values()):raise AgentError('Creative source alias already supplied.')
            creative_sources[alias]={'$from':tid,'path':['artifact']}
        if not {'script','director'}<=roles:raise AgentError('Approved Script and Director outputs required.')
    token=hashlib.sha256(encode([inputs,versions]).encode()).hexdigest()
    tasks={};runs={}
    for key,deps in DEPENDENCIES.items():
        data=copy.deepcopy(inputs[key]);dependencies=list(creative_tasks)+[tasks[d] for d in deps]
        data['sources'].update(copy.deepcopy(creative_sources))
        for source in deps:
            if source in data['sources']:raise AgentError('Graph source alias already supplied: '+source)
            data['sources'][source]={'$from':tasks[source],'path':['artifact']}
        rid=engine.enqueue(key,data,dependencies,mode='software',idempotency_key=token+':'+key)
        runs[key]=rid;tasks[key]=next(r['task'] for r in engine.runs() if r['id']==rid)
    return dict(tasks=tasks,runs=runs,approval_required=True,auto_publish=False)
