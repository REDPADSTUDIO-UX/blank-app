# Phase 3 — অনুমোদিত বাস্তব writing-model পরীক্ষা

১২ নভেম্বর ২০২৬। শুরু checkpoint `edb0adcd041fce7787dfd42e0b1088456aeb834a`; শুধু `feature/video-music-editing-studio`।

**ফল: প্রকৃত model output পাওয়া গেছে; professional Bengali writing বা best-model selection সম্পূর্ণ হয়নি।** Owner-এর অনুমোদিত নির্দিষ্ট Qwen GGUF install ও Hugging Face disclosure test সম্পন্ন হয়েছে। নতুন generation-এ Qwen6টি response +Gemma1টি response সংরক্ষিত; এর আগে Qwen-এর1টি generation timeout-ও সংরক্ষিত। সফল runtime পরীক্ষা creative acceptance নয়।

## অনুমতি ও আগের approval বাধার সমাধান

Owner-এর নতুন স্পষ্ট অনুমতি `verification/approved_gpu_writing/owner_authorization.json`-এ আছে: exact5.68GB Qwen file/freeColab এবং আগে দেখানো কাল্পনিক বাংলা payload → `huggingface-projects/gemma-3-12b-it`। নতুন consent-এর পরে legitimate authenticated browser UI ব্যবহার হয়েছে; approval bypass, CAPTCHA bypass বা secret সংগ্রহ নয়।

পুরোনো HF receipt-এ event ID/raw result ছিল না; সেটি completion-unknown-ই আছে। সেটিকে সফল/ব্যর্থ বানানো বা অজানা completed test পুনঃব্যবহার দাবি করা হয়নি। Owner-এর অনুমতির পরে1টি নতুন UI attempt থেকে সম্পূর্ণ copied raw message এসেছে। নতুন সফল attempt সংরক্ষিত, পুরোনো uncertain receipt আলাদা। এই নির্দিষ্ট payload-এর approval dependency এখন পূরণ হয়েছে; production/private film script পাঠানোর অনুমতি ধরে নেওয়া হয়নি।

## কোন model কোথায় পরীক্ষা হয়েছে

| Model | প্রকৃত পরিবেশ/পরিচয় | ফল/সীমা |
|---|---|---|
| `unsloth/Qwen3.5-9B-GGUF`, `Qwen3.5-9B-Q4_K_M.gguf` | Owner-এর freeColab TeslaT4; revision `3885219b6810b007914f3a7950a8d1b469d598a5`;5680522464bytes;SHA256 `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8` actual bytes মিলে গেছে |1 runtime canary +5 specialist responses; final configuration6/6 complete,0 truncated। Earlier1 generation timed out। Model license metadataApache-2.0, ungated। |
| Google Gemma3 12B IT, hosted Space | Owner-authenticated HF ZeroGPU public demo; actual copied Bengali output |1/1 নতুন response এসেছে। Loaded checkpoint digest/GPU/VRAM/seed/temperature/context অযাচাইকৃত। Gemma custom terms; কোনো নতুন gated weight download বা terms acceptance হয়নি। |

Gemma demo source-এর reported BF16 ও Qwen-এর verified Q4_K_M এক precision নয়। Original task/system/source একই dialogue test-এ মিলেছে; তবে runtime/settings সব সমান নয়। Gemma spinbox1024, slider1020 দেখিয়েছে; effective server cap অযাচাইকৃত। Gemma73.145seconds-এর মধ্যে completion দেখা গেছে—এতে operator inspection আছে; pure model latency নয়। তাই এটিকে Qwen-এর measured request latency-এর সঙ্গে speed ranking করা যাবে না।

Qwen settings: context2048, max-new1024, seed117, temperature0.7, thinking off। Runtime canary cap32। প্রাথমিক proposal-এর512 cap-এর বদলে existing suite-এর1024 cap ব্যবহার হয়েছে যাতে task output budget মেলে;180s per-call bound বজায় ছিল। Existing4096-context NF4 jobs থেকে এটি স্বতন্ত্র2048-context GGUF variant; পুরোনো job relabel বা production route বদলায়নি।

