"""Small CPU evaluation contracts; these do not replace production contracts."""
import copy,json,unicodedata
from .agents import AgentError,nonempty
from .screenwriter import validate as screenplay_validate


def validate_micro(kind,result,source=None,targets=None):
    def need(condition,message):
        if not condition:raise AgentError(message)
    if kind=='story':
        need(isinstance(result,dict),'Story object required.')
        for key in ('title','premise','hook','cliffhanger'):need(nonempty(result.get(key)),'Missing story '+key)
        need(isinstance(result.get('characters'),list) and len(result['characters'])==2,'Two adult character profiles required.')
        for row in result['characters']:
            need(isinstance(row,dict) and all(nonempty(row.get(k)) for k in ('name','want')),'Character name/want required.')
        need(isinstance(result.get('beats'),list) and len(result['beats'])==3,'Three causal beats required.')
        for row in result['beats']:
            need(isinstance(row,dict) and all(nonempty(row.get(k)) for k in ('id','action','cause','consequence')),'Causal beat fields required.')
    elif kind=='script':
        issues=screenplay_validate(result,60)
        need(not issues,'; '.join(issues))
        need(len(result['scenes'])==2,'Exactly two small screenplay scenes required.')
    elif kind=='direction':
        need(isinstance(result,dict) and isinstance(result.get('findings'),list),'Director findings required.')
        text=json.dumps(source,ensure_ascii=False)
        for row in result['findings']:
            need(isinstance(row,dict) and all(nonempty(row.get(k)) for k in ('criterion','quote','issue','instruction')),'Evidence-based finding required.')
            need(unicodedata.normalize('NFC',row['quote']) in unicodedata.normalize('NFC',text),'Director quote absent from actual source.')
    elif kind=='rewrite':
        need(isinstance(source,dict) and isinstance(source.get('scenes'),list),'Actual source screenplay required.')
        single_object=isinstance(result,dict)
        if single_object:result=[result]
        need(isinstance(result,list) and len(result)==1 and result[0].get('id')=='s2','Only scene s2 may be replaced.')
        merged=copy.deepcopy(source)
        merged['scenes']=[result[0] if r['id']=='s2' else r for r in merged['scenes']]
        need(not screenplay_validate(merged,60),'Revised screenplay violates existing timing/speaker/action-first contract.')
        need(merged['scenes'][0]==source['scenes'][0],'Accepted scene s1 was changed.')
        return dict(scope='CPU micro-benchmark only',normalization='single scene object wrapped as one-element array' if single_object else 'none',merged_screenplay=merged,unchanged_scene_s1=True,production_approved=False)
    elif kind=='dialogue':
        need(isinstance(result,dict) and isinstance(result.get('dialogue'),list) and len(result['dialogue'])==2,'Two dialogue turns required.')
        need(all(isinstance(r,dict) and nonempty(r.get('speaker')) and nonempty(r.get('text')) for r in result['dialogue']),'Speaker/text required.')
    elif kind=='continuity':
        need(isinstance(result,dict) and isinstance(result.get('contradictions'),list),'Contradiction findings required.')
        baseline=json.dumps(source['baseline'],ensure_ascii=False);candidate=json.dumps(source['candidate'],ensure_ascii=False)
        valid=[]
        for row in result['contradictions']:
            need(isinstance(row,dict) and all(nonempty(row.get(k)) for k in ('before','after','issue')),'Before/after evidence required.')
            if row['before'] in baseline and row['after'] in candidate and row['before']!=row['after']:valid.append(row)
        return dict(scope='Controlled metadata contradiction test only',evidence_matched_findings=valid,production_approved=False)
    else:raise AgentError('Unknown micro-benchmark contract.')
    return dict(scope='CPU micro-benchmark only; artistic merit unverified',production_approved=False)
