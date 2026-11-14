# REDPAD — Director recovery, ১৩ নভেম্বর ২০২৬

শুরুতে GitHub feature HEAD যাচাই: `8326ea046b5690c4ee2c6608322145f2dab48bf2`।
শুধু `feature/video-music-editing-studio`। আগের রিপোর্ট, raw controls, review packet,
registry এবং Director/local routing code পড়ে অসম্পূর্ণ অংশ থেকে চালিয়েছি।

**অসম্পূর্ণ ৩০-সেকেন্ডের Director পরীক্ষা উদ্ধার হয়েছে; model output এসেছে। কিন্তু
Director পেশাদারভাবে সম্পূর্ণ হয়নি। Production selection নেই; যাচাইকৃত professional
completion ০/২১।** এই রিপোর্টের সঙ্গে সংরক্ষিত feature commit পরের checkpoint।

## নতুন বাস্তব inference

একই owner-authenticated free Hugging Face Gemma 3 12B IT Space-এ পাঁচটি submission:
চারটি response সংরক্ষিত, একটি Error/no-response। পুরোনো সফল generation পুনরায় নয়।

| পরীক্ষা | প্রকৃত ফল | গ্রহণযোগ্যতার সীমা |
|---|---|---|
| অসম্পূর্ণ ৩০-সেকেন্ড plan | আগের response ছিল না; আংশিক input ছিল। ১,০৪২-character prompt ৪০০-character-এর ছোট অংশে বসিয়ে full equality যাচাই করে একবার Submit। | Output মাঝপথে string-এ শেষ; JSON অসম্পূর্ণ। একই scene-এ performance/continuity পুনরাবৃত্ত, department fields ভুল জায়গায়। English prose ও Cyrillic নাম। কোনো usable plan নয়। |
| Source diagnostic | Quote ও motivation hypothesis দিয়েছে। | প্রথম prompt-এ উত্তর values দেখানো ছিল এবং employment status অস্পষ্ট ছিল। তাই factual accuracy-র প্রমাণ থেকে এই response বাদ দিয়েছি; raw রেখে দিয়েছি। |
| Locked camera revision | বৈধ JSON; `/scenes/0/camera` target এবং ছোট replacement দিয়েছে। | Scope ঠিক, কিন্তু camera framing/movement স্পষ্ট নয়; gesture ও “স্মৃতির ভার” বেশি। Artistic acceptance নয়। |
| সংশোধিত source questions | চাকরি হারানোর কথা source-এ নেই, রুবা interview জানে না, advance একবার, মা টাকা এনে উদ্ধার করেন না—চার উত্তর সঠিক source quote-সহ। | এটি bounded comprehension-এ ইতিবাচক evidence। Markdown fence রয়ে গেছে; স্বাধীন specialist evaluation নয়। আগের leading diagnostic-এর বদলে corrected design। |
| চার specialist-এ delegation | একবার Submit-এর পর শুধু `Error`; assistant response নেই। Stop চেয়েছি; reload-এর পর interface ready। | Server completion অজানা; কারণকে quota/model failure বানাইনি। Blind resubmit করিনি। |

প্রকৃত camera response:

> রুবার হাত সনদটির উপর স্থির, যেন স্মৃতির ভার তাতে। সামান্য কাঁপুনি তার দ্বিধা ফুটিয়ে তুলছে।

প্রকৃত source answer:

> না, source-এ উল্লেখ নেই যে মা চাকরি হারিয়েছেন। বলা হয়েছে তিনি স্কুলের চাকরির ইন্টারভিউতে যাবেন।

Reported model `google/gemma-3-12b-it`; exact serving/weights revision অজানা। Token input
১০২৪, slider ১০২০; effective cap, seed, temperature, context, GPU, peak memory ও finish
reason প্রকাশিত নয়। Receipt-এ operator observation times আছে; pure inference latency
হিসেবে ব্যবহার করিনি। Plan-এর দৃশ্যমান অসম্পূর্ণ ending প্রমাণিত, তার token-limit
root cause প্রমাণিত নয়। Hosted evidence-কে controlled local GPU evidence বলিনি।

## বর্তমান GPU/cache — নতুন সরাসরি পরীক্ষা

Colab-এ দৈনিক free allowance শেষ এবং zero compute units দেখিয়েছে। Existing connected
runtime-এ নতুন read-only cell চালিয়েছি; পুরোনো tensor/model canary চালাইনি:

- `nvidia_smi_present=false`, GPU query নেই। বর্তমান GPU benchmark সম্ভব নয়।
- RAM total ১৩,২৮৬,৯৩২ KiB ≈ ১২.৬৭ GiB; available ১১,৯৯৫,৯৯৬ KiB ≈ ১১.৪৪ GiB।
- Disk free ১১৫,৫৫৩,২১০,৩৬৮ bytes ≈ ১০৭.৬২ GiB।
- Exact approved GGUF path নেই; পরিচিত exact HF snapshot cache-এও নেই। Verified
  prebuilt runtime binary নেই। অন্য কোথাও সব সম্ভাব্য copy খোঁজা হয়েছে—এমন দাবি নয়।
- Download ০, model inference ০ এই probe-এ। নতুন connection/resource বা billing নয়।

আগের notebook-এর saved T4 output এখনও দেখা যায়; সেটিকে বর্তমান hardware ধরিনি।
আগের exact Qwen অনুমতি বহাল, কিন্তু GPU ছাড়া ৫.৬৮ GB পুনরায় নামাইনি। Lightning
region restriction ও Kaggle verification retry করিনি। Free session lifetime/reset
সময় provider নিশ্চিত করেনি; অনুমান করিনি।

## Code, integration ও software যাচাই

Recovered plan-এর duplicate fields দেখে বিদ্যমান parser পরীক্ষা করেছি। সাধারণ
`json.loads` শেষ value রেখে আগেরটি মুছে দেয়। Disposable duplicate-findings fixture-এ
পুরোনো benchmark validator ভুল technical pass দিত—before-fix receipt রাখা আছে।

Existing local model parser ও benchmark validator এখন nested duplicate JSON key reject
করে; raw অক্ষত থাকে। কোনো auto-repair, hosted fallback বা production model promotion নয়।
তিনটি নতুন regression test-এ nested direction overwrite, false accusation লুকানো এবং
LocalWriter-এর raw-preserving rejection/no-fallback যাচাই হয়েছে।

এই shared parsing change-এর কারণে প্রভাবিত **১৭২টি regression test পাস**। পরে registry
metadata বদলানোর জন্য শুধু সংশ্লিষ্ট registry check আবার পাস। আগের ৪৩৯ পরীক্ষাকে নতুন
generation বা এই সেশনের full-suite run বলিনি; অপ্রভাবিত successful suite চালাইনি।

প্রকৃত camera replacement বিদ্যমান Director revision API-তে disposable **manual research
fixture** হিসেবে বসিয়ে পরীক্ষা করেছি: অন্য field অপরিবর্তিত; নতুন plan `Awaiting QC`;
unapproved dispatch blocked। এটি production integration বা local inference নয়। কোনো
বাস্তব QC recommendation/owner artistic approval তৈরি করিনি। Dashboard বদলাইনি।

Central registry-তে আগের dialogue/controls ও নতুন run-এর evidence index যুক্ত হয়েছে।
১৮টি pinned profile ও ২১টি agent অক্ষত; production selections এখনও `null`। Hosted
revision-unknown sample-কে pinned local model হিসেবে alias করিনি।

## Director সক্ষমতার অবস্থা

| সক্ষমতা | অবস্থা | যা প্রমাণিত / যা বাকি |
|---|---|---|
| Source understanding | IN PROGRESS | চার corrected প্রশ্নে grounded উত্তর; পূর্ণ story comprehension বাকি। |
| Emotional/character psychology | IN PROGRESS | ছোট hypothesis ও gesture আছে; গভীর arc/psychology স্বাধীনভাবে গ্রহণযোগ্য নয়। |
| বাংলা dialogue/subtext/humor | IN PROGRESS | আগের A preference বহাল; দুটো dialogue sample-ই professionally unaccepted। নতুন full dialogue test নয়। |
| Scene planning/pacing | IN PROGRESS | নতুন বাস্তব plan পেয়েছি, কিন্তু malformed/incomplete; usable staged plan বাকি। |
| Criticism/abstention | IN PROGRESS | আগের দুই Gemma control ও Qwen ফল reuse; নতুন করে চালাইনি। বৃহৎ holdout calibration বাকি। |
| Continuity | IN PROGRESS | Source questions-এ জানা-অজানা/advance রক্ষা; episode ও actual footage continuity বাকি। |
| Specialist delegation | BLOCKED | নতুন bounded attempt Error/no response; server completion অজানা। |
| Targeted revision/owner locks | IN PROGRESS | Actual target response + existing backend gate check; semantic direction দুর্বল, independent acceptance বাকি। |
| Visual/performance judgment | NOT TESTED | তিনটি প্রকৃত generated shot ও স্বাধীন visual evaluation বাকি। |
| Independent QC/approval workflow | IN PROGRESS | Software gate কাজ করে; পূর্ণ বাস্তব intelligent workflow accepted নয়। |

