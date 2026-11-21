"""Run only the explicitly approved installed Qwen model. No download or paid service."""
import json,sys
from redpad_pipeline.local_ollama_session import local_cpu_session
from redpad_pipeline.cpu_creative_trial import call,FOLDER
from redpad_pipeline.phase3 import shape
from redpad_pipeline.creative_ui import samples

BRIEF=dict(title='একটা ছাতা',premise='ঢাকার ভাড়া বাসায় রাশেদ (৩২) ও তানিয়া (২৯), বিবাহিত দম্পতি। বৃষ্টির সকালে দুজনের জরুরি কাজ, একটি ছাতা, হাতে সীমিত বাসভাড়া। তানিয়ার চাকরির ইন্টারভিউ, রাশেদের কাজে উপস্থিত থাকা জরুরি। তাদের ছোট অভ্যাসে রসিকতা আছে; অর্থের চাপ মুখে স্বীকার করতে পারে না। বাস্তবসম্মত যৌথ সিদ্ধান্তে সম্পর্ক বদলাবে।',genre='family romance',tone='সংযত আবেগ, স্বাভাবিক দাম্পত্য উষ্ণতা ও চরিত্রভিত্তিক রসিকতা; coincidence নয়',episodes=3,episode=1,seconds=300)

def run_story():
 template=shape(samples()['romance_season']);template['episodes']=template['episodes'][:3]
 return call('trial_story','story','Create a complete original THREE-episode compact architecture using the supplied schema. Each text field ONE short Bengali sentence. Two adult characters only; honor the brief. Hook types: curiosity/conflict/character/emotional/mystery/reversal/visual. Ending types: suspense/emotional/relationship/reveal/moral_dilemma/decision/resolution. Distinct choices cause each next episode. No copied generic emotional slogans. Research status original/unverified, never invent citations. Schema: '+json.dumps(template,ensure_ascii=False),kind='season',brief=BRIEF,max_tokens=3072)

def run_script():
 story=json.loads((FOLDER/'trial_story.json').read_text())['result']
 template=shape(samples()['screenplay'])
 prompt='Write Episode 1 as a filmable approximate 300-second Bengali screenplay, exactly 3 scenes (30,120,150 seconds), with sequential IDs s1,s2,s3. Opening visible action before dialogue. Clear morning chronology, same married couple, no extra mysterious relatives. Include natural colloquial speech, small everyday humor, pauses and an earned ending. Avoid exposition/sermons. Each scene metadata concise; aim for 12–18 dialogue turns total and meaningful physical actions. Estimate timing honestly; do not fill time with arbitrary silence. Preserve the schema fields. Hook types curiosity/conflict/character/emotional/mystery/reversal/visual; ending types suspense/emotional/relationship/reveal/moral_dilemma/decision/resolution. Ending setup_scene_ids must name real scene IDs. Schema: '+json.dumps(template,ensure_ascii=False)
 return call('trial_script','script',prompt,kind='screenplay',brief=BRIEF,source=story,max_tokens=4096)

def run_director():
 script=json.loads((FOLDER/'trial_script.json').read_text())['result']
 template=shape(samples()['direction_script'])
 prompt='Critically review EVERY source scene, covering all schema fields. COPY evidence quotes verbatim from source. Identify weak motivation, unnatural Bengali, forced humor, time padding and unearned hook/ending. Give precise story/script revision notes with target scene IDs. Do not praise automatically. Humor_type natural/witty/situational/emotional/none/forced. Performance intensity integer 1–10. Every observation is model editorial opinion, not independent human review. Keep each field one SHORT sentence. Schema: '+json.dumps(template,ensure_ascii=False)
 return call('trial_director','director',prompt,kind='direction',brief=BRIEF,source=script,max_tokens=3072)

if __name__=='__main__':
 with local_cpu_session():
  for step in sys.argv[1:] or ['story','script','director']:
   {'story':run_story,'script':run_script,'director':run_director}[step]()
