# REDPAD Phase 3 — বাকি ছয়টির offline engineering checkpoint

১৩ নভেম্বর ২০২৬, বাংলাদেশ সময়। Feature remote HEAD
`0de2bf336ca2c3c1f7abff1b155962aeaec83cc9` যাচাই করে সেখান থেকে কাজ হয়েছে।
এই রিপোর্টসহ authorized feature commit পরবর্তী resume checkpoint।

**নতুন safe source-reviewed preparation বাস্তবায়িত; engineering complete এখনও
১৩/১৯। ছয়টি PARTIAL। Professionally verified/PRODUCTION READY ০/২১।**
ছয়টির real inference **RUNTIME VALIDATION BLOCKED**, artistic acceptance
**HUMAN REVIEW PENDING**। Source inspection/software fixture runtime বা artistic
সক্ষমতার প্রমাণ নয়। কোনো model winner, executable production route বা approval নয়।

| Agent | Engineering | বাস্তবায়িত কাজ | নির্দিষ্ট execution blocker |
|---|---|---|---|
| Performance | PARTIAL | একই Wan native call preparation; image/driving-video pins, actor permission scope, bounded frame/rate/duration ও gesture reference | Exact auxiliary T5/VAE/CLIP revision/hash, `.pth` safety, MPI/device/dependency ও offline bridge review |
| Motion & Physics | PARTIAL | Performance-এর একই Wan প্রস্তুতি reuse; ordered unique source-frame metadata, interaction/time bounds, no silent looping/resampling | একই native component/bridge gap; actual temporal physics/weight/contact validation ও independent visual review |
| Video | PARTIAL | নির্বাচিত LTX 2.5 split BF16 → ModelPaths/DistilledPipeline mapping, component inventory ও explicit missing-upscaler requirement; পুরোনো native Wan/SVD preparation অক্ষত | Spatial upsampler-এর exact SHA/bytes, recipe inclusion/approval, local tokenizer/config ও version-specific BF16 execution bridge |
| Voice | PARTIAL | Bengali original/NFC text; style/pronunciation annotations আলাদা; IndicF5 reference/transcript/scoped consent ও actual PCM WAV metadata checks; Indic-Speak-এ unbound exact-version entry | Gated pinned custom code, Indic-Speak speaker catalogue/SNAC/Vocos `best.pt`, reviewed local loader ও license/voice consent; কোনো remote code enable নয় |
| Music & SFX | PARTIAL | ACE 1.5 native GenerationParams/Config preparation, instrumental-only exact scene cue, 48kHz output contract, deny-auto-download/code-sync requirements; Stable Audio worker reuse | Upstream initialize_service-এর auto-download/code-sync বন্ধ করা reviewed local execution bridge; complete model-code/component review ও bounded auxiliary tensor checks |
| Casting Director | PARTIAL | Wan/voice preparation reuse; actor↔reference consent scope, portrait/performance/voice/partner evidence পৃথক; source-bound persistent assessment draft, abstention ও Director/QC/Producer-lock requirements | Wan/voice native blockers; actual actor/voice/partner performance, consent confirmation ও independent chemistry review |

## এই checkpoint-এর বাস্তব source changes

`offline_specialist_preparation.py` shared pure preparation layer; নতুন ছয়টি engine
তৈরি হয়নি। Existing `SharedServices.prepare_offline_request`-এ explicit specialist
spec দিলে source-reviewed call descriptor তৈরি হয়। `worker_module=None`,
`contract_only=true`, `launch_authorized=false` থাকে। Unsupported custom controls,
endpoints, clone mode, dimensions/time mismatch ও evidence substitution reject।

`PreparedRequests`-এর existing immutable/restart-safe store reuse। Spec, primary
source/reference, extra consent/frame reference বা preparer source বদলালে saved
preparation stale হয়। Missing execution family-তে `verify_bundle=True` আগে silently
ignored হচ্ছিল; এখন fail closed। এই bug fix কোনো model/runtime চালায় না।

Metadata inventory selected model files-এর existence/size `stat` করে; কোনো weight
open/hash/load করে না। `ready_to_load=false`, `hash_verified=false`; manifest বানালেই
authentication বা permission হয় না। Unit fixtures ছাড়া এই সেশনে model folder
inventory-ও চালানো হয়নি। LTX missing auxiliary একই pinned repository-র প্রস্তাবিত
requirement হিসেবে আলাদা আছে—পুরোনো profile/weight recipe পরিবর্তন হয়নি।

