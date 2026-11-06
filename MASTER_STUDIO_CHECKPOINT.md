# REDPAD AI Studio — Unified Master Checkpoint

মূল checkpoint: `28e6ece21d07ee6a5913c1a92a1bde7b16d63743`।
একটি প্রকল্প হিসেবে নতুন master নির্দেশনা অনুসারে কাজ চালানো হয়েছে।
মূল নির্দেশনা: `assets/phase3/master_scope.md`; তার SHA256 ও A–J workstream ledger:
`verification/master_studio/master_ledger.json`।

**এই milestone-এ integration/software উন্নত হয়েছে এবং নতুন বাস্তব CPU evidence
আছে। পুরো Studio, ৩০-পর্বের series বা cinematic production প্রস্তুত হয়নি।**
কোনো স্বাধীন মানব editorial/listening/visual review বা নতুন cinematic owner approval হয়নি।

## A — Master status: সব ২০টি agent

সব পুরোনো department, contract, approval, routing, recovery ও পরীক্ষার evidence রাখা হয়েছে।
প্রতিটি agent-এর পৃথক বর্তমান status: `verification/master_studio/agents_matrix.json`।
কোনোটিকে শুধু software test পাস করার কারণে production-ready করা হয়নি।

| Agent group | Software / integration | এই milestone-এর প্রকৃত AI evidence | বাকি বাধা |
|---|---|---|---|
| Story, Script | আগের contracts/guards রাখা; unified project-এর primary roles | Qwen দিয়ে নতুন story, romance, humor, revision task | গ্রহণযোগ্য বাংলা creative quality নেই |
| Director, QC | source-specific review; QC model observation এখনো unverified | একই Qwen-এ আলাদা critic/QC task; এক seeded prop defect শনাক্ত | স্বাধীন model/human review এবং সঠিক editorial remedy অপরীক্ষিত |
| Character, Art, Location, Costume | approved screenplay ও upstream artifacts থেকে automatic binding; reference hash approval | নতুন reference/image inference হয়নি | অনুমোদিত model/reference ও identity/cultural review |
| Storyboard, Performance, Cinematographer, Motion, Continuity | source IDs, schema guidance, bounded records, versioned handoff | নতুন অভিনয়/মোশন/ক্যামেরা inference হয়নি | বাস্তব footage/reference ও meaningful media review |
| Video | Wan/LTX executable local paths যোগ; SVD strict path ও legacy adapter রাখা | তিন engine-ই inference BLOCKED | অনুমোদিত checkpoint/license ও compatible CUDA GPU |
| Voice | offline preset Indic Parler-TTS worker ও local tokenizer boundary | speech inference হয়নি | অনুমোদিত weights, compatible dependency environment, listening review |
| Music, Editing | আগের procedural cues, asset-aware rendering ও approval gates রাখা | নতুন neural music/film হয়নি | অনুমোদিত genuine media, listening ও edit review |
| Production Manager | master ledger, hierarchy, automatic ১৭-task coordination, bounded execution/recovery | handoff tests-এ স্পষ্ট simulation | বর্তমান approved creative source ও real model quality |
| Growth, YouTube | preparation/read-only controls রাখা | নতুন external read/write হয়নি | final approved media; publishing অনুমোদিত নয় |

## B — নতুন বাস্তব writing benchmark

আগে অনুমোদিত **Ollama 0.40.15 এবং ঠিক একই Qwen3-4B-Instruct-2507 Q4_K_M**
পুনরুদ্ধার করা হয়েছে। Archive checksum এবং প্রতিটি model blob-এর SHA256 আলাদা করে
যাচাই হয়েছে (`restoration.json`)। নতুন কোনো model variant download হয়নি।
CPU-only runtime extraction; system service বা cloud/GPU resource চালু হয়নি।

বাস্তব preflight-এ routing bug পাওয়া যায়: Ollama bare hex digest দেয়, অথচ approval
registry `sha256:` prefix চায়। Canonical normalization ও malformed-digest rejection
যোগ হয়েছে; বাস্তব baseline এবং regression test দিয়ে সংশোধন যাচাই হয়েছে।

একই প্রস্তুত benchmark suite-এর ছয়টি **আগে না-চালানো** case-এ প্রথম control run:

| Task | Role | Runtime / schema | Tokens | Wall seconds |
|---|---|---|---:|---:|
| story | Story | complete / valid | 301 | 52.605 |
| romance | Script | complete / valid | 237 | 37.440 |
| humor | Script | complete / valid | 241 | 31.543 |
| revision | Script | complete / valid | 192 | 27.704 |
| criticism | Director | complete / valid | 219 | 36.324 |
| qc | QC | complete / valid | 203 | 28.734 |

