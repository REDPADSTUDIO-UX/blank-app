# Phase 2 — Private host ও Voice runtime checkpoint

শুরুর verified feature HEAD: `dfbcd2412d0b31f737d34f18a5519e20a0d4f2aa`।
Branch: `feature/video-music-editing-studio`। এই সেশনে Phase 3 শুরু হয়নি।

| বিষয় | প্রকৃত ফলাফল |
|---|---|
| Private CPU host | **FOUND / PASS** — Google Cloud Shell free, private account terminal |
| Indic-Speak source startup + secure binding | **PASS** — exact revision, actual isolated imports; model-free only |
| IndicF5 full runtime | **BLOCKED** — mel-only diagnostic এগিয়েছে, trained decoder/rights প্রমাণিত নয় |
| Native Wan startup | **BLOCKED** — namespace-capable CUDA host পাওয়া যায়নি |
| LTX auxiliary integrity | **BLOCKED / CLOSED** — authoritative SHA-256 এখনও নেই |
| 18-profile matrix | **16/18** model-free CPU startup + secure binding; আগের 15 অপরিবর্তিত |
| Phase 2 final acceptance | **BLOCKED** — 18/18 নয়; GPU purchase approval দেওয়া হয়নি |

## Access recovery ও নতুন host

GitHub connector ও feature-branch browser, authenticated Hugging Face, Kaggle notebook editor এবং signed-in Colab recent notebook list পুনরায় খোলা হয়েছে। Kaggle session off ছিল। আগের ব্যর্থ Work/Colab/Kaggle isolation probe চালানো হয়নি। কোনো login/CAPTCHA bypass হয়নি।

নতুন Cloud Shell CPU VM-এ REDPAD-এর বর্তমান `isolation_command` ব্যবহার করে native ও shared উভয় worker boundary-তে user/mount/PID/network namespace, private file read/enumeration denial, read-only input/source, writable output boundary, host loopback denial, timeout/cancellation/controller-loss ও descendant cleanup PASS হয়েছে। প্রথম `/tmp` VM connection হারানোর পরে replacement VM-এ নিজস্ব persistent private directory এবং standalone CPython 3.11.18 দিয়ে নতুন host acceptance হয়েছে। একই kernel-এর সফল gate আবার চালানো হয়নি।

পরিমাপ: 2 CPU, RAM `8,134,088 KiB`; dependency staging-এর আগে private filesystem free `4,271,915,008 bytes`। এটি CPU host; GPU নেই। Cloud API credential permission প্রত্যাখ্যান করা হয়েছে; কোনো project, billing বা cloud API resource তৈরি করা হয়নি। Runtime/source mount-এ home directory বা credentials দেওয়া হয়নি।

## Indic-Speak — প্রকৃত source startup

`bodhan-ai/indic-speak@76e0814f189321efe550011850cd288dae366aad`-এর আগের lock-এর **9টি** file authenticated session থেকে পড়ে exact byte size/SHA-256 মেলানো হয়েছে। Gated source শুধু private task directory-তে আছে, GitHub/CI-তে নেই।

Exact `inference.py:TTS`, `vocos/model.py:VocosDecoder`, Transformers `LlamaForCausalLM`/`AutoTokenizer`, SNAC class বাস্তবে import হয়েছে। TTS constructor, checkpoint loader, neural forward বা speech generation চালানো হয়নি। CPU Torch/Torchaudio `2.7.1+cpu` ব্যবহৃত; CUDA initialized হয়নি। এটি পৃথক explicit CPU diagnostic variant, approved future GPU runtime-এর বিকল্প নয়।

44 official wheels, মোট `236,926,439 bytes`, full SHA-256 verified; offline install এবং `pip check` PASS। Standalone bootstrap-সহ exact runtime identity-তে 45 distributions ও 23,944 runtime files আছে; 13 host ABI files pinned। `RuntimeBindings.validate` ও sandbox-এর ভিতরে `verify_running_runtime` PASS। App/production worker source digest অপরিবর্তিত: `b164ef5072c53e6053443332930f574d833470dd436d42c16a2c4d27e77448d2`।

Initial uv lock platform-wheel mismatch reject করেছে। Failed wheel hash গ্রহণ না করে official PyPI/PyTorch metadata থেকে একই selected versions-এর পূর্ণ hash lock বানানো হয়েছে। Package indexes আলাদা রাখা হয়েছে। Copied interpreter-এর obsolete pip metadata conflict-ও validator reject করেছে; byte-identical পুরোনো metadata শুধু task-owned copy থেকে সরানো হয়েছে, মূল interpreter অক্ষত। চারটি নতুন repair regression test PASS। প্রথম preflight failures সংরক্ষিত আছে।

