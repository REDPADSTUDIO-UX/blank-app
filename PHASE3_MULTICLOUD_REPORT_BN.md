# Phase 3 — multi-cloud continuation, ১২ নভেম্বর ২০২৬

## ফলাফল ও সীমা

`712e6d80944d612b25c35e61f0b9306493aaac92` local ও remote feature HEAD মিলিয়ে কাজ শুরু হয়েছে। Main তখন `c03550cb6facc27ba90c3f3286a5b0a0e69748a8`। পূর্বের সফল development পুনরায় করা হয়নি।

**একটি প্রকৃত hosted image output পাওয়া গেছে; নতুন verified Bengali writing output নেই। Phase 3 model selection সম্পূর্ণ নয়।** ২১ agent-এর কোনো নতুন production winner, professional readiness বা independent artistic acceptance দাবি করা হচ্ছে না। Existing matrix, ১৮ model profile, text/image adapters, benchmark cases, Casting ও Dashboard অপরিবর্তিত।

## Provider পরীক্ষা

| Provider | প্রত্যক্ষ অবস্থা | বাস্তব execution | বাকি dependency |
|---|---|---|---|
| Lightning AI | Cloud browser official sign-in পৃষ্ঠায়; API credential অনুপস্থিত | GPU/model চালু হয়নি | Secure owner login, তারপর প্রকৃত credits/GPU/RAM/disk/session দেখা; promotional credits অনুমান নয় |
| Hugging Face | Browser logged out; public Space-এর documented API anonymous call গ্রহণ করেছে | নিচের একটি image; writing request result যাচাই হয়নি | Writing payload-এর বাহ্যিক disclosure consent; controlled benchmark-এর exact checkpoint/runtime/settings এখনও অনুপস্থিত |
| Google Colab | Cloud browser-এ Sign in; Google OAuth/ADC অনুপস্থিত | Runtime/GPU সৃষ্টি হয়নি | Secure owner authentication, official API/MCP enablement বা permitted notebook execution; প্রকৃত free GPU/quota |
| Runpod | গবেষণা ও হিসাবমাত্র; account/API key ব্যবহার হয়নি | Paid resource সৃষ্টি বা charge হয়নি | নির্দিষ্ট spend ও exact model/license/download approval; নিচের proposal এখনো অনুমোদিত নয় |

Owner-এর অন্য browser login এই cloud browser-এর session নয়। কোনো CAPTCHA bypass, free-Colab SSH/remote desktop, credential collection, public Space deployment বা billing fallback হয়নি। Colab-এর এখন official MCP/API ও CLI আছে; তাই “কোনো supported API নেই” বলা ভুল। কিন্তু এই পরিবেশে authorized OAuth/MCP connection নেই।

### প্রকৃত image canary

- Public Space: `prithivMLmods/Flux.2-Klein-Edit-Ultra-Fast`। Space source revision `2225fd5fab9790c7e393c14f08d23fa182a7b71c`।
- Source-ঘোষিত pipeline: `black-forest-labs/FLUX.2-klein-4B` + **`black-forest-labs/FLUX.2-small-decoder`**। Original/full decoder benchmark-এর সঙ্গে এক করা যাবে না। Model repository license metadata Apache-2.0; source ও repository metadata server-এর loaded weight digest প্রমাণ করে না।
- সম্পূর্ণ কাল্পনিক প্রাপ্তবয়স্ক রুবার নতুন portrait prompt; private film script বা বাস্তব ব্যক্তির ছবি পাঠানো হয়নি। Raw prompt/settings receipt-এ আছে।
- Anonymous, token ছাড়া; seed117, randomize false, 512×512, steps4, guidance1। HTTP200 এবং image bytes এসেছে।
- PNG RGB, **393,884 bytes**, SHA256 `943b00e32a922cc51321d3b29f73932f2dd8e4c4136cf3790a1dcda15ab2e592`।
- End-to-end wall time **13.88778143 seconds**; queue/network-সহ, pure generation latency নয়।
- Actual GPU model, peak VRAM, exact loaded checkpoint revision/weight hash, server execution environment মাপা যায়নি। Hub runtime label hardware measurement নয়।
- চিত্র দেখে loose bun, নীল পোশাক, kitchen/pots ও morning light দৃশ্যমান। Ethnicity/acting/continuity/identity fidelity/expert quality এই এক ছবি থেকে যাচাই করা হয়নি। Human reviewer নেই।
- Classification: **hosted demo canary; reproducible local benchmark নয়; selection-ineligible**। Art/Casting capability-এর ছোট sample, ২১-agent readiness-এর প্রমাণ নয়।

