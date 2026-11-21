"""Two extra diagnostic calls after demonstrated goal inversion.
The story plan is excluded as unreliable; ONLY user-brief facts seed this scene.
This does not establish that Story AI succeeded.
"""
from pathlib import Path
import json
from redpad_pipeline.staged_writing import StagedDraft, scene_schema, director_schema, ground_review, digest, compact_scene_schema, expand_compact_scene
from redpad_pipeline.staged_bengali import MODEL, NAMES, BRIEF, INITIAL
from redpad_pipeline.local_ollama_session import local_cpu_session

FOLDER=Path(__file__).resolve().parents[1]/'verification/phase3_grounded'
if __name__=='__main__':
    import sys
    lab=StagedDraft(FOLDER)
    if '--retry-compact' in sys.argv:lab.retry('scene')
    with local_cpu_session():
        scene=lab.run('scene','script',{'brief':BRIEF,'state':INITIAL,
            'fixed_goals':{'রাশেদ':'নিজের অফিসে পৌঁছানো','তানিয়া':'নিজের চাকরির সাক্ষাৎকারে পৌঁছানো'},
            'excluded':'Previous generated character wants contradicted the brief and must not be used.'},
            'শুধু বাসায় বেরোনোর আগের মুহূর্তটি লিখুন। প্রথমে চোখে দেখা কাজ, তারপর স্বামী-স্ত্রীর ছোট কথোপকথন। রাশেদের নিজের অফিস, তানিয়ার নিজের ইন্টারভিউ—এ দুটি লক্ষ্য বদলাবেন না। একটি ছাতা টেবিলে; দ্বিতীয় ছাতা নেই। ছাতা নিয়ে হালকা খুনসুটি হবে, প্রতিটি উত্তর আগের কথার জবাব দেবে। তানিয়াকে বাড়িতে আটকানো নয়। দুজনই অন্যের কাজের গুরুত্ব বোঝে, কিন্তু বক্তৃতা দেয় না। শুধু পাঁচটি field দিন: heading-এ INT. বাসা; opening_action-এ দৃশ্যমান কাজ; first_reply-তে রাশেদের কথা; second_reply-তে তার জবাবে তানিয়ার কথা; closing_action-এ ছোট যত্নের কাজ। প্রতিটি কথায় সর্বোচ্চ আটটি বাংলা শব্দ। পরের বাসযাত্রা বা ইন্টারভিউ লিখবেন না।',
            compact_scene_schema(),model=MODEL,tokens=640,check=lambda result:expand_compact_scene(result,NAMES))
        print('scene',scene['status'],scene['error'],flush=True)
        if scene['status']=='validated_stage':
            source=expand_compact_scene(scene['result'],NAMES);h=digest(source)
            (FOLDER/'expanded_scene.json').write_text(json.dumps({'source_record_sha256':digest(scene),'source_result_sha256':digest(scene['result']),'scene':source,'method':'fixed-slot protocol adapter; every narrative text unchanged'},ensure_ascii=False,indent=2))
            review=lab.run('director','director',{'source_sha256':h,'lines':{f'L{i+1}':b for i,b in enumerate(source['beats'])}},
                'শুধু উৎসের প্রকৃত দুর্বলতা চিহ্নিত করুন। line_id ব্যবহার করুন, উদ্ধৃতি লিখবেন না। অযথা প্রশংসা বা কল্পিত ভুল নয়। কথার জবাব অর্থপূর্ণ কি না ও চোখে দেখা কাজটি করা সম্ভব কি না বিচার করুন। নিশ্চিত না হলে findings খালি রাখুন। সর্বোচ্চ একটি finding; problem ও suggestion প্রতিটি সর্বোচ্চ আটটি বাংলা শব্দ।',
                director_schema(source),dependencies=['scene'],model=MODEL,tokens=512,
                check=lambda result:ground_review(result,source,h))
            print('director',review['status'],review['error'],flush=True)
