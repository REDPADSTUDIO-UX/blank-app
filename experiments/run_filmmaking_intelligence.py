"""Sixteen bounded, fresh CPU tasks; original baseline model only, no retry.
Two paired controls isolate knowledge conditioning. Remaining tasks are not
comparisons to old benchmark briefs. Every response remains unapproved.
"""
import json,hashlib,threading,time
from pathlib import Path
import psutil
from redpad_pipeline.local_ollama_session import ROOT,local_cpu_session
from redpad_pipeline.agents import AgentStore
from redpad_pipeline.model_routing import ModelRoutes,inventory
from redpad_pipeline.staged_writing import StagedDraft,obj,text_schema,enum,compact_scene_schema,expand_compact_scene,blind_package,digest
from redpad_pipeline.filmmaking_knowledge import retrieve
from redpad_pipeline.craft_validation import dialogue_findings,unchanged_requested_lines
from redpad_pipeline.series_ledger import SeriesLedger
from redpad_pipeline.screenwriter import WritingError

MODEL='qwen3:4b-instruct-2507-q4_K_M'
DIGEST='sha256:0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0'
OUT=ROOT/'verification/filmmaking_intelligence/inference'
SPEC=[
 ('breakfast',['মাহী','মাকসুদা'],'ঢাকার বাসায় সকালের নাশতা। মাহী অফিসের বাস ধরতে চায়; মা মাকসুদা চান সে ভাঙা চেয়ারটি ঠিক করে যাক। স্নেহ ও সময়ের টান, বক্তৃতা নয়।'),
 ('father_son',['আবির','কামাল'],'আবির চাকরি ছাড়ার কথা বাবা কামালকে বলতে চায়; বাবা পুরোনো জুতোয় আঠা লাগাচ্ছেন। বাবা ভয় পান ছেলে নিজের মতো কষ্ট পাবে, কিন্তু বাধা দিতে চান না। সংযত আবেগ।'),
 ('first_encounter',['মিতু','রনি'],'বইয়ের দোকানে কর্মী মিতুর ফেরত-টাকার হিসাব মেলেনি; ক্রেতা রনি বেশি টাকা ফেরত পেয়ে নিজে ফিরে এসেছেন। দুজনের ছোট যত্নে প্রথম আকর্ষণ, ফোন নম্বর বা প্রেম ঘোষণা নয়।'),
 ('wit',['রেবা','শুভ'],'শুভ ঘরে বিদ্যুৎ বাঁচাতে বাতি নেভায়, মা রেবা জানেন সে ফোনের চার্জার সারাদিন লাগিয়ে রাখে। অভ্যাসের দ্বন্দ্বে স্নেহপূর্ণ responsive witty exchange; অপমান নয়।'),
 ('confrontation',['শীলা','কামাল'],'শীলা জানতে পেরেছে বাবা কামাল তার নিজের চিকিৎসা পিছিয়ে ভর্তি-ফি রেখেছেন। সে সাহায্য চায়, বাবা করুণা চান না। দোষারোপ বা কান্নার বক্তৃতা ছাড়া একটি কঠিন সিদ্ধান্ত।'),
 ('horror',['রুনা','হালিমা'],'রুনা মেঝেতে সরু চালের দাগ টেনেছে: পাশের বন্ধ ঘরে কেউ হাঁটলে দাগ ভাঙবে। খালা হালিমা বলেন জানলার বাতাসে শব্দ হচ্ছে। জানলা বন্ধ, দরজার নিচে দাগের এক জায়গা সরছে। শব্দে চমক নয়, একটি যৌক্তিক ছোট পরীক্ষা।'),
 ('cliffhanger',['আবির','কামাল'],'আবিরের চাকরির আবেদন কাল জমা দিতে হবে। বাবা কামাল নিজের বন্ধ কারখানার পুরোনো ঠিকানা লিখে পরিচিতকে সুপারিশ করতে গিয়েছিলেন; আবির সেই বন্ধ গেটের নতুন ছবি টেবিলে রাখে। বাবার ভুল তথ্য প্রকাশের পর সিদ্ধান্তজনিত hook; অচেনা ফোন নয়।')]

def checked_scene(names):
    def check(result):
        scene=expand_compact_scene(result,names)
        f=dialogue_findings({'characters':[{'name':n} for n in names],'scenes':[dict(scene,id='scene_test')]})
        if f:raise WritingError(f[0]['code']+': '+f[0]['path'])
    return check

def measure(label,call):
    stop=threading.Event();samples=[];start=time.monotonic()
    def monitor():
        while not stop.is_set():
            rss=0
            for p in [psutil.Process(),*psutil.Process().children(recursive=True)]:
                try:rss+=p.memory_info().rss
                except psutil.Error:pass
            samples.append(rss);stop.wait(.5)
    t=threading.Thread(target=monitor,daemon=True);t.start()
    try:r=call()
    finally:stop.set();t.join(timeout=2)
    (OUT/(label+'-resource.json')).write_text(json.dumps({'wall_seconds_including_checks':round(time.monotonic()-start,3),'peak_aggregate_rss_bytes':max(samples,default=0),'sample_interval_seconds':.5,'limitations':'Aggregate sampled RSS, shared pages may be counted twice; not PSS or minimum RAM.'},indent=2)+'\n')
    print(label,r['status'],r.get('error',''),flush=True)
    return r

