# REDPAD AI Studio Phase 2 owner handoff

**PHASE 2 BLOCKED · GPU PURCHASE NOT APPROVED**

Engineering checklist deadline ৩০ নভেম্বর ২০২৬। Evidence checkpoint `b07f94c5de88d5e5e63c90f5973fb37f7cd35c5a`। বর্তমান অনুমোদিত পরিসরে কোনো অবশিষ্ট critical CPU defect চিহ্নিত হয়নি। বাধা হলো exact runtime acceptance, artifact integrity, upstream support, licensing ও hardware verification।

## এখন মালিকের সিদ্ধান্ত

| সিদ্ধান্ত | সুনির্দিষ্ট অনুমোদনের পরিসর | ফল বা বন্ধ থাকার শর্ত |
|---|---|---|
| **QWEN-OFFLINE** | CPython 3.11 Linux x86-64, glibc ≥2.28-এর জন্য বিদ্যমান manifest-এর নির্দিষ্ট ৭৯টি public package wheel staging ও যাচাই। Dedicated disposable prefix-এ offline install, `pip check`, এবং existing supervisor configuration-এর বাইরে exact signed v4 CUDA bundle-এর read-only immutable binding যাচাই। এই প্রস্তাবের মধ্যে pinned dependency wheels আছে, model checkpoint install বা activation নেই। | প্রত্যেক wheel-এর filename, size ও SHA-256 যাচাই করে `--no-index --only-binary=:all: --require-hashes` দিয়ে install। Exact kernel commit `3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8`, signature, read-only path এবং v4 lookup-এর receipt নিন। Missing or changed wheel, digest বা kernel resolution-এ stop। Production integration, model acquisition ও GPU execution আলাদা সিদ্ধান্ত। |
| **WAN-PUBLISHER** | প্রস্তুত message exact model maintainer বা Diffusers PR #14412-এ পাঠানোর অনুমোদন। | Normative processor contract, exact supported loader exports ও immutable component revisions চাই। Exact solution না পাওয়া পর্যন্ত route বন্ধ। |
| **LTX-PUBLISHER** | প্রস্তুত SHA-256 request প্রকাশককে পাঠানোর অনুমোদন। আগে অনুমোদিত metadata-only access ব্যবহার করা যাবে যদি repository-তে আগে থেকেই read access আছে এমন credential নিরাপদভাবে উপলভ্য হয়। | Exact revision, path, 995,778,752 bytes ও authoritative SHA-256 মেলা পর্যন্ত installation BLOCKED। |
| **INDIC-SPEAK-SOURCE** | Exact gated revision-এর source-only review আলাদাভাবে অনুমোদন করুন। মালিক নিজের account-এ applicable terms পর্যালোচনা করে বৈধ access নেবেন। | Intended commercial use নির্ধারণ, Bodhan ও Llama terms, SNAC/Vocos এবং associated weights rights, speaker consent ও প্রয়োজনে publisher hosting agreement। |
| **INDICF5-SOURCE** | Exact gated revision-এর source-only review আলাদাভাবে অনুমোদন করুন। মালিক publisher/Hugging Face terms যাচাই করে বৈধ access নেবেন। | Exact code, model ও codec stack-এর commercial rights এবং mel/decoder contract যাচাই। Encodec 0.1.1-এর প্রকাশিত noncommercial সীমা বহাল। Codec substitution-এর পৃথক সিদ্ধান্ত প্রয়োজন। |

Voice সিদ্ধান্তে internal commercial production এবং direct third-party hosting আলাদা করে লিখুন। Source access পাওয়ার পরে approved source-only review-তে exact revision, scope ও rights evidence দিন। Gated terms, credentials বা raw reference recordings evidence হিসেবে প্রকাশ করবেন না। [Indic-Speak সিদ্ধান্তপত্র](../phase2_final_triage_20261122/INDIC-SPEAK-DECISION.md) · [IndicF5 সিদ্ধান্তপত্র](../phase2_final_triage_20261122/INDICF5-DECISION.md)

