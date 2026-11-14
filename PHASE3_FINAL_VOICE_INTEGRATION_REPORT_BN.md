# Phase 3 — Final Voice no-GPU engineering

**ফলাফল: ১৯/১৯ NO-GPU ENGINEERING COMPLETE।**
Runtime: **MODEL/GPU VALIDATION BLOCKED**। Artistic: **HUMAN REVIEW PENDING**।
Professionally accepted / production-ready: **০/২১**। Director ও Script-এর পৃথক কাজ অপরিবর্তিত।

Resume checkpoint: `e7dc992f187d9bd545b88d3ee11dd174ac08566c`। কাজের শুরুতে remote feature HEAD
এই SHA-তেই ছিল। অনুমোদিত branch: `feature/video-music-editing-studio`। এই রিপোর্টসহ verified
code/evidence-এর final remote commit SHA সমাপ্তির উত্তরে দেওয়া হবে; commit-এর নিজের SHA ফাইলে
আত্মউল্লেখ করে লেখা হয়নি। তার আগে remote save সম্পন্ন দাবি করা হয়নি।

## Access ও exact source review

Owner-এর বিদ্যমান authenticated **Chrome** session-এ দুই exact revision-এর actual source
পড়া গেছে। আগের Agree gate এখন বাধা নয়। আমি নতুন agreement গ্রহণ, form submission,
credential/cookie/token extraction বা model-weight access করিনি। Repository access-এর জন্য
owner-এর আর কোনো action এই verification-এ লাগেনি।

| Repository | Reviewed revision | Lightweight files |
|---|---|---|
| `bodhan-ai/indic-speak` | `76e0814f189321efe550011850cd288dae366aad` | `inference.py`, `voices.md`, `token_contract.md`, `config.json`, `tokenizer_config.json`, `generation_config.json`, `vocos/load.py`, `vocos/config.yaml`, `vocos/model.py` |
| `ai4bharat/IndicF5` | `fb652a96e508091045890dae5bb99fe511facbcf` | `model.py`, `config.json`, `checkpoints/vocab.txt`, `f5_tts/infer/utils_infer.py`, `f5_tts/model/__init__.py`, `f5_tts/model/utils.py`, `f5_tts/model/cfm.py`, `f5_tts/model/modules.py`, `f5_tts/model/backbones/dit.py` |
| `charactr/vocos-mel-24khz` | `e7e2fcf1f10089bbedc1e6f658685c26498c20c7` | Matching F5 vocoder `config.yaml` only; no vocoder weights |

মোট **১৯টি source/config file**। Exact-revision Raw-page text-এর UTF-8 size/SHA256 ও URLs:
`assets/professional/phase3_voice_selected_source_lock.json`। এটি authenticated source-text
evidence; independent Git-blob byte attestation নয়। Future approved local checkout bytes
মিলতে হবে; mismatch হলে বন্ধ হবে। Gated third-party source GitHub-এ পুনঃপ্রকাশ করিনি।

## Indic-Speak — engineering complete, runtime blocked

- Selected `inference.TTS.__call__` binding; unsafe/networking constructor বদলে fixed
  local `LlamaForCausalLM`/tokenizer/SNAC/Vocos initialization। আগের reviewed public-engine
  helper সংরক্ষিত; selected binding public preview-এর সমতুল্য ধরে নেওয়া হয়নি।
- Bengali recommended preset: **Ishita / Sourav**। Invented speaker, wrong revision,
  embedded control token ও unsupported endpoint/emotion/pronunciation controls reject।
  Owner notes provenance-এ থাকে; native style হিসেবে চুপচাপ প্রয়োগ হয় না।
- Vocab size 156960, SNAC base 128266, সাত-position audio layout এবং সব audio/conditioning/
  nonverbal IDs যাচাইয়ের pure contract। Original Bengali request অক্ষত; payload NFC।
- Selected Vocos **v9 EMA**; bounded architecture/tensor checks, mandatory
  `weights_only=True`, strict state loading। Unsafe upstream pickle loader এবং old/stock
  decoder fallback ব্যবহার হয় না। SNAC local component absence-এ download হয় না।
- 24 kHz mono PCM16 bounded WAV, native dtype/raw-array output/provenance retention, truncation
  warning-এ failure। সব external Python execution/weight loading future isolated worker-এর
  explicit research authorization-এর পরে; এই কাজের সময় কিছুই execute হয়নি।

