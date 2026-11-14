# REDPAD AI Studio — PROFESSIONAL READINESS REPORT

> পরবর্তী functional engineering work ও বর্তমান handoff: [PRE_GPU_COMPLETION_REPORT_BN.md](PRE_GPU_COMPLETION_REPORT_BN.md)। নিচের report/evidence historical e43 milestone; model capability এখনো professional verified নয়।

তারিখ: 2026-11-07 · continuation: `b0d37be` · branch: `feature/video-music-editing-studio`

**বর্তমান রায়: ০/২০ agent-এর professional readiness প্রমাণিত।** এই checkpoint সফটওয়্যার ও evaluation infrastructure উন্নত করে; কোনো agent-কে professional creative intelligence বা production-ready ঘোষণা করে না। Director, Story ও Script তিনটিই প্রধান owner-facing agent; অন্য ১৭টি existing internal workflow-তেই থাকে।

## প্রমাণের সীমা ও আগের কাজ

আগের contract, knowledge, approval, recovery, routing, rendering ও workflow tests সংরক্ষিত। এগুলোর passing status software foundation-এর প্রমাণ। প্রত্যেক department-এর specialist end-to-end creative workflow এখনও আংশিক বা অযাচাইকৃত; blanket software-complete দাবি করা হয়নি। নিচের matrix-এ model, বাস্তব কাজ, বিশেষজ্ঞ এবং বাকি development আলাদা।

আগের তিন writing model: Qwen3 4B, Gemma3 4B এবং Qwen3.5 4B-এর genuine CPU outputs [আগের রিপোর্টে](APPROVED_MODEL_TEST_REPORT.md) ও raw evidence-এ অপরিবর্তিত আছে। দুই approved বিকল্পের ১৮টি actual call, default-thinking-এর ৬টি failure এবং পরের knowledge-workflow checkpoint-এর actual calls নতুন benchmark হিসেবে গণনা করা হয়নি। শব্দচয়ন, causality, revision ও criticism-এর দুর্বলতা আছে; কোনো winner বা independent human approval ছিল না। বর্তমান workspace-এ শুধু original Qwen3 manifest restored; নতুন weights restore/download করা হয়নি।

**এই continuation: নতুন inference ০; নতুন model-generated artistic samples ০; independent human review ০।** একই দুর্বল 4B-তে hypothesis ছাড়া আর পরীক্ষা চালানো হয়নি। Unit-test synthetic text/image/audio/video fixtures artistic evidence নয়। নতুন পদ্ধতির পরে creative improvement দাবি করার মতো নতুন output নেই।

## ২০ agent: consolidated model, compute, test ও development matrix

Model IDs-এর exact version/license/download/compute নিচের reusable model table-এ। একই model একাধিক department-এ চলবে; সব candidate unselected। Count হলো per-trial minimum, কাজের পূর্ণ coverage-এর বিকল্প নয়।