def main():
    OUT.mkdir(parents=True,exist_ok=True);store=AgentStore(ROOT/'phase3_runs/filmmaking_intelligence/agent_control.sqlite3')
    requests=[]
    with local_cpu_session():
        assert inventory().get(MODEL)==DIGEST
        ModelRoutes(store).approve_installed(MODEL,DIGEST,'Prior authorized Apache-2.0 baseline; exact restored digest','existing owner authorization',True)
        lab=StagedDraft(OUT)
        def run(key,role,data,task,schema,check=None,guided=True):
            requests.append({'id':key,'role':role,'data':data,'task':task,'schema':schema,'knowledge_conditioned':guided})
            saved=OUT/(key+'.json')
            if saved.exists():
                old=json.loads(saved.read_text());req=old['request']
                if old['status'] not in ('validated_stage','failed') or old['request_sha256']!=digest(req) or old['raw_sha256']!=hashlib.sha256(old['raw'].encode()).hexdigest() or old.get('evidence',{}).get('model_digest')!=DIGEST:raise WritingError('Saved experiment is interrupted or its evidence differs; preserve and recover explicitly.')
                if any(req[k]!=v for k,v in [('role',role),('data',data),('task',task),('schema',schema)]):raise WritingError('Existing case request differs; no overwrite or regenerated success allowed.')
                print(key,'preserved',old['status'],flush=True);return old
            def invoke():
                r=lab.run(key,role,data,task,schema,model=MODEL,tokens=768,check=check,guidance=retrieve(role,json.dumps(data,ensure_ascii=False)) if guided else None)
                if inventory().get(MODEL)!=DIGEST:r['status']='failed';r['error']='Post-inference model identity differs.'
                r.setdefault('evidence',{})['model_digest']=DIGEST
                (OUT/(key+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');return r
            return measure(key,invoke)
        for key,names,brief in SPEC:
            task=f'বাংলা visual-first ছোট দৃশ্য দিন। opening_action, {names[0]}-এর first_reply, {names[1]}-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।'
            if key in ('breakfast','wit'):run(key+'-control','script',brief,task,compact_scene_schema(),checked_scene(names),False)
            run(key,'script',brief,task,compact_scene_schema(),checked_scene(names))
        source={'action':'বাবা বিলটি হাতে নিয়ে চুপ।','father':'আমি তোমার জন্য সব করেছি।','son':'আমি সব বুঝি।'}
        def revision_check(r):
            if unchanged_requested_lines(source,r,['father','son']):raise WritingError('Explicitly requested dialogue revision was copied unchanged.')
        run('locked-rewrite','script',{'locked_scene':'s1: বাবা ছেলের জুতো মেরামত করেন।','target':'s2','source':source},
            'শুধু s2-র action/father/son fields দিন। বাবার পুরোনো কথা ও ছেলের পুরোনো কথা দুটিই বদলাবেন, একই বাক্য ফিরিয়ে দেবেন না। সংক্ষিপ্ত দৃশ্যমান কাজ আগে, সংযত সরাসরি কথায় টাকার কথা এড়ানোর চেষ্টা। নতুন scene বা locked s1 নয়।',
            obj({'action':text_schema(90),'father':text_schema(80),'son':text_schema(80)}),revision_check)
        for clean in (True,False):
            lines={'L1':'মিতা ঘরে, কামাল বারান্দায়।','L2':'মিতা টেবিলের একমাত্র চাবি নিজের ব্যাগে রাখেন।',
                   'L3':'মিতা ব্যাগ থেকে চাবি বের করে কামালকে দেন; কামাল দরজা খোলেন।' if clean else 'চাবি কেউ ফেরত দেননি; কামাল টেবিল থেকে সেই একমাত্র চাবি তুলে দরজা খোলেন।'}
            schema=obj({'findings':{'type':'array','maxItems':2,'items':obj({'line_id':enum(lines),'issue':text_schema(100),'repair':text_schema(100)})}})
            for role in ('director','qc'):
                run(role+('-clean' if clean else '-defect'),role,lines,
                    'শুধু বাস্তব source continuity defect থাকলে findings দিন। clean source হলে খালি findings বৈধ। line_id সঠিক হতে হবে। উদ্ধৃতি বানাবেন না, আলাদা পছন্দকে ভুল বলবেন না।',schema)
        series=SeriesLedger(OUT/'series')
        series.create('মিতা কলেজে ভর্তি হতে চায়। বাবা কামাল ভর্তি-ফি লুকিয়ে নিজের মায়ের ওষুধে খরচ করেছেন; মিতা জানে না। কোনো উদ্ধারকারী নয়। প্রতিটি চরিত্রের চাওয়া থেকে সিদ্ধান্তের দাম ও পরবর্তী পর্বের কারণ দেখান।',['মিতা','কামাল'],{'fee':'spent_on_medicine','mita_knows':'no'},30)
        while series.state()['completed']<2:
            n=series.state()['completed']+1
            existing=series.folder/f'ep{n:03}.json'
            if existing.exists() and json.loads(existing.read_text()).get('status')=='failed':
                print('Series failure preserved; explicit targeted retry required.',flush=True);break
            r=measure('series-'+str(n),lambda:series.run_next(model=MODEL,store=store))
            if r['status']!='validated_stage':break  # preserve failure, never invent a successor.
    (OUT/'requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2)+'\n')
    records={p.stem:json.loads(p.read_text()) for p in OUT.glob('*.json') if 'request_sha256' in json.loads(p.read_text())}
    for p in (OUT/'series').glob('ep[0-9][0-9][0-9].json'):records['series-'+p.stem]=json.loads(p.read_text())
    blind,key=blind_package({k:{'role':r['request']['role'],'data':r['request']['data'],'task':r['request']['task'],'output':r['result'],'raw':r['raw'],'status':r['status']} for k,r in records.items()})
    (OUT/'blind-package.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2)+'\n')
    (OUT/'blind-admin-key.json').write_text(json.dumps(key,ensure_ascii=False,indent=2)+'\n')
    print('Actual calls saved:',len(records),flush=True)

if __name__=='__main__':main()
