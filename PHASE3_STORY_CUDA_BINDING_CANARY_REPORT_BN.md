# Story AI — CUDA binding recovery ও genuine canary

১৬ নভেম্বর ২০২৬। **CUDA BINDING / MODEL LOAD / CANARY TECHNICAL: VERIFIED COMPLETE।**
**পূর্ণ Story benchmark: BLOCKED — unchanged call budget mismatch। Creative acceptance: PENDING।**

Remote feature HEAD `684ce29ebe59170ca0161342769e2fa460975dcd` থেকে কাজ হয়েছে।
আগের failed pre-generation launch ও সমস্ত historical evidence অক্ষত। Production Story Secure Worker,
main, Render, production data এবং YouTube settings পরিবর্তন হয়নি।

## Driver correction ও resources

- Existing `/usr/lib64-nvidia/libcuda.so.1` → `/usr/lib64-nvidia/libcuda.so.580.82.07` উপস্থিতি নিশ্চিত করা হয়েছে।
- শুধু research subprocess-এর minimal `LD_LIBRARY_PATH`-এ `/usr/lib64-nvidia` যুক্ত হয়েছে। System driver,
  CUDA package, global environment বা production worker পরিবর্তন হয়নি।
- Bounded `ldd`-তে সব dependency resolve হয়েছে; `libcuda.so.1` provider-এর verified directory থেকে এসেছে।
- Model না লোড করে exact verified binary-এর `--list-devices` সফল:

```text
Available devices:
 CUDA0: Tesla T4 (14912 MiB, 14807 MiB free)
```

`CUDA0` enumeration-এর পরে বেছে নেওয়া হয়েছে; আগে থেকে ধরে নেওয়া হয়নি।
NVIDIA preflight: Tesla T4, 15360 MiB total / 14913 MiB free। Host RAM 13,605,810,176 bytes total /
12,222,455,808 bytes available। Runtime-reported usable memory ও nvidia-smi totals আলাদা measurement।
Free account: not subscribed, zero compute units; UI session estimate up to 3h10m, guaranteed quota নয়।

## Exact reused model/runtime

`unsloth/Qwen3.5-9B-GGUF@3885219b6810b007914f3a7950a8d1b469d598a5`,
`Qwen3.5-9B-Q4_K_M.gguf`, 5,680,522,464 bytes;
SHA256 `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`।
Official llama.cpp b12318, commit `7021f7e09`; binary SHA256
`0ec391741c38d09eb4074db407c162686e310799c0dc36ebb734775688384ff5`।

আগের three-artifact full checksum receipts reuse হয়েছে। Current cached model presence/size ও binary hash
যাচাই হয়েছে; model বা দুই archive আবার download হয়নি। Model Apache-2.0 / runtime MIT-এর পূর্বের source evidence বহাল।

## প্রকৃত নতুন canary

Unique attempt: **`driverbound_canary_v1`**। Original canary brief ও schema অপরিবর্তিত।
Seed 117, temperature 0.2, thinking disabled, 4096-token context, 384-token output ceiling,
schema-constrained response ও previously prepared repeat-penalty setting 1.08।
Exact request/prompt, raw HTTP body, output, hashes ও GPU/server log সংরক্ষিত।

| Technical measurement | Actual result |
|---|---|
| Model load | 33/33 layers GPU-তে offload; CUDA0 model buffer 4861.28 MiB |
| Prompt / completion tokens | 127 / 118 |
| Finish | `stop`; complete valid JSON; original canary schema PASS |
| Load / generation wall time | 71.14s / 67.68s |
| Total wall time | 142.11s |
| Sampled device used | 5231 MiB; whole-device sampling, baseline সহ; allocator peak নয় |
| Sampled server RSS peak | 1,417,281,536 bytes |
| Cleanup | Owned server stopped; postflight GPU process list খালি |

Generation wall time prompt processing অন্তর্ভুক্ত করে; decode-only speed হিসেবে ব্যবহার করা হয়নি।
Raw output SHA256: `1ff2f6a5c4173cdd1841c1ac043f48ca3ac3eb8586ebe1bf45a9aa418e76b7ff`।

### Actual raw output — অপরিবর্তিত

```json
{
  "cause": "হাসান নীরাকে টিকিটের বিষয়টি গোপন রেখেছেন।",
  "choice": "নীরা এখনও টিকিট খুঁজে পায়নি।",
  "consequence": "তিনি কোনো আনন্দ বা উৎসাহ প্রকাশ করতে পারেননি।",
  "knowledge": "মানুষ যখন অপরিচিত কিছু সম্পর্কে অবহিত থাকে, তখন তা নিয়ে প্রতিক্রিয়া দেখাতে পারে না।"
}
```