| Agent | Professional capability | Candidate model IDs | প্রকৃত output / minimum | পরীক্ষার কাজ | স্বাধীন reviewer | বাকি specialist development |
|---|---|---|---|---|---|---|
| Story AI | Causal Bengali narrative and long-form memory | writer9, writer12, gemma4e4 | text: 3 | Write three unseen family/romance/mystery season treatments and a three-episode causal segment; a lost fee cannot reappear, secrets change knowledge only after a disclosure. | Bengali screenwriter/showrunner | End-to-end long-series draft-to-approved-season bridge and capable writer remain unverified. |
| Script AI | Bangladeshi spoken dialogue, subtext, humor, restrained emotion | writer9, writer12, gemma4e4 | text: 8 | Produce eight complete filmable scenes spanning breakfast, father–daughter conflict, romance, wit, quiet grief, horror, earned ending and locked rewrite. No manual polishing of model samples. | Bengali screenwriter/dialogue editor | A stronger writer must pass unseen scenes and exact revision instructions; current 4B samples failed creative quality. |
| Director AI | Grounded dramatic criticism plus visual/performance judgment | writer9, vision7, gemma4e4 | text: 10, video: 3 | Critique five clean and five seeded-defect scenes; identify precise evidence, abstain on clean material, then direct and inspect three real generated short shots. | Film director/editor | Separate critic calibration from approval; multimodal video understanding and actual directed-shot evaluation missing. |
| Quality Control AI | Calibrated multimodal defect detection with uncertainty | vision7, writer9, gemma4e4 | text: 10, video: 3, audio: 3 | Blindly inspect balanced clean/defect script, image, motion, subtitle and audio samples. Measure false positives and misses against an authored hidden answer key and expert adjudication. | Independent script and audiovisual QC specialists | A line-ID match alone is insufficient; requires actual media and specialist adjudication. |
| Character AI | Psychology bible and stable visual identity | writer9, sdxl, flux | text: 1, image: 4 | Generate character bible plus front/three-quarter/profile and changed-light references of the same two fictional adults; blind match identities and reject facial/age drift. | Casting/character designer | Image/reference conditioning adapter and approved identity references are needed; text-to-image alone does not solve identity lock. |
| Art Director AI | Bangladeshi production design and prop continuity | writer9, sdxl, flux | text: 1, image: 3 | Deliver three views of one modest Dhaka tailoring-home set, with the same red tin box, worn table and motivated morning light; verify practical layout and budget. | Production designer | Actual set-image consistency and production-designer review missing. |
| Location AI | Spatial geography and physically buildable camera access | writer9, sdxl, vision7 | text: 1, image: 3 | Produce a measurable floor plan and three generated views; east window, west entry and north kitchen must agree. Validate performer and camera paths. | Location manager/cinematographer | Needs plan-to-view constraint conditioning, not only free text-to-image. |
| Costume Designer AI | Character-appropriate wardrobe and scene state | writer9, sdxl | text: 1, image: 4 | Render one outfit in four chronological shots including wet sleeve and documented change; preserve actor identity, jewelry and social context. | Costume designer/continuity supervisor | Reference-conditioned wardrobe edits and visual continuity evaluation missing. |
| Storyboard AI | Dramatic coverage and visual continuity | writer9, sdxl, vision7 | text: 1, image: 3 | Create three complete six-panel sequences from locked screenplay beats; no premature reveal, incorrect gaze direction, or unexplained geography. | Storyboard artist/director | Panel-generation conditioning and comparison to actual shot outputs still required. |
| Performance Director AI | Playable acting direction and observable performance | writer9, wan, ltx, vision7, animate14 | text: 1, video: 3 | Generate quiet worry, concealed affection and restrained anger clips using the same actor/reference; judge gaze, pauses, partner reactions and emotional transitions. | Performance director/actor | No current video engine guarantees acting control; paired real clips and expert review required. |
| Cinematographer AI | Motivated composition, light and camera behavior | writer9, sdxl, wan, ltx, vision7 | text: 1, image: 3, video: 3 | Render matched wide/reverse/insert coverage and one motivated camera move. Verify window lighting, eyelines, axis and whether the actual shot communicates the intended beat. | Cinematographer | Reference/geometry control and measured generated-camera fidelity missing. |
| Motion & Physics AI | Temporal physics, contact and object permanence | writer9, wan, ltx, svd, vision7 | text: 1, video: 4 | Generate hand-to-table key transfer, sitting on chair, doorway walk and prop pickup; inspect frame-level support, contact, duplicate objects and chronology. | Animation/movement supervisor | Generated frames and frame-level annotations are required; planned constraints are not motion evidence. |
| Video Generation AI | Realistic and reproducible image-conditioned video | wan, ltx, svd | video: 9 | Run three identical reference-conditioned motion briefs per engine, same framing and duration as engine permits. Save native frames, outputs, settings, failures, identities and measured memory. | Director/cinematographer/VFX reviewer | Approved checkpoints/GPU absent. SVD-XT has no text control; compare only equivalent supported conditions. |
| Voice & Dialogue AI | Bangladeshi pronunciation, prosody and speaker consistency | writer9, parler, indicf5 | text: 1, audio: 6 | Generate two speakers across neutral, warm and restrained-angry delivery; include names, numbers, address forms and pauses. Blind listeners transcribe and judge accent/emotion. | Native Bangladeshi dialogue/voice director | Preset TTS versus reference-audio TTS are separate arms; IndicF5 needs authorized voice reference and reviewed code. |
| Continuity Supervisor AI | Longitudinal state tracking across real media | writer9, vision7 | text: 6, image: 3, video: 3 | Inspect a multi-scene packet with planted wet-sleeve, key-holder, door, knowledge, time and axis changes; pair each with a clean control, identify exact frame/beat. | Script/continuity supervisor | Requires real matched frames and expert-labeled positive and negative examples. |
| Music & SFX AI | Musical structure, dramatic fit and motivated Foley | writer9, music35, sfxsmall | text: 1, audio: 4 | Generate separate restrained family score, tender romantic cue, suspense cue and source-motivated Foley; audition under the same real dialogue and evaluate ducking, transitions and rights. | Composer/sound designer | Music/SFX inference adapters and listening evaluation missing; procedural tones are not a cinematic score. |
| Editing & VFX AI | Narrative editing, sync and technical delivery | writer9, vision7, ffmpeg | text: 2, video: 2, audio: 2 | Assemble two complete 60–90 second edits from approved real clips/audio; preserve the emotional reaction beat, continuity, sync, subtitle readability and delivery specs. | Film editor/sound editor | Existing renderer needs approved genuine assets and expert review, not replacement by a model. |
| Production Manager AI | Resource-aware real execution and recovery | writer9, deterministic | text: 3, trace: 3 | Run three real isolated project traces: successful dependency chain, blocked GPU with independent CPU work progressing, and stopped-worker recovery with no duplicate calls or stale approvals. | Line producer/production coordinator | Planning contracts are implemented; real multi-model workload execution and resource measurements remain unverified. |
| Growth AI | Truthful Bengali audience positioning and visual packaging | writer9, sdxl | text: 3, image: 3 | Produce three title/description/thumbnail/trailer packages for the same actually generated approved episode. Reject fake story events, spoilers and misleading imagery; record audience tests separately. | Bengali audience/editorial marketing specialist | Requires approved actual episode assets and human packaging/audience review. |
| YouTube AI | Read-only channel validation and safe release preparation | writer9, deterministic | text: 2, trace: 2 | Prepare two release packets from approved actual media and a consented read-only metadata snapshot. Verify rights, channel binding, token scope and drafts; no upload/publish/schedule. | Channel operations/rights reviewer | Real read-only connection evidence and approved media still needed; publishing remains outside scope. |

