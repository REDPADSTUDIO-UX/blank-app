# Story AI — approved bundle restore ও বাস্তব partial benchmark

২০ নভেম্বর ২০২৬, Asia/Dhaka। **Runtime/bundle: VERIFIED COMPLETE। Story benchmark: BLOCKED / INCOMPLETE। Artistic acceptance: PENDING।**

Base feature HEAD: `7e779578bc919b6cca5e3a40f345c3775265e582`। Branch: `feature/video-music-editing-studio`।

## প্রকৃত execution

Existing `REDPAD_Stages_1_3_20261115.ipynb`-এর ইতিমধ্যে connected Free T4 reuse হয়েছে। নতুন reconnect, paid resource বা provider change নেই। Tesla T4: 15360 MiB total / 14913 MiB free, driver 580.82.07। Restore preflight RAM: 13605818368 bytes total / 12267323392 bytes available; disk free 120839217152 bytes। Remaining quota/session duration অজানা; কোনো সংখ্যা বানানো হয়নি।

Owner-authorized তিনটি exact artifact restore হয়েছে; প্রত্যেকটির full SHA256 ও size PASS:

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Qwen3.5-9B-Q4_K_M.gguf | 5680522464 | 03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8 |
| cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 594371580 | caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea |
| llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 197999267 | e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797 |

Model source: `unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`। Runtime official b12318/7021f7e09; binary SHA256 `0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5` PASS। License source evidence Apache-2.0 model / MIT runtime reuse; নতুন license acceptance নেই।

`libggml-cuda.so` dependency check-এ libcuda.so.1 verified `/usr/lib64-nvidia` directory থেকে resolve হয়েছে। Historical binding receipt ও successful canary byte content restore; canary আবার চালানো হয়নি। পুরোনো download receipt-এর 2/7 metadata historical template থেকে এসেছে—এটি current budget authority নয়। Actual restored ledger-এ তিন consumed call অক্ষত, scoped ceiling 8।

Existing `sections_only_resume_cell.py` source unchanged: Git blob `c96920edee05bd382b1de90e3e4ad072161df161` PASS। কোনো production worker/adapter engineering নয়; Colab-এ শুধু operational restore, existing runner invocation ও evidence-only validation cells যোগ হয়েছে।

## Section ও call count

| Section | Actual outcome | New generation calls | Prompt/output tokens | Total seconds |
|---|---|---:|---|---:|
| Foundation | finish=stop; original JSON schema PASS; creative/lock defects remain | 1 | 1150 / 867 | 167.34 |
| Act 1 | finish=stop; original JSON schema PASS; semantic handoff invalid | 1 | 1866 / 1256 | 53.03 |
| Act 2 | BLOCKED before model load/reservation/submission: KeyError 'knowledge' | 0 | — | — |
| Act 3 | NOT RUN; predecessor unavailable | 0 | — | — |
| Reflection/Treatment | NOT RUN; predecessor unavailable | 0 | — | — |

**Previous 3 + new 2 = 5/8 consumed; 3 remaining।** Historical failure/canary entries retained; Act 2 preparation error leaves ledger byte-identical। No retry, skipped section, rewritten output, extra canary or budget increase। Context 4096, output ceiling1536, generation timeout240 seconds unchanged।

Foundation: load70.15s / generation94.07s, sampled device used5249MiB, server RSS1568313344bytes। Act1: load5.11s / generation47.58s, sampled device used5251MiB, RSS1466253312bytes। Whole-device sampling includes baseline; allocator peak নয়। Both33/33 layers offloaded। Raw output hashes:

- Foundation: `61046abd5a395d4ae3b74a2d3ee83432a3894bcd3fe2f5d0b974d6b42f484756`
- Act 1: `7dac5fbe11683a192bd5ea4f4360769d40134b3a4bd7f8f012f6d009f68daabe`

## Actual blocker ও সীমিত textual findings

Existing context builder `generate_section('act_2')` earlier learns entries-কে character-keyed knowledge map ধরে। Act1/B2 `learns={"knowledge":["বাবার একাকীত্ব ভয়"]}`, কিন্তু Foundation knowledge-map keys `H-01,N-01`। ফলে line215-এ `known[k]` → `KeyError: 'knowledge'`। কোনো Act2 model request হয়নি। Original output বদলে, inferred actor দিয়ে repair করে বা guard পাশ কাটিয়ে এগোনো হয়নি।