দুটি source inconsistency এখনও actual inference-এ মেটাতে হবে: `inference.py` speech-start
token prefills, কিন্তু token contract model-emitted start বর্ণনা করে; `voices.md` measurements
ckpt-8944 বলে, selected source commit ckpt-8937 বলে। Exact inference implementation retained;
speaker performance বা prompt correctness experimentally verified দাবি নয়।

## IndicF5 — engineering complete, runtime blocked

Selected `model.py`-তে **unguarded model generation/upload code**, automatic Hub/vocoder
downloads এবং required checkpoint argument ছাড়া loader call আছে। এটি import/execute করা
হয়নি এবং native worker এটিকে ভবিষ্যতেও import করবে না।

Fixed local loader selected INF5 wrapper-এর `ema_model` ও `vocoder` structure, exact DiT
1024/22/16 architecture, CFM mel contract, reviewed character vocabulary ও FP32 recipe
ব্যবহার করে। Selected safetensors-এ strict full-state match লাগে। Source-এর compiled wrapper
ও explicit uncompiled wrapper layout ছাড়া generic F5/EMA checkpoint, partial loading বা
fuzzy key rewriting নেই। Actual selected tensor keys/shapes এখনও weight/runtime পরীক্ষা বাকি।

Matching `f5_tts` inference modules only; training initializer, model.py, CLI/demo ও upload
path import হয় না। Vocos fixed classes/arguments; arbitrary YAML class loading, remote
AutoModel, `trust_remote_code`, Whisper/ASR বা implicit downloads নেই।

Reference: explicit original transcript, mono PCM16 24 kHz, ০.১–১৫ সেকেন্ড এবং nonzero energy।
Wrong rate, truncation বা silent reference deterministic failure; RMS division-এর আগেই
বন্ধ। Implicit resampling/clipping/silence removal/loudness rewriting নেই। Original hashes
রক্ষিত; upstream transcript punctuation adaptation ও Unicode normalization disclosed।

## Shared integration ও Casting

Existing `native_local_bundle` / `NativeInstalls`, `PreparedRequests`, isolated
`native_local_worker` ও `NativeExecution` supervisor reuse হয়েছে। দুই selected Voice dispatch,
exact source/model/component receipts, bridge/source-lock staleness এবং copied-reference
binding যোগ হয়েছে। কোনো নতুন inference engine/Casting store তৈরি হয়নি।

Voice-to-Casting-এর দুই selected candidate-এর task preparation এবং IndicF5 scoped consent
handoff CPU fixtures-এ সফল। Uploaded document/rights metadata human consent review নয়;
actor/audio/transcript/task/revision-bound explicit receipt লাগে। Revocation বা stale evidence
preparation/result invalidates করে। Test declarations মানব অনুমোদন নয়।

Producer identity/approved Character source, Director inspection ও independent QC অক্ষত।
Mock/unrelated audio artistic evidence হতে পারে না। Generic text execution audition চালাতে
পারে না। **Indic-Parler পৃথক explicit candidate**; automatic fallback/promotion নেই।
`launch_authorized=False`, no production route বা professional winner selection।

## CPU QA ও preservation

**৩৬টি distinct সফল check: ২৪টি নতুন + ১২টি affected existing check।**
প্রথম run-এ একটি test-selector name ভুল ছিল; প্রকৃত intended check পরে pass। কোনো code
assertion failure ছিল না। Actual attempts ও ওই error রাখা হয়েছে। নতুন reference guard-এর
পরে শুধু চারটি affected F5 check এবং source-manifest gate-এর পরে শুধু দুটি affected gate
পুনরায় চালানো হয়েছে; পুনরায় চলা test নতুন independent test হিসেবে গণনা হয়নি।

Coverage: exact access/revision/source receipts, local loader contracts, all-token mapping,
speaker/codec restrictions, reference/transcript/consent/revocation, Unicode/source integrity,
missing components, no inference permission, no implicit downloads/hosted endpoint, source
staleness, both selected Casting preparations, read-only approval boundaries এবং ১৯-role
candidate/operation compatibility। Tests শুধু injected ordinary fake classes ও manually
constructed fixtures; `cuda` device strings fake method arguments, real device calls নয়।