## Reusable model ও compute requirement matrix

সব RAM/VRAM engineering planning envelope; measured minimum নয়। CPU RAM, VRAM ও weights-এর storage এক জিনিস নয়। One model/pipeline at a time, bounded context/short media। Exact revision/file SHA [model registry](assets/professional/models.json) ও [metadata inventory](verification/professional_readiness/model_inventory.json)-তে। Size decimal GB; tokenizer/config/dependencies/transfer overhead অতিরিক্ত। Quantized pull থাকলে তা full-precision HF weights থেকে আলাদা।

| ID / exact model | License ও commercial condition | Selected download GB | Host RAM GiB | VRAM GiB planning | Adapter / বাস্তব validation |
|---|---|---:|---:|---|---|
| writer9 — Qwen/Qwen3.5-9B; qwen3.5:9b-q4_K_M | Apache-2.0; Commercial use subject to license conditions | 6.551 (Ollama full layers) | 16 | [8, 12] | existing; নতুন actual inference নেই |
| writer12 — google/gemma-3-12b-it; gemma3:12b-it-q4_K_M | Gemma terms; Custom use/distribution conditions; new variant approval and access terms required | 8.164 (Ollama full layers) | 24 | [12, 16] | existing; নতুন actual inference নেই |
| vision7 — Qwen/Qwen2.5-VL-7B-Instruct; cc594898137f460bfe9f0759e9844b3ce807cfb5 | Apache-2.0; Subject to Apache conditions | 16.584 (selected weights) | 32 | [16, 24] | not_yet_integrated; নতুন actual inference নেই |
| sdxl — stabilityai/stable-diffusion-xl-base-1.0; 462165984030d82259a11f4367a4eed129e94a7b | CreativeML Open RAIL++-M; Commercial use subject to use/distribution restrictions | 6.938 (selected weights) | 32 | [8, 12] | offline worker implemented, real inference blocked; no reference identity control; নতুন actual inference নেই |
| flux — black-forest-labs/FLUX.1-schnell; 741f7c3ce8b383c54771c7003378a50191e9efe9 | Apache-2.0; Subject to license plus gated access/data-sharing approval | 33.721 (selected weights) | 64 | [16, 24] | not_yet_integrated; নতুন actual inference নেই |
| wan — Wan-AI/Wan2.2-TI2V-5B-Diffusers; b8fff7315c768468a5333511427288870b2e9635 | Apache-2.0; Subject to Apache conditions | 34.180 (selected weights) | 64 | [24, 24] | existing; নতুন actual inference নেই |
| ltx — Lightricks/LTX-Video-0.9.5; e58e28c39631af4d1468ee57a853764e11c1d37e | LTX Video 2B 0.9.5 Open RAIL-M, 2025-03-05; Commercial use permitted subject to variant use/distribution restrictions | 25.390 (selected weights) | 64 | [12, 16] | existing; নতুন actual inference নেই |
| svd — stabilityai/stable-video-diffusion-img2vid-xt; 9e43909513c6714f1bc78bcb44d96e733cd242aa | Stability AI Community License, 2024-07-05; Conditional limited commercial license: registration required; revenue/affiliate threshold and attribution/use restrictions apply. Owner eligibility and acceptance unverified; no account or agreement action authorized. | 9.018 (selected weights) | 32 | [8, 12] | existing; নতুন actual inference নেই |
| parler — ai4bharat/indic-parler-tts; 660bc53c64ae83150613264111708a0465211237 | Apache-2.0; Subject to license and gated information-sharing approval | 3.751 (selected weights) | 16 | [4, 8] | existing; নতুন actual inference নেই |
| indicf5 — ai4bharat/IndicF5; fb652a96e508091045890dae5bb99fe511facbcf | MIT; Subject to license, gated access, reference-voice rights and reviewed custom code | 1.403 (selected weights) | 16 | [4, 8] | not_yet_integrated; নতুন actual inference নেই |
| music35 — ACE-Step/ACE-Step-v1-3.5B; 82cd0d7b6322bd28cd4e830fe675ddb6180ce36c | Apache-2.0; Subject to Apache conditions; generated originality still needs checking | 8.259 (selected weights) | 32 | [12, 24] | not_yet_integrated; নতুন actual inference নেই |
| sfxsmall — stabilityai/stable-audio-open-small; ea2772170fc06f80dfd02bea6e57a44d9d4bc9d3 | Stability AI Community License, 2024-07-05; Conditional limited commercial license: registration required; revenue/affiliate threshold and attribution/use restrictions apply. Owner eligibility and acceptance unverified; no account or agreement action authorized. | 1.677 (selected weights) | 16 | [4, 8] | not_yet_integrated; নতুন actual inference নেই |
| legacy4 — Qwen/Qwen3-4B-Instruct-2507; qwen3:4b-instruct-2507-q4_K_M | ;  | Existing / not newly sized | — | — | legacy restricted; নতুন actual inference নেই |
| animate14 — Wan-AI/Wan2.2-Animate-14B; cb93a225fbaf1ca100f54e79da8f994995b689b3 | apache-2.0; Publisher license metadata only; exact access/component terms must be reviewed and owner-approved before use | 39.668 (selected weights) | 128 | [80, 80] | research_only_not_integrated; নতুন actual inference নেই |
| gemma4e4 — google/gemma-4-E4B-it; 4ecc2ba63bcac23ba4a767fc87025b1450f84c9c | apache-2.0; Apache-2.0 subject to its conditions; no stronger Bengali quality established | 15.993 (selected weights) | 32 | [16, 24] | research_only_not_integrated; নতুন actual inference নেই |

