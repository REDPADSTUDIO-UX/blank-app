"""Versioned specialist contracts. Pure metadata workflows; no inference or media claims."""
import copy
import hashlib
import math
from .agents import AgentError, encode, AGENTS

STAGES = {'A': ('qc','character','art','location','costume'),
          'B': ('storyboard','performance','cinematographer','motion','continuity'),
          'C': ('video','voice','music','editing'), 'D': ('production_manager','growth','youtube')}
IMPLEMENTED = set(STAGES['A'])


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
    old={r['id']:r for r in base};new={r['id']:r for r in rows}
    return sorted(k for k in old.keys()|new.keys() if old.get(k)!=new.get(k))


def check_handoff(key, data, sources):
    """All declared sources and revision bases must be exact approved artifacts."""
    for value in data.get('sources',{}).values():
        need(any(value == body.get('artifact') for body in sources.values()),'Source must match a current approved dependency artifact.')
    if data.get('base') is not None:
        need(any(data['base']==body.get('artifact') for body in sources.values()),'Revision base must match a current approved dependency artifact.')


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
    artifact=dict(department=key,project=data['project'],records=rows,derived=derived)
    return dict(agent=key,artifact_type='specialist_'+key,artifact=artifact,findings=findings,
                revision_changes=delta,upstream=upstream or [],provenance='software',
                model_inference=False,media_generated=False,creative_quality_verified=False,human_review_required=True)


def example(key):
    from .specialist_examples import EXAMPLES
    return dict(specialist_v1=True,project='ফেরার চাবি — fictional manual test',records=copy.deepcopy(EXAMPLES[key]),sources={},base=None,targets=[])
