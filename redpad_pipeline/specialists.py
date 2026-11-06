"""Versioned specialist contracts. Pure metadata workflows; no inference or media claims."""
import copy
import hashlib
import math
from .agents import AgentError, encode, AGENTS

STAGES = {'A': ('qc','character','art','location','costume'),
          'B': ('storyboard','performance','cinematographer','motion','continuity'),
          'C': ('video','voice','music','editing'), 'D': ('production_manager','growth','youtube')}
IMPLEMENTED = {key for stage in STAGES.values() for key in stage}


def need(value, message):
    if not value: raise AgentError(message)


def text(value):
    return isinstance(value,str) and bool(value.strip())


def number(value, low=0, high=100000):
    return type(value) in (int,float) and math.isfinite(value) and low <= value <= high


def records(rows, fields):
    need(isinstance(rows,list) and 1 <= len(rows) <= 200,'Supply 1–200 records.')
    ids=set()
    for row in rows:
        need(isinstance(row,dict) and set(fields).issubset(row),'Missing record fields: '+', '.join(fields))
        need(text(row.get('id')) and row['id'] not in ids,'Unique stable record IDs required.')
        ids.add(row['id'])
        for f in fields:
            need(row[f] is not None and row[f]!='','Empty required field: '+f)
    return rows


def finding(record, code, expected, actual, target, severity='error', kind='rule_based'):
    return dict(record=record,code=code,expected=expected,actual=actual,target_agent=target,
                severity=severity,evidence_kind=kind,revision='Resolve '+code+' on '+record)


def changed(base, rows):
    def supplied(row):return {k:v for k,v in row.items() if k not in ('identity_hash','analytics_summary')}
    old={r['id']:supplied(r) for r in base};new={r['id']:supplied(r) for r in rows}
    return sorted(k for k in old.keys()|new.keys() if old.get(k)!=new.get(k))


def check_handoff(key, data, sources, prior=None):
    """All declared sources and revision bases must be exact approved artifacts."""
    need(isinstance(data.get('sources'),dict),'Specialist sources must be a map.')
    for alias,value in data['sources'].items():
        need(alias in AGENTS or alias=='screenplay','Unknown source department alias.')
        expected='script' if alias=='screenplay' else alias
        need(any(value == body.get('artifact') and body.get('agent')==expected for body in sources.values()),'Source must match the named current approved dependency department.')
    if data.get('base') is not None:
        need(data['base']==prior or any(data['base']==body.get('artifact') for body in sources.values()),'Revision base must match a current approved dependency or this task’s immutable previous revision.')