[Qwen package lock](../phase2_cpu_gaps_20261122/qwen-candidate.lock) · [Exact wheel manifest](../phase2_cpu_gaps_20261122/qwen-platform-wheels.json) · [Qwen technical handoff](../phase2_final_triage_20261122/QWEN-GPU-HANDOFF.md) · [Wan প্রকাশক বার্তা](WAN-PUBLISHER.md) · [LTX checksum request](../phase2_final_triage_20261122/LTX-PUBLISHER-REQUEST.md)

## ১৮টি profile-এর বর্তমান অবস্থা

PASS মানে সংরক্ষিত actual model-free CPU startup ও binding evidence। GPU/model execution status আলাদা।

| Profile | Model-free CPU | অসম্পূর্ণ শর্ত |
|---|---|---|
| `qwen35_27` | PASS | Actual model/GPU acceptance বাকি |
| `qwen35_moe` | PARTIAL | Offline wheelhouse, immutable kernel binding, alternative artifact approval ও FP8 CUDA acceptance |
| `qwen36_27` | PASS | Actual model/GPU acceptance বাকি |
| `qwen35_9` | PASS | Actual model/GPU acceptance বাকি |
| `gemma3_27` | PASS | Actual model/GPU acceptance বাকি |
| `gemma3_12` | PASS | Actual model/GPU acceptance বাকি |
| `flux2_klein4` | PASS | Actual model/GPU acceptance বাকি |
| `z_image_turbo` | PASS | Actual model/GPU acceptance বাকি |
| `wan_animate2` | BLOCKED | Pinned source import CUDA চায় বা publisher-supported deferred-device revision দরকার |
| `wan_animate2_distilled` | BLOCKED | Exact loader ও processor contract unverified, modular loader-এর missing exports পুনরুৎপাদিত |
| `wan22_5` | PASS | Actual model/GPU acceptance বাকি |
| `ltx25` | PASS | পৃথক auxiliary SHA-256 installation gate এবং actual model/GPU acceptance বাকি |
| `svd_xt` | PASS | Actual model/GPU acceptance বাকি |
| `indic_speak` | BLOCKED | Exact gated source, applicable license/hosting rights, codec ও consent review |
| `indicf5` | BLOCKED | Exact gated source, commercially eligible codec ও consent review |
| `indic_parler` | PASS | Actual model/GPU acceptance বাকি |
| `ace15` | PASS | Actual model/GPU acceptance বাকি |
| `stable_audio_small` | PASS | Actual model/GPU acceptance বাকি |

Wan Distilled-এর PARTIAL হলো সংরক্ষিত diagnostic evidence। BLOCKED হলো profile acceptance verdict। [পূর্ণ JSON ম্যাট্রিক্স](../phase2_final_triage_20261122/updated-18-profile-matrix.json)

## সম্পন্ন CPU engineering ও অবশিষ্ট external gates

- ১৩টি actual model-free startup/runtime binding receipt, ২১-agent consistency এবং native/shared supervisor-এর আগের kernel isolation ও fail-closed evidence সংরক্ষিত। ২১টি approved, ৭টি focused Wan এবং শেষ triage-এর চারটি diagnostic check-এর লগ বহাল। এই handoff-এ নতুন diagnostics চালানো হয়নি। [স্বাধীন sign-off](../phase2_signoff_20261122/FINAL-BN.md) · [Limited approval receipts](../phase2_approved_20261122/RESULTS-BN.md) · [CPU gap evidence](../phase2_cpu_gaps_20261122/RESULTS-BN.md) · [Final triage](../phase2_final_triage_20261122/GATE-BN.md)
- Qwen-এর ৭৯টি wheel pin ও hash, ১০টি kernel file digest এবং publisher Sigstore validation সম্পন্ন। Offline install ও immutable runtime binding এখনও যাচাই করা সম্ভব, তবে উপরের পৃথক approval ও verified wheelhouse দরকার। [Signature log](../phase2_final_triage_20261122/qwen-signature.log)
- Wan-এর monolithic omission ও modular failure, LTX-এর authoritative digest, এবং voice source/rights এখন external gates। প্রাপ্ত publisher responses exact source ও artifact tuple-এর সঙ্গে মিলিয়ে নেওয়ার আগে profile status বদলাবে না। [Wan receipt](../phase2_final_triage_20261122/wan-publisher-receipt.json) · [LTX redacted status](../phase2_cpu_gaps_20261122/ltx-auth-status.json)