### সীমিত assistant textual triage — human score নয়

- `choice`-এ deliberate decision নেই; ticket আবিষ্কার না হওয়ার অবস্থা বর্ণিত হয়েছে।
- `knowledge`-এ “অবহিত” অর্থ informed হলেও reaction দিতে না পারার যুক্তি ব্যবহার করা হয়েছে; semantic অসংগতি আছে।
- Consequence-এর pronoun অস্পষ্ট; কোনো বাস্তব সিদ্ধান্তের earned consequence প্রতিষ্ঠিত হয়নি।

তাই format/runtime pass-কে professional creative pass বলা হচ্ছে না। Schema constraint creative weakness
দূর করেছে—এমন প্রমাণ নেই। No measured before/after creative improvement claim।

## কেন পূর্ণ গল্পে এগোনো হয়নি

| Budget item | Actual |
|---|---:|
| Historical consumed calls | ২ |
| নতুন generation | ১ |
| মোট consumed / ceiling | ৩ / ৭ |
| Remaining calls | ৪ |
| Unchanged full Story sections/calls required | ৫ |

নতুন request পাঠানোর আগেই durable ledger reservation করা হয়েছে; saved reservation payload hash actual
request-এর সঙ্গে মিলেছে। আগের unsuccessful worker launch model submission ছিল না; সেটি আলাদা immutable evidence।

বাকি mandatory sections: **foundation, act_1, act_2, act_3, reflection**। Historical foundation truncated/
unsuccessful হওয়ায় সেটি reuse করা যায় না। নতুন canary foundation-এর বিকল্প নয়।

Owner-এর instruction 12 অনুযায়ী এই budget checkpoint-এ থামা হয়েছে: পাঁচটি required section-এর জন্য
পাঁচ call লাগে, বাকি চার। কোনো section skip/batch, output/context limit বৃদ্ধি, ledger reset, cap বৃদ্ধি
বা partial story-কে complete বলা হয়নি। Foundation/acts/reflection-এর নতুন generation হয়নি।

## QC, tests ও preservation

- Complete Story artifact না থাকায় existing **১৫-criterion full-story QC চালানো হয়নি**। সব নতুন artistic score null;
  human review ও owner artistic acceptance PENDING। Canary triage পূর্ণ story/QC বা independent review নয়।
- শুধু affected section-routing-এর **৩টি নতুন CPU fixture check PASS**: unique ID + original schema/limit preservation;
  নতুন failed canary-র বদলে old success নেওয়া প্রত্যাখ্যান; failed required foundation skip করা প্রত্যাখ্যান।
- Actual new canary-র raw HTTP/content/hash/schema/reservation validation PASS। পুরোনো successful tests/benchmarks পুনরায় চালানো হয়নি।
- **৫৩টি protected/previous evidence file byte-identical**। পুরোনো failed launch hash
  `624eb565dd41c2f734af35a86dd1d5b37a279019c619c1aac0395bb5d67d51f0` অপরিবর্তিত।
- Existing Colab notebook-এর নতুন cells ও output শেষে **All changes saved**। Raw model artifacts GitHub-এ পাঠানো হয়নি;
  শুধু lightweight source, logs, text/JSON evidence ও screenshot সংরক্ষিত।

## Security ও exact resume point

Option C research-only boundary বহাল: no Drive mount, secret values, production DB/private media, hosted API,
public inference endpoint, new downloads, paid resource, system driver install, Bubblewrap retry বা deployment।
Production Story Secure Worker-এর kernel isolation fixed বা equivalent হয়েছে—এমন দাবি নেই।

CUDA/runtime access এখন blocker নয়। বর্তমান exact blocker: **৪ remaining call বনাম ৫ mandatory section-call**,
এবং professional artistic acceptance অনুপস্থিত। একই অনুমোদিত download বা driver-path অনুমোদন আবার লাগবে না।

পরবর্তী resume: verified binding, cached bundle এবং completed canary reuse; cells 19/20 বা এই attempt আবার চালানো নয়।
Unchanged পূর্ণ benchmark-এর budget mismatch নিয়ে explicit owner-scoped সিদ্ধান্তের আগে সম্পূর্ণ গল্পের প্রতিশ্রুতি নয়।
Independent মানব evaluation কেবল genuine completed Story evidence পাওয়ার পরে করা যাবে।
Final verified remote feature commit সমাপ্তির উত্তরে দেওয়া হবে।