def prepare(key, data, upstream=None):
    need(key in IMPLEMENTED,'Specialist workflow unavailable.')
    need(isinstance(data,dict) and data.get('specialist_v1') is True,'Specialist v1 contract required.')
    need(set(data)=={'specialist_v1','project','records','sources','base','targets'},'Invalid specialist envelope.')
    need(text(data['project']) and isinstance(data['sources'],dict),'Project and source map required.')
    rows=copy.deepcopy(data['records']);records(rows,['id'])
    need(isinstance(data['targets'],list) and all(text(x) for x in data['targets']),'Revision target IDs required.')
    base=data['base']
    if base is not None:
        need(isinstance(base,dict) and base.get('department')==key,'Revision base department mismatch.')
        delta=changed(base['records'],rows)
        need(bool(data['targets']) and set(delta)<=set(data['targets']),'Changes outside targeted revision.')
    else: delta=[];need(not data['targets'],'Revision targets require an approved base.')
    findings=[];derived={}
    if key=='character':
        records(rows,['id','name','age','face','hair','appearance','personality','relationships','evolution','references','scene_states'])
        ids={r['id'] for r in rows}
        for r in rows:
            need(number(r['age'],0,120),'Invalid character age.')
            need(isinstance(r['relationships'],dict) and set(r['relationships'])<=ids,'Unknown relationship character.')
            need(isinstance(r['references'],list) and isinstance(r['scene_states'],list),'Reference/state lists required.')
            r['identity_hash']=hashlib.sha256(encode({k:r[k] for k in ('id','age','face','hair','appearance')}).encode()).hexdigest()
        derived['handoff_departments']=['storyboard','video','costume','continuity']
    elif key=='art':
        records(rows,['id','scene_ids','palette','set','props','period','culture','lighting','style'])
        for r in rows:
            need(isinstance(r['scene_ids'],list) and r['scene_ids'] and isinstance(r['props'],dict),'Scene IDs and prop inventory required.')
            need(isinstance(r['palette'],list) and r['palette'],'Palette required.')
        derived['affected_scenes']=sorted({s for r in rows if r['id'] in delta for s in r['scene_ids']})
    elif key=='location':
        records(rows,['id','architecture','geography','connections','openings','camera_access','references'])
        rooms={r['id']:r for r in rows};doors={}
        for r in rows:
            need(isinstance(r['connections'],list) and isinstance(r['openings'],list),'Room connections/openings must be lists.')
            for other in r['connections']:
                need(other in rooms and other!=r['id'],'Unknown or self-connected room.')
                if r['id'] not in rooms[other]['connections']:
                    findings.append(finding(r['id'],'asymmetric_adjacency',r['id'],rooms[other]['connections'],key))
            for door in r['openings']:
                need(isinstance(door,dict) and set(door)=={'id','to','kind'} and door['to'] in rooms,'Invalid opening destination.')
                pair=sorted([r['id'],door['to']])
                if door['id'] in doors and doors[door['id']]!=pair:
                    findings.append(finding(r['id'],'door_destination_conflict',doors[door['id']],pair,key))
                doors[door['id']]=pair
        derived['room_graph']={r['id']:r['connections'] for r in rows}
    elif key=='costume':
        records(rows,['id','scene','character','outfit','color','material','weather','culture','accessories','reference','change_reason'])
        last={}
        identities=data['sources'].get('character',{}).get('records',[])
        for r in rows:
            if identities: need(r['character'] in {x['id'] for x in identities},'Unknown costume character.')
            if r['character'] in last and last[r['character']]!=r['outfit'] and r['change_reason']=='none':
                findings.append(finding(r['id'],'unexplained_costume_change',last[r['character']],r['outfit'],key))
            last[r['character']]=r['outfit']
        derived['wardrobe_by_character']=last
    elif key=='qc':
        records(rows,['id','subject_agent','scene','criterion','expected','actual','evidence_kind','evidence','severity'])
        for r in rows:
            need(r['subject_agent'] in AGENTS and r['subject_agent']!='qc','QC cannot review itself.')
            need(r['evidence_kind'] in ('objective_metadata','rule_based','subjective','unverified_model'),'Unknown QC evidence provenance.')
            need(r['severity'] in ('info','warning','error','blocker') and text(r['evidence']),'QC evidence/severity required.')
            if r['expected']!=r['actual'] or r['evidence_kind'] in ('subjective','unverified_model'):
                findings.append(finding(r['id'],r['criterion'],r['expected'],r['actual'],r['subject_agent'],r['severity'],r['evidence_kind']))
        derived.update(recommendation='block' if any(f['severity']=='blocker' for f in findings) else 'revise' if findings else 'owner_review',
                       revision_routes={k:[f for f in findings if f['target_agent']==k] for k in {f['target_agent'] for f in findings}},
                       owner_approval=False,observations='Supplied evidence only; no footage inspected.')
    else:
        from .specialist_workflows import process
        derived,findings=process(key,rows,data)
    validate_links(key,rows,data['sources'],findings)
    if key=='qc':
        derived['recommendation']='block' if any(f['severity']=='blocker' for f in findings) else 'revise' if findings else 'owner_review'
        derived['revision_routes']={k:[f for f in findings if f['target_agent']==k] for k in {f['target_agent'] for f in findings}}
    artifact=dict(department=key,project=data['project'],records=rows,derived=derived)
    return dict(agent=key,artifact_type='specialist_'+key,artifact=artifact,findings=findings,
                revision_changes=delta,upstream=upstream or [],provenance='software',
                model_inference=False,media_generated=False,creative_quality_verified=False,human_review_required=True)


def example(key):
    from .specialist_examples import EXAMPLES
    return dict(specialist_v1=True,project='ফেরার চাবি — fictional manual test',records=copy.deepcopy(EXAMPLES[key]),sources={},base=None,targets=[])


def validate_links(key,rows,sources,findings):
    identities={r['id']:r for r in sources.get('character',{}).get('records',[])}
    locations={r['id']:r for r in sources.get('location',{}).get('records',[])}
    shots={r['id']:r for r in sources.get('storyboard',{}).get('records',[])}
    for row in rows:
        characters=row.get('characters',[])
        if 'character' in row:characters=[row['character']]
        if identities:need(all(c in identities for c in characters),'Unknown approved character reference.')
        if locations and 'location' in row:need(row['location'] in locations,'Unknown approved location reference.')
        if shots and 'shot' in row:need(row['shot'] in shots,'Unknown approved shot reference.')
        if key=='performance' and row['character'] in identities:
            for state in identities[row['character']]['scene_states']:
                if state.get('scene')==row['scene'] and state.get('emotion')!=row['emotion_from']:
                    findings.append(finding(row['id'],'character_emotion_state',state.get('emotion'),row['emotion_from'],key,'warning'))
    if key=='qc':
        for char in identities.values():
            for state in char['scene_states']:
                for field in ('age','face','hair','appearance'):
                    if field in state and state[field]!=char[field] and not state.get('change_reason'):
                        findings.append(finding(char['id'],'character_'+field,char[field],state[field],'character'))
        for row in rows:
            if row['criterion']=='media_spec':
                spec=row['actual']
                need(isinstance(spec,dict),'Technical media specification must be an object.')
                for field,low,high in [('fps',1,60),('width',64,4096),('height',64,4096),('seconds',.01,3600)]:
                    if not number(spec.get(field),low,high):findings.append(finding(row['id'],'invalid_'+field,[low,high],spec.get(field),row['subject_agent'],'blocker','objective_metadata'))
        # Include derived metadata defects in routing and recommendation.
        # The supplied review fields are never treated as unseen-media inspection.