Reference audio-র PCM WAV format, sample rate, channels, declared duration ও truncated
data check stdlib দিয়ে হয়। Transcript, accent, emotion, speaker বা consent সত্য
যাচাই করা হয় না। Compressed reference-কে silently resample/convert করা হয় না।
Video timing metadata supplied evidence; decode/ffprobe/physical judgment নয়।

Casting assessment `stage_tool_request`-এর existing task/source revision/QC workflow-তে
যুক্ত। Portrait দিয়ে acting/voice/chemistry findings substantiated বলা যায় না।
Registered real-person reference-কে fictional বলে specific consent এড়ানো reject।
Document attached থাকলেই consent confirmed নয়। Actual Director inspection ও Producer
identity-lock controls আগের workflow-তেই; assessment draft সেগুলো সৃষ্টি/অতিক্রম করে না।

## Exact official native interfaces — static review only

Code-source revisions model-weight revisions থেকে পৃথক; weight profiles অপরিবর্তিত।

- **Wan Animate:** `Wan-Video/Wan-Animate-2@3ad2fef7d61d6200c9c653e0fe47be7616b323f3`।
  `infer/wan_animate_2_demo.py`, native YAML ও `WanAnimate2MPIPipeline.__call__` review।
  Reference image/video, width/height/fps/clip_len/step/seed/prompt/prompt_ref mapping
  বাস্তব source থেকে। YAML-এর class factory বা upstream process setup চালানো হয়নি।
  YAML transformer ছাড়াও T5, VAE, CLIP checkpoints/tokenizers চায়; এই auxiliary
  recipe-এর exact origin/hash ও safe loaders অসম্পূর্ণ। Generator acting critic নয়।
- **LTX:** `Lightricks/LTX-2@f0f2f8607189c78a72420b2b63cb1975b5eca179` (package 1.6.2)।
  `ModelPaths.from_split`, `DistilledPipeline`, distilled CLI ও component flags review।
  নির্বাচিত `Lightricks/LTX-2.5@49b093a39c19169a8a81721dcc541e07e945232f` card একই
  native split layout নির্দেশ করে। Required component-এর exact published path:
  `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors`।
  এটি একই pinned model repository-তে, আলাদা auxiliary repository বা পুরোনো LTX নয়।
  File metadata page accessible হয়নি; SHA/size বানাইনি। Download/terms approval নেই।
  Optional temporal upsampler/DFR detailing LoRA যোগ হয়নি। Quantized/Diffusers substitute নয়।
- **ACE:** `ace-step/ACE-Step-1.5@ca1e85fe9430179831e6bc6be790c332190a3866`।
  `AceStepHandler`, `GenerationParams`, `GenerationConfig`, `generate_music` ও native
  initialization/loader source review। `silence_latent.pt` loader-এ explicit
  `weights_only=True` আছে; তাই আগের loader-policy uncertainty আংশিক resolved। কিন্তু
  size/type/shape/finite tensor validation ও full model-code review বাদ দিয়ে safe
  executable বলা যায় না। Missing component-এ upstream downloader এবং model-code
  auto-sync আছে। Preparation policy এগুলো নিষিদ্ধ করে; বাস্তবে সেগুলো আটকানোর native
  runtime wrapper এখনও implemented/verified নয়, তাই execution BLOCKED। ACE 3.5B নয়।
- **IndicF5:** public official card-এ target text, reference audio/transcript ও 24kHz
  save contract আছে। Exact pinned gated code access হয়নি, license acceptance হয়নি।
  Documented remote custom-code sample executable adapter হিসেবে ব্যবহার করিনি।
- **Indic-Speak:** current public card `inference.TTS(local_dir)` দেখালেও example
  preview-v2 উল্লেখ করে। নির্বাচিত revision-এর local implementation/speaker map
  যাচাই হয়নি; entry `None` রেখেছি। Vocos/SNAC/upstream terms unresolved।

Primary sources, exact code revisions, reviewed paths এবং retrieved-text SHA256:
`verification/offline_6/source_review.json`। Entire upstream files commit করিনি;
source কেবল text হিসেবে পড়েছি, import/execute নয়।

Public model documentation:
- https://huggingface.co/Lightricks/LTX-2.5/blob/49b093a39c19169a8a81721dcc541e07e945232f/README.md
- https://huggingface.co/ai4bharat/IndicF5
- https://huggingface.co/bodhan-ai/indic-speak