আগের successful generation/regression suite পুনরায় চালানো হয়নি। Existing supervisor
timeout/cancellation/restart evidence reuse হয়েছে; সংশ্লিষ্ট functions-এর AST এবং আগের
workers/Casting/consent/Director/QC/Producer hooks checkpoint-এর সঙ্গে অপরিবর্তিত যাচাই হয়েছে।
Other ১৭ agent ও Director/Script registry records, সব pinned profile এবং `models.json` hash
অক্ষত। Central registry/readiness-তে শুধু Voice/Casting integration metadata আপডেট।

Evidence:

- `verification/voice_final/access_verification.json`
- `verification/voice_final/cpu_attempt_*.json` এবং `cpu_first_attempt.txt`
- `verification/voice_final/preserved_workflows.json`
- `verification/voice_final/final_audit.json`
- `verification/voice_casting/readiness_19.json` — current central matrix
- `verification/voice_final/readiness_19_at_e7dc.json` — historical ১৮/১৯ snapshot

Audit একই assistant-এর আলাদা code/evidence pass; independent human review নয়।

## Final nineteen-agent matrix

প্রতিটি row-এর Runtime **MODEL/GPU VALIDATION BLOCKED**, Artistic **HUMAN REVIEW PENDING**।

| Agent | Engineering |
|---|---|
| QC AI | NO-GPU ENGINEERING COMPLETE |
| Story AI | NO-GPU ENGINEERING COMPLETE |
| Character AI | NO-GPU ENGINEERING COMPLETE |
| Art Director AI | NO-GPU ENGINEERING COMPLETE |
| Location AI | NO-GPU ENGINEERING COMPLETE |
| Costume / Hair & Makeup AI | NO-GPU ENGINEERING COMPLETE |
| Storyboard AI | NO-GPU ENGINEERING COMPLETE |
| Performance AI | NO-GPU ENGINEERING COMPLETE |
| Cinematographer AI | NO-GPU ENGINEERING COMPLETE |
| Motion & Physics AI | NO-GPU ENGINEERING COMPLETE |
| Video AI | NO-GPU ENGINEERING COMPLETE |
| Voice AI | NO-GPU ENGINEERING COMPLETE |
| Continuity AI | NO-GPU ENGINEERING COMPLETE |
| Music & SFX AI | NO-GPU ENGINEERING COMPLETE |
| Editing & VFX AI | NO-GPU ENGINEERING COMPLETE |
| Production Manager AI | NO-GPU ENGINEERING COMPLETE |
| Growth AI | NO-GPU ENGINEERING COMPLETE |
| YouTube Channel AI | NO-GPU ENGINEERING COMPLETE |
| Casting Director AI | NO-GPU ENGINEERING COMPLETE |

## Remaining dependencies ও next checkpoint

Repository access blocker সমাধান হয়েছে। বাকি: approved exact local weights/components,
complete installed dependencies/source receipts, applicable upstream usage/license review,
kernel isolation (আগের bwrap restriction unresolved), separately authorized local GPU/runtime,
actual output technical validation এবং independent Bengali listening/artistic/owner review।

Indic-Speak selected recipe: 7,068,852,569 bytes plus SNAC/tokenizer/dependencies;
IndicF5: 1,402,789,408-byte selected safetensors plus local code/vocabulary/dependencies।
এই সংখ্যাগুলো existing pinned metadata; **download permission দেওয়া বা weights পড়া হয়নি**।
Access agreement model-use scope, upstream rights বা commercial/hosted serving clearance
স্বয়ংক্রিয়ভাবে প্রমাণ করে না। নতুন license acceptance লাগলে owner নিজে করবেন।

Existing overall QC-first GPU sequence বদলাইনি। Voice-এর পরবর্তী **single-model** checkpoint:
আগে exact approved local Indic-Speak + separately approved pinned SNAC bundle ও isolation
যাচাই; তারপর নতুন অনুমোদনে এক ছোট fictional Bengali utterance, reviewed preset, bounded
settings, raw native-array/WAV, runtime/token completion evidence ও independent listening review।
সফল পুরোনো case পুনরাবৃত্তি নয়। ওই case pass না হওয়া পর্যন্ত IndicF5 বা Casting audition-এ
ছড়িয়ে execution নয়; কোনো automatic production promotion নয়।

এই কাজের GPU/CUDA, CPU/GPU inference, real model-weight read/load/download, hosted/paid
generation, new agreement acceptance, Render/production/main/YouTube পরিবর্তন **সব শূন্য**।
Dashboard বা Phase 4-এ কোনো কাজ হয়নি।
