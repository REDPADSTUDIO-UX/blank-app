"""One original manually authored acceptance project, NOT model output.
All QC/owner decisions in run_fixture are SIMULATED SOFTWARE TEST decisions.
Never use run_fixture against an existing owner production project.
"""
import copy,json
from pathlib import Path
from .agents import AgentError,encode
from .creative import digest
from .story_bridge import StoryBridge
from .specialists import example
from .specialist_project import queue_project,DEPENDENCIES
from .production_execution import ProductionOps

TITLE='ফিরতি টিকিট'
BRIEF='ঢাকার কাঁঠালবাগানে নীরা রাজশাহীর চাকরিতে যাবে। দর্জি বাবা হাসান তার ব্যাগ সারান, একা থাকার ভয় লুকান। বাসের টিকিট লাল টিনের বাক্সে। মায়ের সেলাই সমিতির পুরোনো হিসাবের গরমিল বাবা-মেয়েকে সিদ্ধান্তের মুখে ফেলে। তদন্তে সাক্ষ্য ও consent লাগবে; অলৌকিক উদ্ধার নয়।'
PLOTS=[
 'নীরা টিকিটের নিচে মায়ের নামে কিস্তির রসিদ পায়; বাস পিছিয়ে বাবার কাছে হিসাব চায়।',
 'বাবা সদস্যদের ঠিকানা দিতে অস্বীকার করায় নীরা প্রথমে মায়ের পুরোনো সহকর্মী মিতার অনুমতি চায়।',
 'মিতা নিজের খাতা দেখিয়ে জমার তারিখ মেলান; একই মাসের দুটো নম্বর দেখে নীরা কপি রাখার অনুমতি চায়।',
 'কপির বদলে মূল খাতা চাইলে মিতা না বলেন; নীরা মালিকানার শর্ত মেনে ছবি তোলার consent নেয়।',
 'ছবিতে বাবার স্বাক্ষর দেখে নীরা তাঁকে জেরা করে; তিনি বলেন টাকা তুলেছিলেন, কিন্তু প্রাপকের নাম বলেন না।',
 'জেরায় আহত বাবা দোকান বন্ধ করেন; নীরা অভিযোগ থামিয়ে দোকানের বকেয়া কাজ শেষ করতে বসে।',
 'বকেয়া জামা দিতে গিয়ে নীরা সমিতির আরেক সদস্যের বেতন আটকে থাকার কথা শোনে; সাক্ষাৎ চায়।',
 'সদস্য সাক্ষ্যে রাজি হন শুধু নাম গোপন রাখলে; নীরা প্রকাশের বদলে হিসাবের তারিখ যাচাই করে।',
 'তারিখে মায়ের অসুস্থতার দিন মিলে যাওয়ায় নীরা নিজের সন্দেহ সংশোধন করে; বাবার সঙ্গে হাসপাতালে যায়।',
 'হাসপাতালের পুরোনো বিল পেতে পরিচয় ও অনুমতি লাগে; বাবা নিজে আবেদন করেন, মেয়েকে অপেক্ষা করতে বলেন।',
 'অপেক্ষায় চাকরির যোগদানের সময় ফুরোয়; নীরা নিয়োগকর্তাকে সত্য জানিয়ে সময় বাড়ানোর আবেদন করে।',
 'সময় মেলে না; নীরা চাকরিতে যোগ দেয়, বাবাকে হিসাবের কপি পাঠানোর অনুরোধ করে।',
 'দূরত্বে বাবা কপি পাঠান কিন্তু একটি পাতায় কালির দাগ; নীরা মিতাকে স্বাধীনভাবে মিলিয়ে দিতে বলে।',
 'মিতা দাগকে অপরাধের প্রমাণ মানতে অস্বীকার করেন; নীরা সন্দেহ আর তথ্য আলাদা খাতায় লেখে।',
 'স্বতন্ত্র খাতায় জমা আছে, কিন্তু বাবার রসিদে কম; নীরা বাবাকে মিতার সামনে কথা বলতে আমন্ত্রণ জানায়।',
 'বাবা জানান সদস্যের চিকিৎসায় জরুরি টাকা দিয়েছিলেন; লিখিত অনুমতি ছিল না বলে দায় স্বীকার করেন।',
 'সাহায্যপ্রাপ্ত সদস্য নিজের গোপন অসুখ প্রকাশ চান না; নীরা হিসাব মেরামতের এমন পথ চায় যাতে পরিচয় না ফাঁসে।',
 'মিতা নাম মুছে সমষ্টিগত হিসাবের প্রস্তাব দেন; কয়েক সদস্য স্বচ্ছতার জন্য মূল নথি দেখতে চান।',
 'বাবা ব্যক্তিগত সঞ্চয় ফেরত দিতে চান; নীরা ক্ষতি ঢেকে রাখা আর হিসাব মেলানো আলাদা বলে সভা ডাকে।',
 'সভায় নীরা নিজের ভুল অভিযোগ আগে স্বীকার করে; সদস্যরা স্বাধীন হিসাবরক্ষক চান।',
 'ফি জোগাতে সমিতি খরচ কমায়; নীরা নিজের চাকরির টাকা না ঢেলে অনুমোদিত বাজেট লিখে দেয়।',
 'হিসাবরক্ষক বিলের সঙ্গে একটি অনাথ অঙ্ক পান; বাবা স্মৃতির বদলে ব্যাঙ্কের নথি চান।',
 'ব্যাঙ্কে পুরোনো হিসাবের উত্তরাধিকার প্রক্রিয়া লাগে; নীরা বৈধ কাগজ জমা দিয়ে অপেক্ষা করে।',
 'অপেক্ষায় রটনা ছড়ায়; মিতা সদস্যের পরিচয় রক্ষা করে শুধু যাচাইকৃত অঙ্ক প্রকাশ করেন।',
 'নথিতে দ্বিগুণ কাটা সার্ভিস চার্জ ধরা পড়ে; নীরা ব্যাঙ্কে লিখিত সংশোধনের আবেদন করে।',
 'ব্যাঙ্ক ভুল মেনে ফেরত দেয়, কিন্তু বাবার অনুমতিহীন ধার থেকে যায়; তিনি কিস্তিতে ফেরতের প্রস্তাব দেন।',
 'সদস্যরা প্রস্তাব গ্রহণের আগে নতুন নিয়ম চান; মিতা দ্বৈত স্বাক্ষর ও জরুরি তহবিলের সীমা লেখেন।',
 'বাবা নিয়মে সই করেন; নীরা বুঝতে পারে ভুল স্বীকারের সাহসকে নিখুঁত বাবা বানানোর দরকার নেই।',
 'সমিতি নতুন তহবিল চালু করে; নীরা পরের ফিরতি টিকিট নিজে কিনে বাবাকে আগে জানায়।',
 'হাসান মেয়ের ব্যাগ না খুলে জিজ্ঞেস করেন মেরামত লাগবে কি না; নীরা চাবি রেখে সম্মতি দিয়ে বাড়ি ফেরার সম্পর্কটি নতুন করে বেছে নেয়।']

