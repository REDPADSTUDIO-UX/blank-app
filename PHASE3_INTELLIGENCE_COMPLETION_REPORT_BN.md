# REDPAD AI Studio — ২১-agent Intelligence ও Creative Quality প্রস্তুতির সমাপ্তি audit

তারিখ: ১৫ নভেম্বর ২০২৬, Asia/Dhaka। শুরুর যাচাইকৃত local ও remote checkpoint:
`9122eca96881550826d3aa7f2d2e0e895bece471`। অনুমোদিত branch:
`feature/video-music-editing-studio`। `main` পরিবর্তন করা হয়নি।

এই রিপোর্ট **software preparation ও integration QA** সম্পর্কে। নতুন model inference,
GPU test, creative ranking বা professional acceptance সম্পন্ন হওয়ার দাবি নয়।

## আগে সম্পন্ন ছিল

- বিদ্যমান ২১-agent registry, intelligence profiles, Story/Character context,
  knowledge provenance ও task/approval ledger integration।
- প্রতি role-এর realistic task, adversarial case, evidence-completeness policy,
  anchored rubric, pass/fail/abstain, targeted revision, handoff ও future recipe।
- Director-এর ৬০০–৭২০ সেকেন্ডের পূর্ণ episode preparation; Script-এর পূর্ববর্তী
  screenwriting/benchmark কাজ। এগুলো পুনর্নির্মাণ বা inference দিয়ে rerun করা হয়নি।
- Source revision/owner gate, QC findings এবং `9122eca`-এর source-bound departmental
  revision requests; আগের ১৪৭-test checkpoint অক্ষত।

## এইবারের বাস্তব সংযোজন ও সংশোধন

১. `benchmark_audit()` বিদ্যমান আট ধরনের coverage-কে ২১ role-এর জন্য machine-readable
ভাবে যাচাই করে। অনুপস্থিত benchmark specification: **০**। তাই duplicate benchmark
registry তৈরি করা হয়নি। Specification coverage ও বাস্তব creative benchmark execution
আলাদা রাখা হয়েছে।

২. পুরোনো professional catalog-এ বর্তমান selected pinned models ছিল না; Casting-এর
পুরোনো candidate list-ও খালি ছিল। `pinned/<existing-id>` দিয়ে বর্তমান registry-কে
ProfessionalLab-এর সঙ্গে যুক্ত করা হয়েছে। পুরোনো IDs, model selections, snapshots ও
পরীক্ষার case বদলানো হয়নি। সব ২১ selected primary-র trial planning CPU tests-এ চলে।

৩. Existing shared text/image ও native audio/video worker evidence এখন একই
ProfessionalLab-এর pre-execution binding ও capture workflow-তে যায়। Exact model,
revision, install/source hash, source revisions, original artifact bytes ও call budget
রক্ষা পায়। Native binding নতুন worker চালায় না; মূল explicit runtime authorization,
local bundle, isolation, consent ও rights checks বহাল। CPU mock, late binding,
changed source/checkpoint এবং media tampering প্রত্যাখ্যান করা হয়।

৪. Independent review-তে শেষ reviewer-এর মত আগের reviewer-এর dissent মুছতে পারে না।
বর্তমান evidence set-এর প্রতি reviewer-এর সর্বশেষ attested মত ধরে criterion-ভিত্তিক
disagreement দেখানো হয়; unresolved disagreement-এ benchmark acceptance বন্ধ থাকে।
আগের সব review সংরক্ষিত থাকে। সমাধানের জন্য সংশ্লিষ্ট reviewer-দের প্রকৃত পুনঃপরীক্ষা
ও নতুন attested judgment দরকার; software কোনো artistic winner বেছে নেয় না।

৫. Blind packet-এ anonymous sample IDs, unchanged raw text/asset hash, original brief,
rubric, পূরণ না করা review form এবং disagreement anchors থাকে। Candidate metadata ও
model-চেনানো asset path আলাদা administrator mapping-এ থাকে। Completed anonymous review
আমদানি করলে private ID mapping, exact evidence-set hash ও একই expert qualification/
inspection gate যাচাই হয়। Content/style পরিচয় প্রকাশ করতে পারে—সম্পূর্ণ double-blind
দাবি করা হয়নি। Reviewer expertise/independence owner-attested; software বাস্তব পরিচয়
বা যোগ্যতা স্বাধীনভাবে প্রমাণ করে না।