## Actual GPU/runtime evidence

আগের সফল tensor canary পুনরায় চালানো হয়নি। Existing freeT4 session ব্যবহৃত হয়েছে:15GiB VRAM,12.67GiB hostRAM। Exact weight download+hash60.012s। CPU source build প্রায়13min পরে interrupt; completed object files মুছে/পুনরায় compile করা হয়নি। Official runtime release `b12318`, source commit `7021f7e0993c2bae3860a9b7e6507bead16c90af`, embedded version0.9.0-dev। Binary SHA256 `0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5`।

Official CUDA12.8 runtime archives594371580 +197999267bytes, release digests উভয় actual download-এ যাচাই; prepare36.846s। এগুলো runtime dependencies, অতিরিক্ত model weights নয়। Source-build interruption-এর পরে command-line exact-match cleanup9টি child/compiler process থামায়নি; পরে owned build-directory+compiler-name সীমিত cleanup দিয়ে সেগুলো বন্ধ করা হয়েছে। Raw cleanup receipt রাখা হয়েছে, ভবিষ্যৎ helper-এ boundary ও completion checks শক্ত করা হয়েছে।

Load/debug sequence:

1. First load120s deadline exceeded; server বন্ধ; generation request0।
2. ExplicitCUDA/no-warmup variant health-ready হলেও old log-format offload guard reject করে; generation0। একটি মধ্যবর্তী notebook editor replacement syntax error-ও হয়েছিল; clean empty cell-এ full source copy-back equality দিয়ে সংশোধন করা হয়েছে। এটি model failure নয়।
3. GPU guard এখন actual owned server PID-এর≥4096MiB allocation মাপে। Real load6.085s;33/33 layers offloaded; PID78391 used5200MiB। First generation180.102s timeout; raw failure/RSS/device-memory/log রাখা হয়েছে; blind retry বন্ধ হয়েছে।
4. Verbose log first decode-এ থেমেছিল;9 residual compiler process সরানো, FlashAttention off, batch/microbatch128, CPU batch threads2 এবং tiny canary32-token configuration দিয়ে আলাদা compatibility variant পরীক্ষা। Load22.069s;33/33 layers offloaded; actual PID81394 used5124MiB। এবার6/6 response এসেছে। একাধিক condition বদলেছে, তাই কোনো একটিকে isolated root cause প্রমাণ বলা হচ্ছে না।

Final sampled whole-device peak5303MiB ≈5.18GiB; এতে notebook baseline-ও আছে। Maximum sampled server RSS2685669376bytes ≈2.50GiB; এটি whole-host/model-load peak নয়। Screenshot-এর approximate5.2GiB label rounded whole-device working usage; precise owned-process load allocation5124MiB ≈5.00GiB। API localhost127.0.0.1-এ cell-এর ভিতরে সীমিত ছিল; public endpoint/proxy/SSH নয়। শেষে active llama-server processes=[]।

## Qwen actual calls এবং নতুন validation

| Test | Wall seconds | Response | Technical acceptance after fix | Creative/editorial observation |
|---|---:|---|---|---|
| Runtime canary |3.591|stop|pass, creative test নয়|ঠিক “আজ সকালটা শান্ত।” |
| Natural dialogue |23.962|stop|fail:scene array, requested string নয়|মায়ের interview/চাকরি নিয়ে অযৌক্তিক knowledge jump ও delivery-এর সঙ্গে চাকরি হারানোর বানানো causal link; অস্বাভাবিক exchange/repetition; visual opening নেই |
| Causal outline |48.424|stop|structural pass|Beat পুনরাবৃত্ত, সনদ থেকে interview জেনে যাওয়া earned নয়; চরিত্রের choice/consequence দুর্বল। Format pass মানেই story pass নয় |
| Director defect control |10.165|stop|pass:1 actual prop-state defect detected, exact source substring|একটি positive control সঠিক; general editorial intelligence প্রমাণ নয় |
| Clean abstention control |4.692|stop|fail:1 false-positive accusation|ব্যাগ একই চেয়ারের পাশে থাকাকে continuity error বলেছে; quote সত্য হলেও judgment ভুল |
| Targeted rewrite |1.872|stop|scope/schema pass|শুধু target replacement দিয়েছে; “জানালাটি বন্ধ” gesture-এ দ্বিধা কতটা প্রকাশ পায় তা human review দরকার |