**৬টি actual call, ৬টি complete reply, ০ literal timeout/truncation,
৬টি schema-valid reply; মোট 214.350 seconds।** Complete JSON-এর কিছু text field
এখনো মাঝ-বাক্যে শেষ হয়েছে; এটি finished prose-এর প্রমাণ নয়। অন্য মডেল এখনো
এই suite-এ চালানো হয়নি। কোনো comparative winner বা production model নির্বাচন হয়নি।

প্রকৃত raw text, exact request/schema/system/settings, model digest, counters,
timing ও validation: `verification/master_studio/qwen_control/`।
পুরো report: `control_report.json`। পুরোনো successful/failed trials পুনরায় চালানো হয়নি।

### Creative findings — assistant assessment, human review নয়

- Story চিকিৎসার টাকার উদ্দেশ্য উল্টে দিয়েছে: raw `want` হলো
  `মা মেয়ের চিকিৎসার টাকা পাবে।`। causal consequence ও cliffhanger গ্রহণযোগ্য নয়।
- Romance-এ `তুমি যদি চায়, আমি চাই না।` অর্থপূর্ণ responsive exchange নয়।
  closing action-এ অপ্রস্তুত সোনার পাত্র/আলোর ঘটনা এসেছে।
- Humor-এ `অসামান্য খাবার দেয় না, আমি কখনো কালো চাল না খাই।` স্বাভাবিক
  বাংলাদেশি রসিকতা নয়; সম্পর্কভিত্তিক wit প্রমাণিত হয়নি।
- Revision শুধু s2 দিয়েছে; কিন্তু `তুমি কখনো না না কাজ করে দেখি না।` সংলাপ দুর্বল,
  আর action field-এ spoken dialogue ঢুকেছে। Target ID অনুসরণ artistic pass নয়।
- Director ও QC উভয়েই L3-এর prop-continuity defect শনাক্ত করেছে। এই **একটি seed**-এ
  TP=1, FP=0, FN=0, precision=recall=1। একই Qwen-এর দুই task; independent model
  criticism নয়। প্রস্তাবিত সংশোধন অস্পষ্ট/অকার্যকর, তাই editorial judgment approved নয়।
- Blind package প্রস্তুত: `blind_review.json`; administrator key আলাদা
  `blind_admin_mapping.json`। এটি single-model baseline-এর ছয় আলাদা task,
  multi-model winner comparison নয়। কোনো মানব reviewer/score বানানো হয়নি।

Gemma 3 / Qwen3.5 download এবং Gemma terms consent আগের মতো pending।
বর্তমান model-selection table-এ Story, Script, Director, QC চারটিই **None**।

## C — তিনটি offline video engine

| Engine / exact variant | Software | Install / runtime / inference | Quality / owner |
|---|---|---|---|
| Wan2.2 TI2V 5B Diffusers | T2V/I2V local worker call path, native frame grid, pinned checkpoint manifest | weights অনুপস্থিত; CUDA নেই; বাস্তব inference হয়নি | reviewed নয় / approved নয় |
| LTX Video 2B 0.9.5 | T2V/I2V worker call path; আলাদা concrete initial variant | weights অনুপস্থিত; CUDA নেই; বাস্তব inference হয়নি | reviewed নয় / approved নয় |
| SVD-XT | strict 1024×576, 25 frames, 7fps image-only path; legacy adapter রাখা | weights অনুপস্থিত; CUDA নেই; বাস্তব inference হয়নি | reviewed নয় / approved নয় |

আলাদা eight-status preflight: `video_status.json`। Capability/variant registry:
`assets/offline/engines.json`। Optional dependency recipe:
`assets/offline/requirements-media.txt`। Recipe তৈরি মানে dependency compatibility
hardware-এ যাচাই হয়েছে নয়। CPU host-এ Torch/Diffusers install করা হয়নি।

Wan-এর official 1280×704 offload example অন্তত 24GB VRAM নির্দেশ করে। LTX/SVD-এর
12/8 GiB budget floor এই software-এর conservative planning choice; measured minimum
বা guaranteed fit নয়। BF16 compatibility-ও preflight-এ পরীক্ষা হয়।
LTX 0.9.8 distilled গবেষণায় আছে; 0.9.5 code-কে 0.9.8-এ tested বলে দাবি করা হয়নি।