def bible():
    chars=[dict(id='nira',name='নীরা',biography='২৭, প্রথম স্থায়ী চাকরি পেয়েছে।',want='চাকরিতে যোগ দেওয়া',need='সাহায্য ও নিয়ন্ত্রণের পার্থক্য বোঝা',internal_conflict='বাবাকে ছেড়ে যাওয়ার অপরাধবোধ',relationship_arc='অভিযোগ থেকে প্রাপ্তবয়স্ক সমঝোতা'),
           dict(id='hasan',name='হাসান',biography='৫৮, কাঁঠালবাগানের দর্জি।',want='মেয়েকে স্বাধীন দেখতে চান',need='একাকিত্ব স্বীকার করা',internal_conflict='যত্নে নিয়ন্ত্রণ ঢুকে পড়ে',relationship_arc='গোপন রাখা থেকে দায় স্বীকার'),
           dict(id='mita',name='মিতা',biography='৪৬, সেলাই সমিতির সদস্য।',want='সদস্যদের টাকা ও গোপনীয়তা রক্ষা',need='বিশ্বাসের সঙ্গে লিখিত জবাবদিহি',internal_conflict='বন্ধুর প্রতি আনুগত্য বনাম সাক্ষ্য',relationship_arc='মধ্যস্থতা থেকে স্বাধীন তত্ত্বাবধান')]
    return dict(id='series-bible',title=TITLE,logline='চাকরিতে যাওয়ার সকালে মায়ের পুরোনো রসিদ পেয়ে মেয়েকে বাবার যত্নের ভিতরে থাকা ভুলের দায় আলাদা করতে হয়।',premise=BRIEF,conflict='পরিবারের বিশ্বাস বনাম সদস্যদের জবাবদিহি',season_arc='হিসাবের রহস্য স্বচ্ছ সম্মতিতে সম্পর্ক বদলায়।',ending_strategy='সব রহস্য নয়, স্বাধীন যত্নের সিদ্ধান্তে সম্পর্কের সমাপ্তি।',feasibility='ঘর, দোকান, সমিতির ছোট সভা; অনুমতিসাপেক্ষ নথি, স্বল্পলোকেশন।',characters=chars,rules=['রসিদ দেখার আগে নীরা সেটির কথা জানে না।','বিনা consent-এ নথি প্রকাশ নয়।'],initial_state={'event':'চাকরির টিকিট বাক্সে','knowledge':'নীরা পুরোনো রসিদ জানে না'})

