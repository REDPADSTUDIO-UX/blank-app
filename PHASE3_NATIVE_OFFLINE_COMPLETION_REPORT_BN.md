# REDPAD Phase 3 — native offline execution engineering

১৩ নভেম্বর ২০২৬, বাংলাদেশ সময়। Remote feature HEAD
`391ca986b08b15ba5080a4c36fcc586e623e3568` যাচাই করে কাজ হয়েছে। এই রিপোর্টসহ
পরবর্তী verified feature commit-ই resume checkpoint। Branch:
`feature/video-music-editing-studio`।

**Engineering complete ১৭/১৯, PARTIAL ২/১৯; professionally validated/production-ready
০/২১।** এই ধাপে চারটি নতুন no-GPU engineering completion। Real inference বা cinematic
মানের সাফল্য নয়। ছয়টির runtime **MODEL/GPU VALIDATION BLOCKED**, artistic status
**HUMAN REVIEW PENDING**। কোনো production route, winner বা artistic acceptance নয়।

| Agent | Engineering status | নতুন executable engineering / অবশিষ্ট gate |
|---|---|---|
| Performance | NO-GPU ENGINEERING COMPLETE | Shared native Wan class wrapper, pinned component paths, existing image/driving-video/rights/timing contracts, isolated supervisor, stop/timeout/cleanup। Exact approved auxiliary weights ও real MPI/GPU/performance review বাকি। |
| Motion & Physics | NO-GPU ENGINEERING COMPLETE | একই Wan implementation reuse; existing source-frame/interaction metadata, independent temporal review contract। Physics score বানানো হয়নি; actual contact/weight/trajectory judgment বাকি। |
| Video | NO-GPU ENGINEERING COMPLETE | Native LTX 2.5 split BF16 worker; ModelPaths, image conditioning, stream encoding; existing Wan/SVD worker bindings reuse; objective output frame/FPS/dimension/duration gate। Exact upsampler SHA/bytes ও approved bundle/GPU loading বাকি। |
| Voice | PARTIAL — EXACT UNFINISHED ENGINEERING | Parler existing worker, local supervision, Bengali original/NFC, style annotations, WAV/transcript/consent checks প্রস্তুত। Selected Indic-Speak exact gated implementation/speaker map এবং IndicF5 pinned custom source পাওয়া/যাচাই ছাড়া ওই দুই native binding নিরাপদে লেখা যায়নি। |
| Music & SFX | NO-GPU ENGINEERING COMPLETE | ACE 1.5 fixed reviewed local class loader, offline initialization hooks, bounded safe auxiliary tensor checks, instrumental cue settings; Stable Audio SFX worker reuse। Actual authenticated bundle/package/BF16/audio/listening tests বাকি। |
| Casting Director | PARTIAL — EXACT UNFINISHED ENGINEERING | Existing Character/image/text workflow, shared Wan, evidence-grounded pair/performance/voice assessment, Director/QC/Producer locks অক্ষত। Selected Indic-Speak voice binding-এর exact gated source dependency অসম্পূর্ণ; portrait দিয়ে acting/chemistry acceptance হয় না। |

## বাস্তব code ও integration

- `native_local_bundle.py`: exact model/profile/revision/precision fingerprint, source
  lock, selected weights, complete file manifest, auxiliary origins, license/owner/code
  receipt validation। Missing/changed/unmanifested/symlink/unknown hash ও cached Python
  bytecode reject। Actual bundle approval/verification শুধুই ভবিষ্যৎ explicit owner
  action; এই সেশনে real weight পড়া বা model/license approval তৈরি হয়নি।
- `native_local_worker.py`: LTX, Wan এবং ACE native bridges। Model imports lazy;
  actual authorized worker entry ছাড়া কোনো model package import নয়। Parler, native
  Wan/SVD ও Stable Audio-র existing local workers reuse; নতুন duplicate engine নয়।
- `native_execution.py`: existing prepared task/source/rights snapshots থেকে explicit
  research queue; immutable worker/controller hashes, atomic idempotency, persistent
  state, process groups, timeout, cancellation/escalation, controller/PID identity,
  crash recovery ও separate output directories। Auto-retry/model fallback নেই।
