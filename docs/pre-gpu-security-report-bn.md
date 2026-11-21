# REDPAD AI Studio — প্রি-GPU নিরাপত্তা ও ইঞ্জিনিয়ারিং

তারিখ ২১ নভেম্বর ২০২৬, ঢাকা। কাজ শুরুর সময় যাচাইকৃত feature HEAD `39777ee627fb796f239a16340c50cbc24ec8677c`। অনুমোদিত শাখা `feature/video-music-editing-studio`। ২১ এজেন্টের registry, matrix, Dashboard বা approval contract-এ কোনো পরিবর্তন করা হয়নি।

**পূর্ণ PRE-GPU ENGINEERING SIGN-OFF স্থগিত।** কার্যকর kernel namespace-এ filesystem denial canary, প্রকৃত interpreter bundle দিয়ে startup validation এবং target host-এর ABI compatibility বাকি। GPU কেনার ছাড়পত্রও দেওয়া যাচ্ছে না।

| বিষয় | অবস্থা | ফল ও সীমা |
|---|---|---|
| Native worker filesystem isolation | PARTIAL | পুরো filesystem-এর read-only bind অপসারণ হয়েছে। Bubblewrap-এ model, reviewed source, reference, request ও host ABI file manifest ধরে bind হয়। রানটাইমের নিজস্ব manifest-যাচাইকৃত prefix read-only। শুধু নির্দিষ্ট output writable, সঙ্গে namespace-local temporary storage। Synthetic private-file denial-এর আসল kernel test এই host-এ UID map তৈরির সময় আটকে গেছে। |
| Shared text/image supervisor | FIXED | পুরনো সরাসরি worker subprocess সরানো হয়েছে। Shared worker native supervisor-এর timeout, cancellation, process cleanup ও persisted run state ব্যবহার করে। Kernel বা runtime approval অনুপস্থিত হলে launch বন্ধ হয়। Terminal receipt এবং text/image artifact SHA-256 পরের software handoff-এ যাচাই হয়। একই sandbox-এর kernel যাচাই আগের সারির বাধার অধীন। |
| Per-profile runtime compatibility | PARTIAL | Exact model revision, interpreter, local distribution versions, Studio source digest ও pinned Linux ABI manifest যাচাই করে runtime বাঁধা হয়। Child-ও interpreter ও distributions পরীক্ষা করে। ভিন্ন dependency lock একই prefix-এ অনুমোদিত হয় না। প্রকৃত per-model runtimes বা CUDA compatibility যাচাই হয়নি। |
| CPU regression ও CI | FIXED | Final suite-এ 700টি distinct test ID, 699টি pass, 1টি kernel skip, failure/error শূন্য। Full log, Python ও dependency receipt, command এবং run history সংরক্ষিত। Non-deployment smoke workflow-এ native, isolation এবং pre-GPU tests যোগ হয়েছে। |
| LTX 2.5 spatial upscaler | BLOCKED | Official tree-তে exact size **995,778,752 bytes**। LFS SHA-256 redacted। Exact pinned artifact-এর HEAD এবং metadata lookup দুটোই HTTP 401। ওজন নামানো বা access/license গ্রহণ ছাড়াই size যোগ হয়েছে। SHA-256 অনুপস্থিত থাকায় installation gate বন্ধ। |
| এজেন্ট ও অনুমোদন integration | FIXED | বিদ্যমান ২১-agent matrix check, Director/QC/Producer gates, Casting, stale-source, handoff ও restart-এর CPU পরীক্ষা চালানো হয়েছে। |

## Runtime ও evidence

`RuntimeBindings.approve(profile, receipt, owner=..., confirmed=True)` একটি owner-approved standalone runtime-এর জন্য। Receipt-এ exact `profile`, `revision`, `prefix`, `interpreter`, `dependency_lock`, `files`, `system_files` ও `studio_sha256` লাগে। Filesystem manifest-এর প্রতিটি ফাইলে `bytes` এবং `sha256` লাগে। সক্রিয় host-এর default interpreter বা virtualenv-এ automatic fallback নেই। আলাদা পরিবেশে Torch, Transformers, Diffusers, bitsandbytes, audio codec এবং native video package lock করুন। Host loader, CUDA driver soname ও ঐচ্ছিক FFmpeg libraries পৃথক system manifest-এর অন্তর্ভুক্ত। ইতিমধ্যে queue করা native কাজের runtime hash বদলালে আবার explicit queue প্রয়োজন। পুরনো কাজের ইতিহাস সংরক্ষিত।

Shared কাজের run ID দিয়ে একই isolated store-এ `cancel`, `recover` ও `status` ব্যবহার করা যায়। Interrupted কাজ স্বয়ংক্রিয়ভাবে পুনরায় চালানো হয় না। Result hash terminal receipt পরিবর্তন শনাক্ত করে। Research output-এর পরে স্বাধীন QC ও owner acceptance আগের মতো প্রয়োজন।

এই host-এ kernel probe-এর ফল `bwrap: setting up uid map: Read-only file system`। Probe-এ synthetic private marker এবং read-only request ব্যবহার করা হয়েছে। এই ফল UID map block প্রমাণ করে। Namespace-এর ভেতরে private file denial প্রমাণ করতে test-টি isolation-সক্ষম host-এ পাস করতে হবে।

## বাকি কাজ

- **CPU ও নিরাপত্তা।** Linux target host-এ synthetic private-file denial, read-only input, writable isolated output ও network namespace canary পাস করুন। একই kernel-এ fixed dummy worker দিয়ে PID namespace-এর descendant cleanup ও controller-loss recovery মাপুন। প্রকৃত owner-approved profile prefix-এ model import ছাড়াই interpreter, locked distributions, read-only mounts ও loader/FFmpeg ABI startup যাচাই করুন। LTX-এর জন্য exact revision-এর authenticated publisher metadata বা Git LFS pointer থেকে SHA-256 সংগ্রহ এবং আগের size-এর সঙ্গে মিলিয়ে gate যাচাই প্রয়োজন।
- **GPU।** অনুমোদিত device, driver/CUDA runtime এবং checkpoint দিয়ে cold load, smallest valid generation, native clip বা audio, timeout, cancellation, cleanup ও unload পরীক্ষা করুন। Per-profile peak VRAM/RAM, timing, reference binding এবং output provenance রাখুন। Voice/video/music এবং Bengali writing-এর জন্য স্বতন্ত্র technical ও artistic acceptance আগের মতো প্রযোজ্য।
- **সীমা।** কোনো নতুন runtime/model installation, weight download, license acceptance, GPU inference, deployment, production database/media change বা YouTube publishing করা হয়নি। CI source বদলেছে। এই push-এর জন্য বিদ্যমান `[skip ci] [skip render]` safeguards রাখা হয়েছে।

[CPU evidence](../verification/pre_gpu_security_20261121/) · [LTX metadata receipt](../verification/pre_gpu_security_20261121/ltx-upscaler-metadata.json) · [Isolation tests](../tests/test_worker_isolation.py)