def outlines():
    before=bible()['initial_state'];out=[]
    for n,plot in enumerate(PLOTS,1):
        after={'event':plot,'knowledge':'নীরা জানে: '+plot.split(';')[0]}
        out.append(dict(number=n,hook={'type':'character','image':'ব্যাগের সেলাই ও হিসাবের পাতায় কাজের চিহ্ন।','question':'সম্পর্ক অটুট রেখে এই সিদ্ধান্তের দায় কীভাবে নেবে?','promise':'তথ্য থেকে সিদ্ধান্তের পরিণতি'},ending={'type':'decision','payoff':plot,'question':'এই সিদ্ধান্তে পরের আলোচনায় কী মূল্য দিতে হবে?','next_connection':PLOTS[n] if n<30 else 'নতুন সম্পর্কের স্বাভাবিক জীবন','earned_by':plot},reveals=[plot],objective=plot,cause='শুরুতে চাকরির প্রস্তুতি' if n==1 else PLOTS[n-2],development=plot,escalation='সিদ্ধান্তের ব্যবহারিক ও সম্পর্কের মূল্য: '+plot,payoff=plot,character_change='নীরা সন্দেহের বদলে consent ও যাচাইয়ের পথ বেছে নেয়: '+str(n),state_before=copy.deepcopy(before),state_after=after,knowledge_changes=[{'character':'nira','fact':plot,'learned_by':'এই পর্বের প্রত্যক্ষ নথি বা consent-সহ আলাপ; narrative adequacy requires editorial review.'}]))
        before=after
    out[0]['plants']=[{'id':'receipt','question':'মায়ের জমায় অঙ্কের গরমিল কেন?'}]
    out[4]['plants']=[{'id':'signature','question':'হাসান কার অনুমতিতে টাকা তুলেছিলেন?'}]
    out[16]['plants']=[{'id':'consent','question':'সদস্যের চিকিৎসার তথ্য গোপন রেখেও হিসাব পরিষ্কার করা যাবে?'}]
    for r in out:r.setdefault('plants',[]);r.setdefault('payoffs',[])
    out[15]['payoffs']=[{'id':'signature','answer':'জরুরি চিকিৎসায় টাকা দিয়েছিলেন, লিখিত অনুমতি ছিল না; হাসান দায় স্বীকার করেন।'}]
    out[23]['payoffs']=[{'id':'consent','answer':'নাম না বলে শুধু যাচাইকৃত সমষ্টিগত অঙ্ক প্রকাশ করা হয়।'}]
    out[24]['payoffs']=[{'id':'receipt','answer':'ব্যাঙ্কে দ্বিগুণ চার্জ ধরা পড়ে; ব্যক্তিগত ধার আলাদা করে ফেরত দিতে হবে।'}]
    return out

