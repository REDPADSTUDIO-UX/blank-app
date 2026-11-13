# REDPAD — বাকি ১১ agent-এর offline engineering

১৩ নভেম্বর ২০২৬। Remote feature checkpoint `0220a69787883b0c60b178571995f0019a4a9541`
যাচাই করে কাজ হয়েছে। এই রিপোর্টের সঙ্গে সংরক্ষিত authorized feature commit পরবর্তী
checkpoint। GPU, CUDA execution, CPU/GPU model inference, বাস্তব model-weight read/load,
weight download, hosted generation, paid API এবং license acceptance—সব **০**। শুধু
official public model documentation পড়েছি; local Python interface মানে বাহ্যিক API নয়।

**নতুন ৫টি no-GPU engineering complete; মোট ১৩/১৯। বাকি ৬টি PARTIAL।**
সব ১১টির actual execution **RUNTIME BLOCKED**, artistic acceptance **HUMAN REVIEW
PENDING**। Production-ready ০; professionally validated agent এখনও ০/২১।

| Agent | এই ধাপের engineering status | প্রকৃত কাজ / blocker |
|---|---|---|
| QC | NO-GPU ENGINEERING COMPLETE | Exact vision bundle binding, local critic payload, bounded findings/regions, abstention ও seeded control guards। Unsupported audio/whole-video mode reject; accuracy/listening acceptance বাকি। |
| Location | NO-GPU ENGINEERING COMPLETE | Supplied-reference spatial/camera-access schema, version/hash pins; কোনো automatic real-world location verification নয়। |
| Performance | PARTIAL | Native Wan Animate reference-image + driving-video contract ও temporal assessment inputs। Exact native code/YAML revision unverified; generator acting critic নয়। |
| Cinematographer | NO-GPU ENGINEERING COMPLETE | Framing/light/blocking/screen-direction schema; lens value-তে supplied metadata evidence লাগে। Exact local critic preparation ও raw response contract প্রস্তুত। |
| Motion & Physics | PARTIAL | Native animation contract, separate frame inspection ও temporal sampling checks। Exact Wan execution interface ও actual temporal physics judgment বাকি। |
| Video | PARTIAL | Existing native Wan/SVD worker payload mapping সম্পন্ন। LTX 2.5 নির্বাচিত recipe-তে required upsampler অনুপস্থিত; reviewed code/CLI binding বাকি। |
| Voice | PARTIAL | Parler local payload, NFC-preserved Bengali text/annotations, reference/transcript/consent contracts। Indic-Speak pinned interface ও IndicF5 reviewed custom-code dependencies বাকি। |
| Continuity | NO-GPU ENGINEERING COMPLETE | Character/costume/prop/location state ledger; same scene/time contradictory বনাম consistent state checks; local frame critic binding। |
| Music & SFX | PARTIAL | Stable Audio local payload ও published Small sampling recipe; scene beat/cue timing checks। Exact ACE 1.5 component/API loader ও `.pt` safety policy বাকি। |
| Editing & VFX | NO-GPU ENGINEERING COMPLETE | Local frame critic binding, source-pinned edit decisions, trim/track/timestamp/A-V tolerance checks। কোনো footage বা film render হয়নি। |
| Casting Director | PARTIAL | Identity/voice consent evidence, separate portrait/performance/voice/partner checks; existing Director inspection/Producer lock অক্ষত। Wan/voice execution gaps ও actual chemistry assessment বাকি। |

Complete এখানে **safe adapter preparation architecture, exact model binding checks,
request/response contracts ও CPU validation** বোঝায়। Runtime compatibility, image
understanding বা filmmaking competence বোঝায় না। Unsupported media modes-কে accepted
capability বানানো হয়নি। QC/Editing-এর automatic audio understanding নেই; explicit
rejection ও actual independent listening review-এর gate রাখা হয়েছে।

## কী বাস্তবায়িত হয়েছে

`SharedServices.prepare_offline_request` এবং `prepared_offline_request` existing staging
থেকে immutable local-worker preparation বানায়। Source/spec/worker পরিবর্তনে stale হয়;
restart/idempotency বজায় থাকে। একই stage-এর আলাদা inspection spec আলাদা preparation
ও output destination পায়। কোনো worker launch করার method বা নতুন inference engine নেই।

Existing vision, Wan/SVD, Parler এবং Stable Audio worker schemas reuse হয়েছে। Exact
bundle verification-এ repo/revision, selected file bytes/SHA256, owner/license receipt,
complete manifest ও origin receipt মিলতে হয়; symlink, absent model ও changed files
reject। এই ধাপে শুধু tiny **manual unit metadata fixtures** দিয়ে positive hash checks;
বাস্তব model weights পড়া হয়নি। Prepared payload-এর `launch_authorized=false`,
`inference_completed=false`; কোনো নতুন owner/license approval লেখা হয়নি।

Department checks একই `stage_tool_request`-এ যুক্ত। Reference version/content/rights,
approved source/task revision ও owner note pins আগের মতো enforce হয়। Cue/edit/voice/
casting/temporal evidence বদলালে preparation stale। Original output বা human approval
ছাড়া কোনো professional acceptance নেই। Director/Script code/selection, অন্য আট agent-এর
ledger rows/registry records, ১৮ pinned profile ও models.json hash অপরিবর্তিত যাচাই হয়েছে।

