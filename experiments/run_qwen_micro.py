"""Real short creative trials after the larger architecture exceeded CPU time budget."""
import copy,json,sys
from redpad_pipeline.local_ollama_session import local_cpu_session
from redpad_pipeline.cpu_creative_trial import call,FOLDER

BRIEF=dict(title='একটা ছাতা',premise='ঢাকার বৃষ্টির সকাল। রাশেদ (৩২) ও তানিয়া (২৯) বিবাহিত। তানিয়ার চাকরির সাক্ষাৎকার, রাশেদের অফিসে জরুরি উপস্থিতি; একটি ছাতা আর সীমিত বাসভাড়া। তাদের অভ্যাসের তফাতে স্বাভাবিক রসিকতা ও মমতা আছে। বাস্তব সিদ্ধান্তে সমস্যা সামলাবে; জোর করা কাকতাল বা নীতিকথা নয়।',genre='family drama',tone='natural Bangladeshi Bengali, restrained emotion, gentle character wit')

def load(name):return json.loads((FOLDER/(name+'.json')).read_text())['result']
def story():return call('trial_story_compact','story','তিনটি causal beat-এ মূল গল্প তৈরি করুন। প্রতিটি text field সর্বোচ্চ এক ছোট বাক্য। একই বিবাহিত দম্পতি, স্পষ্ট সকাল ও ছাতার অবস্থান বজায় রাখুন। Return {"title":str,"premise":str,"characters":[{"name":str,"want":str},{"name":str,"want":str}],"beats":[{"id":"b1","action":str,"cause":str,"consequence":str},{"id":"b2","action":str,"cause":str,"consequence":str},{"id":"b3","action":str,"cause":str,"consequence":str}],"hook":str,"cliffhanger":str}. একটি যৌক্তিক ছোট পরিবর্তন; অনর্থক রহস্য নয়।',brief=BRIEF,max_tokens=1200,micro_kind='story')
def script():return call('trial_script_compact','script','Write a 60-second Bengali screenplay in exactly TWO scenes, s1 and s2, 30 seconds each. Use only রাশেদ and তানিয়া. Scene1 inside breakfast room, scene2 at the front door. Action before dialogue; 2–3 SHORT dialogue turns per scene. Natural affection, small habit-based wit; no moral speech, random relatives, vehicle or location teleportation. Ending is a small concrete choice, not generic philosophy. Return {"title":str,"hook":{"image":str,"question":str,"payoff":str},"characters":[{"name":str,"want":str,"voice":str}],"scenes":[{"id":str,"heading":"INT. ...","seconds":30,"objective":str,"obstacle":str,"turn":str,"consequence":str,"beats":[{"type":"action","text":str},{"type":"dialogue","speaker":str,"text":str}],"sound":{"music":str,"sfx":str}}]}. All prose and dialogue in Bangla. Keep every metadata field one SHORT phrase.',brief=BRIEF,source=load('trial_story_compact'),max_tokens=1800,micro_kind='script')
def director():return call('trial_director_compact','director','Review the ACTUAL source screenplay critically. Return {"strengths":[str],"findings":[{"criterion":str,"quote":str,"issue":str,"instruction":str}]}. Up to THREE issues. Criteria: logic, natural Bengali dialogue, emotion, humor, hook/cliffhanger, pacing. Quote COPY EXACTLY from source. Prefer concrete problems to praise. If wording is unnatural, explain a specific colloquial alternative. This is model criticism, not human approval.',brief=BRIEF,source=load('trial_script_compact'),max_tokens=1200,micro_kind='direction')
def rewrite():
 source=load('trial_script_compact');review=load('trial_director_revision') if (FOLDER/'trial_director_revision.json').exists() else load('trial_director_compact')
 return call('trial_script_revision','script','Return a JSON ARRAY containing ONLY revised scene s2, same complete scene fields and 30 seconds. Keep s1 and the two character names unchanged. Apply only relevant criticism: '+json.dumps(review,ensure_ascii=False)+'. Additional observed defect to fix ONLY in s2: bus fare is money, not a building/location. s2 is the actual front door of their rented home; keep time morning and make the umbrella handoff and choice physically coherent. Preserve the existing source character identities for this isolated scope test; global name corruption is a separate Story revision. Dialogue must be colloquial Bengali, 2–3 short turns. Replace exposition or vague sentiment with visible action and understated warmth. Do not add characters, cars, vehicles or unexplained money. Do not rewrite s1 or the outer screenplay.',brief=BRIEF,source=source,targets=['s2'],max_tokens=1100,micro_kind='rewrite')
def dialogue_revision():
 original=json.loads((FOLDER/'cpu_smoke.json').read_text())['result']
 return call('trial_dialogue_revision','script','আগের সংলাপের “বাবার চোখে দেখি না” অর্থহীন এবং নাস্তার প্রসঙ্গ হারিয়েছে। কেবল দুই লাইন নতুন করে লিখুন: মা ছেলেকে আরেকটা পরোটা দিতে চাইছেন; ছেলে অফিসে দেরি হচ্ছে বলে মায়ের বাড়তি যত্ন নিয়ে আদরভরা হালকা রসিকতা করে। বাবা, মৃত্যু, অনুপস্থিত আত্মীয় বা নতুন তথ্য আনবেন না। স্বাভাবিক কথ্য বাংলাদেশি বাংলা; জোর করে punchline নয়। Return {"dialogue":[{"speaker":"মা","text":str},{"speaker":"ছেলে","text":str}]}.',source=original,max_tokens=256,micro_kind='dialogue')
