# REDPAD AI STUDIO — Phase 2 CPU completion

**CPU ENGINEERING COMPLETE — PHASE 2 BLOCKED।** আগের ১১টি যাচাইকৃত profile-এর প্রমাণ পুনর্ব্যবহার করা হয়েছে। Exact LTX 2.5 ও ACE-Step 1.5 যোগ হয়ে **১৮টির মধ্যে ১৩টির model-free CPU startup ও secure binding যাচাইকৃত**। Model loading, GPU inference ও production approval পৃথক gate। Phase 3 শুরু হয়নি। [পূর্ণ ১৮-profile matrix](final-18-profile-matrix.json)

| Profile | ফল ও পরবর্তী নির্দিষ্ট শর্ত |
|---|---|
| LTX 2.5 | **CPU ও secure binding PASS।** Pinned LTX Core/Pipeline 1.6.2 থেকে চারটি exact import, Python 3.11 এবং Torch 2.10.0+cpu-তে। Torch 2.7.1-এর compiler API ঘাটতি লগে আছে। Publisher spatial-upscaler-এর exact SHA-256 এখনও প্রয়োজন এবং checkpoint gate বন্ধ। |
| ACE-Step 1.5 | **CPU ও secure binding PASS।** Pinned handler, generate_music callable ও condition model class sandbox-এ import হয়েছে। Approved production bundle, publisher CUDA 12.8 stack এবং GPU generation পরীক্ষা বাকি। Optional training packages এই CPU lock-এর বাইরে। |
| Qwen 3.5 MoE | **CPU recipe evidence।** Published packed geometry মেনে 128×128 synthetic E4M3FN tile conversion ও routed CPU reference পাস। Exact FP8 recipe ও checkpoint realization-এর owner approval এবং actual CUDA kernel পরীক্ষা প্রয়োজন। |
| Wan Animate 2 | **CPU startup BLOCKED।** Exact dependency/source pin ও sandbox child যাচাই হয়েছে। Pinned T5Encoder-এর default argument import-এর সময় torch.cuda.current_device() চালায়। Exact route-এর জন্য CUDA-capable host অথবা publisher-reviewed deferred-device revision দরকার। |
| Wan Animate 2 Distilled | **BLOCKED।** Official Diffusers main export-এ WanAnimatePipeline আছে। Pinned model index যে WanAnimate2Pipeline চায়, সেটির exact publisher-supported implementation ও lock এখনও প্রয়োজন। |
| Indic-Speak | **BLOCKED।** Exact source gated। Owner-authorized access, publisher terms review এবং exact SNAC/Vocos dependency closure প্রয়োজন। |
| IndicF5 | **BLOCKED।** Exact source gated। Upstream F5-এ BigVGAN বিকল্প আছে এবং পরীক্ষিত NVIDIA code/model metadata MIT দেখায়। IndicF5-এর pinned mel/decoder contract-এর সঙ্গে এর compatibility অযাচাইকৃত। Owner-approved exact commercial route ও source review প্রয়োজন। Vocos-এর noncommercial Encodec ব্যবহার বা codec substitution হয়নি। Speaker-consent gate বহাল। |

## সংশোধন ও পরীক্ষা

Engineering commits 650b307 এবং d5795b3 hash-pinned empty publisher source ও fixed sanitized worker identity সমর্থন করে। Empty model component এখনও প্রত্যাখ্যাত হয়। Sandbox-এ host account database ছাড়াই Torch cache username resolution চলে। Host username বা environment যোগ হয়নি।

OpenImageIO shutdown warning শুধু import-এ পুনরুৎপাদিত হয়নি। নির্দিষ্ট Torch, OpenImageIO ও colour import combination-এ nanobind reference-leak warning এসেছে, exit code 0। Exact LTX sandbox startup পাস করেছে। Third-party teardown warning production/long-running compatibility যাচাইয়ের জন্য নথিভুক্ত।

**নতুন targeted regression ১২১টি স্বতন্ত্র test pass, ০ fail/error/skip।** পৃথক focused ২-test ও ১-test run এই ১২১টির সঙ্গে overlap করে। Exact kernel checks চারটি LTX ও তিনটি ACE import পাস করেছে। Wan-এর একটি intentional CPU import probe CUDA initialization-এ ব্যর্থ হয়েছে। কোনো weight download, model inference, production approval, deployment বা Phase 3 execution হয়নি।

[সফল LTX run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44932910851) · [সফল ACE run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44933003941) · [Wan CPU limitation](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44933044564) · [রসিদ](sandbox-receipts.json) · [Regression receipt](regression-receipt.json)