৬. Benchmark → evaluate → defect classification → owner-requested targeted revision →
re-evaluate পথ existing Engine ও event ledger-এ সংযুক্ত। Defect-এর category এবং
supported defect/evidence gap আলাদা হয়। Recheck-এ মূল finding ID, একই criterion,
target ও responsible agent এবং বদলানো source লাগে। Finding বাদ দেওয়া closure নয়।
বিরোধী supported defect থাকলে closure হয় না। পুরোনো review-গুলোর comparison history
থাকে; checksum-এর scope স্পষ্ট। Reviewer closure owner acceptance নয়।

৭. অন্য scene থেকে সঠিক quote এনে বর্তমান scene-এর অভিযোগ সমর্থন করা যেত;
এখন textual evidence সংশ্লিষ্ট target-এর মধ্যেই থাকতে হয়। Uninspected finding থাকলে
অন্য finding দিয়ে rubric পূর্ণ হলেও abstain বহাল।

৮. Existing application-এ QC intake, blind-review import, native evidence binding/capture,
coverage/plan download এবং পৃথক readiness layers যুক্ত হয়েছে। Read-only page opening
কোনো generation, approval বা publication শুরু করে না। পুরোনো `০/২০` summary সংশোধন করে
registry থেকে `০/২১` দেখানো হয়।

## Economical future GPU evaluation plan

`verification/intelligence/completion_20261115/sequential_evaluation_plan.json`-এ বর্তমান
pinned revision ও adapter ধরে **৮টি primary model batch**, এবং পূর্ণ three-engine Video
benchmark-এর জন্য **২টি required support batch** আছে। সর্বোচ্চ এক model ও এক agent
একসঙ্গে; শুরুতে Story canary, তারপর independent review। Successful exact-case evidence
থাকলে সংরক্ষণ/যোগ্য reuse; নতুন trial হিসেবে পুরোনো ফল relabel নয়। Failure-এর পরে
কারণ ও নির্দিষ্ট পরিবর্তন ছাড়া blind retry নয়।

Shared approved references/media ব্যবহার করে অপ্রয়োজনীয় generation কমাতে হবে। Primary
model সব modality পরীক্ষা করতে পারে এমন অনুমান নেই। Supporting media হওয়ার পরে
modality-dependent expert review হবে; দরকার হলে শেষে একবার shared critic reload করা যাবে।
এক-engine canary পূর্ণ Video benchmark নয়। Budget-এ supporting media ও failed attempts-ও
ধরা হবে; প্রতি role-এর existing minimum unique outputs সংরক্ষিত। কোনো measured VRAM,
speed, dollar cost বা model superiority বানানো হয়নি। Plan-এর execution disabled।

## CPU verification ও দ্বিতীয় code-level audit

- Final regression: **২৮১ tests passed**, ১৬টি test module।
- দ্বিতীয় audit-এর checksum correction-এর পরে focused recheck: **৪ tests passed**।
- Compilation ও `git diff --check` সফল।
- Intermediate broad run-এর একমাত্র failure ছিল test harness-এ Unix socketpair বন্ধ
  করে Streamlit event loop আটকে যাওয়া। শুধু local Unix socketpair অনুমতি দিয়ে ঠিক
  করা হয়েছে; network sockets, GPU probe ও inference launch নিষিদ্ধই ছিল।
- Tests-এর model/worker receipts, reviewer judgments ও PCM/image examples **synthetic
  fixtures**; এগুলো real model result বা সত্যিকারের professional review নয়।
- Native lifecycle tests কেবল আগের CPU dummy process চালায়; model worker নয়।
- ৬৯টি protected registry/profile/previous evidence document-এর SHA256 অপরিবর্তিত;
  `preservation.json`-এ তালিকা আছে। Production database/media খোলা হয়নি।

দ্বিতীয় source audit-এ `intelligence`, `agent_engine`, `agent_execution_ui`,
`professional_readiness`, `professional_ui`, shared services/media bridge ও native
supervisor-এর নতুন integration পড়ে দেখা হয়েছে। Profile/knowledge binding, exact source
gates, target-local evidence, creator/reviewer separation, immutable samples, dissent,
anonymous anchor import, native budget reservation, stale-source invalidation এবং
owner-only revision/acceptance boundary test evidence-এর সঙ্গে মিলেছে। নতুন database,
agent registry বা orchestration engine তৈরি হয়নি।