def continuity():
 base=load('trial_script_compact');candidate=copy.deepcopy(base)
 changed=False
 for beat in candidate['scenes'][1]['beats']:
  if beat.get('type')=='dialogue':
   beat['speaker']='মিতু' if beat.get('speaker')!='মিতু' else 'শীলা';changed=True;break
 if not changed:raise RuntimeError('No dialogue turn available for a controlled identity perturbation.')
 return call('trial_continuity','director','Compare baseline with candidate. Identify changed speaker identity in scene s2 without assuming a new character is authorized. Return {"contradictions":[{"before":str,"after":str,"issue":str}]}. Cite EXACT before and after values. Keep answer concise; do not invent other defects.',source={'baseline':base,'candidate':candidate},max_tokens=512,micro_kind='continuity')
def horror():return call('trial_horror_compact','story','একটি মৌলিক বাংলাদেশি horror ধারাবাহিকের তিনটি connected episode beat লিখুন। রাফি (৩৩) ও হাজেরা (৬০), পুরোনো ঢাকার বাড়ি, পিতলের চাবি। প্রত্যেক episode-এ ভিন্ন causal সিদ্ধান্ত এবং একটি ছোট payoff থাকবে; শুধু “ছায়া দেখল” পুনরাবৃত্তি নয়। কোনো গবেষণা করার দাবি নয়। Return {"title":str,"premise":str,"characters":[{"name":str,"want":str},{"name":str,"want":str}],"beats":[{"id":"e1","action":str,"cause":str,"consequence":str},{"id":"e2","action":str,"cause":str,"consequence":str},{"id":"e3","action":str,"cause":str,"consequence":str}],"hook":str,"cliffhanger":str}. প্রতিটি text field একটি ছোট বাক্য।',max_tokens=1200,micro_kind='story')


def story_revision():
 source=load('trial_story_compact')
 return call('trial_story_revision','story','এই source-এ verified text defects আছে: “তানিiflowerা” চরিত্রের ভুল নাম; সঠিক নাম তানিয়া। “বাসভাড়া থেকে বাইরে যায়” অর্থহীন—বাসভাড়া হলো টাকা, জায়গা নয়। সাক্ষাৎকারে গিয়ে হঠাৎ স্ক্রিনে ছাতা দেখা কোনো প্রতিষ্ঠিত ঘটনার ফল নয়। তিনটি beat পুরো সংশোধন করুন। সব ঘটনা এখন বাসার ঘর ও সামনের দরজায় সীমিত রাখুন; কোনো স্ক্রিন, রহস্যময় ব্যক্তি বা teleportation নয়। প্রতিটি cause আগের action-এর সরাসরি ফল। দুই চরিত্র ঠিক রাশেদ ও তানিয়া। পরস্পরের ছোট অভ্যাসে মমতা থাকবে, বক্তৃতা নয়। শেষ beat-এ একটি বাস্তব যৌথ সিদ্ধান্ত থাকবে; নতুন অবাস্তব mystery নয়। Return the SAME story JSON keys, characters list and exactly THREE beats. Keep all Bengali fields short, spell names EXACTLY as supplied. No Latin letters inside character names.',brief=BRIEF,source=source,max_tokens=1200,micro_kind='story',temperature=.2)


def director_revision():
 source=load('trial_script_compact')
 return call('trial_director_revision','director','আগের review-এ quote বানানো হয়েছে এবং ভুল grammar পরামর্শ ছিল। এবার শুধু TWO findings লিখুন, প্রতিটিতে issue ও instruction একটি ছোট বাংলা বাক্য। প্রথম quote হুবহু “INT. বাসভাড়া - সকাল”; দ্বিতীয় quote হুবহু “তানিiflowerা”। এগুলো actual source-এ আছে—কোনো নাম বা শব্দ যোগ করবেন না। Return {"strengths":[],"findings":[{"criterion":"dialogue","quote":str,"issue":str,"instruction":str},{"criterion":"logic","quote":str,"issue":str,"instruction":str}]}. বাসভাড়া টাকা, স্থান নয়; চরিত্রের মিশ্র-অক্ষরের বিকৃত নামও লক্ষ্য করুন। নতুন ঘটনা, midnight, hat বা তথ্য বানাবেন না। কোনো numeric score বা approval নয়।',brief=BRIEF,source=source,max_tokens=512,micro_kind='direction',temperature=.2)

if __name__=='__main__':
 with local_cpu_session():
  for step in sys.argv[1:] or ['story','script','director']:
   {'story':story,'script':script,'director':director,'rewrite':rewrite,'dialogue':dialogue_revision,'continuity':continuity,'horror':horror,'story_revision':story_revision,'director_revision':director_revision}[step]()
