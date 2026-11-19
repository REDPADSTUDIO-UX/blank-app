"""Explicit owner-scoped budget amendment. No model/runtime/network operations."""
import copy
import hashlib
import json

AUTHORIZATION='owner-story-total8-five-sections-20261119'
SECTIONS=('foundation','act_1','act_2','act_3','reflection')

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate(ledger,baseline):
    if baseline['ceiling']!=7 or len(baseline['historical'])!=2 or len(baseline['new_calls'])!=1:
        raise ValueError('Exact three-consumed-call baseline required')
    if baseline['new_calls'][0]['id']!='driverbound_canary_v1' or baseline['new_calls'][0]['state']!='completed':
        raise ValueError('Successful genuine canary baseline required')
    if ledger['ceiling']!=8 or ledger.get('authorization')!=AUTHORIZATION:
        raise ValueError('This benchmark requires the exact explicit ceiling-eight authorization')
    if ledger['historical']!=baseline['historical'] or ledger['new_calls'][:1]!=baseline['new_calls']:
        raise ValueError('Historical calls or completed canary changed')
    extra=ledger['new_calls'][1:]
    if len(extra)>5:
        raise ValueError('Five additional calls exhausted')
    for section,entry in zip(SECTIONS,extra):
        if entry['section']!=section or entry['id']!='driverbound_'+section+'_v1':
            raise ValueError('Mandatory section order/attempt identity changed')
    return extra

def authorize(ledger,baseline,authorization):
    if authorization!=AUTHORIZATION:
        raise ValueError('Missing exact owner budget authorization')
    if ledger==baseline:
        upgraded=copy.deepcopy(ledger)
        upgraded.update(ceiling=8,authorization=AUTHORIZATION,
          amendment={'previous_ceiling':7,'revised_ceiling':8,'consumed_at_authorization':3,
                     'baseline_sha256':digest(baseline),'scope':'Five mandatory Story sections only'})
    else:
        upgraded=copy.deepcopy(ledger)
    validate(upgraded,baseline)
    return upgraded

def reserve(ledger,baseline,section,payload,*,context_tokens=4096,timeout_seconds=240):
    extra=validate(ledger,baseline)
    if len(extra)>=5:
        raise ValueError('Eight-call ceiling exhausted')
    if section!=SECTIONS[len(extra)]:
        raise ValueError('Cannot skip, repeat or substitute mandatory sections')
    if any(entry['state']!='completed' for entry in extra):
        raise ValueError('Required previous section is incomplete; inspect preserved failure')
    if payload.get('max_tokens')!=1536 or context_tokens!=4096 or timeout_seconds!=240:
        raise ValueError('Per-call token/context/time limits must remain unchanged')
    result=copy.deepcopy(ledger)
    result['new_calls'].append({'id':'driverbound_'+section+'_v1','section':section,
      'state':'submitted','payload_sha256':digest(payload)})
    return result
