# REDPAD AI Studio — Phase 2 owner sign-off evidence

২২ নভেম্বর ২০২৬, ঢাকা। Audited feature checkpoint ca71238ba55b0c4dc2dec4c29f16a5e89db0c90d।

| Gate | সিদ্ধান্ত |
|---|---|
| CPU ENGINEERING COMPLETE | অনুমোদিত source, dependency ও CPU-only কাজের আওতায়। Diagnostic evidence যোগ হয়েছে। কোনো production worker বা route বদলায়নি। |
| EXTERNAL APPROVALS PENDING | Exact FP8 recipe, pinned publisher pipeline, gated voice source, commercial codec যাচাই ও LTX auxiliary integrity evidence বাকি। |
| GPU-DEPENDENT VERIFICATION PENDING | Exact model load, device binding, CUDA/precision, memory, cancellation ও artifact acceptance বাকি। |
| PHASE 2 | **BLOCKED**। ১৮টির মধ্যে ১৩টির model-free CPU startup ও secure runtime binding যাচাইকৃত। Mandatory criteria পরিবর্তনের owner approval পাওয়া যায়নি। |
| GPU PURCHASE | **NOT APPROVED**। Phase 3 শুরু হয়নি। |

## স্বাধীন evidence review

আগের ১৩টি PASS-এর actual import JSON compressed job log থেকে পুনরুদ্ধার করে receipt, exact lock, interpreter path এবং current pinned model registry-এর সঙ্গে মিলিয়েছি। LTX/ACE source manifest count ও SHA-256-ও মিলেছে। GitHub-এর live job conclusion ও tested commit committed receipts-এর সঙ্গে মিলে। নতুন করে কোনো completed runtime profile চালানো হয়নি। [১৮-profile matrix](final-18-profile-matrix.json) · [স্বাধীন receipt audit](receipt-audit.json)

বর্তমান ২১-agent matrix check পাস। ঐতিহাসিক kernel run-এ native/shared launcher-এর private-file denial, read-only input, writable boundary, network isolation, timeout, cancellation, controller loss ও launcher parity রেকর্ড আছে। Current supervisor প্রতি run-এ পৃথক child launch করে এবং process group cleanup করে। আগের exact runtime locks ও kernel evidence সংরক্ষিত। [Kernel canary](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44921166025) · [সর্বশেষ lifecycle-fix kernel run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44931884961)

## পাঁচটি অসম্পূর্ণ profile

| Profile | Evidence ও ঝুঁকি | Owner decision ও ক্ষুদ্রতম পরবর্তী কাজ |
|---|---|---|
| Qwen 3.5 MoE | CPU/meta 128×128 FP8 geometry পাস। নতুন exact backend guard probe-এ CPU-তে quantize-on-load প্রত্যাখ্যান হয়েছে, কিন্তু prequantized config BF16 dequantization চালু করেছে। এর ফলে precision ও RAM/VRAM budget বদলাতে পারে। | Exact FP8/backend ও checkpoint অনুমোদন দিন অথবা route বন্ধ রাখুন। অনুমোদনের পরে fallback বন্ধ রাখা ও CUDA capability যাচাইয়ের preflight যোগ করে GPU pilot চালানো যাবে। পরীক্ষিত backend-এর CUDA floor 8.9। |
| Wan Animate 2 | Pinned source ও diagnostic sandbox binding যাচাইকৃত। T5Encoder-এর default argument import-এর সময় torch.cuda.current_device() চালায়। | Pinned source-এর জন্য অনুমোদিত CUDA import-only host, অথবা publisher-reviewed deferred-device revision অনুমোদন প্রয়োজন। Source pin অক্ষত রেখে প্রথমে entrypoint-only test করুন। |
| Wan Animate 2 Distilled | Pinned model index WanAnimate2Pipeline চায়। Tested Diffusers ও verified main exports-এ আলাদা WanAnimatePipeline আছে। Substitution করলে pinned conditioning contract হারায়। | Publisher থেকে exact class source, dependency lock ও revision receipt চাওয়া প্রয়োজন। এগুলো পাওয়া গেলে CPU symbol ও sandbox test চালান। |
| Indic-Speak | Selected source gated। Public metadata license other এবং actual source access 401। SNAC/Vocos support probes পূর্ণ source বা use rights প্রমাণ করে না। | Owner account-এ exact revision-এর source access ও publisher terms review প্রয়োজন। অনুমোদিত source-only bundle-এর hashes মেলান এবং reviewed codec/speaker contract দিয়ে CPU startup পরীক্ষা করুন। |
| IndicF5 | Exact source gated। Vocos-এর Encodec pin noncommercial। Upstream BigVGAN-এর MIT code/model metadata আছে, pinned IndicF5 mel/decoder compatibility বাকি। | Owner-authorized exact source ও commercially eligible codec-এর explicit approval প্রয়োজন। প্রথমে mel, decoder shape ও rate যাচাই করুন। Speaker/reference consent এবং no-fallback gate বহাল রাখুন। |

এ ছাড়া **LTX 2.5 checkpoint gate বন্ধ**। Exact publisher SHA-256 অনুপলব্ধ। Artifact-এর size 995,778,752 bytes এবং public report-এ LFS OID masked। Publisher-এর exact hash ও approved auxiliary manifest লাগবে। [Publisher checkpoint evidence](../runtime_phase2_targeted_20261121/ltx-publisher-check.json)

## OpenImageIO lifecycle

একই pinned CPU prefix-এ চারটি child process চলেছে। প্রতিটিতে একই PID-তে ১৬০টি synthetic PNG write/read cycle এবং প্রতি ১৬ cycle-এ RSS ও file-descriptor sample নেয়া হয়েছে। উভয় colour-enabled process-এর shutdown-এ nanobind warning এসেছে। উভয়ের warm-up-পরবর্তী RSS delta 0 KiB। চারটির sampled descriptor count 4 এবং exit code 0। দ্বিতীয় colour-enabled process আগের warning-এর পর একইভাবে শেষ হয়েছে। এই bounded host diagnostic-এ crash, hang বা observed resource growth পাওয়া যায়নি। দীর্ঘমেয়াদি production workload-এর ফল বাকি। [Lifecycle evidence](oiio-lifecycle.json)

নতুন যাচাইয়ে চারটি fail-closed gate check, একটি exact FP8 backend guard probe, ৬৪০টি synthetic image cycle এবং ২১-agent consistency check ছিল। কোনো নতুন profile startup pass দাবি করা হয়নি। Production code বদলায়নি, তাই পুরোনো পূর্ণ suite পুনরায় চালানো হয়নি। [Gate audit](gate-audit.json) · [FP8 backend probe](fp8-gate-probe.json)

## GPU handoff এবং sign-off

Owner approvals ও exact source/model/auxiliary manifests সম্পূর্ণ হলে প্রথমে driver ও runtime build, precision, device allowlist, offline mounts এবং cold load যাচাই করুন। পরে bounded load/unload ও cancellation চালিয়ে GPU/host memory, wall time এবং artifact provenance মাপুন। Voice-এর ক্ষেত্রে consent receipt ও স্বাধীন listening review এবং ভিডিও/music-এর ক্ষেত্রে technical QC ও স্বাধীন creative acceptance প্রয়োজন। কোনো পরীক্ষার জন্য এই sign-off-এ GPU inference বা deployment করা হয়নি।

Phase 2 acceptance criteria পূরণ বা documented owner-approved পরিবর্তন ছাড়া Phase 2 বন্ধ থাকবে। Phase 3-এর জন্য আলাদা owner authorization প্রয়োজন। [পুনরুৎপাদন commands](COMMANDS.md)
