# Story GPU — নতুন Internet-access পরীক্ষা, ১৪ নভেম্বর ২০২৬

**Real Story benchmark সম্পন্ন হয়নি। নতুন network access কার্যকর হয়েছে, কিন্তু authenticated free GPU runtime পাওয়া যায়নি। Owner এখন sign-in করতে পারবেন না বলে অগ্রগতি সংরক্ষণ করতে বলেছেন।**

এই report আগের access-failure report মুছে বা পুনর্ব্যবহার করে নতুন ফল দাবি করে না। Fresh shell checks-এর সময় প্রায় ১৪:৪৫–১৪:৪৭ Asia/Dhaka; exact UTC timestamps evidence JSON-এ আছে। Browser observations এই session-এর সরাসরি screenshot থেকে লেখা; আলাদা screenshot binary Git-এ সংরক্ষিত নয়।

## Repository ও checkpoint

Repository identity: `https://github.com/REDPADSTUDIO-UX/blank-app.git`। Clean initial local checkout ছিল `work`; remote feature HEAD fetch করে একই নামের local tracking counterpart `feature/video-music-editing-studio`-এ switch করা হয়েছে। কোনো replacement remote branch বানানো হয়নি। Checkout-এর single-branch fetch configuration-এর কারণে প্রথম সাধারণ switch ব্যর্থ হয়েছিল; explicit remote ref fetch ও একই feature নামের local checkout সফল হয়েছে।

Verified baseline: `9a2304e3b60f8198364d4b02f7b9bdfcc45d0acc`। আগের intelligence reports, Story benchmark/schema, quality/bridge/Engine, native shared model registry/worker ও runtime evidence পড়া হয়েছে। Existing source/registry এবং prior test evidence byte-identical রয়েছে। আগের ৫৮ CPU test পুনরায় চালানো হয়নি। নতুন report/evidence ছাড়া engineering পরিবর্তন নেই।

## Fresh platform results — অনুরোধের ক্রমে

| Provider | যাচাইকৃত ফল | Runtime status |
|---|---|---|
| Google Colab | Shell HTTP 200; browser homepage সফল। New notebook চাপলে “Google sign-in required” এবং “You must be logged in with a Google Account to continue.” | REACHABLE / LOGIN_REQUIRED; কোনো kernel বা GPU শুরু হয়নি |
| Kaggle | Shell HTTP 200; Code page সফল। New Notebook-এ guest scratchpad editor আসে; “Sign In or Register to continue editing”, run controls disabled। | REACHABLE / LOGIN_REQUIRED; guest editor shell GPU session নয় |
| Lightning AI | Browser: “Coming soon”, “Lightning hasn’t expanded to your area yet.” Shell HTTP 403। | Browser REACHABLE / BLOCKED by observed regional availability; quota/GPU অজানা |
| Hugging Face | Shell HTTP 200; browser homepage Log In/Sign Up দেখায়। Official ZeroGPU documentation HTTP 200। | REACHABLE / NOT_VERIFIED; signed-in account, eligible private runtime বা actual GPU নেই |
| অন্য free runtime | Current available/deferred tool inventory-তে GPU allocation/notebook connector নেই। Attached host-এ exposed NVIDIA device নেই। | NOT_VERIFIED; অতিরিক্ত eligible no-cost runtime প্রতিষ্ঠিত হয়নি |

এটি সব free provider-এর global unavailability বা ব্যক্তিগত quota exhaustion-এর দাবি নয়। Login-এর আগে hardware, account eligibility, terms ও quota যাচাই সম্ভব হয়নি। কোনো provider GPU_AVAILABLE বা EXECUTION_SUCCEEDED নয়।

Current environment instructions network enabled বলছে; inherited proxy/TLS দিয়েই test হয়েছে। Colab/Kaggle/HF-এর fresh success আগের blanket network block থেকে আলাদা। Lightning-এর 403-কে stale allowlist failure বা bot detection বলা হয়নি। Proxy bypass, route পরিবর্তন বা security downgrade হয়নি।

Browser extension control tool পাওয়া যায়নি; Cloud tab creation “Browser Use could not read requirements” দিয়েছিল। Native Chromium window input/screenshot দিয়ে বাস্তব চার provider পরীক্ষা করা হয়েছে। Native accessibility tree সীমিত; screenshots থেকে ফল দেখা হয়েছে। Browser automation failure ও website reachability আলাদা evidence।

## ZeroGPU-র বর্তমান public documentation

`https://huggingface.co/docs/hub/spaces-zerogpu`-এর fresh response অনুযায়ী verified email ও ৩০ দিনের বেশি পুরোনো good-standing free personal account সর্বোচ্চ দুটি ZeroGPU Space host করতে পারে। Documentation-এ large: ৪৮ GB এবং xlarge: ৯৬ GB NVIDIA RTX Pro 6000 Blackwell allocation; Gradio SDK এবং বিশেষ dynamic GPU lifecycle-এর শর্ত আছে। এগুলো **documentation-এর specification**, এই run-এর accessible/allocated GPU নয়।

Account eligibility, private hosting suitability, usable quota, exact pinned NF4 model compatibility ও existing isolated worker-এর সঙ্গে binding যাচাই হয়নি। Public demo থেকে অজানা model output নেওয়া হয়নি; private benchmark public Space-এ পাঠানো হয়নি। নতুন subscription, Space deployment বা prepaid credit কেনা হয়নি।

