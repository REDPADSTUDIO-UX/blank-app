# REDPAD AI Studio — Professional Filmmaking Intelligence: যাচাইকৃত অগ্রগতি

তারিখ: ৭ নভেম্বর ২০২৬, ঢাকা। Continuation parent: `f71e282a7274da850bab51c9848de925fe718e9a`।
Branch: `feature/video-music-editing-studio`। এই রিপোর্টসহ final commit-এর exact SHA final delivery message-এ দেওয়া হয়েছে।
মূল নির্দেশনা অপরিবর্তিত: `assets/phase3/professional_scope.md`; SHA ও recovery ledger: `verification/filmmaking_intelligence/scope_checkpoint.json`।

## A. বাস্তবে যা উন্নত হয়েছে

**২০টি agent-এর software ও knowledge integration উন্নত হয়েছে; পেশাদার বাংলা গল্প, অভিনয় বা cinematic media quality এখনো প্রমাণিত হয়নি।**
পুরোনো feature checkpoint, benchmark, task/approval workflow ও media adapters রাখা হয়েছে। পুরোনো dirty checkout-এ কোনো edit/reset হয়নি।

১. প্রতিটি বিভাগের জন্য আলাদা original teaching example, failure/correction, তিনটি craft lesson, evaluation rubric ও cross-department contract যোগ হয়েছে।
২. Offline retrieval সরাসরি agent execution-এর system conditioning-এ ব্যবহৃত হয়; শুধু অব্যবহৃত documentation নয়।
৩. প্রতিটি run knowledge version, bundle hash, selected lesson IDs ও context hash সংরক্ষণ করে। Retry-তে পুরোনো snapshot বদলায় না; mismatch/tampering হলে কাজ থামে।
৪. Story workspace-এ ১–১০০ পর্বের bounded draft ledger আছে: আগের state, causal predecessor, character, setup/payoff ও parent version যাচাই হয়। একটি বড় ৩০-পর্বের call নয়।
৫. অসম্পূর্ণ/অপরিবর্তিত state, অঘোষিত setup, missing predecessor, duplicate worker ও অতিরিক্ত retry আটকানো হয়েছে। সফল পুরোনো episode আবার generate হয় না।
৬. Script-এ narrated dialogue, action-এর মধ্যে quoted speech এবং একই target হুবহু ফিরিয়ে দেওয়া revision শনাক্ত করার ব্যবস্থা শক্ত হয়েছে।
৭. Voice guidance-এ versioned Bangla pronunciation lexicon যুক্ত; শব্দ request-এ থাকলেই প্রাসঙ্গিক entry আসে। এটি audio training বা pronunciation certification নয়।
৮. বর্তমান ছোট মডেল দিয়ে ১৬টি নতুন CPU inference সংরক্ষিত; পুরোনো সফল baseline/model-comparison cases পুনরায় চালানো হয়নি।

কোড: `filmmaking_knowledge.py`, `craft_validation.py`, `series_ledger.py`, `filmmaking_ui.py` এবং বর্তমান Engine/Script/Studio integration।

### উৎস ও ব্যবহারাধিকার

`assets/filmmaking/knowledge.json`-এ author, license, permitted use, attribution ও exclusion আছে।
২০টি বাংলা department example নিজস্ব authored teaching fixture; এগুলো model output বা approved film assets নয়।
আগের অনুমোদিত Sintel curriculum রাখা হয়েছে; নতুন protected screenplay সংগ্রহ করা হয়নি।
Audacity Manual-এর CC BY 3.0 attribution-সহ খুব ছোট technical guidance ব্যবহার হয়েছে; audio/image কপি করা হয়নি।
OpenStax-এর বর্তমান page-এ অসঙ্গত license/AI-use বক্তব্য পাওয়ায় সেটি conditioning থেকে বাদ। Poetics শুধু bibliographic reference; ebook text ingest হয়নি।

