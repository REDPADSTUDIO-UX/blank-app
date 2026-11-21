# REDPAD Story AI — বাস্তব T4 benchmark ও human-review packet

**ফল: GPU execution সফল; সম্পূর্ণ গল্প তৈরির benchmark ব্যর্থ।**

১৪ নভেম্বর ২০২৬। Existing feature checkpoint থেকে আলাদা approved 9B GGUF fallback run। Qwen3.5-27B চালানো হয়নি।

## কী যাচাই হয়েছে

- Live Tesla T4: 15,360 MiB মোট, শুরুতে 14,913 MiB ফ্রি। RAM 12.67 GiB; disk প্রায় 112.64 GiB, শুরুতে প্রায় পুরোটাই ফ্রি।
- Free account: subscription নেই, paid compute units 0। Colab-এ শুরুতে সর্বোচ্চ 1h20m, শেষে 1h estimate; এটি guaranteed quota নয়।
- 27B primary-এর 24/32 GiB এবং Gemma27-এর 24/48, Gemma12-এর 16/24 GiB registry planning gate বর্তমান runtime পূরণ করে না। এগুলো measured absolute minimum নয়। Gemma local terms/access receipt নেই; নতুন gated license গ্রহণ হয়নি।
- Existing approved evaluation variant: unsloth/Qwen3.5-9B-GGUF, revision 3885219b6810b007914f3a7950a8d1b469d598a5; Q4_K_M exact 5,680,522,464 bytes ও SHA-256 মিলে গেছে। Apache-2.0 README pinned hash-ও মিলে গেছে।
- Fresh session-এ approved weights/runtime অনুপস্থিত ছিল; একই অনুমোদিত source পুনঃস্থাপন হয়েছে, পুরোনো specialist benchmarks পুনরায় চালানো হয়নি।
- 33/33 layers GPU-তে offload এবং owned GPU process verified। Localhost-only standalone inference; kernel egress isolation দাবি নেই। Production Engine gate/registry পরিবর্তন করা হয়নি।

## প্রকৃত দুই call

| Call | Prompt / output tokens | Generation / model load | Sampled GPU used | Finish |
|---|---:|---:|---:|---|
| canary | 127 / 124 | 70.36s / 71.13s | 5231 MiB | stop |
| foundation | 1135 / 1536 | 74.08s / 4.23s | 5249 MiB | length |

GPU used হলো whole-device 1-second sampling, baseline সহ; exact allocator peak নয়। Generation wall time prompt evaluation-ও অন্তর্ভুক্ত করে। Canary-তে প্রথম prompt processing 65.94s; foundation decode প্রায় 21.19 tokens/s। Foundation context fit 1135+1536=2671 ≤4096; সমস্যাটি context overflow নয়।

## কেন থামানো হয়েছে

Canary সম্পূর্ণ Bengali JSON দিয়েছে, তবে সিদ্ধান্ত/ফল generic ও নির্দেশসদৃশ। Foundation বারবার assumptions লিখে 1536-token cap ছুঁয়েছে; finish_reason=length; JSON বন্ধ হয়নি। Brief-এ পশ্চিমে প্রবেশদ্বার, generated text-এ দক্ষিণে। চাকরি নিতে যাওয়া বদলে interview preparation-ও এসেছে।

Existing checkpoint truncation হলে stop করতে বলে। তাই 2/7 call-এর পর acts/reflection/revision চালানো হয়নি; raw output repair, fixture substitution বা অতিরিক্ত token দিয়ে success বানানো হয়নি। Budget বাড়ানো বা নতুন variant run করা হয়নি।

## ১৫-criterion review

Existing rubric অপরিবর্তিতভাবে প্রয়োগ করে নিচে evidence triage করা হয়েছে। পূর্ণ artifact/beat IDs নেই বলে existing full-story validator ও independent review acceptance contract পূরণ করা যায়নি। সব numeric score null; AI textual observations qualified human review নয়।

