# Story AI Budget-11 — প্রকৃত Act1 v3 এবং Act2 ফল

২১ নভেম্বর ২০২৬, Asia/Dhaka। Source remote HEAD আগে যাচাইকৃত `b2eb7d24c8408328413c5866adde86ebfdfc52bd`; শুধু `feature/video-music-editing-studio`।

**Runtime/Act1 structural recovery: VERIFIED COMPLETE। সম্পূর্ণ Story benchmark: BLOCKED — Act2 handoff FAIL। Professional creative acceptance: PENDING।**

## সংরক্ষিত কাজ ও বর্তমান GPU

Foundation v2-এর সম্পূর্ণ receipt/raw text byte-equivalent রেখে পুনর্ব্যবহার হয়েছে; আবার generation নয়। সাতটি historical call ও পুরোনো amendment অপরিবর্তিত। Canary, পুরোনো CPU suites, Bubblewrap test ও CUDA enumeration পুনরায় চালানো হয়নি। শুধু Budget11 ledger/prompt specialization এবং নতুন actual evidence-এর scoped checks করা হয়েছে। Production Story Secure Worker বদলানো হয়নি।

আগের notebook `REDPAD_Stages_1_3_20261115.ipynb`-এর বর্তমান Free T4 সংযুক্ত ছিল; reconnect করা হয়নি। Model/cache প্রথমে অনুপস্থিত। এই prompt-এর current/replacement-VM restore অনুমোদনে শুধু তিনটি pinned artifact restore হয়েছে। Observed hardware: Tesla T4 15360MiB total /14913MiB free; driver580.82.07, compute capability7.5। HostRAM total13605810176bytes, available12189589504bytes; disk free120839204864bytes। Remaining quota/session lifetime অজানা।

| Artifact | Bytes | Full SHA256 |
|---|---:|---|
| Qwen3.5-9B-Q4_K_M.gguf |5680522464|03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8|
| cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz |594371580|caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea|
| llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz |197999267|e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797|

তিনটির original size ও full hash PASS before execution। Model `unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`; official ggml-org/llama.cpp b12318/7021f7e09। Extracted server SHA256 `0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5` PASS। Actual `libggml-cuda.so` dependency resolution-এ `/usr/lib64-nvidia/libcuda.so.1` পাওয়া গেছে। আগের selected CUDA0/driver binding receipt reused; actual model loads33/33 GPU layers নিশ্চিত করে। Model Apache-2.0/runtime MIT-এর পুরোনো pinned source record reused; নতুন license acceptance নয়।

Restore receipt-এর static `historical_calls_consumed=2`, `total_call_ceiling=7`, `model_inferences=0` এবং compatibility wording পুরোনো template-এর restore-stage metadata; এগুলো current inference count নয়। এগুলো পরিবর্তন করে historical receipt বানানো হয়নি। Current budget authority `final_call_ledger.json` ও below actual responses। Preparation-only `prompt_v3.json`-এর runtime_installed/generation_submitted=false-ও final state নয়।

## Budget ও প্রকৃত generation

Owner Budget11 amendment: historical7, সর্বোচ্চ4 নতুন call; Foundation পুনরায় generation/retry নিষিদ্ধ। Actual **7+2=9/11 consumed**। বাকি2 allocation Act3/Reflection-এর; failed Act2 retry বা dependent execution-এর অনুমতি নয়। বর্তমান eligible call0।

| Section | Result | Prompt/output tokens | Load/generation/total seconds |
|---|---|---|---|
| Foundation v2 | আগের accepted technical receipt reused; অপরিবর্তিত | আগের1481/815 | নতুন call0 |
| Act1 v3 | finish=stop; schema PASS; unchanged handoff PASS |2322/914|70.133 /102.438 /175.814|
| Act2 | finish=stop; schema PASS; unchanged handoff FAIL,7 findings |2420/971|5.037 /34.477 /39.813|
| Act3 | NOT RUN — failed predecessor |—|—|
| Reflection/Treatment | NOT RUN — failed predecessor |—|—|

