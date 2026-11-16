# Story AI — Option C execution checkpoint

১৬ নভেম্বর ২০২৬। **BLOCKED — exact local model/runtime bundle নেই; download decision প্রয়োজন।**

সর্বশেষ remote feature HEAD `ed1362f44df708ab19a103412f422a2cd2b5e160` থেকে কাজ চালানো হয়েছে।
মূল compatibility report এবং read-only notebook পড়ে reuse করা হয়েছে; পুরোনো report/notebook পরিবর্তন করা হয়নি।
Owner-এর বর্তমান explicit Option C অনুমোদন কার্যকর। এটি আলাদা research-only boundary;
production Story Secure Worker-এর isolation সমস্যা সমাধান বা gate অপসারণের অনুমোদন নয়।

| বিষয় | প্রকৃত ফল |
|---|---|
| Chrome / Colab | Existing signed-in notebook accessible। Inactivity disconnect-এর পরে একটি normal reconnect সফল; নতুন metadata ও summary notebook-এ All changes saved |
| Actual GPU | Tesla T4; total 15360 MiB, free 14913 MiB; driver 580.82.07, compute capability 7.5 |
| RAM / disk | Host RAM 12.67 GiB total, 11.41 GiB available; disk প্রায় 112.54 GiB free |
| Free account | Not subscribed; zero compute units। UI estimate up to 3h40m; guaranteed quota বা remaining GPU allowance নয় |
| Observation | `2026-11-16T15:09:07.508433+00:00`; Python 3.13.16 |
| Model cache | দুই exact approved cache root অনুপস্থিত; GGUF ও installation receipt নেই। Private/global cache exhaustively search করা হয়নি |
| Runtime | Expected llama-server ও দুই pinned runtime archive অনুপস্থিত; current executable compatibility NOT TESTED |
| Boundary | Drive mount detected false। কোনো Drive mount, secret-value inspection, private media/production DB access, hosted inference, weight read/download/load হয়নি |
| Production isolation | অপরিবর্তিত, NOT VERIFIED। Bubblewrap/unshare/mount test আবার চালানো হয়নি; Option C-কে equivalent secure worker বলা হচ্ছে না |
| New model / canary | কোনো model ব্যবহার হয়নি; নতুন canary call ০ |
| Complete story | অনুপস্থিত; নতুন story generation ০ |
| Human / artistic | HUMAN REVIEW PENDING; artistic acceptance নেই; professional readiness নেই |

## নির্দিষ্ট missing bundle ও একমাত্র প্রয়োজনীয় download সিদ্ধান্ত

নতুন model choice নয়: আগেই অনুমোদিত **`unsloth/Qwen3.5-9B-GGUF`**,
revision **`3885219b6810b007914f3a7950a8d1b469d598a5`**,
file **`Qwen3.5-9B-Q4_K_M.gguf`**, **5,680,522,464 bytes**।
Expected SHA256: `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`।

Reviewed runtime **`ggml-org/llama.cpp` release b12318**, commit `7021f7e09`,
binary version 0.9.0-dev build 12318। Expected llama-server SHA256:
`0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5`।

| Official runtime asset | Bytes | SHA256 |
|---|---:|---|
| cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 594371580 | caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea |
| llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz | 197999267 | e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797 |

প্রয়োজনীয় binary transfer মোট **6,472,893,311 bytes ≈ 6.47 GB**; unpacked runtime-এর অতিরিক্ত disk লাগে।
Exact URLs ও fingerprints `verification/story_option_c_20261116/continuation_manifest.json`-এ।
Model Apache-2.0, runtime MIT—পূর্বের pinned source evidence অনুযায়ী; নতুন license গ্রহণ বা source re-fetch হয়নি।
আগের একই bundle T4-তে offload হয়েছিল, sampled GPU usage প্রায় 5.2 GiB; সেটি current runtime compatibility guarantee নয়।

Owner-এর বর্তমান instruction 8 অনুযায়ী missing bundle স্বয়ংক্রিয় download করা হয়নি।
উপরের model ও দুই runtime archive পুনরায় download করার নির্দিষ্ট অনুমোদন দরকার। Option C boundary
বা model-selection approval আবার চাওয়া হচ্ছে না। নতুন model/gated weights/paid compute দরকার নেই।

## Call ledger ও creative evidence

সীমা **৭**, historical consumed **২**, নতুন **০**, অবশিষ্ট সর্বোচ্চ **৫**।
আগের narrow canary format/knowledge-boundary check সফল হলেও convincing dramatic choice প্রমাণ করেনি।
আগের foundation `finish_reason=length`, 1536 tokens, truncated invalid JSON—সেটিও consumed call।
Original raw outputs, hashes এবং partial-defect assessment অপরিবর্তিত রাখা হয়েছে।

Fresh canary + existing পাঁচ section = ছয় call; পাঁচ remaining slot-এ তা সম্ভব নয়।
Budget বাড়ানো, reset বা ব্যর্থ generation বাদ দেওয়া হয়নি। Existing standalone runner শুধু output
directory-এর JSON গোনে; নতুন empty directory দিয়ে launch করার আগে historical দুই call effective ledger-এ
bind করতে হবে। কোনো runner import/launch এই checkpoint-এ হয়নি। Model পাওয়ার পরে remaining budget অনুযায়ী
মূল benchmark contract অক্ষত রেখে কোন sections এক call-এ নিরাপদে করা যায় তার feasibility যাচাই করতে হবে;
না পারলে পূর্ণ গল্পের দাবি করা যাবে না। নতুন canary প্রযুক্তিগতভাবে সফল না হলে পরের generation বন্ধ থাকবে।

বিদ্যমান **১৫টি creative criterion-এর নতুন score সব null**: complete story না থাকায় নতুন মূল্যায়ন সম্ভব নয়।
আগের partial output-এ repetition/psychology/knowledge-boundary দুর্বলতার cited evidence reuse হয়েছে;
নতুন before/after improvement বা independent reviewer score বানানো হয়নি।

## সংরক্ষণ ও পুনরায় কাজ না করে পরের ধাপ

- Actual browser stdout/JSON, screenshot, Option C authorization receipt, exact missing-bundle manifest এবং preserved call ledger সংরক্ষিত।
- `STORY_OPTION_C_RESEARCH_PREFLIGHT.ipynb` actual নতুন Colab metadata cell-এর faithful export; model launcher নয়। Original paused notebook অক্ষত।
- একটি নতুন artifact consistency/static syntax/preservation validation PASS; **২৮ protected file byte-identical**। পুরোনো CPU regression/benchmark আবার চালানো হয়নি। এটি model বা artistic validation নয়।
- Production code, primary 27B candidate, worker gates, previous results এবং responsibilities অপরিবর্তিত। `main`, Render, YouTube ও production data পরিবর্তন শূন্য।

পরের ধাপ: শুধু exact missing-bundle download অনুমোদন পেলে current approved paths inspect করে missing files
download; pinned source/license ও পূর্ণ artifact checksums যাচাই; আলাদা clean research workspace, dependencies,
budget binding ও current resources যাচাই; এরপর bounded canary। Existing successful tests বা failed isolation probe পুনরাবৃত্তি নয়।
Final remote feature commit যাচাই করে সমাপ্তির উত্তরে দেওয়া হবে।