নিচের findings partial textual triage; independent human review বা full-story 15-criterion evaluation নয়:

1. **Knowledge/continuity:** Foundation-এ N-01 আগে থেকেই “হাসান টিকিট লুকিয়ে রেখেছেন।” জানে; owner brief-এ ticket দেখার আগে জানে না। Act1/B1 আবার নীরাকে ticket সম্পর্কে অজ্ঞ বলে।
2. **Identity/instruction following:** Foundation exact N/H-এর বদলে N-01/H-01; Act1 actor fields-এ সেই IDs-এর বদলে বাংলা নাম। Beat IDs B1–B4-এর বদলে B1-act_1 ইত্যাদি।
3. **State consistency:** Act1-এর তিনটি adjacent before/after chain একটিও exact match নয়। পাঁচটি requires/learns entry-তে unknown `knowledge` key।
4. **Causal logic/agency:** B1-এ supplied brief-এর বাইরে “বাবার চাপে” সিদ্ধান্ত যোগ হয়েছে। পরের cause values earlier beat IDs cite করে না। B2 choice “বাবার কাঁপুনি লক্ষ্য করা” সচেতন costly decision প্রতিষ্ঠা করে না।
5. **Humor/বাংলা ভাষা:** চারটি Act1 beat-এই humor ও humor_motivation empty। B3-এ “বাবার জন্য দোহা করা” / “একটি দোহা দেয়”, B2 sound “চামড়ায় আওয়াজ”—অস্বাভাবিক বা অস্পষ্ট ভাষা।
6. **Grounding:** Foundation assumption “বাংলাদেশের কৃষকরা কাঁঠাল তৈরি করে বিক্রি করে বাসায় ভাড়া দেয়।” supplied fictional brief থেকে প্রতিষ্ঠিত নয়। এটিকে verified cultural fact হিসেবে ব্যবহার করা হয়নি।
7. **Psychology:** father/daughter স্বাধীনতা ও একাকীত্বের conflict আছে, কিন্তু Foundation need “নিজের শরীর ও মস্তিষ্কের কাজে ফুটিয়া উঠা” অস্পষ্ট। Theme-এর উপস্থিতি professional emotional execution প্রমাণ নয়।

Complete story নেই; lossless full assembly, full structural validator ও15-criterion full-story QC **NOT RUN**। Numeric artistic scores দেওয়া হয়নি। Independent complete-story human-review packet **NOT READY**; human/Producer/Owner acceptance **PENDING**। নিচের raw samples diagnostic reading-এর জন্য; complete screenplay/story নয়।

## Preservation, cleanup ও exact resume point

Actual raw HTTP/text, request/settings/schema, usage, source hashes, ledger ও server logs preserved:

- `verification/story_budget8_20261120/restored_foundation_actual.json`
- `verification/story_budget8_20261120/restored_act1_actual.json`
- `verification/story_budget8_20261120/restored_final_partial_checkpoint.json`

Output raw HTTP/text equality, raw-file hash, reservation payload hash এবং original schemas **PASS** for both sections। এগুলো software/runtime evidence; semantic/creative pass নয়। Owned servers stopped; postflight GPU process list empty, freeVRAM14913MiB। Notebook **All changes saved** দেখা হয়েছে। Failed operational checks-ও notebook-এ retained: main executable-এ ভুল direct-driver assertion এবং evidence checker-এর historical canary-তে optional section-field assumption; corrected read-only checks passed। এগুলো extra model calls নয়।

Option C research-only boundary retained: no Drive mount, secrets/private media/production DB, public model endpoint, hosted generation API, system driver install, Bubblewrap retest, paid resources, Render/main/YouTube changes। Local model endpoint127.0.0.1 only। Production Secure Worker fixed দাবি নেই।

**Stop checkpoint:** GPU/weights এখন available, কিন্তু generated character/knowledge contract invalid। Current instruction stop-after-required-failure অনুযায়ী আর generation হয়নি। Next work requires a separately authorized limited decision on the semantic handoff/validation failure and the locked-fact violations. Original model output must remain immutable; automatic relabel/rewrite নয়। Existing3-call remainder preserves only Act2/Act3/Reflection; a regeneration/revision call would need an explicit revised budget, never silent consumption. Do not rerun successful Foundation/Act1 merely to resume. Cached VM may expire; verify presence before any later inference, and do not assume fresh downloads are authorized indefinitely.

## Genuine Foundation raw output — অপরিবর্তিত

