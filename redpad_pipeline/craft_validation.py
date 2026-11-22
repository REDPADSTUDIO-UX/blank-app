"""Observable screenplay protocol checks, not an artistic scoring model."""
import re,unicodedata

def canonical(text):return unicodedata.normalize('NFC',text).strip()

def dialogue_findings(script):
    items=lambda value:value if isinstance(value,list) else []
    names=[c['name'] for c in items(script.get('characters')) if isinstance(c,dict) and isinstance(c.get('name'),str)]
    findings=[]
    for s in items(script.get('scenes')):
        if not isinstance(s,dict):continue
        for i,b in enumerate(items(s.get('beats'))):
            if not isinstance(b,dict) or not isinstance(b.get('text'),str):continue
            text=b['text'];path=f"{s.get('id','?')}/beats/{i}"
            if b.get('type')=='dialogue':
                for name in names:
                    if re.match(r'^\s*'+re.escape(name)+r'\s*(?:(?:হেসে|মুচকি হেসে|কেঁদে)\s+)?(?:বলে|বলল|বললো|:)',text):
                        findings.append({'code':'narrated_dialogue','path':path,'evidence':text,'repair':'Keep only the direct utterance under its declared speaker; preserve the raw original.'});break
            if b.get('type')=='action' and re.search(r'''(?:বলে|বলল|বললো)[,\s]*["'“]''',text):
                findings.append({'code':'speech_in_action','path':path,'evidence':text,'repair':'Split speech into a dialogue beat with the correct declared speaker.'})
    return findings

def unchanged_requested_lines(source,replacement,fields):
    """Only for an explicit instruction to change these exact fields, not all rewrites."""
    return [f for f in fields if isinstance(source.get(f),str) and isinstance(replacement.get(f),str) and canonical(source[f])==canonical(replacement[f])]