Context4096/output1536/generationtimeout240s, temperature0.7/seed117/repeat_penalty1.08/thinking=false unchanged। Neither new output truncated। Loopback127.0.0.1:18082 server, bounded lifecycle, minimal environment। Both workers stopped; postflight compute-process list empty; freeVRAM14913MiB। Sampled whole-device peak5253MiB for both; serverRSS1613971456/1414197248bytes। Sampling baseline-সহ, allocator peak নয়।

Act1 rawSHA256 `a3986dbcb4e6a73c0e96c9e558e13d0af706e1418e55d01be290f33ed622d8be`। Act2 rawSHA256 `02ab4077f2814e70ca491380a1cb60cef286c1477f9d77f97b025e1bd41890fc`। Exact prompts, request hashes/reservations, original HTTP body base64, raw responses, usage, finish reason, server logs ও postflight retained in `verification/story_budget11_20261121/final_actual.json`। Readable raw text আলাদা আছে।

## Act1 recovery: কী ঠিক হয়েছে, কী হয়নি

Versioned prompt/diff-এ exact N/H, B1–B4, literal brief/earlier-beat causes, single progress key/state continuity ও prior B-number emotion references স্পষ্ট করা হয়েছিল। Original brief/Foundation/schema/rubric বদলানো হয়নি; corrected narrative Python-এ বানানো হয়নি।

Act1 v2-এর11 structural findings থেকে v3-তে একই guard-এ0। V3 cause values brief/B1/B2/B2; before/after chain মিলে; B4 emotion_setup B1। এটি syntax/reference compliance-এর প্রমাণ। কারণ হিসেবে B-number লিখলেই ঘটনাটি অর্থপূর্ণ কারণে ঘটেছে বা psychology সঠিক হয়েছে—এমন প্রমাণ নয়।

মূল output-এই ভাষা ও অর্থের গুরুতর সমস্যা রয়ে গেছে:

- B1 action: “ঝরে সারলেন হাতলটি”; sound: “তোরায়_জোঁক”।
- B2 choice: “লাল_টিবুতে_রাজনীতি_করে_লেন”; tin box প্রসঙ্গে sound “কাঁচের_ফিস-ফাস”।
- B1-এ H ব্যাগের হাতল ঠিক করার পর B3-এ N আবার “ব্যাগের_কানে_কাটা_সম্পন্ন_করে_নতুন_হাতল_বাঁধল”; কেন আবার দরকার তা প্রতিষ্ঠিত নয়।
- B4 action: “বিশ্লেষিত_ভাষায়_টিনের_খাবার_দিলেন”; humor: “বাবা_টিবু_ধরে_কেন?_নীরা_হেসে_লইল_‘সংকেত’_দিলেন_না”। Natural Bengali exchange প্রতিষ্ঠিত নয়।

আগের “দরজার পাশের স্টেশন”, “গরমি নিয়ন্ত্রণ” ইত্যাদি phrase এবার নেই, কিন্তু নতুন অসংলগ্ন phrase এসেছে। **ভাষা, humor বা emotion-এর genuine creative improvement দাবি করা যায় না।**

## Act2 mandatory failure — exact findings

| Beat/path | Finding |
|---|---|
| B5 cause | earlier_causal_reference_required |
| B5 requires.H | knowledge_not_established |
| B6 cause | earlier_causal_reference_required |
| B7 cause | earlier_causal_reference_required |
| B7 before | predecessor_state_mismatch |
| B7 requires.H | knowledge_not_established |
| B8 cause | earlier_causal_reference_required |

চার cause-এ actual earlier B-number-এর বদলে narrative/state prose। B5/B7-এ TICKET_BOX_HIDDEN plant-কে H-এর established knowledge ধরে নেওয়া হয়েছে; Foundation fact TICKET_HIDDEN-এর সঙ্গে এক নয়, learns-এ তা যোগ হয়নি। B7 before আবার B5-after-এ ফিরে গেছে, B6-after নয়। Guard কোনো alias/repair প্রয়োগ করেনি। B6 “বাতাসের_ধারে_প্লেট_হয়নি” ও B5 “প্লেটের_ঘর_কাঁচা_বেশেছে” ভাষাগতভাবে অসংলগ্ন। Schema PASS mandatory handoff FAIL override করেনি। এখানেই generation বন্ধ।

## ১৫-মানদণ্ড: সীমিত preliminary triage, পূর্ণ QC নয়