**VERIFIED COMPLETE** শুধু এই সেশনের সীমিত কাজ: pending request উদ্ধার, চার raw response
সংরক্ষণ, বর্তমান hardware/cache probe, duplicate-key rejection ও প্রভাবিত software
regression। কোনো filmmaking capability-কে সম্পূর্ণ ঘোষণা করিনি।

## Model comparison, human review ও পরবর্তী agent

Owner preference A=hosted Gemma, B=Qwen GGUF অপরিবর্তিত; কোনোটিই professionally accepted
নয়। নতুন Gemma bounded facts-এ ইতিবাচক, full plan reliability/format/camera specificity-তে
দুর্বল। Qwen-এর পুরোনো false accusation/source drift-এর তুলনায় এটি সামগ্রিক winner
প্রমাণ করে না; tasks/settings/quantization এক নয়। নতুন Qwen inference হয়নি।

নতুন তিন anonymized output-এর reviewer packet প্রস্তুত; leading diagnostic বাদ। Model
identity key আলাদা। **Independent review PENDING**, blind model ranking নয়। কাউকে
যোগাযোগ/বার্তা পাঠাইনি; artistic approval fabricate করিনি।

Story/Script-এ আলাদা generation ছড়াইনি: শেষে hosted delegation Error এবং Colab GPU/cache
অনুপস্থিত; একই অজানা failure অন্য role দিয়ে ঘুরিয়ে চালানো productive প্রমাণ নয়। Shared
parser fix Story/Script-এরও প্রযোজ্য। নতুনভাবে সম্পূর্ণ agent ০; যাচাইকৃত মোট ০/২১।

## অবশিষ্ট dependency ও exact resume

1. বর্তমান free GPU নেই; exact approved model/cache/runtime হারিয়েছে। GPU সত্যি ফিরে
   এলে current probe result বদলেছে কি না দেখবে। পুরোনো canary/৬ Qwen call পুনরাবৃত্তি
   নয়। একই approved GGUF দরকার হলে কেবল সেটি restore; source CUDA build পুনরায় নয়।
2. Delegation-এর unknown completion আগে reconcile করবে। Server status/result না জেনে
   একই request resubmit নয়। Hosted demo-র exact checkpoint/metrics অযাচাইকৃত থাকলে
   reproducible production selection আটকে থাকবে।
3. Director suite এখনও ১০টি text sample ও তিনটি actual generated shot এবং independent
   বাংলা/visual review চায়। ছোট fact task বা software gate দিয়ে সেই চাহিদা কমানো নয়।
4. Stronger/new/gated model, terms বা compute লাগলে exact version/size/RAM/VRAM/license
   দেখিয়ে আলাদা owner অনুমতি নিতে হবে। এই সেশনে এমন download/terms গ্রহণ করা হয়নি।
5. বর্তমান outputs reviewer packet-এ reviewable; final artistic owner acceptance ও
   স্বাধীন expert review এখনও আবশ্যক। দুর্বল plan-কে শুধু কাজ শেষ করতে approve নয়।

পরের কার্যকর কাজ: `verification/director_recovery_20261113/results.json` ও provider
receipt পড়া; delegation reconciliation; actual free GPU পেলে শুধু অসম্পূর্ণ Director
plan/delegation/revision-এর stage-specific case। পুরোনো completed calls পুনরায় নয়।
কোনো candidate quality gates পার হলে তবেই existing routing-এ integrate করা যাবে।

Main/Render production/DB/media/YouTube বদলানো হয়নি; paid service বা নতুন cloud resource
নেই। Source ও evidence শুধু authorized feature branch-এ; remote verification ছাড়া
save সম্পন্ন বলা হবে না।