| Criterion | পর্যবেক্ষণ |
|---|---|
| originality | পূর্ণ premise বা beat নেই; originality বিচার করা যাচ্ছে না। |
| causal_logic | Causal beats ও consequence chain তৈরি হয়নি; canary-র generic inference পূর্ণ গল্পের causal logic নয়। |
| character_agency | চরিত্রের costly decision অনুপস্থিত; canary-তে সিদ্ধান্তের বদলে কী করবে না তার নির্দেশসদৃশ ভাষা এসেছে। |
| psychological_depth | একাকীত্ব লক্ষ্য করা ও না-বোঝার দাবি পরস্পর অস্পষ্ট; পূর্ণ character motivations নেই। |
| relationship_credibility | সম্পর্কের কোনো enacted progression পাওয়া যায়নি। |
| emotional_authenticity | Earlier investment ও restrained emotional action-এর story evidence নেই। |
| organic_humor | কোনো motivated humor scene তৈরি হয়নি। |
| bangladesh_authenticity | চাকরির সুযোগ কম—এ দাবির source নেই; এটি verified বাংলাদেশি factual context নয়। |
| hook_suspense | একটি assumptions list এসেছে; hook বা suspense narrative বিচার করা যাচ্ছে না। |
| escalation | একই assumptions বারবার এসেছে; escalating choices হয়নি। |
| setup_payoff | Ticket brief-এ আছে; কোনো generated plant-to-payoff story নেই। |
| ending_quality | Ending তৈরি হয়নি; ending score দেওয়া যাবে না। |
| filmability | পশ্চিমের প্রবেশদ্বারকে দক্ষিণ করা হয়েছে; spatial continuity ভেঙেছে। |
| consistency | Brief-এর geography বদলেছে এবং চাকরি নিতে যাওয়াকে interview preparation করা হয়েছে; একাকীত্ব জানার অবস্থাও অস্পষ্ট। |
| audience_engagement | পূর্ণ গল্প/দর্শক-পরীক্ষা নেই; engagement বা viewership দাবি করা যাবে না। |

## Human reviewer-এর কাজ

এটি পূর্ণ গল্পের review নয়; truncated model failure-এর inspection package। নিচের original brief, exact raw canary ও raw foundation পড়ুন। evaluation.json-এ exact source hashes/character offsets/quotes ও original 1/3/5 anchors আছে। পূর্ণ গল্প না থাকলে overall grade দেবেন না। প্রতিটি ভবিষ্যৎ score-এর জন্য actual beat ID, exact quotation, named reviewer inspection receipt লাগবে। Owner acceptance এখনো pending।

## অপরিবর্তিত original brief

ফিরতি টিকিট: ঢাকার কাঁঠালবাগানের ভাড়া বাসায় নীরা (২৭) রাজশাহীতে চাকরি নিতে চায়। বাবা হাসান (৫৮), দর্জি, মেয়ের যাওয়া চান কিন্তু একা থাকার ভয় লুকান। সকালে তিনি ব্যাগের হাতল সারান, বাসের টিকিট লাল টিনের বাক্সে রাখেন। নীরা টিকিট দেখার আগে তার কেনার কথা জানে না। ঘরে পূর্বে জানলা, পশ্চিমে প্রবেশদ্বার, উত্তরে রান্নাঘর। একই সকাল, একই পোশাক ও একটিমাত্র চাবি। পারিবারিক যত্ন কাজে ফুটবে, কৃত্রিম ত্যাগ বা অচেনা উদ্ধারকারী নয়।

## Exact raw canary — অপরিবর্তিত

