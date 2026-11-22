# Phase 2 — authorized execution, 22 November 2026

Starting checkpoint: `ccc6581ba5ebb4717e7c35d57e73b725293dcb6b`। Phase 3 শুরু হয়নি। **Phase 2 BLOCKED; GPU purchase NOT APPROVED।**

## সম্পন্ন বাস্তব কাজ

- Qwen-এর exact 79-wheel, 4,200,362,442-byte closure পূর্ণ SHA256 যাচাই করে offline hash-locked install, pip check এবং actual Torch/Transformers/Qwen MoE imports PASS। Model instance বা GPU চালানো হয়নি। Signed kernel-এর exact 12 file এবং actual offline v4 resolver pin PASS; historical signature verification পুনর্ব্যবহৃত। Base model route বদলানো হয়নি।
- FP8 fail-closed preflight-এ সব assigned device SM >=8.9, exact immutable resolution, grouped/batched entrypoint এবং BF16 dequantization rejection। Synthetic guards actual FP8 CUDA execution প্রমাণ করে না।
- Official merged Diffusers PR #14413-এর `3a2f35d4efa4c059c8bfb3bc0d6c906264895c81` source archive যাচাই। Actual named Wan Distilled classes ও local original modular-index loader PASS। Shared service-এ disabled, version-locked preparation যুক্ত। Floating PR component refs-এর immutable resolution স্পষ্ট, কিন্তু tensor equivalence অনুমোদিত বলে দাবি করা হয়নি। Native generation worker এখনো চালু নয়।
- Indic-Speak/IndicF5-এর owner-authenticated exact 18 source files পুরোনো lock-এর সঙ্গে byte/hash matched। Unsafe IndicF5 `model.py` execute করা হয়নি। Gated source bytes public GitHub-এ দেওয়া হয়নি।
- Indic-Speak selected local Torch decoder-এর জন্য ভুল pip Vocos dependency সরিয়ে আসল `einops` requirement যোগ করা হয়েছে। Actual source/decoder ও dependency CPU imports, pip check PASS; TTS instance নেই।
- IndicF5-এর exact দুই mel function এক-second authored sine-এ CPU পরীক্ষা: Vocos `[1,100,94]`, BigVGAN `[1,100,93]`, common-frame mean absolute difference `3.221302032470703`। Decoder/checkpoint compatibility প্রমাণিত নয়; বিকল্প codec চালু করা হয়নি। Encodec NC gate বন্ধ।
- 15 নতুন CPU regression method; সংশ্লিষ্ট পুরোনো regression মিলিয়ে 95 distinct PASS। পুনরায় run-কে নতুন test গণনা করা হয়নি। Initial setup/fixture failures এবং সংশোধিত successful receipts সংরক্ষিত। Current 21-agent matrix check PASS; historical 20-agent matrix অক্ষত।

## নিরাপদ runtime acceptance

নতুন public Qwen/Wan prefix-এর জন্য exact interpreter/file/dependency/ABI receipt এবং existing production `isolation_command` ব্যবহার করে bounded CPU-only CI প্রস্তুত। প্রথমে ঐ ephemeral host-এর kernel boundary পাস করতে হবে; পরে 79 approved public wheels install। Private/gated source, secrets, model weights বা GPU নেই। Registry `contract_only` model routes promote হয় না। Prior completed full suites বা Colab failed Bubblewrap test পুনরায় চালানো হয়নি।

Current Work host-এর নতুন ABI preflight existing allowlist অনুযায়ী **বন্ধ হয়েছে**: `/lib/x86_64-linux-gnu/libpmix.so.2` resolves to `/usr/lib/x86_64-linux-gnu/pmix2/lib/libpmix.so.2.13.7`, outside approved system ABI path contract। Unknown library কপি বা allowlist শিথিল করা হয়নি। আলাদা free public CPU CI-র ফল পাওয়ার আগে নতুন secure runtime PASS দাবি নেই।

## প্রকাশককে বাস্তব submission

- LTX exact auxiliary SHA256: https://huggingface.co/Lightricks/LTX-2.5/discussions/113
- Wan exact component tensor/ref contract: https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers/discussions/3
- IndicF5 commercial codec/exact mel route: https://huggingface.co/ai4bharat/IndicF5/discussions/48

তিনটি public page সৃষ্টি ও পর্যবেক্ষণ করা হয়েছে; publisher উত্তর এখনো নেই। GitHub external comment integration 403; duplicate GitHub comment নেই। LTX authenticated exact artifact page-ও 403: not in authorized list। Hash/install gate CLOSED।

## বিস্তারিত প্রমাণ

- `18-profile-readiness.json`: 18 exact profiles, পৃথক CPU/binding/dependency/integrity/license/GPU/inference status। Historical evidence অক্ষত।
- `cpu-test-summary.json`, `affected-cpu-tests.log`, `new-tests-final.log`: test identity ও actual ফল।
- `qwen-fp8-cpu-startup.json`, `indic-speak-cpu-startup.json`, `wan-merged-import.log`, `f5-mel-comparison.json`: actual model-free diagnostics।
- `wheel-acquisition.json`, selected/voice/mel locks: official source, sizes, hashes এবং install ফল।
- `storage.json`: 98 staged wheel archives = 4,313,802,698 bytes; physical/logical storage আলাদা, hardlink double count এড়ানো। Exact transfer total অরেকর্ডকৃত CPython/metadata bytes থেকে বানানো হয়নি।
- `voice-source-access.json`, `voice-license-review.json`, `publisher-submissions.json`: access/rights/compatibility; full future weight rights cleared নয়।
- `render-safety.json`: owner-confirmed workspace-এর তিন service-এ live autoDeploy=no / trigger=off। Render mutation নেই।

## অবশিষ্ট বাধা

1. Qwen: exact secure CPU CI receipt, পরে eligible secure CUDA host, SM >=8.9, actual grouped FP8 precision/memory/kernel acceptance। Exact checkpoint assets আলাদা অনুমোদন ও integrity gate। T4 এই FP8 capability floor পূরণ করে না।
2. Native Wan: official source এখনও `3ad2fef7d61d6200c9c653e0fe47be7616b323f3`; CUDA module-default initialization অপরিবর্তিত। Secure CUDA host বা publisher supported deferred-device revision প্রয়োজন।
3. Distilled Wan: merged loader gap নিরসন হয়েছে; exact component tensor equivalence, active native generation adapter/full checkpoint acceptance ও motion/visual review বাকি।
4. Indic-Speak: source access ও actual CPU import gap নিরসন; exact gated source নিয়ে namespace-capable authorized host-এ secure startup, component weight rights/manifest, consent ও listening review বাকি।
5. IndicF5: exact commercial codec/checkpoint route publisher নিশ্চিত করেনি। CPU math test BigVGAN-কে drop-in বলে সমর্থন করে না।
6. LTX: separate exact auxiliary authoritative SHA256/access বাকি।

Known Colab kernel blocker পুনরায় পরীক্ষা করা হয়নি। Kaggle browser বর্তমানে signed out; free GPU বা secure host পাওয়া গেছে বলে দাবি নেই। Owner-এর সম্ভাব্য দরকারি একটি action: existing eligible free account/secure CUDA host-এ legitimate access দেওয়া। এটি publisher license বা compatibility বাধা নিজে থেকে দূর করবে না। কোনো GPU purchase/paid resource অনুমোদন চাওয়া বা চালানো হয়নি।

Story Budget-11, 21 agents, Director/Script/QC/Producer gates, main, production এবং YouTube অপরিবর্তিত। নতুন model inference, weights, deployment বা Phase 3 কাজ নেই।
