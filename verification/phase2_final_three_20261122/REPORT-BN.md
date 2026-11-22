# Phase 2 — final-three execution, 22 November 2026

Starting verified remote feature HEAD: `d1c5904697085e55ab30acf77084d7e7b0c84d64`। Branch `feature/video-music-editing-studio`। **Phase 2 BLOCKED; 15/18 model-free CPU startup + secure binding acceptance retained। GPU purchase NOT APPROVED। Phase 3 শুরু হয়নি।**

## বাস্তব execution ও ফল

| কাজ | ফল | প্রকৃত প্রমাণ / যা বাকি |
|---|---|---|
| Native Wan Animate 2 | BLOCKED | Official source main/pin `3ad2fef7d61d6200c9c653e0fe47be7616b323f3` অপরিবর্তিত। Saved source lock ও original CUDA-default failure পুনর্ব্যবহৃত; failed import পুনরায় চালানো হয়নি। Fresh private Kaggle session namespace test ব্যর্থ; তাই CUDA import/supervisor/lifecycle acceptance হয়নি। Existing Torch 2.7.1+cpu diagnostic lock-কে CUDA closure বলা হয়নি। |
| Indic-Speak | BLOCKED | Authenticated exact `inference.py` আবার পড়ে পূর্বের 7,939-byte SHA256 মিলেছে। Source access blocker নেই; secure host blocker আছে। Gated source public CI বা notebook-এ পাঠানো হয়নি। Actual secure source startup/cancellation/recovery যাচাই বাকি। |
| IndicF5 | BLOCKED | Authenticated exact `model.py` 5,774-byte hash matched; unsafe code execute হয়নি। Original mel comparison preserved। New MIT Vocos mel-only candidate statically prepared/tested; no Encodec/BigVGAN activation। Full checkpoint state, decoder/waveform/24kHz, rights ও secure binding বাকি। |
| LTX auxiliary | BLOCKED | #113-এ authoritative উত্তর নেই। Exact pinned artifact page authenticated session-এও 403: not in authorized list। Size 995,778,752 bytes; authoritative SHA256 এখনো null; installation CLOSED, checkpoint download হয়নি। |

## Free host যাচাই

মালিক এই session-এ Kaggle login সম্পন্ন করেছেন; authenticated owner UI যাচাই হয়েছে। Existing `notebookd995a6419e`-এর Share dialog-এ **Private — only collaborators can view** checked ছিল। Sharing/permissions বদলানো হয়নি। পুরোনো দুইটি cell/output অক্ষত রেখে নতুন, পৃথক `kaggle_host_20261122_v1` cell যোগ করা হয়েছে।

Existing free **GPU T4 x2** setting-এ session start সফল। একটিমাত্র stdlib security preflight চালানো হয়েছে (reported execution 0.025s):

```
bwrap: absent
unshare --user --map-root-user --mount --pid --net --fork /bin/true
exit code: 1
unshare: unshare failed: Operation not permitted
```

এটি resource quota/GPU availability failure নয়; mandatory REDPAD kernel isolation failure। Device enumeration, actual VRAM/driver বা CUDA যাচাই করা হয়নি, কারণ security gate আগেই ব্যর্থ। Torch/model imports, packages/weights download ও private source transfer হয়নি। নিজের start করা session **Stop session** করে UI-তে `Session stopped` এবং `Draft Session off` পর্যবেক্ষণ করা হয়েছে। Notebook private draft saved; পুরোনো experiment clear/restart/re-run করা হয়নি।

এই Work snapshot-এ `/proc` rw এবং bwrap উপস্থিত দেখে একবার বর্তমান private host canary চালানো হয়েছে—পুরোনো Colab Bubblewrap failure পুনরায় নয়। Result **SKIPPED/BLOCKED**, PASS নয়:

```
bwrap: loopback: Failed to create NETLINK_ROUTE socket: Operation not permitted
```

আগের known Colab security blocker পুনরায় চালানো হয়নি; current browser শুধু signed-in Colab home দেখায়, connected notebook/GPU-এর প্রমাণ নয়। অন্য secure free CUDA host যাচাইকৃত পাওয়া যায়নি। Existing public GitHub CPU acceptance অন্য 15 profile-এর জন্য আগেই সংরক্ষিত; gated Voice source সেখানে upload করা হয়নি এবং সেই suite/install পুনরায় চালানো হয়নি।

## IndicF5 — নতুন বাস্তব engineering, সীমিত দাবি

Official PyPI `vocos==0.1.0`-এর **24,085-byte** public source wheel পূর্ণ SHA256 `0ac13eaef68596074301e912d781399b3defa4b4ca60b6bc52c8a4b9209ca235` যাচাই করে শুধু source পড়া হয়েছে; package install/execute করা হয়নি। Exact wheel-এর MIT notice: Copyright 2023 Charactr Inc.; notice retained। Original wheel metadata এখনও `encodec==0.1.1` requires করে।