```json
{"assumptions":["বাংলাদেশের কৃষকরা কাঁঠাল তৈরি করে বিক্রি করে বাসায় ভাড়া দেয়।","ঢাকার কাঁঠালবাগান অঞ্চলটি দক্ষিণ ঢাকার একটি ঘনবসতিপূর্ণ এলাকা।","হাসানের কুশলী হাতে কাজ করার অভ্যাস তার মস্তিষ্ককে শান্ত রাখতে সাহায্য করে।","নীরা আগামী দুই বছর সপ্তাহে দুবার রাতের বেলা ফিরে আসবে বলে ধরে।"],"characters":[{"id":"N-01","want":"স্বাধীনতা এবং নতুন জীবন পাওয়া","need":"বাস্তবিক মূল্যবোধের অনুভূতি","fear":"অপরের কাছে দুর্বল হিসেবে দেখা যাওয়া","contradiction":"স্বাধীন হতে চায় কিন্তু বাবার একাকীত্ব ভয় পেয়ে পিছিয়ে দিতে পারে","relationship":"হাসানের প্রতি শ্রদ্ধাশীল কন্যা","internal_conflict":"ক্যারিয়ার বনাম পরিবারের যত্ন","behavior":"চোখ নিচু করে টিকিট লুকানোর চেষ্টা করছে","emotional_change":"আমন্ত্রণ পেয়ে সন্দেহ থেকে আশাবাদী হয়ে ওঠে","name":"নীরা","biography":"২৭ বছর বয়সী এক অফিস কর্মী যিনি রাজশাহীতে চাকরি খুঁজছেন।"},{"id":"H-01","want":"মেয়ের কল্যাণ এবং সন্তোষজনক পরিবার","need":"নিজের শরীর ও মস্তিষ্কের কাজে ফুটিয়া উঠা","fear":"মৃত্যুর আগে একা থাকার ভয়","contradiction":"মেয়ের যাত্রাকে সমর্থন দেন কিন্তু ব্যাগের হাতল সরাতে গিয়ে হাত কাঁপেন","relationship":"নীরার প্রতি ভালোবাসাপূর্ণ পিতা","internal_conflict":"কন্যার স্বপ্ন বনাম নিজের একাকীত্বের ভয়","behavior":"লাল টিনের বাক্সে টিকিট রেখে হাতের ব্যাগ সাজান","emotional_change":"আশায় থাকা থেকে আবেগহীন হয়ে পড়ে","name":"হাসান","biography":"৫৮ বছর বয়সী এক দারজি যিনি কুশলী হাতে কাজ করেন।"}],"conflict_stakes":"নীরা যদিও চাকরি পাচ্ছেন, তবু বাবা একা থাকতে পারবেন না।","dramatic_question":"হাসান কি সত্যিই নীরাকে বাদ দিয়ে একা থাকতে চান নাকি তার কল্যাণে নিজের ভয়কে দমন করছেন?","initial_knowledge":{"H-01":["টিকিট কিনেছে কিন্তু নীরা জানে না।","বাসার উত্তর দিকে রান্নাঘর।"],"N-01":["হাসান টিকিট লুকিয়ে রেখেছেন।","হাসানের হাত কাঁপছে।"]},"logline":"একটি ছোট বাসায় পিতা ও কন্যার মধ্যে টিকিট কেনার গোপনীয়তা এবং একাকীত্বের ভয়ের সংঘর্ষ।","relationship_dynamics":"পিতা-কন্যার সম্পর্কে উন্মুক্ত বিশ্বাস ও গোপনীয়তার মিশ্রণ।","schema_version":1,"theme":"পরিবারিক যত্ন বনাম ব্যক্তিগত স্বাধীনতা","unresolved_questions":["হাসান কি টিকিট কিনেছেন?","নীরা কি টিকিট খুঁজে পাবে?"]}
```

## Genuine Act 1 raw output — অপরিবর্তিত