বাস্তব কাজের path এখন model download বা hosted fallback ছাড়া executable, কিন্তু
বর্তমানে শুধু mocked pipeline protocol এবং negative/preflight tests পাস করেছে।
সব তিনটি engine-এর genuine inference ছাড়া video system validated হবে না।
Checkpoint-এর `.py`/pickle components ও symlinks নিষিদ্ধ; সব files-এর digest pin
করতে explicit owner/license confirmation লাগে। Model/reference mutation হলে stale
media গ্রহণ হয় না। Completed inference, approved model identity এবং technical output validation আলাদাভাবে record হয়—codec failure-কে inference না-হওয়া বলা হয় না। Owned subprocess-এর timeout, failure evidence retention,
interrupted-job recovery, local MP4 decode/dimension/duration inspection আছে।

SVD text prompt conditioning নয়; editorial guidance মাত্র। Wan/LTX-তে prompt বা
single-image conditioning-এর বাইরে identity-lock, exact acting/physics/camera বা
lip-sync control দাবি করা হয়নি। এগুলো এখনো specialist guidance/পরীক্ষার লক্ষ্য।

Primary sources:
- https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers
- https://huggingface.co/docs/diffusers/api/pipelines/wan
- https://huggingface.co/Lightricks/LTX-Video-0.9.5
- https://huggingface.co/Lightricks/LTX-Video
- https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt

## D — Visual references, acting, camera ও continuity

নতুন local reference review SHA256-bound; পরিবর্তিত image আবার review ছাড়া
conditioning-এ যায় না। PNG/JPEG size/pixel/path validation ও isolated project
storage আছে। Generated reference model বা identity consistency এখনো যাচাই হয়নি।
আগের character/location/costume/shot/performance/physics contracts রাখা হয়েছে;
নতুন internal inference prompts source facts ও IDs ধরে department records চাইবে।
এসব plan, বাস্তব অভিনয় বা physical simulation নয়। কোনো new reference frame বা
দুই-চরিত্রের AI shot এই milestone-এ তৈরি হয়নি।

## E — Offline Bengali speech ও audio

Indic Parler-TTS-এর documented synthetic Bengali presets-এর worker যোগ হয়েছে;
নিজস্ব real-person reference/voice cloning নেই। শুধু local model ও দুই tokenizer
bundle; network/paid fallback নেই। Unicode text, short duration, finite/non-silent
signal, WAV metadata এবং retained failure evidence check আছে।

PyPI `parler-tts==0.2.3` Transformers **4.46.1** চায়, তাই video environment থেকে
আলাদা optional recipe রাখা হয়েছে (`requirements-speech.txt`)। Compatible actual
environment, weights, dependent-component terms, pronunciation ও listening review
সবই pending; কোনো কথা শোনানো/প্রাকৃতিক accent/character voice accepted নয়।
Source: https://huggingface.co/ai4bharat/indic-parler-tts

Lip-sync backend integrated/inference-verified নয়। আগের MuseTalk/dependency-license
research আছে; Wav2Lip/MusicGen non-commercial weights commercial default করা হয়নি।
Music/SFX-এর পুরোনো procedural composition স্পষ্টভাবে procedural; neural score নয়।
আগের editing/ducking/subtitle/real-asset gates রাখা হয়েছে; নতুন dramatic mix হয়নি।

## F — Unified Dashboard ও coordination

নতুন **REDPAD Studio** tab-এ পাঁচটি functional workspace:
Creative Studio; Production Studio; Post-Production Studio; Project Management;
Admin / Advanced। পুরোনো সব tabs ও ২০টি advanced agent workspace রাখা হয়েছে।

- Owner-এর Director/Story/Script notes সত্যিকার owner notes হিসেবে সংরক্ষিত হয়;
  AI reply নকল হয় না। Real task execution ছাড়া generated output দেখানো হয় না।
- Project hierarchy: Series → Season → Episode → Sequence → Scene → Shot → Asset।
  ১–১০০ planned episode এবং ১৮০–৪২০০ second target support করে। Planned nodes
  generated story নয়। Existing nodes/brief অপরিবর্তনীয়; versioned revision আলাদা।
- Approved screenplay ও তার Director review নির্বাচন করে একই graph-এ **১৭টি local
  generation task** automatic queue হয়। Records fixture থেকে production output
  বানানো হয় না; model-এর নতুন records আগের validators-এ পাস করতে হবে।
- সব source bindings existing Engine-এর current approved versions থেকে আসে।
  QC ও owner approval নিজে থেকে দেওয়া হয় না; notes/source copy-paste লাগে না।
