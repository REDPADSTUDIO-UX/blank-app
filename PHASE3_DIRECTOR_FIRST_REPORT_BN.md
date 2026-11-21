# REDPAD Phase 3 — Director-first যাচাইকৃত রিপোর্ট

তারিখ: ১৩ নভেম্বর ২০২৬। শুরু: remote feature checkpoint
`7f665cbbb819a5cb62750d62740160fffed25eea`। এই রিপোর্টের সঙ্গে সংরক্ষিত
feature commit-ই পরবর্তী resume checkpoint। Branch শুধু
`feature/video-music-editing-studio`।

**Director AI পেশাদারভাবে সম্পূর্ণ নয়; যাচাইকৃত artistic completion ০/২১।**
এই সেশনে দুইটি নতুন hosted Gemma Director response পাওয়া গেছে, পূর্বের
Qwen/Gemma সফল generation পুনরায় চালানো হয়নি। একটি বাস্তব software revision
ঘাটতি সংশোধিত। কোনো candidate-কে production winner করা হয়নি।

## Director-এর ১০টি সক্ষমতা

| সক্ষমতা | অবস্থা | প্রকৃত প্রমাণ ও যা বাকি |
|---|---|---|
| গল্প ও source বোঝা | IN PROGRESS | আগের Qwen causal output আছে; source/causality দুর্বল। পূর্ণ Director comprehension পরীক্ষা বাকি। |
| theme, motivation ও emotional arc | IN PROGRESS | Owner দুই dialogue sample-ই গ্রহণ করেননি; গভীর psychology/arc-এর specialist acceptance নেই। |
| evidence-grounded criticism ও abstention | IN PROGRESS | নতুন Gemma clean control-এ সঠিক abstention; defect শনাক্ত করেও category ভুল। Qwen clean control-এ false accusation ছিল। |
| cinematic visual ও performance direction | NOT TESTED | এই ধাপে কোনো generated shot দেখিয়ে Director judgment যাচাই হয়নি; তিনটি প্রকৃত shot ও visual review বাকি। |
| scene design ও pacing | BLOCKED | ৩০-সেকেন্ডের plan অনুরোধ interface/connection সমস্যায় সম্পন্ন হয়নি; actual model plan নেই। |
| বাংলা humor, emotion ও subtext | IN PROGRESS | A-কে owner B-এর চেয়ে পছন্দ করেছেন; দুটিই professional standard-এর নিচে। নতুন artistic acceptance নেই। |
| specialist delegation ও integrated execution | NOT TESTED | পুরোনো task-handoff software আছে; নতুন মডেল দিয়ে বাস্তব end-to-end departmental workflow চলেনি। |
| character/prop/knowledge continuity | IN PROGRESS | দুই tiny Director control-এর content evidence আছে; episode-level continuity পরীক্ষা বাকি। |
| targeted revision ও owner locks মানা | IN PROGRESS | নতুন backend field guard যাচাইকৃত; real-model locked revision এখনও পরীক্ষা হয়নি। |
| independent QC, owner gate ও নিরাপদ autonomy | IN PROGRESS | বিদ্যমান software gates regression-এ পাস; পূর্ণ intelligent workflow-এর স্বাধীন artistic/visual গ্রহণযোগ্যতা বাকি। |

**VERIFIED COMPLETE — সীমিত software কাজ:** owner-authored structured revision
scope সংরক্ষণ ও enforce করা; scope-এর বাইরে লেখা reject হলে নতুন plan না বানানো;
revision-এর scene ID/order রক্ষা; save-এর সময় সর্বশেষ owner scope পুনরায় দেখা;
নতুন plan-এর independent QC ও owner gate বজায় রাখা। এই তালিকা model capability
completion নয়।

## বাস্তব model ফল

| মডেল/variant | এই ধাপের কাজ | ফল |
|---|---|---|
| Hosted reported Gemma 3 12B IT | নতুন clean-abstention control | Raw: `{"findings":[]}` Markdown fence-সহ। সঠিকভাবে অযথা revision চায়নি। |
| একই hosted Gemma | নতুন planted bag-continuity control | তালাবদ্ধ আলমারির source verbatim quote করেছে এবং ব্যাগ হাতে আসার বিরোধ ধরেছে। কিন্তু required `contract`-এর বদলে `continuity` category দিয়েছে; ব্যাখ্যায় আলমারির তালা/ব্যাগের তালা গুলিয়েছে। |
| একই hosted Gemma | নতুন ৩০-সেকেন্ড staged Director plan | JSON-form input `text/plain` attachment হিসেবে reject; sequential input আংশিক অবস্থায় timeout; plain-text recovery ও পরের observation-এ MCP timeout। কোনো নতুন plan response সংরক্ষিত হয়নি। |
| Qwen3.5-9B Q4_K_M GGUF | আগের evidence পুনর্মূল্যায়ন, inference পুনরায় নয় | আগের ৫ specialist response-এ ৩টি technical pass; clean scene-এ ভুল অভিযোগ ও dialogue-এ source distortion। আগের canary-সহ ৬টি complete response; একটি পুরোনো timeout আলাদা সংরক্ষিত। |

Gemma-এর **দুই raw response-ই JSON-only protocol ভেঙেছে**। Fence বাদ দেওয়া derived
content আলাদা রেখেছি: clean content control পাস, defect-এর required category ব্যর্থ।
Hosted serving-এর exact weights, finish reason, seed, temperature, context, GPU ও
memory অজানা; তাই overall technical acceptance বা reproducible speed comparison
দিচ্ছি না। UI-তে token input ১০২৪, slider ১০২০ দেখা গেছে। কোনো runtime সংখ্যা বানানো হয়নি।