Vision response validator শুধু schema/reference/region/declared certainty পরীক্ষা করে;
pixel-এর সত্য নিজে যাচাই করে না। Known clean/seeded control-এ false-positive/missed
category ধরতে পারে। Continuity checks supplied assertions-এর বিরোধ ধরে, unseen footage-এর
judgment নয়। Edit manifest কোনো transition/mix/gap নিজে বানায় না; actual FFmpeg render
ও A/V inspection পরের authorized execution workflow-তেই হবে।

## Official interface যাচাই ও সৎ সীমা

- **Wan Animate:** বর্তমান official card native image/video/prompt/YAML entry দেখায়;
  Diffusers example একটি আলাদা `*-Diffusers` pack ব্যবহার করে। নির্বাচিত native pinned
  card এই tool-এ accessible হয়নি। Exact code/YAML review ছাড়া worker নাম invent করিনি।
- **LTX 2.5:** নির্বাচিত revision-এর card-এ `ltx_pipelines.distilled` ও separate
  components আছে। Required spatial upsampler বর্তমান selected file list-এ নেই।
  পুরোনো LTX-Video, Comfy quantization বা Diffusers repack substitute করিনি।
- **Indic-Speak:** pinned card accessible হয়নি; current local example preview-v2
  উল্লেখ করে। Exact selected version/components/speaker mapping unverified; gated
  Indic Open Model ও upstream terms owner review ছাড়া গ্রহণ নয়।
- **IndicF5:** target text, reference audio ও তার transcript লাগে; public example
  custom code enable করে। এই task সেই code execution বা gated terms অনুমোদন করে না।
- **ACE 1.5:** existing 3.5B worker আলাদা model। Exact code revision/component-loading
  contract ও selected `silence_latent.pt`-এর safe policy যাচাই হয়নি। Contract-only।
- **Stable Audio Small:** published recipe-এর ৮-step, CFG ১, pingpong sampler-এর সঙ্গে
  staged request/worker guidance মিলিয়েছি। পুরোনো generic audio settings-কে Small-এর
  pinned profile হিসেবে চালাইনি। Actual package/components/output/listening unverified।
- **Qwen2.5-VL/Parler:** official documented local classes/input structure-এর সঙ্গে
  existing worker mapping মিলেছে; exact installed runtime/device/dtype এখনো মাপা হয়নি।

Primary source URLs, pinned-card access ফল ও uncertainty:
`verification/offline_11/upstream_interfaces.json`। কোনো paid/hosted model endpoint নয়।
Licenses/rights review এখনও owner-dependent; source availability commercial clearance নয়।

## CPU-only tests ও evidence

**২১টি নতুন software test + ৮টি essential existing compatibility check = ২৯টি distinct
test সফলভাবে যাচাই।** নতুন test log-এ প্রথম ১৯টি; audio recipe ও motion frame-এর নতুন
দুটি targeted follow-up আলাদা logs-এ। Related follow-up rerun-কে নতুন test হিসেবে বাড়াইনি।
আগের ৪২টি পুরো suite বা সফল model generation পুনরায় চালাইনি।

Compatibility run-এর ৮টির ৭টি সরাসরি পাস; একটি `requests` dependency না থাকায় error।
Project-এর HTTP client dependency install করে শুধু ওই failed check পুনরায় পাস। কোনো
model/runtime package install নয়। Test execution-এ model imports, GPU probe, subprocess
launch ও network transport guard করা; current compatibility execution counters ০।

একটি audit correction: আগের `verification/no_gpu_19agent/affected_regression_receipt.json`
বাস্তবে **১টি blocked socket construction** দেখায়। আগের রিপোর্টের zero-attempt বাক্যটি
সঠিক ছিল না। Successful external model request-এর প্রমাণ নয় এটি; কারণও নিশ্চিত বলে
দাবি করিনি। Historical receipt/report মুছিনি। Correction আলাদা audit JSON-এ আছে।

Evidence: `verification/offline_11/`। সব fixtures software-only; কোনো synthetic
test image/audio/JSON-কে real generation বা independent artistic review বলা হয়নি।

## Exact resume

1. এই checkpoint ও `verification/offline_11/readiness.json` পড়ে অবশিষ্ট ছয়টি agent-এর
   interface/component blocker ধরে কাজ চালাবে। বিশেষত LTX missing component/code pin,
   Wan native code/YAML pin, Indic custom code/consent এবং ACE 1.5 safe loader review।
2. Owner-এর explicit অনুমতি ছাড়া নতুন weight, gated license বা paid compute নয়।
3. পরের authorized local-hardware phase-এ প্রথমে **QC-এর exact vision7 bundle/hash ও
   native request compatibility** যাচাই; clean/seeded visual controls ও human review।
   এটি আগের সফল Bengali text controls পুনরাবৃত্তি নয়। Cache থাকলে reuse।
4. একই vision worker-এর role-specific Location/Cinematographer/Continuity/Editing cases
   একে একে চালাবে; generation নয় inspection বোঝাবে। Unsupported audio/video mode reject।
5. Actual runtime output, technical checks, independent visual/listening assessment ও
   owner final acceptance ছাড়া কোনো candidate winner বা production route নয়।

এই সেশনে main, Render deployment/restart/DB/media এবং YouTube publishing অপরিবর্তিত।
অন্য আট agent ও Director/Script-এর কাজ পুনরায় করা হয়নি; Phase 4 শুরু হয়নি।