- Existing `SharedServices.native_research_workers()` integration; staging/QC/source
  revision checks reused। Queueing launch authorization নয়। Owner অনুমতি ছাড়া run
  হয় না। Source/reference/consent/code/bundle বদলালে stale/fail; native result existing
  task output/owner approval/production route নিজে বদলায় না।
- Output provenance/raw media, logs ও ACE raw result metadata থাকে। Future video
  artifact-এ container, exact dimensions, decoded frame count, frame rate ও duration
  check; technical pass-ও human/QC approval নয়। Software fixture result কখনো real
  inference/artistic evidence হতে পারে না।

## যাচাইকৃত native source ও offline safety

আগের verified code revisions reuse; নতুন model/version/repack নেওয়া হয়নি:

| Family | Reviewed source revision | Implemented interface |
|---|---|---|
| LTX | `f0f2f8607189c78a72420b2b63cb1975b5eca179` | `ModelPaths.from_split`, `DistilledPipeline.stream_chunks`, `ImageConditioningInput.at`, `encode_media_segments` |
| Wan Animate | `3ad2fef7d61d6200c9c653e0fe47be7616b323f3` | Fixed `WanAnimate2MPIPipeline(cfg)` ও `__call__`; pinned native YAML থেকে local component paths |
| ACE 1.5 | `ca1e85fe9430179831e6bc6be790c332190a3866` | `AceStepHandler`, fixed `AceStepConditionGenerationModel`/`AceStepConfig`, `GenerationParams`, `GenerationConfig`, `generate_music` |

LTX-এর pinned packed TE loader tokenizer/config/processor assets file-এর ভেতর থেকেই
পড়তে পারে—আলাদা remote tokenizer বাধ্যতামূলক নয়। Actual embedded metadata/content
weight validation এখনও হয়নি। Required spatial upsampler একই selected repository:
`Lightricks/LTX-2.5@49b093a39c19169a8a81721dcc541e07e945232f`, path
`latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors`।
Official pinned file metadata accessible হয়নি। Third-party mirror result দিয়ে
official hash পূরণ করিনি। SHA/size null থাকলে installation approval fail closed।
পুরোনো LTX/quantized Comfy/Diffusers pack substitute নয়; optional temporal/DFR weights নয়।

Wan-এর T5/VAE/CLIP `.pth`, দুই tokenizer এবং BF16 transformer local paths fixed।
Exact auxiliary origin/revision/hash অনুমান করা হয়নি; সম্পূর্ণ owner-approved bundle
না থাকলে startup বন্ধ। `TORCH_FORCE_WEIGHTS_ONLY_LOAD=1` child processes-তেও যায়;
unsupported payload fail করে, unsafe pickle fallback নয়। Actual MPI/device behavior
বা `.pth` compatibility mock দিয়ে verified দাবি করা হয়নি।

ACE-তে upstream auto-download/code-sync hooks override। Model-side Python/custom
AutoModel dispatch বাদ দিয়ে exact reviewed local class; local-only safetensors,
explicit tokenizer/VAE paths। Silence `.pt` future loader weights-only CPU mapping,
file-size/tensor-type/shape/element-count/floating/finite bounds পরীক্ষা করে। এখানে
শুধু fake tensor/loader fixtures ব্যবহৃত; actual `.pt` payload খোলা হয়নি। Selected
BF16 unavailable হলে FP16/quantized fallback নয়। Instrumental text2music ও SFX ভিন্ন
worker/candidate-এ থাকে।

Native process বাধ্যতামূলক kernel network namespace, read-only filesystem, isolated
writable work directory ও explicit device allowlist পায়। Worker namespace check
model imports-এর আগে। Inherited tokens/proxies বাদ, HF offline flags, outbound
network/shell/unapproved child-command guards আছে। Wan loopback rendezvous namespace-এর
ভেতরে; hosted server/public inference endpoint নয়।

**এই environment-এ actual CPU-only bwrap isolation probe ব্যর্থ:**
`Failed to create NETLINK_ROUTE socket: Operation not permitted`। কোনো escalation বা
bypass করা হয়নি। তাই এখানে native inference launch বন্ধ থাকবে। এটি GPU/MPI পরীক্ষা
নয়। Dummy process lifecycle tests-এর জন্য শুধু fixed CPU fixture launch অনুমোদিত ছিল।

## CPU QA ও second audit

