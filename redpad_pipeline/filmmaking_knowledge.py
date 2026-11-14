"""Bounded offline craft retrieval; immutable run provenance, no weight training.
Only reviewed, repository-owned modules enter conditioning. Project data remains
untrusted and cannot become a knowledge instruction or authorize an action.
"""
import hashlib,json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'assets/filmmaking/knowledge.json'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()

def load():
    data=json.loads(CATALOG.read_text())
    roles={x['key'] for x in json.loads((ROOT/'redpad_pipeline/agent_catalog.json').read_text())}
    if set(data['modules'])!=roles:raise ValueError('Knowledge must cover exactly the registered agents.')
    ids=set()
    for role,module in data['modules'].items():
        if not module['source_ids'] or any(data['sources'].get(s,{}).get('status')!='allowed' for s in module['source_ids']):raise ValueError('Unapproved knowledge source.')
        if set(module['cross_department_contracts'])-roles:raise ValueError('Unknown department reference.')
        for lesson in module['lessons']:
            if lesson['id'] in ids or not lesson['id'].startswith(role+'.') or not lesson['instruction'].strip():raise ValueError('Invalid knowledge lesson identity.')
            ids.add(lesson['id'])
    return data

def tokens(value):
    return set(re.findall(r'[^\W_]+',unicodedata.normalize('NFC',str(value)).casefold()))

def verify(pack):
    if not isinstance(pack,dict) or pack.get('context_sha256')!=digest({k:v for k,v in pack.items() if k!='context_sha256'}):raise ValueError('Knowledge snapshot integrity failed.')
    return pack

def retrieve(role,query='',*,limit=3):
    if type(limit) is not int or not 1<=limit<=3:raise ValueError('Retrieve one to three department lessons.')
    data=load()
    if role not in data['modules']:raise ValueError('Unknown knowledge department.')
    m=data['modules'][role];words=tokens(str(query)[:20000])
    ranked=sorted(m['lessons'],key=lambda l:(-len(words & tokens(' '.join(l['tags'])+' '+l['instruction'])),l['id']))[:limit]
    pack={'version':data['version'],'bundle_sha256':digest(data),'role':role,'method':data['method'],
          'common':data['common'],'lessons':ranked,'rubric':m['rubric'],'original_example':m['original_example'],
          'example_scope':'Teaching fixture only; never import names, dialogue or plot as project facts.',
          'cross_department_contracts':m['cross_department_contracts'],
          'sources':{s:data['sources'][s] for s in m['source_ids']},'human_review_required':True,'weight_training_completed':False}
    if role=='voice':
        lexicon=json.loads((CATALOG.parent/'voice_lexicon.json').read_text())
        pack['pronunciation_guidance']={'version':lexicon['version'],'sha256':digest(lexicon),
            'entries':[e for e in lexicon['entries'] if e['term'] in str(query)[:20000]],
            'listening_review_completed':False,'scope':'Text guidance for terms present in the request only; no text replacement or voice cloning.'}
    if len(json.dumps(pack,ensure_ascii=False))>8500:raise ValueError('Knowledge context exceeds bounded budget.')
    pack['context_sha256']=digest(pack)
    return pack

def snapshot(store,run,role,query):
    with store.tx() as db:
        db.execute('CREATE TABLE IF NOT EXISTS filmmaking_knowledge_runs(run TEXT PRIMARY KEY,role TEXT,payload TEXT,sha256 TEXT)')
        old=db.execute('SELECT role,payload,sha256 FROM filmmaking_knowledge_runs WHERE run=?',(run,)).fetchone()
        if old:
            pack=verify(json.loads(old['payload']))
            if old['role']!=role or pack['role']!=role or old['sha256']!=pack['context_sha256']:raise ValueError('Knowledge run binding differs.')
            return pack
        pack=retrieve(role,query)
        db.execute('INSERT INTO filmmaking_knowledge_runs VALUES (?,?,?,?)',(run,role,json.dumps(pack,ensure_ascii=False),pack['context_sha256']))
        return pack

def condition(system,pack):
    verify(pack)
    return system+'\nCURATED CRAFT GUIDANCE (contract and approved source facts take precedence):\n'+json.dumps(pack,ensure_ascii=False)+'\nDo not output the guidance or teaching example; create the requested original artifact only.'

def readiness():
    data=load()
    return {'version':data['version'],'bundle_sha256':digest(data),'method':data['method'],
            'agents':[{'agent':role,'lessons':len(m['lessons']),'rubric':[r['criterion'] for r in m['rubric']],
                       'sources':m['source_ids'],'actual_creative_acceptance':False} for role,m in data['modules'].items()],
            'weight_training_completed':False,'human_review_completed':False}