## Model সিদ্ধান্ত ও host

| Registered candidate | Exact revision | এই run |
|---|---|---|
| Primary `Qwen/Qwen3.5-27B` | `fc05daec18b0a78c049392ed2e771dde82bdf654` | চালেনি |
| `google/gemma-3-27b-it` | `005ad3404e59d6023443cb575daa05336842228a` | চালেনি |
| `google/gemma-3-12b-it` | `96b6f1eccf38110c56df3a15bffe176da04bfd80` | চালেনি |

সবগুলোর selected adapter `hf_text_nf4`। Registry GPU/RAM planning gates যথাক্রমে ২৪/৩২, ২৪/৪৮ ও ১৬/২৪ GiB; এগুলো measured minimum বা free T4 fit guarantee নয়। Original selected source weights যথাক্রমে প্রায় ৫৫.৬, ৫৪.৯ ও ২৪.৪ GB; load-time NF4-কে prequantized ছোট download ধরে নেওয়া হয়নি। Exact bundle manifest/component hashes ও license/install receipts বর্তমান runtime-এ verified নয়। Gemma gated terms গ্রহণ হয়নি। কোনো weight download বা model substitution হয়নি।

Attached host: `nvidia-smi` নেই, `/dev/nvidia*` নেই, cgroup RAM limit ৮ GiB, check-time free disk প্রায় ৬৪ GB decimal। এটি remote free GPU নয়; CPU inference চালানো হয়নি। Dependency metadata ও known cache directory presence JSON-এ আছে; private account/global cache খোঁজা হয়নি।

## Story, QC ও integration

Actual model calls **০/৭**। Primary Qwen এবং registered fallback কোনোটিই চলেনি। Canary, complete Bengali story, raw generated sections, fifteen-criterion creative QC, targeted revision এবং before/after comparison—কোনোটিই হয়নি। Generation duration, input/output tokens ও peak VRAM **null / not measured**, fabricated zero measurement নয়।

পূর্ণ গল্প নেই বলে Full Story বা human review package-এর ছদ্ম artifact তৈরি হয়নি। Independent human review এবং owner creative acceptance **PENDING**। Owner-এর progress-save নির্দেশ creative acceptance নয়। Readable story link নেই। Standalone benchmark success, real pipeline integration ও production readiness—তিনটিই প্রতিষ্ঠিত নয়।

আরও একটি পূর্ববিদ্যমান software blocker অক্ষত: `story_quality.require_runtime` unconditional block করে, যতক্ষণ scoped owner-authorized isolated worker binding প্রতিষ্ঠিত না হয়। বর্তমান request bounded free inference-এর authorization দেয়; generic অনুমতি আবার চাইতে হবে না। কিন্তু exact source/rights receipts, actual free allocation, tokenizer/resource compatibility ও scoped execution binding যাচাই ছাড়া সেই gate সরানো যাবে না। এটি accessible GPU পাওয়া গেলেই সমাধান হয়ে গেছে বলা হচ্ছে না।

## Owner-এর সবচেয়ে ছোট পরবর্তী action

Owner-কে shared Cloud Desktop-এর **Take over** দিয়ে Colab-এ Google sign-in করে **Return control** দিতে বলা হয়েছিল। Owner উত্তর দিয়েছেন: **“এখন পারব না—অগ্রগতি সংরক্ষণ করুন”**। তাই login, credentials, MFA বা account permissions নিয়ে আর এগোনো হয়নি।

যখন পারবেন, একই shared Desktop-এ Colab sign-in করে control ফেরত দিলেই প্রথম বাধা পরীক্ষা করা যাবে। Sign-in GPU পাওয়ার নিশ্চয়তা নয়। তারপর actual free quota/allocation, GPU/VRAM, RAM/disk, pinned bundle/rights ও existing worker binding যাচাই করতে হবে। প্রয়োজন হলে কেবল eligible registered fallback-এর আলাদা labelled result হবে।

Existing canary এবং পাঁচ bounded primary section reuse করতে হবে। Failures-সহ সাত call ceiling; canary প্রথমবার pass করলে সর্বোচ্চ একটি targeted revision-এর জায়গা আছে। Exact prompts/raw outputs/telemetry capture ও lossless assembly-এর পরেই QC এবং readable owner package। কোনো generic Master Prompt বা redundant CPU engineering প্রয়োজন নেই।

## সংরক্ষিত evidence

`verification/story_gpu_recheck_20261114/`-এ:

- `http_checks.json`: fresh ordered shell results ও exact timestamp/duration।
- `platform_attempts.json`: browser observations, status, owner defer এবং unverified fields।
- `zerogpu_docs.json`: current official documentation excerpts; allocation proof নয়।
- `effective_environment.json`: effective reachability, host/dependency/cache inventory ও control limitation।
- `execution_status.json`: exact registry candidates, zero calls, null outputs/telemetry এবং resume blockers।
- `preservation.json`: checkpoint থেকে ১২টি source/registry/evidence file-এর unchanged SHA-256।

শুধু feature branch-এ lightweight evidence/report commit ও push। Commit message-এ `[skip ci] [skip render]`; কোনো manual workflow/deploy trigger নয়। `main` modify/merge/push, paid GPU/API/billing/trial, Render deploy/restart/migration, production DB/media change বা YouTube publication হয়নি। Final pushed commit ও remote verification chat-এর উত্তরে থাকবে।