[Actual PNG + unchanged raw SSE + request/settings/timing/hash evidence](https://chatgpt.com/library?file_id=libfile_1a38cccfb7c08191ae6f59220f9304bf&account_id=personal)। Bundle SHA256 `1cecab60feba4cd35de4618a22816eefa556d13eb9c8fcd5fb6e08c400f6031d`। Git-এ media/base64/weights নেই; retrieval receipt ও hash manifest আছে।

### Writing attempt: exact authorization blocker

`huggingface-projects/gemma-3-12b-it` public source দেখায় Gemma3 12B BF16 + ZeroGPU। Model revision pinned নয়; API seed/temperature/context প্রকাশ করে না। তাই এই call সফল হলেও controlled existing NF4 benchmark-এর equivalent বা winner evidence হতো না।

Existing original `natural_dialogue` case দিয়ে request process শুরু হয়েছিল। পরবর্তী result poll-এ **automatic approval review প্রত্যাখ্যান করেছে**: repository benchmark prompt/source বাহ্যিক untrusted Hugging Face Space-এ disclosure এবং hosted-API fallback restriction। কাজটির সর্বশেষ user instruction free hosted options evaluate করতে বলেছে, কিন্তু এই নির্দিষ্ট payload disclosure নিয়ে review বাধা দিয়েছে। এটিকে পাশ কাটানো হয়নি। Request completion **unknown**, verified writing sample **0**; “কোনো তথ্য যায়নি” বা “inference ব্যর্থ/সফল” বলা যাচ্ছে না। সম্ভাব্য output file পড়ে বা অন্য পথে poll করে rejection bypass করা হয়নি; unknown result commit/bundle করা হয়নি।

Reviewable exact outbound payload: [WRITING_EGRESS_APPROVAL.json](verification/multicloud_phase3/WRITING_EGRESS_APPROVAL.json)। Destination: `https://huggingface-projects-gemma-3-12b-it.hf.space/gradio_api/call/v2/run`। শুধু fictional case/source/system instructions; credential, Studio DB, owner chat, private film script বা image নয়। Owner consent না পাওয়া পর্যন্ত নতুন submission নয়। Consent-এর পরেও আগের request status আগে মেলাতে হবে; blind retry নয়।

`Gwx4/Qwen-Qwen3.5-27B` source paid Novita provider ও HF login ব্যবহার করে: generation call করা হয়নি। `cmh/Qwen3.5-9B-GGUF-quant-drift` static demo, live inference নয়। এগুলোকে free actual benchmark হিসেবে গণনা করা হয়নি।

### Kaggle-এর অবশিষ্ট blocker

আগের checkpoint-এ owner browser connection/secure authorization ছিল না; পুরোনো মানব verification বাধার ইতিহাসও আছে। এই continuation-এ Kaggle session বা CAPTCHA পুনরায় চালানো হয়নি। বর্তমান authenticated Notebook/Code access, account verification, actual GPU eligibility/quota অযাচাইকৃত। Notebook/model guards software-এ প্রস্তুত থাকলেও authenticated permitted runtime access ছাড়া model test চালানো যায়নি। Kaggle-এর account যাচাই হয়ে গেছে বলে দাবি নয়।

## Development — metadata/resume, কোনো Dashboard পরিবর্তন নয়

নতুন `redpad_pipeline/multicloud_ledger.py`: provider-neutral source/case/model/settings identity; exact match হলে existing Kaggle queue ID পুনঃব্যবহার; completed কাজ অন্য provider-এ skip। Provider বদলালে source/model variant বদলে গেলে একই experiment দাবি করা যাবে না। Small decoder hosted sample তাই controlled local profile থেকে আলাদা।

Append-only provider attempts, explicit payload/account/model/license/persistence/runtime/free-budget gates; Runpod paid approval+budget; finite quota ও timeout margin; in-flight/failed uncertain calls blind retry নিষিদ্ধ। Actual output file hash যাচাই, immutable sample, hosted sample কখনো automatic winner নয়। Historical completed imports require intact actual inference evidence, software fixture নয়।

এটি **ledger/helper**, নতুন cloud executor নয়। কোনো provisioning/billing/download/network call এই module করে না। Existing worker/engine/Dashboard route বদলায়নি; অনুমোদিত runtime-এর future execution এখনও verify করতে হবে। Actual image receipt ও access blockers isolated ignored SQLite-তে রাখা এবং safe JSON export করা হয়েছে।

### নতুন পরীক্ষা

**৮ focused test পাস**: stable identity, canonical queue reuse ও failed import, completed skip, payload/free/paid approval ও NaN rejection, no duplicate in-flight/failed calls, immutable selection-ineligible sample, hash/symlink rejection, append-only history। Evidence: `verification/multicloud_phase3/ledger_tests.txt`। Fixtures actual model outputs নয়।

পূর্বের **৪১৮ full regression +৪ retry guard test** আগের checkpoint-এর evidence; নতুন করে চালানো হয়নি। বর্তমান নতুন helper-এর এই আটটি test-ই চালানো হয়েছে। এগুলো creative intelligence বা whole-app নতুন regression pass-এর প্রমাণ নয়।

## Runpod fallback — অনুমোদনের জন্য proposal, launch নয়

১২ নভেম্বর দেখা official Pods Secure Cloud price: RTX Pro6000 **96GB VRAM /188GB host RAM /16vCPU, $2.49/hour**। A100SXM80GB-এর listed host RAM125GB, conservative128GiB gate-এর নিচে; VRAM একা যথেষ্ট নয়। RTX5090 32GB-এর listed host RAM35GB, সব বড় media test-এর বিকল্প নয়। Availability ও checkout price পুনরায় যাচাই করতে হবে।

প্রথম bounded pilot: Pro6000 সর্বোচ্চ **4 ঘণ্টা**, compute **$9.96**। 200GB container disk $0.10/GB/month ধরে4h প্রায় **$0.11** (720h/month prorating অনুমান); provider rounding/tax/network charge অযাচাইকৃত। Proposed hard total ceiling **$15**, model download সময় এই4h-এর মধ্যেই। এটি cost proposal, owner approval বা provider-enforced budget নয়।

Scope: stronger writing-এর ছোট comparable batch এবং ছোট reference-image test, exact model/download/license approval-এর পরে। সব২১ agent, Wan/LTX/SVD/voice/music এই4h-এ শেষ করার নিশ্চয়তা নয়। Stop policy implement ও verify করতে হবে: independent deadline watchdog, quota/cost polling, no new job near cap, 4h বা$15 যেটি আগে; export যাচাইয়ের পরে owned container cleanup; idle/network volume না রাখা। এই turn-এ watchdog/provider execution implement বা verified হয়নি; সেগুলো ছাড়া paid pilot launch নিষিদ্ধ। Extra large model approvals আলাদা; license terms এখানে নতুন করে accept করা হয়নি।

## অবশিষ্ট professional acceptance

Existing [২১-agent exact candidate matrix](assets/professional/phase3_candidates.json) ও [professional readiness report](PROFESSIONAL_READINESS_REPORT.md) প্রযোজ্য; কোনো role-এর validated selection পরিবর্তন করা হয়নি। Story/Script/Director/QC-এর জন্য identical source/settings-এ অন্তত তুলনাযোগ্য actual stronger-model responses, continuity/revision/grounded-criticism metrics ও independent Bangladeshi editorial review দরকার। অন্য agents-এর নিজস্ব visual/listening/acting/production tests এখনও actual artifacts ও বিশেষজ্ঞ মূল্যায়ন চায়।

Human review **pending**; blind writing comparison এখন তৈরি করলে নতুন actual writing sample থাকবে না। পুরোনো review framework অক্ষত; এই sample আলাদাভাবে blind image viewing-এ দেওয়া সম্ভব, কিন্তু single image থেকে model ranking নয়। No production route promotion, Phase4, Render deploy/restart/data access, main change, YouTube publish, paid API/GPU বা নতুন model weights হয়নি।

## পরের resume action

1. Exact fictional writing payload → named HF Space disclosure consent চাইতে হবে; automatic rejection-এর কারণ owner-কে জানাতে হবে। Unknown request আগে reconcile; successful call অনুমান/পুনরাবৃত্তি নয়।
2. Lightning/Colab-এর secure owner login হলে actual free resources দেখেই bounded runtime canary ও exact install approval; CAPTCHA/credential chat নয়।
3. Reproducible exact checkpoint evidence পাওয়া গেলে existing worker/queue ব্যবহার; verified output export/hash মিলিয়ে তারপর equivalent Bengali comparison ও independent review।
4. Free paths অপর্যাপ্ত হলে উপরোক্ত concrete paid proposal approval এবং verified cost/stop controls ছাড়া Runpod নয়।

## Official references checked

- Lightning SDK/auth: https://api.lightning.ai/docs/platform/overview/getting-started/
- Lightning billing/free eligibility: https://api.lightning.ai/docs/platform/overview/faq/billing/
- HF ZeroGPU: https://huggingface.co/docs/hub/spaces-zerogpu
- HF documented Space API: https://huggingface.co/docs/hub/en/spaces-api-endpoints
- Colab restrictions: https://research.google.com/colaboratory/intl/en-GB/faq.html
- Colab official MCP: https://developers.google.com/colab/api/reference/mcp
- Colab official CLI: https://github.com/googlecolab/google-colab-cli
- Runpod current Pods/storage pricing: https://www.runpod.io/pricing