Source review-এ দেখা গেছে NC Encodec path হলো আলাদা `EncodecFeatures` path এবং generic loader-এর optional branch। একই Vocos mel-only path প্রস্তুত করতে BigVGAN-এ পরিবর্তন অপরিহার্য নয়। `experiments/phase2_f5_codec_candidate.py` full-hash locked public source থেকে exact selected AST নিয়ে একটি **review candidate** তৈরি করে:

- Original `MelSpectrogramFeatures`, ConvNeXt backbone ও ISTFT math-এর selected AST অক্ষত।
- `Vocos`-এর শুধু constructor/forward/decode; Encodec, generic checkpoint/download loaders বাদ।
- Syntax compilation পর্যন্ত; `exec`, Torch imports, model construction বা decoder execution হয় না।
- Generated candidate `.py.txt` হিসেবে রাখা; active native worker, runtime requirements বা registry বদলানো হয়নি।

এটি source-code-only সম্ভাব্য mel route; **full commercially cleared / checkpoint-compatible codec বা actual runtime PASS নয়**। Existing F5 model and component rights, embedded vocoder state/key/tensor compatibility, waveform/sample-rate and exact dependency startup still unverified। Host access এবং প্রয়োজনমতো publisher clarification/authorized compatibility test বাকি। Existing BigVGAN mel mismatch (`94` vs `93` frames, mean absolute difference `3.221302032470703`) অপরিবর্তিত; বিকল্প codec সমতুল্য বলে দাবি নেই।

## নতুন tests

শুধু নতুন candidate-এর **5 distinct CPU unittest PASS**:

1. Changed source/license hash rejects before compilation.
2. Missing/extra source rejects.
3. No source execution during preparation; launch remains disabled.
4. Encodec/Hub/checkpoint-loader entrypoints absent from candidate.
5. Original mel class AST এবং attribution preserved; full rights/checkpoint acceptance remain false.

আলাদা current Work host canary: **1 skipped**, 0 runtime acceptance। Kaggle primitive: **1 actual failed eligibility probe**, no retries। Historical 95 tests এবং Qwen installation পুনরায় চালানো হয়নি। Application worker source digest `b164ef5072c53e6053443332930f574d833470dd436d42c16a2c4d27e77448d2` unchanged; all 15 accepted profile records exactly retained।

## প্রকাশক-উত্তর

Existing তিনটি discussion reload করে শুধু owner-এর original request দেখা গেছে; **publisher reply নেই**, নতুন duplicate post/comment নেই:

- LTX: https://huggingface.co/Lightricks/LTX-2.5/discussions/113
- Wan Distilled: https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers/discussions/3
- IndicF5: https://huggingface.co/ai4bharat/IndicF5/discussions/48

Wan Distilled-এর পূর্বের artifact-identity/CPU binding PASS অক্ষত; নতুন acceptance হিসেবে গণনা করা হয়নি। LTX access agreement মালিকের পক্ষে গ্রহণ করা হয়নি।

## পরবর্তী অপরিহার্য শর্ত

- **Native Wan:** Linux host with actual permitted user/mount/pid/network namespaces, approved CUDA device/ABI + exact CUDA dependency closure; then bounded pinned import/supervisor/lifecycle acceptance। শুধু GPU allocation এই শর্ত পূরণ করে না।
- **Indic-Speak:** এমন private namespace-capable host-এ owner-authorized exact gated source ও dependency prefix। আগে secure source startup/binding; component weights, consent ও real TTS আলাদা approval/evaluation।
- **IndicF5:** private secure host-এ exact source startup এবং staged MIT mel candidate-এর real contract testing; then complete rights/checkpoint state/decoder/waveform verification। বর্তমান default pip route/NC component production-এ চালু নয়।
- **LTX:** publisher-authenticated exact digest অথবা মালিকের legitimate authorized metadata access। ততক্ষণ gate CLOSED।

Kaggle login বাধা এইবার সমাধান হয়েছে; একই account-এ আবার login চাওয়া এই kernel বাধা সমাধান করবে না। Known failed namespace probes অনাবশ্যক পুনরায় নয়; access/policy/host বদলালে একবার নতুন eligibility check। নিরাপত্তা শিথিল, untrusted remote code, GPU purchase/paid resource, deployment, main/production/media/YouTube পরিবর্তন বা Phase 3 নয়।

## Checkpoint evidence

`18-profile-readiness.json` হলো previous matrix-এর preserved continuation। শুধু বাকি তিনটির latest blockers এবং আলাদা LTX auxiliary gate updated; 15 accepted profile rows unchanged। `publisher-replies.json`, `kaggle-host-receipt.json`, `private-host-kernel.log`, source checks, candidate/AST report, `new-static-tests.log` এবং screenshot actual evidence। Render-এর তিন service-এর live autoDeploy=no / trigger=off যাচাই; final checkpoint uses `[skip ci] [skip render]` so old suites/Qwen installation/deployment do not restart।