```json
[{"id":"B1-act_1", "act": 1, "actor": "হাসান", "goal": "মেয়ের ব্যাগ সাজানো", "choice": "লাল টিনের বাক্সে টিকিট রাখা", "cause": "বাবার চাপে মেয়েকে রাজশাহীতে পাঠানোর সিদ্ধান্ত নেওয়া হয়েছে", "consequence": "নীরা এখনও টিকিট সম্পর্কে কিছু জানেন না", "action": "হাসান হাতের ব্যাগের হাতল সোজা করে লাল টিনে টিকিট ঢুকিয়ে দেন", "location": "কাঁঠালবাগানের ঘর", "sound": "কুচকুচ শব্দ", "emotion": "শান্ত কিন্তু উদ্বেগযুক্ত", "before": {"H-01_intent": "মেয়ের জন্য সবসময় সাজানো"}, "after": {"H-01_intent": "গোপনে প্রস্তুতি নিওয়া", "N-01_knowledge": "টিকিট সম্পর্কে অজ্ঞতা"}, "requires": {"knowledge": ["বাসার ভৌগোলিক গঠন"]}, "learns": {}, "plants": ["টিকিটের গোপনীয়তা"], "payoffs": [], "emotion_setups": ["বাবার একাকীত্ব ভয়"], "subtle_emotion": true, "humor": "", "humor_motivation": ""}, {"id":"B2-act_1", "act": 1, "actor": "নীরা", "goal": "সকালের রান্না শেষ করা", "choice": "বাবার কাঁপুনি লক্ষ্য করা", "cause": "হাসানের হাতের ব্যাগ সাজানো দেখে হাসানের ভয় বোঝা যায়", "consequence": "নীরা বুঝতে পারেন বাবা একা থাকতে চান না", "action": "নীরা রান্নার পাত্র উঠিয়ে বাবার কাঁপুনি লক্ষ্য করে মৃদু হাসেন", "location": "রান্নাঘর", "sound": "চামড়ায় আওয়াজ", "emotion": "সন্দেহ থেকে আশাবাদী", "before": {"N-01_feelings": "অজানা ভবিষ্যৎ"}, "after": {"N-01_feelings": "বাবার চিন্তা বুঝেছি", "H-01_state": "হাত কাঁপছে"}, "requires": {"knowledge": ["হাসানের শরীরের ভাষা"]}, "learns": {"knowledge": ["বাবার একাকীত্ব ভয়"]}, "plants": [], "payoffs": [], "emotion_setups": [], "subtle_emotion": true, "humor": "", "humor_motivation": ""}, {"id":"B3-act_1", "act": 1, "actor": "নীরা", "goal": "বাবার জন্য দোহা করা", "choice": "অল্প কথা বলে বাবার সমর্থন জানানো", "cause": "রান্নাঘরে বাবার কাঁপুনি দেখে এবং তার চিন্তা বুঝতে পেরে", "consequence": "হাসান মেয়ের কথায় শান্ত হন", "action": "নীরা 'বাবা, আমি যাবো' বলে হাসানকে একটি দোহা দেয়", "location": "রান্নাঘরের দরজার পাশে", "sound": "কুচকুচ শব্দ বন্ধ হয়", "emotion": "নির্ভরশীল এবং স্পষ্ট", "before": {"N-01_state": "অস্পষ্ট ভয়"}, "after": {"N-01_state": "নির্ধারিত সিদ্ধান্ত", "H-01_state": "আবেগহীন থেকে শান্ত"}, "requires": {"knowledge": ["মেয়ের স্বাধীনতার প্রয়োজনীয়তা"]}, "learns": {}, "plants": [], "payoffs": [], "emotion_setups": [], "subtle_emotion": true, "humor": "", "humor_motivation": ""}, {"id":"B4-act_1", "act": 1, "actor": "হাসান", "goal": "মেয়ের স্বাধীনতা সমর্থন করা", "choice": "একাকীত্বের ভয় দমন করে মেয়েকে পাঠিয়ে দেওয়া", "cause": "নীরা তার সিদ্ধান্ত নিয়েছে এবং বাবার কথায় শান্ত হয়েছেন", "consequence": "হাসান মৃদু হাসেন এবং ব্যাগটি তুলে নেন", "action": "হাসান ব্যাগটি মাঝখানে রেখে মেয়ের চোখের দিকে তাকিয়ে বলেন, 'সফল হও'", "location": "বাসার প্রবেশদ্বার", "sound": "জুতোর শব্দ পড়ায়", "emotion": "আশাবাদী কিন্তু দুঃখপ্রবণ", "before": {"H-01_state": "কাতর এবং ভয়ানক"}, "after": {"H-01_state": "সম্মতি দিয়েছেন", "N-01_state": "প্রস্তুত হয়েছেন"}, "requires": {"knowledge": ["মেয়ের সাফল্যের গুরুত্ব"]}, "learns": {}, "plants": [], "payoffs": [], "emotion_setups": [], "subtle_emotion": false, "humor": "", "humor_motivation": ""}]
```