**৩৮টি নতুন + ১৪টি affected existing check = ৫২টি distinct successful check।**
Actual dummy subprocess-এ success/failure, timeout, running cancellation, descendant
cleanup ও restart/cancellation recovery যাচাই। Injected software-only local classes
দিয়ে LTX/Wan/ACE API mapping checks; real torch/CUDA/model execution নয়।

প্রথম run-এ ৭টি old check pass; নতুন ২৪টি setup error দেয় কারণ fixture ভুল sidecar
filename দিয়েছিল। Existing safety rule বদলাইনি; fixture-তে dedicated
`agent_control.sqlite3` দিয়ে শুধু ওই ২৪টি আবার pass। পরে ১৪টি নতুন focused check ও
৭টি অতিরিক্ত affected regression pass। Changed paths-এর rerun-কে নতুন test গুনিনি।
আগের পুরো ৪২/২৯/৩৫ suite কিংবা successful model benchmark আবার চালানো হয়নি।

Fresh runtime-এ `requests` নেই; download/install না করে import-only no-transport shim
ব্যবহার। HTTP transport compatibility পরীক্ষা দাবি করা হয়নি। Test filters native
inference child launch বন্ধ করে; only fixed fixture process চলে। Existing ১৩ prepared
agent, Director/Script, Casting/QC locks এবং সব pinned profile preservation যাচাই।

Second automated code-level audit unit assertions থেকে আলাদা pass। একই assistant-এর
engineering audit; independent human reviewer নয়। Audit-এ atomic dedup, worker ও
controller fingerprint, unreviewed bytecode, nested output/symlink, PID reuse/stop
escalation এবং active-controller preflight/postprocess recovery gap সংশোধন হয়েছে।
শেষ audit-এ ordinary CPU-safe engineering finding open নেই; exact gated voice binding
দুটির dependent source work আলাদা PARTIAL। Actual artistic review এখনও ০।

Evidence: `verification/offline_execution/`। Initial failures, targeted retries,
actual isolation failure, complete successful-test ID list ও second audit রাখা আছে।

## সংরক্ষণ ও exact resume

Main/Render/production DB/media/YouTube অপরিবর্তিত। Dashboard/Director/Script evidence
বা owner creative locks বদলায়নি। Existing ১৩ role rows/records, ১৮ pinned profile ও
`models.json` hash preserved। Central agent-readiness ledger-এ শুধু ছয়টির status ও
native evidence links update। Historical profile adapter labels/weight recipes
অপরিবর্তিত; current native implementation state linked execution ledger-তে আছে।

GPU/CUDA execution, CPU/GPU inference, actual model-weight read/load/download, hosted
inference, paid service, new cloud resource, billing এবং license acceptance **সব ০**।
No production promotion; Phase 4 শুরু হয়নি।

পরবর্তী কাজ:

1. **Voice → Casting:** owner-authorized gated source/terms access ছাড়া exact
   `bodhan-ai/indic-speak@76e0814f189321efe550011850cd288dae366aad` speaker-map/entry
   এবং `ai4bharat/IndicF5@fb652a96e508091045890dae5bb99fe511facbcf` local code bind
   করা যাবে না। Code-only access approval/full terms review আগে; weight download-এর
   আলাদা অনুমতি লাগবে। Voice consent independent confirmation-ও বাকি।
2. **GPU readiness:** kernel isolation-সক্ষম owner hardware, existing approved model
   cache/bundle, exact metadata/hash/origin/license এবং installed dependency/code
   receipt যাচাই। LTX upsampler official hash unresolved থাকলে LTX বন্ধ থাকবে।
3. আলাদা authorized real-runtime session-এ আগে previously prepared **QC visual controls**;
   পরে **Video → Voice → Music/SFX → Performance → Motion → Casting**, প্রতিটি bounded
   case ও actual raw output/technical evidence আলাদা save। Shared cached weights reuse;
   successful পুরোনো Bengali benchmark আবার নয়। Wan MPI-কে mocked success ধরে চালু নয়।
4. Independent Bengali/visual/listening review ও owner final acceptance ছাড়া কোনো
   agent/model production-ready নয়। Queued draft বা CPU fixture acceptance নয়।

এখন ১৯/১৯ দাবি করা যাচ্ছে না: বাকি দুটি selected gated source যাচাইয়ের নির্দিষ্ট
বাধায় PARTIAL; model inference না হওয়াকে engineering অসম্পূর্ণতার কারণ করা হয়নি।
