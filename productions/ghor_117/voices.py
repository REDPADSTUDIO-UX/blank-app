"""Consumer Edge online speech, no Azure API key or billing. Bounded, cached requests."""
import asyncio,json,ssl,hashlib,subprocess
from pathlib import Path
import edge_tts,edge_tts.communicate
P=Path(__file__).parent
ROOT=P.parents[1]/'redpad_media'/'drama'/'ghor117_ep01'
ROOT.mkdir(parents=True,exist_ok=True)
edge_tts.communicate._SSL_CTX.load_verify_locations(cafile=ssl.get_default_verify_paths().cafile)
VOICES={'rafi':'bn-BD-PradeepNeural','echo':'bn-BD-PradeepNeural','mina':'bn-BD-NabanitaNeural','hazera':'bn-BD-NabanitaNeural'}
async def main():
 for s in json.loads((P/'plan.json').read_text())['shots']:
  if not s['text']:continue
  target=ROOT/(s['id']+'.mp3');mark=ROOT/(s['id']+'.voice.json')
  key=hashlib.sha256((s['text']+s['speaker']).encode()).hexdigest()
  if target.exists() and mark.exists() and json.loads(mark.read_text()).get('sha')==key:continue
  if mark.exists() and json.loads(mark.read_text()).get('stage')=='uncertain':raise RuntimeError('Uncertain speech request; inspect before resuming')
  mark.write_text(json.dumps(dict(stage='uncertain',sha=key)))
  pitch='-12Hz' if s['speaker']=='hazera' else '+0Hz'
  rate='-10%' if s['speaker']=='hazera' else '-3%'
  await asyncio.wait_for(edge_tts.Communicate(s['text'],VOICES[s['speaker']],rate=rate,pitch=pitch).save(str(target)),60)
  if target.stat().st_size<1000:raise ValueError('Empty voice')
  mark.write_text(json.dumps(dict(stage='complete',sha=key,voice=VOICES[s['speaker']],provider='Edge consumer speech',cost=0)))
  print('voice',s['id'],s['speaker'],flush=True)
asyncio.run(main())