Gemma4 E4B-it 4.5B effective / প্রায় 8B total including embeddings; text/image/audio input → text, speech generator নয়। নতুন হওয়া Bengali superiority-এর প্রমাণ নয়। FLUX/IndicParler/IndicF5-এর gated access/share-info এবং new terms acceptance বাকি। Gemma3-4B-এর পুরোনো consent Gemma3-12B-এর blanket consent নয়। LTX 0.9.5 custom OpenRAIL-M; SVD-XT ও Stable Audio Open Small-এর Community License-এ commercial registration/revenue eligibility যাচাই দরকার। Owner eligibility ধরে নেওয়া হয়নি।

## বাস্তব GPU benchmark-এর ন্যূনতম practical envelope

| Workload | ছোট পরীক্ষা ও published/estimated memory | সিদ্ধান্ত |
|---|---|---|
| SDXL image | 512/768/1024, batch1; 8–12 GiB planning; নতুন worker conservative 12 GiB gate | বাস্তব fit, speed, identity consistency এখনও মাপা হয়নি |
| Wan2.2 TI2V-5B | Official native 1280×704 example ≥24 GB with model offload, dtype conversion ও T5 CPU | বর্তমান Diffusers adapter-এ একই fit নিশ্চিত নয়; প্রথমে short canary ও peak memory মাপতে হবে |
| LTX-Video 0.9.5 | ছোট clip; 12–16 GiB planning, T5/host RAM বড় | Publisher minimum নয়; exact adapter measurement বাকি |
| SVD-XT | 25 frames, 1024×576; official Diffusers offload/chunking example under 8 GB | আমাদের full-component recipe/worker-এ measured fit নয়; text-conditioned acting নয় |
| Bengali TTS / audio | Parler/IndicF5 4–8 GiB planning; ACE3.5B 12–24; SFX4–8 | Parler current worker CPU-only; অন্য audio adapters এখনও বাকি |
| Wan Animate14B acting | 80 GB class conservative research envelope, host128 GiB; publisher minimum established নয় | common24GB station-এর scope-এর বাইরে; extra permission/implementation লাগবে |