**5 specialist outputs-এর3টি technical acceptance পায়;2টি পায় না। Artistic acceptance0।** Final configuration-এ6/6 HTTP responses complete,0 truncated। All attempted Qwen generation calls ধরলে6 successful response/7 requests,1 timeout; earlier load/guard/syntax failures এর বাইরে আলাদা। Director/QC-এর defect payload হুবহু একই; একবার inference করে দুই role-এর calibration-এ একই evidence ব্যবহার হয়েছে, আলাদা QC call সংখ্যা বাড়ানো হয়নি।

Critic controls:1 true positive,1 false positive,0 missed planted defect,0 unsupported quotation across these2 controls। এই অতি ছোট sample-এ precision1/2, recall1/1; general accuracy বা professional readiness estimate নয়। **Verbatim quote সত্য হলেই critique সত্য হয় না।**

### কিছু প্রকৃত output

Qwen dialogue: “আজ যদি অর্ডার না পৌঁছায়, তবে মায়ের চাকরিও চলে যাবে।” Source-এ মায়ের চাকরি আছে বলা হয়নি; তিনি interview-এ যাবেন। একই output-এ “তাহলে চলুন, আমরা যা করব না, তাই না?”—অর্থ ও স্বাভাবিকতা দুর্বল।

Qwen clean-control critique: “ব্যাগ চেয়ারের পাশেই থাকে।” এই সঠিক source quote-কে defect হিসেবে revision দিয়েছে—স্থির prop position কোনো contradiction নয়।

Gemma: “রুবার মুখের পরিবর্তন টানে” ও “ভাইয়ের দিকে তাকিয়ে রুবার চোখে অসহায়তা দেখে।” Action-writing awkward এবং সম্পর্কের বর্ণনা অসংগত; চাওয়া2 witty exchange পরিষ্কার নেই। Markdown fences ও অতিরিক্ত `interactions` field-এর জন্য strict response contract fail। Diagnosis-এর জন্য fence strip করা হয়েছে; raw output repair/replace করা হয়নি।

এসব assistant-এর preliminary editorial observations; independent Bengali expert evaluation নয়। নতুন model দুটির professional creative improvement প্রমাণিত হয়নি।

## প্রমাণিত validator bug এবং সংশোধন

Actual output ধরেছে2 ভুল:scene list গ্রহণ করা এবং known critic control-এ false-positive/missed defect থাকলেও technical_pass=True। `redpad_pipeline/kaggle_benchmark.py`-এ scene string/nonempty type gate ও critic_control_pass aggregate gate যুক্ত হয়েছে; nonobjectJSON এখন crash ছাড়া fail-closed। Raw results অপরিবর্তিত; before/after validation JSON আলাদা আছে। এই fix model-কে trained/intelligent করে না, unseen screenplay-এর সব semantic error-ও ধরার দাবি নয়—known benchmark truth-এর ক্ষেত্রে ভুল technical pass আটকায়।

**34 relevant regression tests pass**:29 existing Kaggle/model-service checks +5 actual-output/edge-case regressions। এই29 পুনরায় চালানোর কারণ নতুন shared validation change; completed creative benchmarks পুনরায় চালানো নয়। Historical418/8/full-suite evidence নতুন pass হিসেবে গণনা নয়। Runtime scripts syntax-checked, actual executed paths/logs retained; scripts experimental, production integration certification নয়।

## Role selection ও বাকি কাজ