## CPU QA — প্রকৃত ফল ও সীমা

**২৮টি নতুন test + ৭টি affected existing check = ৩৫টি distinct test successful।**
প্রথম executed run-এ ৩১টির ৩০টি pass, Casting persisted draft-এ tuple/list mismatch
ধরা পড়ে। Canonical JSON-safe list করে শুধু failed test আবার pass। পরে ৩টি নতুন
WAV/identity/upscaler check pass। Changed ACE/F5 paths-এর ৩টি targeted recheck pass;
এগুলোকে নতুন distinct test হিসেবে বাড়াইনি। Ledger export-এর পরে শুধু preservation
check পুনরায় চলে; শেষে ১টি নতুন unsupported-profile check pass। আগের ৪২/২৯-test suite বা কোনো successful inference পুনরাবৃত্তি নয়।

Fresh environment-এ optional `requests` dependency অনুপস্থিত; প্রথম command test
শুরুর আগেই import error দেয়। Network/package download করিনি। Test runner-এ import-only
HTTP shim ব্যবহার, transport construction নিষিদ্ধ। তাই HTTP transport compatibility
পরীক্ষিত বলা যাবে না। Existing ১৩ prepared agent-এর declared contracts/readiness,
Wan/SVD/Parler/Stable payloads, restart/idempotency এবং Casting Director/QC lock checks
এর প্রয়োজনীয় subset যাচাই হয়েছে। সব পুরোনো test আবার চালানো হয়নি।

Execution-এ network/process/runtime/inference entry guards এবং blocked model-library
imports ছিল। Recorded outer guard attempts ০। Tiny manual image, header-only MP4 ও
manual PCM silence fixtures software-only; real footage/voice/generated evidence নয়।
Model/component inventory fixture tiny manual bytes, actual weights নয়।

পুরোনো historical audit receipt ও `offline_11` evidence অপরিবর্তিত। এই সেশনের initial
failure ও failed-test recovery logs-ও রাখা হয়েছে; কেবল final pass দেখিয়ে failure গোপন নয়।

## Scope, approvals ও exact resume

সব ২১ agent অক্ষত। Other ১৩ role ledger/registry rows, Director/Script records,
১৮ pinned profiles ও `models.json` SHA256 preserved। Central ledger শুধু ছয়টির
preparation evidence/blocker metadata update করেছে। Candidates, precision, primary/
secondary choices, owner story decisions, Dashboard বা production routes বদলায়নি।

GPU/CUDA access, CPU/GPU model inference, actual weight read/load/download, hosted
inference, paid API, billing/cloud resource এবং license acceptance **সব ০**। Main,
Render deploy/restart/migration/upgrade, production DB/media ও YouTube অক্ষত। Phase 4 নয়।

পরবর্তী resume: এই feature commit ও `verification/offline_6/readiness.json` থেকে:

1. **Video/LTX আগে:** একই pinned repository-র শনাক্ত spatial upsampler-এর public
   SHA/size পাওয়া গেলে metadata recipe পূরণ; tokenizer/config loading path এবং BF16
   native execution wrapper static review। নতুন component inclusion/download/terms
   owner approval ছাড়া নয়। এখনো weight download permission চাওয়ার ধাপে যাইনি।
2. **Performance → Motion:** shared Wan auxiliary exact recipe ও `.pth` safe loading
   review; same local MPI worker wrapper, deny-network/timeout/cleanup preparation।
3. **Voice:** explicit authorized gated-code/license/voice consent ছাড়া custom code
   চালাবে না। Exact Indic-Speak speaker/component ও IndicF5 loader pin আগে মেলাতে হবে।
4. **Music:** native initialization-এর automatic download/code-sync deny করা reviewed
   local bridge এবং bounded auxiliary tensor validation; selected ACE 1.5-ই রাখতে হবে।
5. **Casting:** resolved Wan/Voice components reuse; actual pair-performance/voice
   evidence ও Director/QC/Producer identity-lock workflow পরে বাস্তব outputs দিয়ে।

Authorized real-runtime session আলাদা। প্রথম approved exact local model bundle/cache
যাচাই, তারপর bounded QC visual controls ও এক agent করে real tests; successful পুরোনো
benchmark আবার নয়। Human artistic acceptance ছাড়া professionally complete নয়।
