# REDPAD Phase 3 — ১৯-agent no-GPU engineering

১৩ নভেম্বর ২০২৬। Remote feature HEAD `8741ad26ccd76a6d855b3c4b7c0bdf39dfb9e187`
যাচাই করে সেখান থেকে কাজ হয়েছে। এই রিপোর্টের সঙ্গে সংরক্ষিত authorized feature
commit পরের checkpoint। Branch: `feature/video-music-editing-studio`।

**৮/১৯ NO-GPU ENGINEERING COMPLETE; ১১/১৯ PARTIAL। Production-ready ০।**
Complete কথাটি safe preparation/configuration/routing-contract code ও CPU পরীক্ষা
বোঝায়। Model connection, genuine inference, benchmark, human acceptance বা production
integration বোঝায় না। সব ১৯টির GPU status **GPU TEST BLOCKED**, human status
**OWNER REVIEW PENDING**। কোনো GPU, model inference বা model-weight download হয়নি।

## Agent অনুযায়ী সঠিক অবস্থা

| Agent | No-GPU engineering | Primary candidate ID | বাকি নির্দিষ্ট কাজ |
|---|---|---|---|
| QC | PARTIAL | qwen35_27 | Supplemental vision7 exact binding/calibration; audio critic/listening workflow acceptance। |
| Story | NO-GPU ENGINEERING COMPLETE | qwen35_27 | Approved exact weights/runtime; causal/emotional Bengali benchmark ও independent review। |
| Character | NO-GPU ENGINEERING COMPLETE | qwen35_27 | Text + FLUX identity benchmark; same-person/psychology review। |
| Art Director | NO-GPU ENGINEERING COMPLETE | flux2_klein4 | Real set/prop/palette output ও cultural/visual review। |
| Location | PARTIAL | flux2_klein4 | Supplemental vision7 binding; actual spatial/camera-access inspection। |
| Costume / Hair & Makeup | NO-GPU ENGINEERING COMPLETE | flux2_klein4 | Real reference edits ও chronological identity/state review। |
| Storyboard | NO-GPU ENGINEERING COMPLETE | flux2_klein4 | Actual panels, coverage ও geography review। |
| Performance | PARTIAL | qwen35_27 | Wan Animate exact execution API; actual temporal/performance assessment, generator ≠ critic। |
| Cinematographer | PARTIAL | qwen35_27 | Supplemental image critic exact binding; shot/lighting judgment calibration। |
| Motion & Physics | PARTIAL | wan_animate2 | Exact animation/motion-transfer API; image/frame critic binding ও temporal physics review। |
| Video | PARTIAL | wan22_5 | Existing Wan/SVD controls checked; exact profile execution binding pending। LTX 2.5 adapter missing; পুরোনো LTX-Video নয়। |
| Voice | PARTIAL | indic_speak | Indic-Speak/IndicF5 exact APIs; Parler exact binding; specific reference consent/speaker checks ও listening review। |
| Continuity | PARTIAL | qwen35_27 | Supplemental image critic exact binding; actual cross-scene media controls। |
| Music & SFX | PARTIAL | ace15 | ACE 1.5 execution API missing; Stable Audio exact binding; listening/beat-fit review। |
| Editing & VFX | PARTIAL | qwen35_27 | Supplemental visual binding; audio inspection gap; actual FFmpeg receipt/A-V review। |
| Production Manager | NO-GPU ENGINEERING COMPLETE | qwen36_27 | Exact text runtime ও real schedule/recovery cases; deterministic budget checks প্রস্তুত। |
| Growth | NO-GPU ENGINEERING COMPLETE | qwen35_27 | Real truthful packaging/reference output ও authorized analytics evaluation। |
| YouTube Channel | NO-GPU ENGINEERING COMPLETE | qwen35_9 | Exact text runtime; existing secure read-only connection transport যাচাই। Publishing নিষিদ্ধ। |
| Casting Director | PARTIAL | qwen35_27 | Wan/Indic exact APIs; real acting/voice/chemistry assessment। Current binding-এ video critic নেই। |