## Hardware acceptance ও GPU readiness

নিচের tests ভবিষ্যৎ acceptance criteria। এই handoff কোনো hardware session বা purchase অনুমোদন করে না।

| পরীক্ষা | প্রয়োজনীয় receipt |
|---|---|
| Driver, CUDA ABI ও device assignment | Locked Torch/CUDA build-এর সঙ্গে driver compatibility, অনুমোদিত visible device map, actual device capability ও isolation receipt। |
| Qwen FP8 | প্রতিটি assigned device-এ SM ≥8.9, exact signed v4 bundle, callable 2D/batched/grouped symbols, seeded synthetic grouped FP8 dispatch ও independent reference comparison। Guard validation-এর আগে ও পরে `dequantize is False`; actual expert precision ও fallback refusal যাচাই। |
| Native Wan | Exact native pin-এর import-only CUDA boot, expected source/ABI এবং supervisor device binding। |
| Exact artifact load ও execution | প্রযোজ্য profile-এ owner-authorized immutable weights, sidecar hashes ও offline load, minimal approved workload, host RAM/VRAM peak, wall time, timeout, cancellation, unload ও descendant cleanup। |
| Output acceptance | Artifact provenance, per-modality technical QC ও স্বাধীন creative review। Voice-এর জন্য verified speaker consent। কোনো current CPU receipt এই স্তরের ফল দাবি করে না। |

GPU purchase readiness-এর আগে required external decisions, exact source/artifact/dependency receipts, secure binding, এবং বিদ্যমান mandatory acceptance criteria অনুযায়ী verified runnable routes পর্যালোচনা করতে হবে। Hardware-dependent tests আলাদা authorized checkpoint-এ রেকর্ড করতে হবে। Phase 3-এর জন্য verified Phase 2 completion এবং পরবর্তী explicit owner authorization দরকার। [বিদ্যমান sign-off criteria](../phase2_signoff_20261122/FINAL-BN.md)

## ৩০ নভেম্বর ২০২৬ engineering-completion checklist

- [x] ১৮-profile matrix, ১৩ CPU PASS, supervisor ও regression evidence যাচাইযোগ্য references-এ সংরক্ষণ।
- [x] Qwen scope, Wan/LTX publisher drafts ও পৃথক voice decision sheets প্রস্তুত।
- [ ] Qwen offline wheelhouse/binding scope অনুমোদন বা প্রত্যাখ্যান লিখিতভাবে নথিভুক্ত করা। অনুমোদিত হলে exact checklist অনুযায়ী receipts সংরক্ষণ।
- [ ] Wan publisher outreach-এর সিদ্ধান্ত এবং supported exact loader/processor contract-এর response নথিভুক্ত করা।
- [ ] LTX authoritative SHA-256 exact byte size ও revision-এর সঙ্গে মিলিয়ে দেখা। প্রমাণ অনুপস্থিত থাকলে gate বন্ধ রাখা।
- [ ] দুই voice profile-এর access, internal/hosted usage, codec rights এবং consent পৃথকভাবে নিষ্পত্তি করা।
- [ ] Hardware-dependent requirements এবং pending owner/publisher items evidence register-এ রাখা। Deadline-এ mandatory evidence অনুপস্থিত থাকলে Phase 2 BLOCKED হিসেবেই report করা।
