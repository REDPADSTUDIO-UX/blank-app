# Story AI — approved bundle download ও benchmark resume

১৬ নভেম্বর ২০২৬। **DOWNLOAD VERIFIED COMPLETE / REAL STORY BENCHMARK BLOCKED**।

Remote feature HEAD `0ba7f5c82031e1c16f7dd8635058d18496f355ee` যাচাই করে সেখান থেকে কাজ হয়েছে।
পূর্বের Option C অনুমোদন ও বর্তমান তিন-artifact download অনুমোদন ব্যবহার করা হয়েছে; একই অনুমতি আবার চাওয়া হয়নি।
Production Story Secure Worker, primary model, owner locks, registry এবং পূর্বের evidence অপরিবর্তিত।

## বাস্তব Colab ও নিরাপত্তা

| বিষয় | প্রকৃত ফল |
|---|---|
| Browser | Existing authenticated Chrome Colab notebook; শেষে All changes saved |
| Free account | Not subscribed; zero compute units; free resources not guaranteed |
| Session estimate | UI-তে up to 3h30m; নিশ্চিত quota নয় |
| GPU | Tesla T4; total 15360 MiB, free 14913 MiB; driver 580.82.07; compute capability 7.5 |
| RAM | Download preflight: 13,605,810,176 bytes total / 12,258,385,920 available; প্রায় 12.67 / 11.42 GiB |
| Disk | Download-এর আগে 120,839,188,480 bytes free; পরে UI প্রায় 7.2/112.6 GiB used |
| Boundary | পৃথক research-only runtime; Drive mount নেই; secrets/production DB/private media access নেই |
| Production security | Kernel isolation equivalent দাবি নেই; failed Bubblewrap/unshare পরীক্ষা পুনরাবৃত্তি হয়নি |
| Model generation | নতুন submission ০; নতুন raw Bengali output ০ |

## অনুমোদিত তিনটি download — সম্পন্ন

শুধু missing তিনটি artifact download হয়েছে। কোনো dependency installer, README re-fetch,
অন্য checkpoint, gated license acceptance বা অতিরিক্ত model download হয়নি। পূর্বের pinned source/license
evidence বহাল: Apache-2.0 model, MIT runtime। Exact URLs ও checksums পূর্বের manifest-এর সঙ্গে মিলেছে।

| Artifact | Actual bytes | Download wall time | Full SHA256 |
|---|---:|---:|---|
| Qwen3.5-9B-Q4_K_M.gguf | 5,680,522,464 | 71.35s | MATCH |
| cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 594,371,580 | 17.50s | MATCH |
| llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 197,999,267 | 5.67s | MATCH |

Model: `unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`।
SHA256: `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`।
সব তিনটি full checksum pass করার পর runtime extract হয়েছে। Extracted binary hash
`0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5` মিলে গেছে।
`--version`: **0.9.0-dev, build 12318, commit 7021f7e09, GNU 13.3.0 Linux x86_64**।
এটি model-load বা CUDA backend success প্রমাণ নয়। Download time-এর বাইরে hashing/extraction time আছে।

## Canary launch — নির্দিষ্ট failure ও দায়

আগের repetitive foundation failure-এর পরে পৃথক `option_c_schema_constrained_v1` research variant প্রস্তুত হয়েছে:
একই original brief/section schema, 4096 context, canary 384/section 1536 output tokens, seed 117,
schema-constrained response, repeat penalty 1.08 এবং foundation-এ সর্বোচ্চ চারটি distinct assumption।
Quality gates কমানো হয়নি। Actual model-generated result ছাড়া এই variant-এর কার্যকারিতা প্রমাণিত নয়।

একটি launch attempt **1.001s**-এ থেমেছে:

```text
error while handling argument "--device": invalid device: CUDA0
```

Safe `ldd` diagnostic-এ exact missing resolution:

```text
libcuda.so.1 => not found
```

Driver আসলে host-এ আছে: `/usr/lib64-nvidia/libcuda.so.1` →
`/usr/lib64-nvidia/libcuda.so.580.82.07`। অন্য CUDA runtime/cublas libraries approved archives থেকেই resolve হয়েছে।
**নতুন research launcher-এর minimal environment বানানোর সময় provider-এর existing driver directory library
path-এ বাদ পড়েছে—এটি এই launcher configuration-এর ভুল।** Model বা T4 মৌলিকভাবে অচল, অথবা driver
ডাউনলোড করতে হবে—এমন সিদ্ধান্ত evidence সমর্থন করে না। Production worker-এ এটি প্রয়োগ করা হয়নি।

