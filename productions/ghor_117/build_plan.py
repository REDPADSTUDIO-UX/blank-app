"""Original drama, manually authored here; no paid planner endpoint."""
import json
from pathlib import Path
P=Path(__file__).parent
# 40 shots, 7.5 seconds each. Speaker lines are performed, never narrated directions.
rows=[
('tape','rafi','এই টেপে আমার গলা কেন? আমি তো কথাটা এখনো বলিনি।','reach','hook'),
('door','echo','দরজাটা খুলিস না, রাফি।','listen','breath'),
('rafi_close','rafi','কে? কে কথা বলছে ওখানে?','fear','knocks'),
('title','','','hold','title'),
('arrival','hazera','এই বৃষ্টির মধ্যে আসতে হলো? কাল সকালে আসতি।','talk','rain'),
('two','rafi','কাল অফিস, খালা। বাবার কাগজগুলো নিয়েই চলে যাব।','bag','rain'),
('hazera_close','hazera','তিন মাসে একটা বারও আসলি না। আজ আবার রাত করে।','sad','rain'),
('rafi_close','rafi','এই বাড়িতে ঢুকলেই মনে হয়, বাবা এখনো চেয়ারটায় বসে আছে।','sad','rain'),
('two','hazera','মনে হলে একটু বসিস। মানুষ চলে গেলেই তার ঘর ফাঁকা হয় না।','touch','rain'),
('desk','rafi','চা খাবেন? বানাতে পারি। চিনিটা কোথায় আছে জানি না, এই যা।','smile','cup'),
('hazera_close','hazera','চিনি ছাড়াই খাব। তোর বাবাও শেষে চিনি ছেড়ে দিয়েছিল।','smile','cup'),
('two','rafi','আমাকে তো বলেনি। আমার সাথে সব কথাই কম বলত।','sad','room'),
('hazera_close','hazera','তুই ফোন ধরতি কবে? যাক। রাত বাড়ছে। আমি উঠি।','leave','room'),
('hall','rafi','খালা, ওই ঘরটার চাবি? দোতলার শেষেরটা।','point','metal'),
('door','hazera','তোর বাবা বলেছিল, ওটা যেন না খুলি। তুইও আজ খুলিস না।','warn','room'),
('desk','rafi','আজ খুলিস না মানে? কাল খুললে সমস্যা নাই?','shrug','room'),
('hazera_close','hazera','সব কথার জবাব আমার কাছে নেই, বাবা। দরজাটা লাগিয়ে দিস।','sad','door'),
('desk','rafi','মীনা, পৌঁছেছি। নেটওয়ার্ক বাজে। ফোনটা রাখিস কাছে।','phone','phone'),
('mina','mina','খেয়েছিস? দুপুরেও তো শুধু চা খেয়ে ছিলি।','phone','room'),
('rafi_close','rafi','তুই অডিও নিয়ে কাজ করিস, না আমার খাবারের হিসাব রাখিস?','smile','room'),
('mina','mina','দুইটাই। কেউ তো রাখবে। কাগজপত্র পেলে ছবি পাঠাস।','smile','room'),
('desk','rafi','এই দেখ, বাবার পুরোনো টেপ। লেবেলে আমার নাম।','reach','metal'),
('mina','mina','শুনে দেখ। আঙ্কেলের গলা থাকলে আমাকে পাঠাবি।','soft','room'),
('tape','','','play','tape'),
('desk','rafi','এখানে কে রেকর্ড করেছে? মীনা, তুই শুনতে পাচ্ছিস?','listen','tape'),
('door','echo','ওটা বন্ধ কোরো না।','hold','breath'),
('rafi_close','rafi','মীনা? তুই এখানে? একটু আগে তো ফোনে ছিলি!','fear','room'),
('hall','rafi','খালা? আপনি এখনো যাননি?','walk','steps'),
('door','rafi','ভেতরে কেউ থাকলে কথা বলেন। তালা লাগানো কেন?','reach','knocks'),
('tape','echo','আমি তো আজই এলাম।','spin','tape'),
('rafi_close','rafi','এটা আমার গলা। না, এটা কোনো পুরোনো রেকর্ডিং।','fear','breath'),
('desk','rafi','এখানে রেকর্ড বোতামটাই ভাঙা। তাহলে শব্দটা আসছে কোথা থেকে?','inspect','metal'),
('mina','mina','হ্যালো? লাইন কেটে গেল কেন? তুই এত হাঁপাচ্ছিস কেন?','concern','phone'),
('rafi_close','rafi','মীনা, তুই কোথায়? সত্যি করে বল। এই বাড়িতে আসিসনি তো?','phone','room'),
('mina','mina','আমি বাসায়। তোর কী হয়েছে? তুই চাইলে এখনই আসব।','concern','room'),
('desk','rafi','না। একটা টেপে আমার গলা শুনছি। যে কথা আমি বলিনি।','fear','tape'),
('mina','mina','ফোনটা স্পিকারে দে। আর টেপটা একটু পেছনে নে। আমি শুনি।','listen','room'),
('tape','echo','মীনা, নিচে পানি। আমি দরজাটা খুলছি।','spin','drip'),
('door','rafi','মীনা... সত্যিই পানি আসছে। কিন্তু বৃষ্টি তো থেমে গেছে।','back','drip'),
('rafi_close','mina','রাফি, ওটা খুলিস না। আমি তোকে কথাটা এখনো বলিনি!','fear','knocks'),
]
shots=[dict(id=f'{i+1:03}',start=i*7.5,seconds=7.5,view=v,speaker=s,text=t,action=a,sfx=f) for i,(v,s,t,a,f) in enumerate(rows)]
plan=dict(title='ঘর ১:১৭ — পর্ব ১: না-বলা কথা',series='ঘর ১:১৭',episode=1,seconds=300,language='bn-BD',channel_id='UCtbHkj0GwJxjXZWbItDAyuQ',rights='Original REDPAD fictional story; no Humayun Ahmed adaptation rights established or used.',output_kind='Procedural 2D puppet animation with neural Bengali dialogue; not photorealistic generative video',shots=shots)
(P/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
text='# ঘর ১:১৭ — পর্ব ১: না-বলা কথা\n\nদৈর্ঘ্য ৫ মিনিট। মৌলিক গল্প। কোনো গল্পকথক নেই। 2D অ্যানিমেটেড নাটক।\n\n'
for s in shots:
 text+=f"## {s['start']:05.1f}–{s['start']+7.5:05.1f} সেকেন্ড · {s['view']}\nঅভিনয়: {s['action']}। শব্দ: {s['sfx']}।\n\n{s['speaker'] or 'শুধু দৃশ্য ও শব্দ'}: {s['text']}\n\n"
(P/'screenplay.md').write_text(text)
print('40 shots /',sum(s['seconds'] for s in shots),'seconds')