Primary/secondary candidates বদলাইনি। Registry-র ১৮টি pinned profile, models.json,
Director/Script selection records ও পূর্বের evidence অক্ষত। Existing professional suite-এ
আগে থেকেই অনুমোদিত research candidate `vision7`-কে QC, Location, Cinematographer,
Motion, Continuity ও Editing-এর **supplemental staging binding** করেছি। এটি primary
বদল নয়, active route বা download approval-ও নয়। Profile:
`Qwen/Qwen2.5-VL-7B-Instruct@cc594898137f460bfe9f0759e9844b3ce807cfb5`। Existing
adapter কেবল bounded image/frame inspection করে; whole-video বা audio critic নয়।

## নতুন কার্যকর engineering

- `SharedServices.stage_request`, `staged_request`, `stage_tool_request`: existing
  task store-এ immutable/idempotent preparation drafts; কোনো configure/execute নয়।
- Draft-এ queued run/mode, task revision, bound input/source hashes, source revisions,
  সর্বশেষ revision review-note hash, exact profile/revision/precision ও reference
  version/content hash বাঁধা থাকে। Restart-এর পর থাকে; পরিবর্তন হলে stale/reject।
- Existing approved-source, targeted revision ও independent QC checks reuse। Draft
  তৈরি করে task/output state, production route বা owner decision বদলানো যায় না।
- Text/image native schemas reuse; reference edit বনাম T2I, SVD বনাম T2V, I2V বনাম
  motion transfer, synthetic preset বনাম reference-voice cloning আলাদা validation।
- Wan Animate, LTX 2.5, Indic-Speak/IndicF5 ও ACE 1.5-এর bounded **contract-only**
  preparation; unsupported native API-কে executable বলা হয়নি। Missing execution
  adapters-এর বদলে পুরোনো version silently চালানো বন্ধ।
- Generator বা text-only pipeline-কে image/audio/video critic বলা যায় না। Missing
  capability explicit blocker। Voice reference/transcript/consent-document pins লাগে;
  metadata rights-কে verified cloning consent বলা হয় না।
- Operations-এ sequential schedule budget/DAG checks, source-bound assembly/release
  preparation ও read-only channel operations validation। কোনো analytics fetch,
  actual assembly, upload, schedule বা publish হয়নি; credential input নেই।
- Raw output/media, exact manifest/precision, source/reference hashes, finish/truncation,
  runtime metrics এবং independent review-এর requirements draft-এ সংরক্ষিত। Mock
  output থেকে artistic acceptance তৈরি করার পথ নেই।

## যেসব shared adapter reuse হয়েছে

Existing `shared_model_services` / `shared_model_worker`-এর Qwen/Gemma NF4 text,
FLUX.2 Klein এবং Z-Image schemas; `offline_media`-র native Wan/SVD controls;
Indic-Parler documented presets/styles; `offline_audio`-র Stable Audio controls;
`offline_vision`-এর bounded image contract ও pinned models.json critic metadata;
existing Engine source binding/revision/QC এবং YouTube channel-ID validation।

১৯টি নতুন inference engine তৈরি হয়নি। নতুন অংশ একটি shared **no-GPU preparation
layer ও ledger**; workers/model routes পুনর্নির্মাণ বা Dashboard redesign হয়নি।

## CPU-only পরীক্ষার প্রকৃত ফল

**২১টি নতুন staging test + ২১টি প্রভাবিত existing regression = ৪২টি distinct test পাস।**
শেষ queued-mode ও canonical request fingerprint সংযোজনের পরে শুধু সংশ্লিষ্ট checks
পুনরায় পাস। JSON field order বদলালেও একই staged কাজ duplicate হয় না। Follow-up
rerun-গুলোকে নতুন distinct test হিসেবে বাড়াইনি। পুরো পুরোনো suite/benchmark চালাইনি।

Tests-এ sockets, subprocess launch, runtime probe ও model-loading পথ বন্ধ; model
libraries unavailable রাখা হয়েছে। Existing regression receipt-এ সব forbidden-resource
attempt counter **০**। Coverage-এ সব ১৯ role, supported candidate-operation pairs,
unsupported modalities, version aliasing, privacy/endpoint fields, source approval,
stale source/ref/owner-note, restart/idempotency, existing route snapshots ও QC gates আছে।