def screenplay():
    scenes=[]
    actions=['হাসান ব্যাগের আলগা হাতলে সুই ঢোকান। নীরা ঘড়ির দিকে তাকিয়ে ঠান্ডা চায়ে চুমুক দেয়।',
             'নীরা ব্যাগ তুলতেই সেলাই আটকে যায়। হাসান না টেনে হাত বাড়িয়ে ব্যাগ চান।',
             'সুতো খুঁজতে নীরা বাবার অনুমতি নিয়ে লাল টিনের বাক্স খোলে। টিকিটের নিচে মায়ের নামে পুরোনো রসিদ।']
    dialogues=[ [('নীরা','চা-ও কি আমার সঙ্গে যাবে? এত ঠান্ডা কেন?'),('হাসান','তুই রেডি হতে হতে ও রাজশাহী ঘুরে আসছে।')],
                [('নীরা','আবার খুলবে? বাস তো তোমার সেলাই দেখে ছাড়বে না।'),('হাসান','হাতল ছিঁড়লে বাসও তোকে ব্যাগ ধরবে না।')],
                [('নীরা','এই টাকাটা মা কবে জমা দিছিল?'),('হাসান','টিকিটটা আগে রাখ।'),('নীরা','টিকিট রাখছি। প্রশ্নটা কোথায় রাখব?')]]
    for i in range(3):
        beats=[{'type':'action','text':actions[i]}]+[{'type':'dialogue','speaker':who,'text':line} for who,line in dialogues[i]]
        beats+=[{'type':'action','text':'হাসান সুইয়ে সুতো পরানোর চেষ্টা থামান। নীরা রসিদটি বাক্সের ওপর রাখে।' if i==2 else 'নীরা ব্যাগ ছেড়ে বাবার পাশের চেয়ারে বসে।'}]
        scenes.append(dict(id='s'+str(i+1),number=i+1,heading='INT. কাঁঠালবাগানের বসার ঘর — সকাল',location='living',time='same morning',objective=['প্রস্তুতির মধ্যে যত্নের সম্পর্ক','সাহায্য নেওয়ার সংকোচ','রসিদের ব্যাখ্যা চাওয়া'][i],obstacle='বাসের সময় ও না বলা একাকিত্ব',turn='কাজের ফাঁকে কথার দিক পাল্টায়।',consequence='পরের সিদ্ধান্তের ব্যবহারিক চাপ বাড়ে।',subtext='থাকতে বলব না, কিন্তু চলে যাওয়া সহজ নয়।',performance='সংযত, চোখের বদল; ঘোষণামূলক কান্না নয়।',transition='cut',seconds=60,action_seconds=30,pause_seconds=8,continuity=['same morning','single key with hasan','same outfits'],beats=beats,sound={'music':'ইচ্ছাকৃত নীরবতা; আবেগ ঘোষণার cue নয়।','sfx':'সুই-সুতো, ব্যাগের কাপড়, দূরের গলি; সংলাপ পরিষ্কার থাকবে।'}))
    return {'title':TITLE,'hook':outlines()[0]['hook'],'ending':dict(outlines()[0]['ending'],setup_scene_ids=['s1','s3']),'characters':[{**c,'description':c['biography'],'voice':'নীরার দ্রুত ব্যবহারিক প্রশ্ন' if c['id']=='nira' else 'হাসানের ছোট কাজের উদাহরণে উত্তর'} for c in bible()['characters'][:2]],'scenes':scenes}

def direction(source):
    items=source.get('scenes') or [dict(e,id='episode_'+str(e['number'])) for e in source['episodes']]
    fields=['purpose','want','concealed','conflict','emotion_start','emotion_end','subtext','humor_reason','visual','performance','pacing','transition','audience_effect','contribution']
    rows=[]
    for item in items:
        r={f:'যত্ন ও জবাবদিহি কাজে দেখা যাবে।' for f in fields}
        r.update(id=item['id'],humor_type='natural',intensity=3,evidence=item.get('objective',''))
        rows.append(r)
    return {'vision':'সহানুভূতি মানে ভুল ঢেকে রাখা নয়; নীরব কাজে সম্পর্ক।','scenes':rows,'revision_notes':[]}