Server device নির্বাচনেই বেরিয়ে গেছে; model-load/offload evidence নেই; `/v1/chat/completions` request
submit হয়নি। নতুন generation, token usage, latency বা Bengali sample বানানো হয়নি।
Owner-এর **“If a checksum or compatibility check fails, stop safely”** নির্দেশ মেনে আর launcher retry,
model execution, library-policy change বা অতিরিক্ত download করা হয়নি। Postflight GPU process list খালি;
server stopped। Library path correction ও device validation পরের resume checkpoint।

## Budget এবং পূর্ণ গল্পের সীমা

| গণনা | সংখ্যা |
|---|---:|
| Historical actual calls | ২ |
| নতুন generation submission | ০ |
| নতুন failed worker launch, submission-এর আগে | ১ |
| সর্বমোট model-call ceiling | ৭ |
| Remaining model-call slots | ৫ |

Ledger-এ আগের সফল narrow canary ও failed/truncated foundation—দুটিই বহাল। No reset, no increase।
নতুন request পাঠানোর ঠিক আগে durable reservation করার guard যোগ করা হয়েছে। Completed/failed launch ID
পুনরায় চালানো যায় না। নতুন launch failure-এর JSON/log পৃথক research directory-তে অক্ষত।

Fresh canary + existing foundation/তিন act/reflection = **৬ call**, কিন্তু বাকি **৫**। এই run-এ contract
চুপিসারে batch করা, output/context ceiling বাড়ানো, reflection বাদ দিয়ে complete বলা বা failure লুকানো হয়নি।
Compatibility ঠিক হলেও unchanged full plan এই remaining budget-এ পুরো শেষ করার নিশ্চয়তা নেই।

## Creative / human review

নতুন canary output নেই; নতুন complete story নেই। তাই বিদ্যমান ১৫টি criterion—originality, causal logic,
character agency, psychological depth, relationship credibility, emotional authenticity, organic humor,
Bangladesh authenticity, hook/suspense, escalation, setup/payoff, ending quality, filmability, consistency,
audience engagement—এর **নতুন numeric score সব null**। নতুন before/after creative improvement দাবি নেই।
পুরোনো actual outputs ও cited partial-defect evaluation reuse হয়েছে, rerun নয়।

**Human review PENDING / artistic acceptance নেই / production readiness নেই।**
এই failure-inspection package-কে নতুন বাংলা গল্পের Human Review Package বলা হবে না।

## Verification ও resume

- নতুন runner-এর **৪টি distinct CPU guard check PASS**: historical two-call preservation, sixth-new-call rejection,
  submitted-ID retry rejection, ledger-reset rejection। Fixture-only; GPU/model execution নয়। পুরোনো engineering tests আবার চালানো হয়নি।
- Actual download receipt, complete launch JSON/log, loader diagnostics, postflight resources, ledger ও screenshot সংরক্ষিত।
- Artifact/static validation PASS; **২৮টি protected file byte-identical**। Previous reports/notebook/results অক্ষত।
- `main`, Render, production DB/media, hosted inference, paid services এবং YouTube settings পরিবর্তন শূন্য।

পরবর্তী একক পদক্ষেপ: একই cached তিনটি artifact reuse করে research environment-এ কেবল verified provider
driver directory explicit allowlist-এ যুক্ত করা; model না লোড করে dependency/device enumeration যাচাই।
তারপর এই stop checkpoint থেকে নতুন distinct canary attempt ID ব্যবহার করে resume করতে হবে; আগের failure overwrite নয়।
বর্তমান evidence অতিরিক্ত model/runtime/driver download-এর প্রয়োজন দেখায় না। সাত-call ceiling ও সমস্ত
historical reservations বহাল থাকবে। Production Story Secure Worker-এর কাজ এর থেকে আলাদা থাকবে।

Safe evidence: `verification/story_option_c_20261116/actual_failure_export.json`,
`bundle_verified.json`, `call_ledger_after_download.json`, `bundle_resume_checkpoint.json`,
`story_evaluation_after_download.json`, `new_runner_cpu_guard_receipt.json` এবং screenshot।
Final remote feature commit যাচাই করে সমাপ্তির উত্তরে দেওয়া হবে।