Initial test-এ local `requests` dependency অনুপস্থিত ছিল; project dependency install
করে সেই সমস্যা মিটেছে। কোনো model package/weights/CUDA environment install হয়নি।
Tiny metadata/reference fixtures স্পষ্টভাবে software-only; actual generated samples নয়।

Evidence: `verification/no_gpu_19agent/`। Ledger:
`assets/professional/phase3_19agent_no_gpu_staging.json`। Central registry-তে ১৯ agent-এর
ledger reference যুক্ত; আগের results মুছে যায়নি। Export utility শুধু CPU validation
metadata লেখে; runtime probe/download চালায় না।

## Exact runtime/download/license dependencies

`verification/no_gpu_19agent/runtime_dependencies.json`-এ প্রতি candidate-এর exact
repo/revision, precision, selected weight bytes, license/gated status এবং existing
unmeasured RAM/VRAM planning gate সংরক্ষিত। এগুলো fit guarantee বা measured minimum নয়।

- Qwen/Gemma: compatible Transformers classes, torch/accelerate/bitsandbytes, complete
  pinned tokenizer/config/weights, NF4-on-load/FP16 recipe এবং measured CUDA compatibility।
- FLUX/Z/Wan/SVD: exact Diffusers pipeline/components/approved files; native controls
  ও actual generated output verification। Existing Wan/SVD install receipt আলাদাভাবে
  exact pinned profile-এ bind করতে হবে।
- Vision7: existing offline Qwen2.5-VL processor/weights ও BF16 image worker; exact
  install/component binding ও critic calibration বাকি। Audio understanding নেই।
- LTX 2.5, Wan Animate, Indic-Speak, IndicF5, ACE 1.5: exact reviewed component/API
  execution adapter runtime-dependent; code/weights/versions যাচাই ছাড়া executable নয়।
- Indic-Parler ও Stable Audio: old worker আছে; exact profile installation binding,
  compatible packages, consent/terms ও actual waveforms/listening evidence বাকি।

এই staged exact profiles-এর download approval নেই। পূর্বের অনুমোদিত Qwen GGUF-কে
Qwen BF16→NF4 profile হিসেবে ধরা হয়নি। Gemma custom terms; Indic-Speak upstream এবং
Indic Open Model terms; IndicF5 gated/custom-code/voice consent; LTX gated/community
terms; SVD/Stable Audio custom commercial conditions আলাদাভাবে owner review প্রয়োজন।
কোনো নতুন terms গ্রহণ বা download approval নিজে দেওয়া হয়নি।

## পরের agent-by-agent GPU sequence — এখন চালানো হয়নি

**Story → Character → Art → Costume/Hair/Makeup → Storyboard → Growth → Production
Manager → YouTube → Video → Voice → Music/SFX → Location → Cinematographer →
Continuity → QC → Performance → Motion/Physics → Editing/VFX → Casting।**

প্রতি ধাপে প্রথমে exact model/license/download approval, available hardware এবং
পরিস্থিতি অনুযায়ী missing runtime adapter/binding পূরণ করতে হবে। Approval ছাড়া
primary-কে ছোট quantized variant দিয়ে বদলানো নয়। একই approved weights cache reuse;
role-specific real tests, raw/provenance এবং independent review শেষে তবেই acceptance।
QC/visual/listening gates না মিটলে sample গবেষণাতেই থাকবে; production promotion নয়।

পরের resume: এই ledger ও evidence পড়ে **Story-এর complete preparation** থেকে শুরু;
GPU ব্যবহারের নতুন অনুমোদিত সেশনের আগে কোনো inference নয়। PARTIAL agent-এ listed
binding/API/capability gap আগে মেটাতে হবে; শুধু GPU পাওয়া মানেই প্রস্তুত নয়।

Main/Render/production DB/media/YouTube publishing অপরিবর্তিত। Director ও Script-এর
বর্তমান model-selection work বদলানো হয়নি। Professionally validated agents এখনও ০/২১।