def departments(script):
    """One coherent authored production plan; placeholders remain explicit."""
    d={r:example(r) for r in DEPENDENCIES}
    for data in d.values():data['project']=TITLE+' — manually authored acceptance fixture'
    chars=[]
    for c in bible()['characters']:
        chars.append(dict(id=c['id'],name=c['name'],age={'nira':27,'hasan':58,'mita':46}[c['id']],face='মানবিক স্বতন্ত্র মুখ; approved reference pending',hair='নীরার কালো বাঁধা চুল' if c['id']=='nira' else 'ছোট চুল',appearance={'nira':'নীল সুতি কামিজ','hasan':'ধূসর পাঞ্জাবি','mita':'সবুজ শাড়ি'}[c['id']],personality=c['internal_conflict'],relationships={x['id']:'পরিবার/সমিতির সহযোগী; consent boundary' for x in bible()['characters'] if x['id']!=c['id']},evolution=c['relationship_arc'],references=[],scene_states=[]))
    d['character']['records']=chars
    d['art']['records']=[dict(id='set1',scene_ids=['s1','s2','s3'],palette=['কাঠের বাদামি','সকালের ফিকে সোনা'],set='বাসার বসার ঘর; দর্জির কাজের টেবিল',props={'key':'একটি চাবি হাসানের কাছে','bag':'হাতল মেরামত','receipt':'টিকিটের নিচে পুরোনো রসিদ','box':'লাল টিন'},period='বর্তমান',culture='ঢাকার মধ্যবিত্ত ভাড়াবাসা',lighting='পূর্ব জানালার সকালের আলো',style='photorealistic')]
    d['location']['records']=[dict(id='living',architecture='বসার ঘর',geography='পূর্ব জানলা, পশ্চিম দরজা, উত্তরে রান্নাঘর',connections=['kitchen'],openings=[{'id':'d1','to':'kitchen','kind':'door'}],camera_access='দক্ষিণ দেয়াল, চলার পথ খালি',references=[]),dict(id='kitchen',architecture='ছোট রান্নাঘর',geography='বসার ঘরের উত্তরে',connections=['living'],openings=[{'id':'d1','to':'living','kind':'door'}],camera_access='দরজার বাইরে',references=[])]
    d['costume']['records']=[dict(id=f'w{i}-{c}',scene=f's{i}',character=c,outfit='blue-kamiz' if c=='nira' else 'gray-panjabi',color='blue' if c=='nira' else 'gray',material='cotton',weather='humid morning',culture='Bangladeshi everyday',accessories=[],reference='pending',change_reason='none') for i in range(1,4) for c in ('nira','hasan')]
    board=[];cams=[];motions=[];performances=[]
    for i,scene in enumerate(script['scenes'],1):
        for j in range(1,4):
            id=f's{i}-shot{j}';board.append(dict(id=id,scene=scene['id'],order=len(board)+1,action=scene['beats'][0]['text'],purpose=scene['objective'],composition=['wide geography','hands/prop insert','reaction two-shot'][j-1],characters=['nira','hasan'],location='living',camera='Static',performance=scene['performance'],seconds=20))
            cams.append(dict(id=id,shot=id,scene=scene['id'],lens_mm=50,height_m=1.4,angle='eye level',movement='static',lighting='east window key, south negative fill',exposure='protect window highlights',color='source',framing=board[-1]['composition'],axis_side='A',screen_direction='left',axis_reset=False,purpose=scene['objective']))
            for c in ('nira','hasan'):motions.append(dict(id=id+'-'+c,shot=id,character=c,from_pose='sitting',to_pose='sitting',start=(len(board)-1)*20,seconds=20,contact='chair seat',object=c+'-chair',object_before='beside table',object_after='beside table',gravity='normal',collision='no_penetration',change_reason='none',shot_start=0))
        for c in ('nira','hasan'):performances.append(dict(id=f'p{i}-{c}',scene=scene['id'],character=c,emotion_from='restrained',emotion_to='restrained',transition_reason='partner reacts to practical care',intensity=3,subtext=scene['subtext'],gaze='bag, then partner',body_language='hands finish practical task before eye contact',pause_seconds=1,blocking='sits beside table',micro_expression='a held breath',objective='চলে যাওয়া/ধরে রাখার ইচ্ছা সামলানো',tactic='কাজের কথা বলে যত্ন দেখানো',partner_reaction='উত্তর পেলে হাত থামে'))
    d['storyboard']['records']=board;d['performance']['records']=performances;d['cinematographer']['records']=cams;d['motion']['records']=motions
    d['continuity']['records']=[dict(id=f'ct{i}',episode=1,scene=f's{i}',entity='hasan',attribute='key_holder',value='hasan',change_reason='none',affected_shots=[f's{i}-shot1']) for i in range(1,4)]
    d['video']['records']=[dict(id='v-'+b['id'],shot=b['id'],provider='wan-local',mode='text_to_video',prompt=b['action'],reference='pending',characters=b['characters'],seconds=20,fps=24,width=832,height=480,seed=42) for b in board]
    voices=[];t=0
    for scene in script['scenes']:
        t=(scene['number']-1)*60
        for b in scene['beats']:
            if b['type']=='dialogue':
                c='nira' if b['speaker']=='নীরা' else 'hasan';voices.append(dict(id='line'+str(len(voices)+1),scene=scene['id'],speaker='voice-'+c,character=c,text=b['text'],lexicon={},emotion='restrained warmth',pace_wpm=110,start=t,seconds=5,pauses=[.5],reference='pending',synthesis_style='warm'));t+=5
    d['voice']['records']=voices
    d['music']['records']=[dict(id='ambience',scene='s1',kind='ambience',start=0,seconds=180,emotion='domestic',motif='distant lane',purpose='ঘরের বাইরের জীবন',asset='pending',license='unknown',gain_db=-30,duck_db=-8,dialogue_present=True,review='Actual dialogue-mixed listening required'),dict(id='needle',scene='s1',kind='foley',start=2,seconds=2,emotion='care',motif='sewing',purpose='যত্নের ব্যবহারিক শব্দ',asset='pending',license='unknown',gain_db=-20,duck_db=-6,dialogue_present=True,review='Contact sync and listening required')]
    d['editing']['records']=[dict(id='cut'+str(i),shot=b['id'],order=i,start=(i-1)*20,seconds=20,source_in=0,source_seconds=20,video='pending',audio='pending',subtitle='',subtitle_start=(i-1)*20,subtitle_end=i*20,transition='cut',color='source',vfx='none',export_profile='720p24') for i,b in enumerate(board,1)]
    d['qc']['records']=[dict(id='qc-key',subject_agent='continuity',scene='s3',criterion='single_key',expected='hasan',actual='hasan',evidence_kind='objective_metadata',evidence='Manual supplied key-holder metadata only; no footage observed.',severity='info')]
    d['production_manager']['records']=[dict(id='job-'+r,agent=r,dependencies=['job-'+dep for dep in deps],estimated_seconds=60,gpu_required=r=='video',vram_gb=24 if r=='video' else 0,state='pending',artifacts=[],cost_bdt=0) for r,deps in DEPENDENCIES.items()]
    for r in d['growth']['records']:r.update(audience='বাংলাদেশি পারিবারিক drama দর্শক',genre='family mystery',title_bn=TITLE,title_en='The Return Ticket',description_bn=BRIEF,description_en='A daughter asks about an old receipt before leaving for her first job.',keywords=['বাংলা নাটক','পরিবার'],thumbnail='Approved receipt/box close-up pending; no fabricated face',trailer='Approved s3 reveal; actual media pending, no finished trailer claim')
    d['youtube']['records'][0].update(title=TITLE,description='Original fictional project preparation only; no upload.',keywords=['বাংলা নাটক'])
    return d

