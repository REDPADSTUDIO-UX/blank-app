# Phase 2 targeted CPU gaps

ভিত্তি commit `1888a251c7be91a5d20245ff8f7492b5c79cdb6b`। ১৩/১৮ model-free profile PASS এবং আগের ২১টি approved check-এর প্রমাণ বহাল। নতুন Wan diagnostic-এর ৭টি স্বতন্ত্র check সফল। [আপডেট করা ম্যাট্রিক্স](updated-18-profile-matrix.json)

## Wan Distilled · PARTIAL

পিন করা Diffusers PR #14412 commit `14f482c30c91021cc0e363a0a17a115b44972aee`-এর actual local `from_pretrained` exact index থেকে ছয়টি constructor component loader-কে দেয়। `image_processor` field এবং explicit kwarg উপেক্ষা হয়। Scheduler বাদ দিলে load ব্যর্থ হয়। Exact `encode_image` নিজে default `CLIPImageProcessor()` বানায়। Synthetic non-square RGB image দিয়ে এই path-এর pixel tensor pinned processor configuration-এর output-এর সঙ্গে exact match করেছে। PR-তে আলাদা modular block processor component ব্যবহার করে। সেটি monolithic pipeline-এর component mapping হিসেবে প্রমাণ দেয় না। **Generic loader-এর আচরণ যাচাইকৃত। Publisher-pinned processor load বা override করার mapping এই exact monolithic class-এ পাওয়া যায়নি।** এই route বন্ধ রাখা হয়েছে। [লগ](wan-loader.log) · [Exact publisher index](https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers/blob/59e4141466bcb1bf9733eca1bc78be6891c9fbdf/model_index.json) · [PR](https://github.com/huggingface/diffusers/pull/14412)

CPU diagnostic-এ সাতটি pinned class symbol এবং OpenCV/Decord native imports যাচাই হয়েছে। Transformers 5.22.2 প্রকাশ্য `T5TokenizerFast` নামটি `T5Tokenizer` class alias হিসেবে দেয়। প্রথম fixture-এর class-name equality assertion এতে ব্যর্থ হয়েছিল। সংশোধিত fixture exact export ও loader entrypoint যাচাই করেছে। আগের overlay-এ Transformers 5.22.2-এর জন্য Hub 1.31.0 ও Safetensors 0.8.0 ব্যবহার করা হয়েছে। Exact accelerator dependency closure-এ vendor FlashAttention recipe-এর version/ABI pin অজানা, এবং branch-টি CPU-তে forward চালিয়ে যাচাই করা হয়নি। Public source review বা synthetic loader দিয়ে actual checkpoint compatibility ও production runtime binding প্রতিষ্ঠিত হয় না। [আগের diagnostic dependency receipt](../phase2_approved_20261122/COMMANDS.md)

## Qwen FP8 · metadata dependency closure verified · profile PARTIAL

CPython 3.11 Linux x86-64, glibc 2.28 লক্ষ্য করে PyPI metadata থেকে ৭৯টি version-এর hashed candidate lock resolve হয়েছে। প্রতিটির জন্য উপযুক্ত, non-yanked wheel filename এবং SHA-256 public metadata ও resolver lock উভয়টিতে মিলে। Runtime stack-এ Torch 2.10.0, TorchVision 0.25.0, CUDA 12.8 runtime 12.8.90, Triton 3.6.0 এবং Transformers 5.22.2। CUDA bindings 12.9.4 হলো প্রকাশিত Python binding dependency। এটি runtime library-র version থেকে আলাদা। [Hashed lock](qwen-candidate.lock) · [Exact platform wheel list](qwen-platform-wheels.json)

Transformers 5.22.2-এর kernel loader FP8 bundle **v4** চায়। Public `v4` ref immutable commit `3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8`-এ মিলে। CUDA bundle-এর ১০টি source file-এর SHA-256 publisher metadata-এর digest-এর সঙ্গে মিলেছে। Sigstore bundle-এর byte digest নথিভুক্ত, signature trust এখনো চূড়ান্ত যাচাই হয়নি। আগের `main` v1 metadata এই exact loader-এর lock হিসেবে ব্যবহারযোগ্য নয়। [v4 evidence](qwen-kernel-v4.json) · [Versioned loader source](https://github.com/huggingface/transformers/blob/v5.22.2/src/transformers/integrations/hub_kernels.py)

ভবিষ্যৎ offline setup-এ manifest-এর একটিমাত্র selected wheel প্রতি package অনুযায়ী download ও byte hash যাচাই করে আলাদা wheelhouse বানাতে হবে। Install কেবল no-index, require-hashes মোডে। Exact kernel source ও approved signature identity যাচাই করে version 4-কে read-only immutable cache-এ bind করতে হবে এবং network-denied launcher-এ সেই commit route receipt-এ যাচাই করতে হবে। কোনো wheel install, kernel execution বা checkpoint fetch এই কাজে করা হয়নি। Assigned device SM ≥8.9, grouped symbol উপস্থিতি ও BF16 fallback প্রত্যাখ্যানের আগের policy বহাল। GPU driver ABI, kernel compile/load এবং actual precision execution বাকি। [আগের CPU preflight প্রমাণ](../phase2_approved_20261122/qwen-backend.log)

## External gates ও verdict

- **LTX — AUTHENTICATION REQUIRED।** Configured Hugging Face credential উপস্থিতি যাচাইয়ে usable credential পাওয়া যায়নি। Anonymous retry করা হয়নি। Exact artifact-এর SHA-256 অনিশ্চিত। Installation gate বন্ধ। [Redacted receipt](ltx-auth-status.json)
- **Indic-Speak — BLOCKED।** `bodhan-ai/indic-speak@76e0814f189321efe550011850cd288dae366aad`-এর source-only access আলাদাভাবে অনুমোদন করতে হবে। মালিককে intended use, Bodhan/Llama terms এবং প্রয়োজন হলে third-party hosting-এর written grant নির্ধারণ করতে হবে। Speaker consent বহাল।
- **IndicF5 — BLOCKED।** `ai4bharat/IndicF5@fb652a96e508091045890dae5bb99fe511facbcf`-এর source-only access আলাদাভাবে অনুমোদন করতে হবে। Commercial review-তে exact codec package ও weights-এর অধিকার, mel compatibility ও speaker consent লাগবে। [Voice approval details](../phase2_external_20261122/APPROVAL-BN.md)

**PHASE 2 BLOCKED।** Native Wan-এর pinned import-এর CUDA dependency, Distilled loader mapping ও production binding, Qwen-এর offline installation/FP8 যাচাই, voice access ও rights এবং LTX checkpoint integrity বাকি। Phase 3 শুরু হয়নি।