মূল উৎস: [Audacity Manual](https://manual.audacityteam.org/), [Auto Duck](https://manual.audacityteam.org/man/auto_duck.html),
[বিদ্যমান Sintel license](https://durian.blender.org/sharing/), [OpenStax যাচাই](https://openstax.org/books/psychology/pages/preface),
[Poetics metadata](https://www.gutenberg.org/ebooks/1974)।

**Knowledge retrieval/conditioning হয়েছে। Model weights training বা fine-tuning হয়নি।**

## B. ২০-Agent Development Matrix

প্রতি row-তে নতুন knowledge module ও captured conditioning-system সহ executable contract probe আছে:
`verification/filmmaking_intelligence/software_scenarios/<agent>.json`। এগুলো **injected simulation**।
বাস্তব AI inference আলাদা `inference/` directory-তে। পুরোনো specialist validators পুনর্লিখন না করে regression-এ রাখা হয়েছে।

| Agent | নতুন knowledge / integration | পরীক্ষা ও প্রমাণিত ফল | বাকি বাধা |
|---|---|---|---|
| Director | source-grounded scene analysis, minimal revision, abstention | নতুন clean/defect source-এ ২টি real call; clean-এ zero finding, defect মিস | বিচার ও remedy নির্ভরযোগ্য নয়; independent review |
| QC | defect বনাম taste/uncertainty; exact evidence ও minimal repair | ২টি real call; clean-এ false objection, defect-এ ভুল line | semantic calibration ও মানব review |
| Story | motivation, costly choice, state/setup/payoff; episode ledger | ২টি real attempt ব্যর্থ; ৩০-পর্বের software chain/recovery পরীক্ষা পাস | নতুন real series-এর ০টি validated episode; season quality/approval |
| Script | visual-first, responsive speech, address forms, targeted rewrite | ১০টি real call: দুই paired control-সহ আটটি scene/rewrite test; horror attribution guard-এ থেমেছে | স্বাভাবিক dialogue, emotion, humor এখনও দুর্বল |
| Character | stable identity বনাম state, psychology, relationship-specific voice | নতুন knowledge-conditioned contract probe; existing identity/relationship guards regression | নতুন Character-model output/reference review হয়নি |
| Art | income/work/period অনুযায়ী set, palette, motivated props | original scenario + contract probe; existing prop/culture/source checks | বাস্তব culturally reviewed images নেই |
| Location | room/door graph, sightline, travel path, camera access | module consumed; existing asymmetric door/geography tests | অনুমোদিত location reference ও real coverage |
| Costume | weather, wear, motivated outfit changes, identity binding | module consumed; existing costume-change negative cases | generated wardrobe/reference quality অপরীক্ষিত |
| Storyboard | source beat, shot purpose, reveal order, coverage timing | module consumed; existing exact-scene/shot/targeted-revision tests | actual generated shot coverage review |
| Performance | playable tactic, gaze, partner response, restraint | module consumed; intensity/state tests retained | অভিনয় করা footage ও human performance review নেই |
| Cinematographer | framing/distance, axis, motivated light/movement | module consumed; existing axis/reset validation | বাস্তব lighting/camera/identity acceptance নেই |
| Motion | start/end pose, support/contact, transfer chronology | module consumed; object/support tests retained | real video physics দেখা হয়নি |
| Video | Wan/LTX/SVD checkpoint, frame-grid, source/provenance separation | module consumed; বর্তমান তিন engine preflight blocked | approved checkpoints, dependencies, compatible GPU |
| Voice | identity/rights, context-sensitive pronunciation, pause/timing | term retrieval tested; no dialogue replacement; existing speaker/rights guards | TTS weights/backend ও listening review নেই |
| Continuity | character knowledge, prop/outfit/location/event state | module consumed; new episode-state links ও existing state checks | দীর্ঘ বাস্তব episode/shot continuity অপরীক্ষিত |
| Music/SFX | dramatic cue purpose, silence, Foley, ducking, rights | module consumed; existing mix/rights/timing checks | genuine score/audio ও listening approval নেই |
| Editing/VFX | source-bounded EDL, reaction hold, sync/export separation | module consumed; existing timeline/export/approval tests | approved real assets ও final artistic edit নেই |
| Production Manager | approval/resource DAG, checkpoint, safe recovery | module consumed; existing ১৭-task coordination; নতুন episode worker lock/retry tests | approved current creative sources ছাড়া autonomous production নয় |
| Growth | truthful Bangla packaging, audience hypothesis, spoiler discipline | module consumed; existing factual/metadata campaign guards | measured audience results ও approved film packaging |
| YouTube | metadata preparation, read-only/OAuth boundary, no publishing | module consumed; existing approval/scope/token tests | live connection বা publishing পরীক্ষা করা হয়নি; publishing নিষিদ্ধ |

সম্পূর্ণ machine-readable matrix: `agents_matrix.json`। ২০ agent অক্ষত; ২০টি নতুন model যোগ করা হয়নি।

## C. Creative Intelligence Assessment

### Story, dialogue, emotion ও humor

বর্তমান Qwen3 4B-এর সীমাবদ্ধতা স্পষ্ট। Breakfast-এর guided output-এ:
“মাহী চায়ের বাটিতে বসে থাকে”—ফিল্মযোগ্যতা ও বাস্তবতার ব্যর্থতা।
First encounter-এ বইয়ের দোকানের টাকা ফেরত দেওয়ার conflict হারিয়ে “মাছ বাজারে গেছিলাম” এসেছে।
Father–son দৃশ্যে বাবার reply-তে নিজের নাম সম্বোধন করে relation/speaker drift হয়েছে।

Breakfast ও wit-তে একই brief/task/schema/settings-এর knowledge ছাড়া ও knowledge-সহ দুটি paired comparison আছে।
এই চার sample গ্রহণযোগ্য creative improvement দেখায় না। অন্য task-গুলো নতুন brief; সেগুলো পুরোনো benchmark-এর সরাসরি before/after নয়।
এক sample/arm দিয়ে statistical ranking বা quality guarantee দেওয়া হয়নি।

Locked rewrite-এ এবার দুই মূল dialogue line-ই বদলেছে—formal targeted-change check পাস।
কিন্তু “তুমি কখনো আমার কাছে না বলো যে আমার কাজ কাজ হয় না” স্বাভাবিক বা শিল্পসম্মত সংলাপ নয়।
**কথা বদলানো আর ভালো সংলাপ লেখা আলাদা ফল।** Horror-এ narration dialogue slot-এ আসায় raw output রেখেই protocol fail করা হয়েছে।

### Story retry ও schema correction

প্রথম episode draft `state_before` ও `state_after` একই রেখেছিল; পরবর্তী episode তৈরি হয়নি।
একটি targeted retry-তে `mita_knows: no → yes` হয়েছে এবং খরচ হয়ে যাওয়া fee অপরিবর্তিত ছিল।
কিন্তু model `e1_s1_awareness` setup ID বানিয়েছে, যেখানে `e1_s1`–`e1_s3` প্রয়োজন; retry-ও failed।
এই বাস্তব defect-এর পরে setup ID-গুলো generation schema-তে exact enum করা হয়েছে; negative software scenario পাস।
দুই-attempt সীমা মেনে **তৃতীয় actual generation চালানো হয়নি**। নতুন enum-এর real-model retest বাকি।
মূল ও retry response আলাদা; কোনো generated dialogue/manual edit করে সফল output বানানো হয়নি।

### Director/QC

Director clean source-এ finding দেয়নি, কিন্তু seeded defect source-এও empty findings দিয়েছে।
QC clean source-এ ব্যাগ নেই বলে আপত্তি করেছে, যদিও ব্যাগ source-এই আছে। Defect source-এ L3-এর বদলে L2 লক্ষ্য করেছে,
এবং remedy অস্পষ্ট/অসমাপ্ত। L2 finding-এ contradiction-এর কিছু উল্লেখ থাকলেও strict line test মেলেনি;
এটি পুরো semantic understanding-এর automatic score নয়। মূল লেখা বিচার করে independent review প্রয়োজন।

Director/Story/Script/QC-এর **production model selection: কোনোটিই নয়**।
Blind-review package প্রস্তুত: `verification/filmmaking_intelligence/BLIND_REVIEW.md` ও `inference/blind-package.json`।
Administrator key reviewer থেকে আলাদা রাখতে হবে। Human reviewer, rating, listening/visual review ও artistic acceptance: **০**।

## D. Technical Verification

| যাচাই | প্রকৃত ফল |
|---|---|
| Full regression | ৩৩৪ পাস; ০ failure/skip; 31.118 seconds |
| Standalone | ৮টি check পাস |
| নতুন actual inference | ১৬টি: Script ১০, Director ২, QC ২, Story ২ attempt |
| Runtime complete / JSON schema valid | ১৬/১৬; এই suite-এ runtime truncation/timeout ০ |
| Additional protocol/state validation | ১৩ পাস, ৩ failed: horror ও Story-এর দুই attempt |
| Total measured call wall time | 577.494 seconds; প্রায় ৯ মিনিট ৩৭ সেকেন্ড |
| Peak sampled aggregate RSS | প্রায় 4.446 GiB; shared pages double-count হতে পারে, PSS/minimum RAM নয় |
| Host | প্রায় 9.73 GiB RAM; CPU-only |
| Actual cinematic video/TTS/music inference | ০ |

মডেল: `qwen3:4b-instruct-2507-q4_K_M`। Digest:
`sha256:0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`।
আগে অনুমোদিত Ollama 0.40.15 ও একই baseline weights নতুন environment-এ পুনরুদ্ধার করা হয়েছে;
archive SHA এবং প্রতিটি blob size/hash যাচাই হয়েছে। **নতুন model variant download হয়নি।**
আগের Gemma/Qwen3.5 ফল অক্ষত, পুনরায় চালানো হয়নি।

Regular short-scene calls: context 4096, output cap 768, temperature .35, seed 42, streaming, 180-second cap।
Series calls: একই context/sampling, 1024 output tokens। Fixed loopback; no hosted/paid fallback।
প্রথম development call-গুলোর `.1` knowledge snapshot ও শেষ `.2` bundle পৃথক hash-এ সংরক্ষিত;
script lesson text অপরিবর্তিত, attribution/lexicon metadata-র version change গোপন করা হয়নি।
কিছু software check CPU call-এর সঙ্গে overlap করেছে; speed controlled/isolation benchmark নয়।

প্রমাণ: `regression.json`, `standalone.json`, `final_ui.json`, `restoration.json`, `inference_summary.json`,
প্রতি case-এর raw/result/request/schema/evidence এবং `*-resource.json`।
২০টি নতুন conditioning contract probe **simulation** হিসেবে আলাদাভাবে সংরক্ষিত; real call count-এ যোগ হয়নি।
৩০-পর্বের successful chain test-ও injected fixture, বাস্তব ৩০-পর্বের AI গল্প নয়।

## E. Media Readiness

| বিভাগ | Software | এই host-এ প্রকৃত অবস্থা |
|---|---|---|
| Wan2.2 TI2V 5B Diffusers | existing offline adapter/preflight রাখা | অনুমোদিত checkpoint/dependencies/CUDA নেই; inference blocked |
| LTX Video 0.9.5 | existing offline adapter/preflight রাখা | একই blocker; inference হয়নি |
| SVD-XT | existing native mapping/validation রাখা | একই blocker; inference হয়নি |
| Visual references | current reference/source contracts রাখা | নতুন identity/location image generation হয়নি |
| Indic Parler Bengali TTS | existing offline preset worker + নতুন text pronunciation guidance | weights/Parler/Torch/Transformers নেই; listening review হয়নি |
| Music/SFX | cue, silence, ambience/Foley/ducking knowledge ও existing procedural workflow | নতুন neural score বা assessed audio হয়নি |
| Editing/VFX | source EDL, media validation ও approval/export gates রাখা | approved cinematic input নেই; নতুন final film নয় |

Regression-এ temporary synthetic codec/audio/MP4 fixtures তৈরি হয়; সেগুলো অভিনীত, realistic বা AI-generated cinematic assets বলে দেখানো হয়নি।
চলতি resource blockers `environment.json`-এ বিস্তারিত। GPU/large checkpoint approval ছাড়া অনুমোদন-নির্ভর কাজ খোলা রাখা হয়েছে।

## F. Owner Workflow

১. বর্তমান Studio project খুলুন; Director, Story ও Script-ই primary interface।
২. Story-এর per-episode draft architecture-এ character ও initial fact/state দিন; প্রতিটি action-এ একটি bounded episode draft হয়।
৩. সফল পূর্বের draft আবার generate না করে next state থেকে কাজ এগোয়। ব্যর্থ হলে কারণ দেখুন; একটি নির্দিষ্ট corrective instruction দিয়ে একবার retry, মূল failure অক্ষত।
৪. এই ledger-এর technical draft **approved complete season নয়**। সম্পূর্ণ season/character detail, director/QC/human review এবং owner approval ছাড়া production handoff হয় না।
৫. বর্তমান অনুমোদিত Script ও Director artifact থাকলে existing coordinator ১৭টি internal task তৈরি করে; প্রতিটি নিজের knowledge ও সর্বশেষ approved source binding পায়।
৬. Source revision বদলালে stale task আটকে যায়; QC/Director-এর মতামত owner approval হয়ে যায় না। Model/environment failure পুনঃচেষ্টা স্বয়ংক্রিয় নয়।
৭. GPU/media blocked হলেও independent text/planning কাজ করা যায়। Private Google/Kaggle verification আবার খোলা হয়নি।

Knowledge viewer ও failed episode evidence দেখতে model authorization লাগে না; inference শুরু করতে exact installed/approved local model লাগে।
Long-series draft থেকে পুরো approved legacy season artifact-এ promotion/complete production handoff এই milestone-এ প্রমাণিত নয়;
পুরোনো giant-season-call guard তাই রাখা হয়েছে। Owner-কে terminal বা code চালাতে বলা হয়নি।

## G. Safety ও সংরক্ষণ

শুধু নির্ধারিত feature branch; main merge/edit নয়। Render auto-deploy read-only পরীক্ষা করে off নিশ্চিত করে branch save করা হয়েছে।
Deployment/restart/migration, live SQLite/media access, paid API/billing/GPU rental, নতুন cloud resource/account,
YouTube upload/publish/schedule, OAuth scope change বা credentials exposure হয়নি। Kaggle/Google browser monitoring হয়নি।
ভবিষ্যৎ deployment-এর আগে full backup ও independently verified recovery শর্ত অক্ষত।
Final delivery-তে exact verified GitHub SHA/link দেওয়া আছে।

## H. কী সম্পন্ন, কী বাকি

**Software-এ যাচাইকৃত:** ২০-role knowledge conditioning, provenance snapshots, source/approval workflow preservation,
bounded episode ledger, setup/payoff/state links, worker lock, two-attempt targeted recovery, dialogue/revision guards,
pronunciation guidance retrieval, Dashboard integration, ৩৩৪ regression ও ৮ standalone check।

**AI-এ সীমিত যাচাইকৃত:** ১৬টি সম্পূর্ণ local response; horror/state/setup ভুল বাস্তবে আটকে রাখা;
এক clean Director case-এ abstention; rewrite-এ দুই requested line পরিবর্তিত। এগুলো পেশাদার creative acceptance নয়।

**Human review pending:** blind Bengali writing review, dialogue/psychology/humor, casting/identity, acting, camera,
voice pronunciation, score, final edit—কোনোটিই independently approved নয়।

**GPU/model-dependent:** Wan/LTX/SVD-XT/visual/TTS weights, reviewed variant license, compatible compute, real reference footage/audio।
নতুন GPU/account/resource/model download-এর অনুমতি নেই; কোনোটি শুরু করা হয়নি।

**Production-quality not proven:** গ্রহণযোগ্য full episode, ৩০-পর্বের real architecture, দীর্ঘ feature script,
photorealistic consistent video, natural Bengali voice ও final cinematic export। পুরো autonomous Studio সম্পন্ন বলা হচ্ছে না।

পরবর্তী অনুমোদনের জন্য metadata-only গবেষণা: `next_model_research.json`।
`qwen3:8b-q4_K_M`: 5,225,388,164 layer bytes; RAM আনুমানিক 8–10 GiB, বর্তমান host-এ headroom কম।
`qwen3.5:9b-q4_K_M`: 6,550,825,550 bytes; আনুমানিক 10–14 GiB planning RAM, বর্তমান host-এর বাইরে যেতে পারে।
এগুলো measured minimum বা VRAM guarantee নয়; GPU memory এখানে পরীক্ষিত নয়। Model cards-এ Apache 2.0;
তার শর্ত সাপেক্ষে commercial use, কোনো Bengali quality guarantee নয়। বড় model ভালো হবে ধরে নেওয়া হয়নি।
ওজন download হয়নি; পরবর্তী exact variant/size/resource/license approval ছাড়া হবে না।

উৎস: [Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B), [Qwen3.5 9B](https://huggingface.co/Qwen/Qwen3.5-9B)।
যদি অনুমোদন আসে, একই unseen task, আলাদা thinking-mode arm, একটি loaded model, bounded resource monitoring,
raw failure preservation ও independent blind review দিয়ে তুলনা হবে। কোনো weak model স্বয়ংক্রিয়ভাবে production winner হবে না।