**একটি practical shared first station-এর planning target: CUDA 24 GiB VRAM, host64 GiB RAM, phasewise200 GiB free SSD, এক pipeline এক সময়।** এটি verified minimum/সব model-এর fit guarantee নয়। সব full-precision candidate/dependency একসঙ্গে রাখলে 300–500 GB বা বেশি storage লাগতে পারে; phasewise cache পরিকল্পনা প্রয়োজন। বর্তমান host প্রায়9.73 GiB RAM, CUDA/Torch নেই; এই workstation-এ পুরো video benchmark চালানো সম্ভব নয়। কোনো GPU provision/rental করা হয়নি।

## এখন যা বাস্তবে implement হয়েছে

1. Existing Dashboard-এ ২০-agent audit এবং internal ProfessionalLab যুক্ত: hypothesis, expected change, exact approved installed model identity, queued-run prebinding, per-trial call budget ও immutable case/input fingerprints। Existing role routing/local approved fallback রাখা হয়েছে; benchmark-এ অন্য model-এর fallback output সেই candidate-এর নামে count হয় না। কোনো নতুন production route winner বসানো হয়নি।
2. Raw model response, failure/partial response, settings, runtime evidence ও source hash সংরক্ষণ; simulation/JSON response artistic sample হিসেবে গ্রহণ হয় না। Media requires owned worker, actual-inference completion, model/checkpoint manifest identity ও genuine asset। Source/output/checkpoint বদলালে evidence/review stale।
3. Unchanged weak Qwen4B repeat blocked; সর্বোচ্চ দুই-call narrow schema/state/adapter fix retest-এর জন্য actual code SHA এবং explicit hypothesis দরকার। Token/runtime/call budget অতিক্রম করে অনুমতিহীন retry হয় না।
4. Prospective SDXL offline image worker: exact safetensors manifest, FP16 components, fixed local pipeline, no remote code, bounded subprocess, dimensions/PNG/hash verification। Weights/GPU না থাকায় preflight blocked; identity/pose/room-geometry control এখনও নেই।
5. Video/image/TTS owned workers-এ actual process peak RSS এবং available CUDA peak-memory telemetry; unmeasured values fabricated নয়। TTS seed/style/settings retained। PCM objective duration/peak/RMS/clipping/DC/quiet metrics যুক্ত; এগুলো pronunciation, LUFS, acting বা musicality বিচার করে না।
6. Required text/visual/listening expert review: named reviewer, expertise/independence owner attestation, exact quotation/image region/time anchors, all actual samples examined। Blind packet-এ unchanged output ও opaque IDs; separate admin model key। Reviewer পরিচয়/দক্ষতা software independently verify করে না; human review সম্পন্ন বলা হয়নি। Style থেকে model অনুমান সম্ভব।
7. Story3, Script8, Director10 text+3 clips, QC10 text+3 clips+3 audio; department-wise modality count এবং Video-তে Wan/LTX/SVD প্রত্যেকের ≥3 clip coverage enforced। Accepted benchmark-ও automatic general professional/production badge দেয় না।

## এখনও implementation/acceptance blocker

