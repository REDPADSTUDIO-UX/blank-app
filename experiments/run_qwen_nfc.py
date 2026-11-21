"""Four controlled post-fix retests. Same model, device, seed, temperature and tasks.
Only the canonical Unicode input preprocessing and matching are fixed.
"""
import json,sys
from redpad_pipeline.local_ollama_session import local_cpu_session
from redpad_pipeline.cpu_creative_trial import call,FOLDER


def repeat(previous,name,kind,source_override=None):
 old=json.loads((FOLDER/(previous+'.json')).read_text());request=old['request'];options=old['evidence']['options']
 return call(name,old['agent'],request['instructions'],brief=request['brief'],source=source_override if source_override is not None else request['experimental_source'],targets=request['targets'],max_tokens=options['num_predict'],temperature=options['temperature'],micro_kind=kind,task_last=old.get('prompt_layout')=='source_first_task_last')

if __name__=='__main__':
 with local_cpu_session():
  story=repeat('trial_story_compact','trial_story_nfc','story')
  script=repeat('trial_script_compact','trial_script_nfc','script',story['result'])
  repeat('trial_director_compact','trial_director_nfc','direction',script['result'])
  repeat('trial_dialogue_revision','trial_dialogue_nfc','dialogue')