- এক action-এ ১–৩টি bounded run; dependency blocks স্বয়ংক্রিয় recheck হয়,
  model failures-এ explicit retry লাগে। Recovery পুরোনো worker stopped হলে নতুন run
  identity দিয়ে mapping ঠিক রাখে। কোনো background execution promise নেই।
- Model controls-এর widget namespace projectভিত্তিক, তাই পুরোনো Dashboard-এর সঙ্গে
  duplicate-key সংঘর্ষ হয় না। Models/license approval ও presets নিজেরা install হয় না।
- Project checkpoint source SHA, run IDs, revisions ও input hashes ধরে; SQLite sidecar
  এবং evidence export থেকে resume করা যায়। Production database খোলা হয়নি।

**Known software limitation:** full ৩০-পর্বের staged creative architecture →
পর্বভিত্তিক Director/Script generation-এর complete automatic path এখনো শেষ নয়।
Hierarchy/resume foundation আছে; এক বিশাল season inference বর্তমানে blocked।
অযোগ্য baseline দিয়ে ৩০-পর্বের production-ready output বানানো হয়েছে বলা হচ্ছে না।

## G — End-to-end filmmaking ও acceptance

এই continuation-এ actual cinematic MP4, Bengali speech take, neural music বা নতুন
five-minute episode তৈরি হয়নি। Wan/LTX/SVD clips, reference identity, acting,
pronunciation, lip-sync, musical fit ও final edit independent review হয়নি।
Level 1 creative acceptance-ও হয়নি; পরের levels-এর quality gate অতিক্রম করা হয়নি।
৩০-পর্ব বা ৬০–৭০ মিনিটের film production-ready নয়। Playable output link দেওয়া হয়নি,
কারণ নতুন প্রকৃত dramatic output নেই।

## H — Regression / QA

**৩১২টি regression test পাস, ০ failed, ০ skipped; 34.328 seconds।**
**৮টি standalone check পাস।** নতুন ২১টি test hierarchy, integration, recovery,
digest normalization, model controls, reference approvals, worker protocols,
timeout retention, native capability rejection ও offline speech boundaries cover করে।
বিদ্যমান Wan adapter flag-এর test এখন নতুন implemented code status যাচাই করে;
media-generated=false আলাদা রাখে।

Evidence: `tests.json`, `standalone.json`, `environment.json`, `restoration.json`,
`control_report.json`, `video_status.json`, `audio_status.json`।
Unit-test image/tone/video fixtures ও mocked pipeline calls actual AI film নয়।

## I — GitHub ও safety

সব পরিবর্তন শুধু `feature/video-music-editing-studio`-এ save হবে। Main-এ merge বা
পরিবর্তন নয়। Render deploy/restart/migrate নয়; live SQLite/media/channel/OAuth data
অপরিবর্তিত। কোনো paid API, GPU rental, নতুন account/cloud resource, YouTube
upload/publish/schedule বা scope expansion হয়নি। নতুন weights/লাইসেন্স consent হয়নি।
পুনরুদ্ধার শুধু আগের নির্দিষ্ট অনুমোদিত Ollama/Qwen components। Weights/private
media git-এ commit হয়নি। পুরোনো অসমাপ্ত checkout-ও অক্ষত রাখা হয়েছে।

## J — Exact next steps / consolidated blockers

1. Gemma 3 4B Q4_K_M ও Qwen3.5 4B Q4_K_M-এর পূর্বের exact manifests/6.67GB নতুন
   layers download-এর owner approval এবং Gemma terms consent প্রয়োজন। Master
   prompt Section 5 নিজে এই permission দেয় না। তারপর একই suite-এ তুলনা হবে।
2. Writing model selection-এর আগে independent Bangladeshi Bengali review প্রয়োজন।
3. Media-এর জন্য owner-authorized compatible GPU পরিবেশ, exact checkpoints ও
   variant-specific license/size review প্রয়োজন। Kaggle account/session/quota inspect
   বা activate করা হয়নি; অন্য পরিবেশ নিজেরা বানানো হয়নি।
4. Short actual reference/acting/video/speech tests accepted হলে তবেই cinematic
   scene এবং পরে আলাদাভাবে অনুমোদিত পাঁচ-মিনিট episode workload।
5. Long-series staged generation/orchestration-এর অবশিষ্ট software work এবং সব real
   media quality gates একই master project-এ পরের milestone-এ চলবে; নতুন development
   prompt দিয়ে প্রকল্প নতুন করে শুরু করার দরকার নেই।