Static `ldd`-তে optional FFmpeg/SoX ও preloaded Torch sonames unresolved থাকায় তা receipt-এ রাখা হয়েছে। Actual required imports sandbox-এর ভিতরে resolve করেছে; কোনো ABI allowlist বা filesystem/network policy বাড়ানো হয়নি। Optional multimedia extensions ও CUDA support গ্রহণযোগ্য ঘোষণা করা হয়নি।

## IndicF5 — সীমিত কিন্তু প্রকৃত CPU অগ্রগতি

আগের exact MIT Vocos mel-only candidate (`f5827f41ffd349ad726fe069182cae2d03823f9e9afbee3b9e5eb0b1ac34d6a1`) একই sandbox-এ চালানো হয়েছে। Encodec বা pip Vocos import করা হয়নি; BigVGAN substitution করা হয়নি।

- Authored 1-second, 24 kHz, 440 Hz sine fixture: mel shape `[1,100,94]`; independent explicit Torchaudio mel/log comparison max absolute error **0.0**।
- ISTFT signal reconstruction: 23,808 samples; max absolute error **3.725290298461914e-08**। Centered framing-এর কারণে এটিকে পূর্ণ 24,000-sample learned waveform equivalence বলা হয়নি।
- Meta-device architecture-এ 81 state keys/shapes পরিদর্শন হয়েছে; real parameters/checkpoint load বা model forward হয়নি।

এটি deterministic signal-processing evidence; trained speech, trained decoder waveform, exact IndicF5 checkpoint state compatibility বা full commercial stack acceptance নয়। Candidate inactive। Full IndicF5 source/runtime ও checkpoint integration এখনও BLOCKED।

## External blockers ও পরবর্তী নির্দিষ্ট কাজ

1. **Native Wan:** existing kernel contract পাস করা private Linux CUDA host দরকার। Read-only dependency/source binding, offline filesystem/network boundary, namespace teardown, exact CUDA driver/runtime/dependency lock ও import-only acceptance চাই। CPU host দিয়ে CUDA import বানানো যাবে না। Model-free import পরীক্ষার জন্য full model weights বা 80 GiB GPU দরকার বলে প্রমাণ নেই; registry hardware estimates generation planning, measured acceptance নয়।
2. **IndicF5:** exact wrapper/vocoder checkpoint keys, shapes, mel normalization/frame alignment, trained waveform/sample-rate এবং component checkpoint rights-এর প্রমাণ দরকার। Source MIT হলে সব weights/dependencies-ও licensed ধরে নেওয়া হয়নি। Noncommercial Encodec চালু নয়। Publisher #48-এর বর্তমান page-এ reply নেই। অনুমোদিত trained assets ছাড়া এই gate বন্ধ থাকবে।
3. **LTX:** #113-এ publisher reply নেই। `49b093a39c19169a8a81721dcc541e07e945232f`-এর `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors`, `995,778,752 bytes`-এর authoritative SHA-256 এখনও অনুপস্থিত। Download/install বন্ধ।
4. **Wan distilled follow-up #3:** publisher reply নেই; আগে accepted distilled CPU profile আবার চালানো হয়নি। Native Wan ও distilled profile আলাদা।
5. **Indic-Speak future inference:** exact component weights/license scope, speaker consent, GPU lock/ABI ও listening review আলাদাভাবে অনুমোদন/যাচাই করতে হবে। বর্তমান PASS production inference approval নয়।

## Evidence ও পুনরায় শুরুর স্থান

`verification/phase2_host_resolution_20261122/`-এ matrix, বর্তমান raw kernel log, exact source/binding receipts, wheel provenance, original failed uv lock ও final canonical lock, actual signal-processing results, preflight failures, চারটি unit-test log এবং screenshot আছে। Runtime-এর সম্পূর্ণ 23,944-file manifest private host-এ retained; তার SHA receipt-এ আছে। Gated source, wheelhouse বা weights commit করা হয়নি।

Private task: `~/redpad-phase2-private-20261122`। পুনরায় শুরুতে existing `acceptance/completed.json` ও manifest উদ্ধার করতে হবে; সফল source startup পুনরায় submit করা যাবে না। নতুন VM হলে boot identity বদলেছে কি না দেখে host gate প্রযোজ্য হবে। Dependency download নতুন করে করার আগে existing wheelhouse/lock/receipt ব্যবহার করতে হবে।

আগের 15 profiles, Qwen installation ও CPU suites পুনরায় চালানো হয়নি। কোনো model weight download, GPU/model inference, paid service, Render mutation, production DB/media access, main পরিবর্তন, YouTube publication বা Phase 3 execution হয়নি। Commit-এর আগে তিন existing Render service-এ auto-deploy `off` read-only ভাবে পুনরায় নিশ্চিত করা হয়েছে।