Complete story assembly, three-act validator এবং full-story15-criterion QC **NOT RUN**; mandatory Act2 failed, Act3/Reflection নেই। নিচের findings শুধু actual partial B1–B8-এর assistant assessment, independent professional scores নয়।

| Criterion | Actual partial evidence / limitation |
|---|---|
| Originality | Locked brief অনুসরণ; original complete plot/ending বিচারযোগ্য নয়। |
| Causal logic | Act2 চার invalid causes; Act1 cause IDs valid হলেও meaningful causality দুর্বল। |
| Character agency | B2 nonsense choice, B3 repeated repair; credible costly choice প্রতিষ্ঠিত নয়। |
| Psychological depth | Fear/উদ্বেগ label আছে; coherent choice দিয়ে nuance প্রতিষ্ঠিত নয়। |
| Relationship credibility | Father/daughter IDs ঠিক; B6 consequence-এর “মেয়েকে_জানালেন” actorN-এর সঙ্গে semantic সমস্যা। |
| Emotional authenticity | B4 subtle_emotion=true ও B1reference কেবল metadata; restrained genuine emotion প্রমাণ নয়। |
| Organic humor | B4 humor অস্পষ্ট; বিশ্বাসযোগ্য wit নয়। |
| Bangladeshi authenticity | পরিচয়/ঘর setting আছে; idiomatic natural language ব্যর্থ। |
| Hook/suspense | Concealed ticket পুনরাবৃত্ত; compelling hook প্রমাণ অপর্যাপ্ত। |
| Escalation | Food/bag পুনরাবৃত্ত, পরিষ্কার stakes escalation নেই। |
| Setup/payoff | B2 plant আছে; completed payoff/ending নেই। |
| Ending | NOT TESTED — Act3 অনুপস্থিত। |
| Filmability | Bag/tinbox দৃশ্যায়নযোগ্য; nonsense actions/location/sounds অস্পষ্ট। |
| Continuity | B7 state mismatch; B5/B7 unsupported knowledge; semantic bag repair repetition। |
| Audience engagement hypothesis | কোনো audience test নেই; confusing prose retention সম্পর্কে ইতিবাচক দাবি সমর্থন করে না। |

## Human review এবং validation evidence

`partial_blind_review_bn.md`-এ genuine Act1 v2/v3 anonymous A/B raw samples, common unchanged Foundation ও খালি reviewer instructions। Owner-only key আলাদা। **Partial diagnostic packet PREPARED; actual human review NOT PERFORMED/PENDING।** এটি পূর্ণগল্প approval packet নয়। Full-story review NOT READY; independent review ও Producer/Owner acceptance PENDING। Review gate বাদ দেওয়া হয়নি।

New CPU-only actual-evidence verifier19 check-groups PASS: frozen seven-call history/Foundation, amendment, artifact receipts, source hash, unchanged original guard, raw HTTP/content/hash identity, reserved payload hashes, unchanged generation settings, original case schemas, actual PASS/FAIL replay, stopped workers এবং failed Act2→Act3 reservation rejection। আগের successful suites পুনরায় চালানো হয়নি;19 check-groups-কে19 নতুন independent creative tests বলা হয়নি। Prior scoped adapter/preparation receipts retained, mock output হিসেবে নয়।

Notebook All changes saved observed। No Drive mount detected; only fictional authorized brief transmitted to local loopback runtime; no production secrets/private media, hosted inference API/public model server। Option C research boundary production Secure Worker-এর kernel isolation-এর সমতুল্য নয়। No paid services, new model/license, CPU inference fallback, main/Render/production/YouTube changes।

## Exact remaining blocker ও পরবর্তী checkpoint

**BLOCKED by genuine Act2 structural failure and poor Bengali semantics, not GPU availability this run।** Bাকি2 call failed Act2 skip/retry-তে ব্যবহারযোগ্য নয়। Owner-authorized new Act2 recovery allocation ও evidence-based improvement hypothesis ছাড়া নতুন inference নয়। আগের successful Foundation/canary/Act1 structural call repeat নয়। Act2 recovery successful হলেও Act3/Reflection ও complete-story validation/human acceptance এখনও বাকি। Current Q4_K_M model-কে professional winner/production-ready করা হয়নি।