```text
{
  "cause": "হাসান নীরাকে টিকিটের বিষয়টি গোপন রেখেছেন।",
  "choice": "নীরা বাক্সটি খুলে দেখার আগে কোনো প্রতিক্রিয়া দেখাবে না।",
  "consequence": "সুতরাং, হাসানের চোখের দিকে তাকিয়ে সে প্রশ্ন করবে না।",
  "knowledge": "মানুষ যখন কোনো তথ্য জানে না, তখন সে সেই বিষয়ে কথা বলতে পারে না।"
}
```

## Exact raw foundation — অসম্পূর্ণ, অপরিবর্তিত

```text
{"assumptions":["বাসের টিকিট লাল টিনের বাক্সে লুকানো আছে।","হাসান সন্ধ্যায় একা থাকার ভয় লুকিয়ে রাখেন।","নীরা চাকরির সংগ্রামে নিশ্চিত কিন্তু বাবার সমর্থনের সীমা জানেন না।","বাড়ির চাবি কেবল নীরাই ধারণ করেন।","ঢাকার ভাড়া বাসা ছেড়ে রাজশাহীতে চাকরির সুযোগ খুব কম।","পারিবারিক যত্ন কৃত্রিম নয়, বাস্তব জীবনের অংশ।","হাসানের দর্জির কাজ ও নীরার চাকরির মধ্যে সামঞ্জস্য খুঁজছেন।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা টিকিট কেনার কোনো পূর্বসূত্র জানে না।","হাসান মেয়ের জন্য ভালোবাসা ও ভয় একসাথে বহন করেন।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির ময়লা বাসা পরিষ্কার রাখার অভ্যাস আছে।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","বাড়ির জানলা দিয়ে বাইরের দৃশ্য দেখা যায়।","লাল টিনের বাক্সটি বাসের টিকিটের জন্য ব্যবহৃত হয়।","হাসান ব্যাগের হাতল সারানোর কাজটি করেছেন।","নীরা সকালে ঘুম থেকে উঠে চশমা পরেন।","হাসান পুরনো কাপড় পরে কাজের জন্য প্রস্তুত।","নীরা চাকরির ইন্টারভিউয়ের জন্য প্রস্তুত।","হাসান মেয়ের ভবিষ্যতের জন্য চিন্তিত।","নীরা বাবার একাকীত্বের বিষয়টি বুঝতে পারেন না।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা বাবার একাকীত্বের বিষয়টি গোপনে লক্ষ্য করেন।","হাসান মেয়ের স্বাধীনতাকে নিজের ত্যাগের সাথে তুলনা করেন না।","চাকরির প্রস্তাবটি আসল কিন্তু অসুবিধাজনক।","বাড়ির দক্ষিণ দিক প্রবেশদ্বার, উত্তর দিকে রান্নাঘর।","নীরা
```

## সংরক্ষণ ও resume

colab_export/outputs/*.json-এ exact prompts, HTTP response bytes (base64), content hash, token counts ও telemetry আছে। *.raw.txt-এ exact UTF-8 response। Server logs, installation/license README ও preflight evidence সংরক্ষিত। Export archive SHA-256: 61ed9cc9a23a63f4cfb1bf9c1a01014e119f48ddf082d8b942197112097e7d34।

দুই owned model server বন্ধ হয়েছে; export-time free VRAM আবার 14,913 MiB। Colab session disconnected/deleted করা হয়নি, ফলে temporary weights এখনও আছে; session idle expiry/remaining quota-এর নিশ্চয়তা নেই।

পরবর্তী কাজ completed engineering rerun নয়: এই নতুন repetitive decoding failure diagnose করা; bounded schema-constrained decoding/repetition-control ও section budget-এর আলাদা variant review করা। Existing Story runtime hard gate অক্ষত। নতুন অনুমোদনের নামে paid service, license bypass বা generic approval চাওয়া প্রয়োজন নেই; এই run-এর বাধা actual model output failure।

No main change, deployment, restart, paid API/resource, publishing বা production DB/media change। Evidence-only feature commit-এ [skip ci] [skip render] থাকবে; manual workflow/deploy trigger নয়।