| Roles | বর্তমান সিদ্ধান্ত |
|---|---|
| Story | Qwen sample structure-valid কিন্তু causal/emotional quality দুর্বল; winner নেই; Gemma-এর comparable story trials বাকি |
| Script | দুটির actual dialogue sample আছে; কোনোটিকে professional বলা যাচ্ছে না; independent Bangladeshi review pending |
| Director / QC | Qwen planted error ধরে, clean scene-এ ভুল revision দেয়; production editorial decision model হিসেবে approve নয়; larger independent holdout/calibration বাকি |
| Other17 agents | Existing workflow/matrix অক্ষত; এই writing test তাদের visual/acting/voice/audio/editing/production responsibilities validate করে না |

Existing [২১-agent registry](assets/professional/phase3_candidates.json) ও [professional readiness matrix](PROFESSIONAL_READINESS_REPORT.md) প্রযোজ্য। কোনো validated selection/production route/Dashboard/Casting পরিবর্তন হয়নি। নতুন GGUF runtime গবেষণা notebook-এ চলেছে; existing NF4 worker বা live Studio-তে integrated দাবি নয়।

Same suite-এর5 case এখনো Qwen-এ unrun:premise, emotional_confrontation, romantic_chemistry, hook_cliffhanger, multi_agent_delegation। Director/QC positive control reuse স্পষ্ট; repeated positive control-কে extra independent trial নয়। Genuine shared-source dialogue blind-review packet প্রস্তুত; settings ভিন্ন হওয়ায় quality exploration, controlled scientific ranking নয়। Human reviewer completion/identity/qualification স্বয়ংক্রিয়ভাবে যাচাই বা fabricate হয়নি।

## Exact current blocker / resume

Colab Resources pane শেষে: **“Your daily free-of-charge resource allowance has run out. Your runtime may terminate at any time.”** No paid subscription/zero compute units। নতুন inference চালানো বন্ধ। Existing server বন্ধ, notebook/evidence save হয়েছে; model/cache ephemeral, persistence guarantee নয়। পরের সেশনে free quota/resource ফিরে এলে exact approved file/cache/hash পরীক্ষা করে শুধু unrun tasks এগোবে; সফল6 calls বা Gemma dialogue অকারণে আবার নয়। একই file/payload-এর এই approval বহাল; নতুন বড় model, paid GPU বা অন্য private-data disclosure নিজে অনুমোদিত নয়।

Lightning region restriction আগের Chrome continuation-এ দেখা; এইবার research/login পুনরায় চেষ্টা নয়। Kaggle authentication/verification আগে blocked ছিল; এই assignment-এ পুনরায় CAPTCHA/Notebook probe নয়। Further model comparison ও independent human editorial review ছাড়া Phase3/all21 professional readiness পূর্ণ নয়। কোনো paidAPI/GPU, নতুন weight model, Render deployment/restart, main modification, production DB/media access বা YouTube publishing হয়নি। Phase4 optimization শুরু হয়নি।

## Evidence

- `verification/approved_gpu_writing/qwen_test_summary.json`: latest validation, actual timings/hashes।
- `colab_compat_export/trials_t4_compat_v2/*.json`: exact request, raw HTTP bytes(base64), untouched content, settings, finish/token/runtime/memory receipts।
- `colab_export/`: earlier failed actual call, device detection, cleanup and raw logs।
- `gemma_dialogue_raw.txt`, `gemma_browser_receipt.json`, `gemma_dialogue_validation.json`: actual hosted sample and explicit uncertainty।
- `validation_regression.txt`, `loader_attempts.json`, `artifact_hashes.json`।
- Large verbose logs এবং blind packet-এর portable copy evidence bundle-এ; retrieval receipt Git-এ থাকবে। Model weights/runtime binaries Git/Library bundle-এ নেই।

[Download actual evidence + independent-review packet](https://chatgpt.com/library?file_id=libfile_159e7a84212c8191b1a64e7ba235082f&account_id=personal) — SHA256 `21b5a7395dded123331dcd252d5abd0af818bd1822f06156cdaa5abed2b9c024`। Blind review-এর জন্য শুধু reviewer_packet folder ব্যবহার করুন; owner identity key দেবেন না।