def run_fixture(program):
    if program.summary()['project'] is not None:raise AgentError('Acceptance fixture requires a fresh isolated project; never overwrite owner work.')
    program.create(TITLE,BRIEF,30,180);bridge=StoryBridge(program);log=[]
    def finish(rid):
        state=program.engine.execute(rid)
        run=next(r for r in program.engine.runs() if r['id']==rid)
        if state!='Awaiting QC':raise AgentError('Fixture stopped at '+rid+': '+str(run.get('error')))
        tid=run['task'];task=next(t for t in program.store.tasks() if t['id']==tid)
        if task['agent']!='qc':program.store.review(tid,task['revision'],'Recommend','SIMULATED fixture QC — software exercise only','qc')
        program.store.review(tid,task['revision'],'Approve','SIMULATED fixture owner action — no human artistic approval','owner')
        body=program.current_output(tid);log.append({'run':rid,'task':tid,'role':task['agent'],'artifact_sha256':digest(body['artifact']),'provenance':body['provenance'],'approval':'simulated_fixture_only'})
        return tid
    finish(bridge.queue('bible',records=[bible()]))
    finish(bridge.queue('arcs',records=[{'id':'arc-'+c['id'],'character':c['id'],'want':c['want'],'need':c['need'],'turns':c['relationship_arc']} for c in bible()['characters']]))
    for n,row in enumerate(outlines(),1):finish(bridge.queue('outline',n,[row]))
    season=finish(bridge.compile_season());brief={'title':TITLE,'premise':BRIEF,'genre':'family mystery','tone':'restrained natural Bangladeshi drama','episodes':30,'episode':1,'seconds':180}
    def queue(role,kind,artifact,source,deps):
        data={'creative_v1':True,'kind':kind,'brief':brief,'artifact':artifact,'source':{'$from':source,'path':['artifact']}}
        if role=='script':data['sequence_source']={'$from':deps[-1],'path':['artifact']}
        return program.engine.enqueue(role,data,deps,mode='software')
    director_run=queue('director','direction',direction(program.current_output(season)['artifact']),season,[season]);director=finish(director_run)
    with program.store.tx() as db:db.execute('INSERT INTO studio_links VALUES (?,?)',('director_story',director_run))
    finish(bridge.queue('sequences',1,[dict(id='seq'+str(i),scene_ids=['s'+str(i)],seconds=60,objective=s['objective'],obstacle=s['obstacle'],turn=s['turn'],consequence=s['consequence']) for i,s in enumerate(screenplay()['scenes'],1)]))
    script_run=queue('script','screenplay',screenplay(),season,[season,director,bridge._linked('bridge:sequences:1')]);script=finish(script_run)
    direction_run=queue('director','direction',direction(screenplay()),script,[script]);dr=finish(direction_run)
    with program.store.tx() as db:
        db.execute('INSERT INTO studio_links VALUES (?,?)',('script:episode1',script_run));db.execute('INSERT INTO studio_links VALUES (?,?)',('director_script:episode1',direction_run))
    graph=queue_project(program.engine,departments(screenplay()),[script,dr])
    for role,rid in graph['runs'].items():finish(rid)
    tasks=graph['tasks'];ops=ProductionOps(program)
    # Motion chronology is absolute in the department plan; shot packets retain
    # both chronology and a shot-local offset, rather than silently mixing them.
    packet=ops.shot({'script':script,**{r:tasks[r] for r in ('character','art','location','costume','storyboard','performance','cinematographer','motion')}},'s1-shot1')
    voice=ops.voice({'script':script,'voice':tasks['voice'],'character':tasks['character']},{'nira':'Aditi','hasan':'Arjun','mita':'Rashmi'},{'রাজশাহী':'রাজশাহী'},'bn-v1')
    return {'title':TITLE,'source':'manually_authored_fixture','log':log,'tasks':tasks,'script_task':script,'shot_packet':packet,'voice_packet':voice,
       'agents_exercised':sorted({r['role'] for r in log}),'new_real_model_inference':0,'new_human_reviews':0,'professional_quality_verified':False,'simulated_approvals':True}