- Stronger writing weights ও compute approval pending। Qwen3.5-9B, Gemma3-12B, Gemma4E4B কোনোটি এই benchmark-এ tested নয়; role-wise selected model: **unselected for all20**। Existing approved local research configuration preserved, production winner নেই।
- Reference-controlled character/costume/location generation, VLM inspection adapter, performance-driven acting adapter, ACE music/SFX adapters, IndicF5 reference consent/custom-code review বাকি। Current Parler CPU-only; GPU estimate মানে implemented GPU worker নয়।
- Editing-এ existing deterministic renderer আছে; genuine approved upstream clips দিয়ে composite output-এর linked delivery/provenance receipt import এখনও বাকি। Laboratory media capture neural generation আর assembly আলাদা রাখে; assembly-কে neural intelligence বলা যাবে না।
- Bangladeshi Bengali independent screenwriter/dialogue editor, director/cinematographer, performance reviewer, voice listener, sound/music editor ও production specialist-এর বাস্তব evaluation বাকি। Auto critic বা owner checkbox একা artistic acceptance নয়।
- Long-season consistency, unseen genres, repeated-shot identity, usable emotional acting, dialogue intelligibility, sync, musical dramatic fit, full-scene cut ও recovery under real workloads সব প্রত্যক্ষভাবে পরীক্ষা করতে হবে।

## পরবর্তী approval-এর concrete scope — এখনও শুরু করা হয়নি

প্রথম candidate `qwen3.5:9b-q4_K_M` (Qwen/Qwen3.5-9B, Apache2), exact pinned manifest registry-তে; fresh full layer download **6,550,825,550 bytes (~6.55GB)**। Host16 GiB বা 8–12 GiB GPU planning, bounded4096 context, single loaded model; বর্তমান9.73GiB CPU host-এ fit/speed নিশ্চিত নয়। নতুন model/GPU/terms owner approval ছাড়া download/provision/accept হবে না। প্রথমে small runtime canary; সফল হলে identical original Bengali Story/Script/Director/QC cases, actual failure/runtime retained, blinded expert review। Gemma3-12B ~8.16GB pull এবং Gemma4E4B ~15.99GB selected BF16 weights পৃথক approval proposal; size alone winner নয়।

## Validation ও checkpoint evidence

- Full regression: **349 tests OK**, ~36.3s captured wall time; additional **8 standalone workflow checks passed**। এগুলো safety/software tests; cinematic/model capability pass নয়।
- New image preflight: blocked (weights/Torch/GPU unavailable); actual result preserved। New inference0 / independent reviews0।
- Development failures retained as notes: initial optional telemetry mock lacked CUDA attributes; speech seed mock lacked manual_seed; fixed mocks/optional telemetry then complete suite passed। Initial LTX license UTF-8 decode issue corrected with replacement decoding; original source hash retained।
- Evidence: [audit](verification/professional_readiness/audit.json), [environment](verification/professional_readiness/environment.json), [regression](verification/professional_readiness/regression.json), [standalone](verification/professional_readiness/standalone.json), [preflight](verification/professional_readiness/image_preflight.json), [suite](assets/professional/suite.json), [model registry](assets/professional/models.json)।
- Main unchanged at `c03550cb6facc27ba90c3f3286a5b0a0e69748a8`। Render read-only check: all3 services autoDeploy=no/trigger=off। No deployment/restart/production access, paid API, new cloud resource, license acceptance বা YouTube publish।

## Primary research sources

Model-specific primary HF links are attached below; exact commit revision and file SHA in registry. No third-party GPU estimates treated as verified minima.

- writer9: https://huggingface.co/Qwen/Qwen3.5-9B
- writer12: https://huggingface.co/google/gemma-3-12b-it
- vision7: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- sdxl: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- flux: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- wan: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers
- ltx: https://huggingface.co/Lightricks/LTX-Video-0.9.5
- svd: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt
- parler: https://huggingface.co/ai4bharat/indic-parler-tts
- indicf5: https://huggingface.co/ai4bharat/IndicF5
- music35: https://huggingface.co/ACE-Step/ACE-Step-v1-3.5B
- sfxsmall: https://huggingface.co/stabilityai/stable-audio-open-small
- animate14: https://huggingface.co/Wan-AI/Wan2.2-Animate-14B
- gemma4e4: https://huggingface.co/google/gemma-4-E4B-it
- Wan official memory recipe: https://github.com/Wan-Video/Wan2.2
- SVD official memory optimizations: https://huggingface.co/docs/diffusers/main/en/using-diffusers/svd
- Exact LTX0.9.5 license: https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.5.license.txt
- Exact SVD license: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/blob/main/LICENSE.md
- Exact Stable Audio small license: https://huggingface.co/stabilityai/stable-audio-open-small/blob/main/LICENSE