আগের Qwen variant: `unsloth/Qwen3.5-9B-GGUF`, revision
`3885219b6810b007914f3a7950a8d1b469d598a5`, ৫,৬৮০,৫২২,৪৬৪ bytes। আগের
T4 run-এ control inference প্রায় ৪.৬৯/১০.১৭ সেকেন্ড; এটি আজকের GPU প্রাপ্যতার
প্রমাণ নয়। পূর্ণ পুরোনো metrics: [আগের রিপোর্ট](PHASE3_APPROVED_GPU_WRITING_REPORT_BN.md)।

## Owner review, নির্বাচন ও integration

Identity key ও raw file hashes মিলিয়ে **A = hosted Gemma dialogue, B = Qwen GGUF
dialogue** নিশ্চিত করেছি। Owner-এর পছন্দ A; B-তে চাকরি হারানোর বানানো ঘটনা ছিল,
যেখানে মা চাকরি খুঁজছিলেন। A-ও emotion, psychology, subtext ও depth-এ দুর্বল।
কোনোটিই owner-accepted professional sample নয়; স্বাধীন expert review হয়নি।

চারটি anonymized criticism response-এর review packet প্রস্তুত: দুই case-এ পুরোনো
Qwen ও নতুন Gemma output। এটি চারটি স্বাধীন case নয়, blinding-ও নিখুঁত নয়।
Reviewer response/attestation **PENDING**; কোনো review সম্পন্ন দাবি করছি না।

বিদ্যমান central candidate registry-তেই আলাদা evaluation variant ও evidence link
রেখেছি। GGUF-কে অন্য BF16/NF4 checkpoint-এর installation হিসেবে দেখাইনি; hosted
Gemma-কে pinned local Gemma profile বলে চালাইনি। সব production selection `null`।
Existing Director/agent routes ও approval workflow বজায় আছে; hosted demo কোনো
production fallback নয়। Dashboard বদলাইনি। Structured field scope backend API-তে
ব্যবহারযোগ্য; পুরোনো UI-এর free-text review থেকে exact field lock অনুমান করা হয় না।

## Regression ও evidence

পুরোনো checkpoint-এর disposable fixture দিয়ে camera-only note উপেক্ষা করে wardrobe
ও door-state বদলে save হওয়ার bug পুনরুৎপাদন করেছি। নতুন guard সেই পরিবর্তন আটকায়;
সঠিক camera-only revision নতুন QC-required plan হয়; restart-এর পরেও scope থাকে।

Full regression-এর ৪৩৮টির মধ্যে ৪৩১টি সরাসরি পাস; ৭টি missing dependency error।
ঘোষিত dependency ইনস্টল করে শুধু ওই সাতটি পুনরায় চালিয়ে সব পাস। এরপর নতুন
latest-owner-scope test পাস এবং পরিবর্তিত registry check পাস। মোট **৪৩৯টি স্বতন্ত্র
software test-এর সফল যাচাই** আছে; পুরো সফল suite পুনরায় চালাইনি। Initial failures
ও follow-up logs দুটোই রেখেছি। Software-test output-এর MP4/fixture কোনো নতুন
model-generated film নয়।

সব নতুন raw response, exact request, derived validation, owner review hashes,
resource receipt, review packet ও logs:
`verification/director_first_20261113/`। Recheck script:
`python -m experiments.summarize_director_first` — শুধু সংরক্ষিত output বিশ্লেষণ করে,
কোনো inference/download চালায় না।

## নির্দিষ্ট blocker ও পরের resume

1. Colab-এ একবার Reconnect-এর পর সরাসরি **“You cannot currently connect to a GPU
   due to usage limits in Colab.”** এসেছে। Runtime connected নয়; আজকের GPU/cache
   মাপা সম্ভব হয়নি। Paid option ব্যবহার করিনি।
2. HF Space-এ দুই নতুন control পাওয়ার পর Director-plan input সমস্যা এবং পরপর দুই
   browser MCP timeout হয়েছে। শেষ recovery-তে Submit ধাপ ছিল না; output নেই।
   সংযোগ ফিরলে আগে বর্তমান input/page দেখবে, অন্ধভাবে generation পুনরাবৃত্তি করবে না।
3. Kaggle-এর পুরোনো verification blocker এই সেশনে আবার চেষ্টা করা হয়নি; বর্তমান
   Kaggle access প্রমাণিত নয়। Lightning-এর পরিচিত region restriction-ও retry করা হয়নি।
4. Professional suite-এর **১০টি text sample + ৩টি প্রকৃত generated shot**, exact
   model provenance, role-specific evaluation, independent বাংলা/visual review ও
   owner final acceptance বাকি। Sample count বা quality gate কমানো হয়নি।

পরের কাজ: browser connection ফিরলে অসম্পন্ন Director-plan input inspect করা। Free
Colab GPU সত্যি পাওয়া গেলে আগে cache দেখা; পূর্বের verified prebuilt runtime reuse;
শুধু বাকি Director comprehension/delegation/locked-revision case চালানো। তিনটি
shot-এর জন্য exact model/compute/download approval না থাকলে সেই gate blocked থাকবে।
নতুন বড় model, paid resource বা gated license নিজে অনুমোদন করা যাবে না। Director-এর
মানের gate না মিটিয়ে অন্য agent-কে সম্পূর্ণ বা Phase 4 শুরু বলা যাবে না।

Main অপরিবর্তিত; Render auto-deploy off read-only যাচাই করা হয়েছে। Deployment,
restart, production data/media mutation, নতুন paid resource বা YouTube publishing
করা হয়নি।