## ২১-agent readiness

নিচে **P** = central intelligence/benchmark preparation ও CPU integration যাচাইকৃত;
**R/H/O বাকি** = এই completion run-এ নির্বাচিত model-এর নতুন runtime capability,
স্বাধীন creative assessment ও owner acceptance প্রতিষ্ঠিত হয়নি। আগের বাস্তব inference
চেষ্টা/সীমিত canary evidence মুছে ফেলা বা পুনর্লিখন করা হয়নি। সব model IDs বিদ্যমান
selection; কোনো winner নির্বাচন করা হয়নি।

| Agent | Existing primary candidate | Preparation | Runtime / human / owner |
|---|---|---|---|
| Director | qwen35_27 | P | R/H/O বাকি |
| Script | qwen35_27 | P | R/H/O বাকি |
| Story | qwen35_27 | P | R/H/O বাকি |
| Character | qwen35_27 | P | R/H/O বাকি |
| Art Director | flux2_klein4 | P | R/H/O বাকি |
| Location | flux2_klein4 | P | R/H/O বাকি |
| Costume / Hair & Makeup | flux2_klein4 | P | R/H/O বাকি |
| Storyboard | flux2_klein4 | P | R/H/O বাকি |
| Performance | qwen35_27 | P | R/H/O বাকি |
| Cinematographer | qwen35_27 | P | R/H/O বাকি |
| Motion & Physics | wan_animate2 | P | R/H/O বাকি |
| Video | wan22_5 | P | R/H/O বাকি |
| Voice | indic_speak | P | R/H/O বাকি |
| Continuity | qwen35_27 | P | R/H/O বাকি |
| Music & SFX | ace15 | P | R/H/O বাকি |
| Editing & VFX | qwen35_27 | P | R/H/O বাকি |
| Production Manager | qwen36_27 | P | R/H/O বাকি |
| QC | qwen35_27 | P | R/H/O বাকি |
| Growth | qwen35_27 | P | R/H/O বাকি |
| YouTube Channel | qwen35_9 | P | R/H/O বাকি |
| Casting Director | qwen35_27 | P | R/H/O বাকি |

## সুনির্দিষ্ট অবশিষ্ট blockers

- এই task GPU/inference অনুমোদন করে না। তাই নতুন runtime measurements, model comparison
  বা full creative benchmark চালানো হয়নি। Local model cache/install এই audit-এ probe
  করা হয়নি; ভবিষ্যৎ exact approved bundle, dependency/API compatibility, বাস্তব RAM/VRAM
  ও explicit runtime authorization যাচাই অপরিহার্য। কোনো download অনুমোদন তৈরি হয়নি।
- LTX-2.5-এর spatial upsampler official SHA/size যাচাই না হওয়ার বিদ্যমান installation
  blocker বহাল; `NativeInstalls` সেটি bypass করে না।
- আগের Voice report-এর Indic-Speak start-token/speaker checkpoint inconsistency এবং
  IndicF5 selected state/tensor compatibility actual local runtime-এ যাচাই বাকি।
- Image/audio/video-নির্ভর capability-এর জন্য প্রকৃত original media ও যথাযথ inspection
  দরকার। Text plan, signal metrics বা CPU fixtures দিয়ে অভিনয়, pronunciation,
  naturalness, chemistry, motion বা cinematic quality গ্রহণ করা যাবে না।
- Qualified independent Bengali screenwriter/dialogue, directing, visual, performance,
  listening ও casting reviewers-এর প্রকৃত review এখনো দরকার; dissent থাকলে তা মেটাতে
  হবে। এই run-এ কোনো reviewer-এর সঙ্গে যোগাযোগ করা হয়নি, review বানানো হয়নি।
- Owner/Producer-এর production acceptance আলাদা pending gate। Professionally accepted
  agent count এই engineering থেকে বাড়েনি: **০/২১**।

Review templates-এ sample list ইচ্ছাকৃত খালি: এই run-এ কোনো নতুন real output নেই। ভবিষ্যৎ
অনুমোদিত execution-এর পরে actual bound trial থেকে packet export করতে হবে।

No paid API, billing/resource creation, model download/loading, Render deploy/restart,
YouTube write/publication বা `main` modification করা হয়নি। Commit/push skip markers-সহ
শুধু feature branch-এ; exact remote commit শেষ উত্তরে আলাদাভাবে যাচাই করে দেওয়া হবে।
