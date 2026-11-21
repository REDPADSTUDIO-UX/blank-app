# REDPAD Phase 3 — ২১-agent model integration ও Kaggle benchmark checkpoint

Baseline: `13f45f3a98bf8015e4a027909c97060a6b0da081`; branch: `feature/video-music-editing-studio`। তারিখ: ১২ নভেম্বর ২০২৬।

**Best Model Selection সম্পন্ন নয়। নতুন genuine GPU/model inference: ০; নতুন model-generated artistic media: ০; actual independent human review: ০; নির্বাচিত/production-verified নতুন model: ০।**

এই checkpoint-এ গবেষণার পাশাপাশি Engine-integrated prospective text/image worker, ২১-agent shared service contract, private Kaggle runtime notebook, resumable comparable Bengali benchmark queue এবং evidence/selection gates বাস্তবায়ন হয়েছে। কোনো model download, training, licence acceptance বা production promotion হয়নি। Dashboard/Casting-এর সম্পন্ন development পুনরায় করা বা redesign করা হয়নি।

## A. Kaggle access ও প্রকৃত environment

| বিষয় | প্রকৃত ফল |
|---|---|
| Owner Firefox session | Work browser connection চেষ্টা করা হয়েছে; originating browser context না থাকায় ব্যর্থ। Firefox session দেখা/লগইন যাচাই করা যায়নি। |
| Kaggle connector | Plugin search-এ কোনো matching connector ফেরত আসেনি; এটি সব সম্ভাব্য integration নেই এমন দাবি নয়। |
| Official API fallback | Official Kaggle CLI 2.2.5 ও SDK 0.1.38 আলাদা development environment-এ install ও source inspection হয়েছে। Standard token file/env/legacy credentials অনুপস্থিত। |
| Legitimate OAuth | Headless official flow browser verification code চায় এবং default `resources.admin:*` scope ব্যবহার করে। Secure handoff না থাকায় শুরু করা হয়নি; chat-এ code/password/token চাওয়া হয়নি। |
| Kaggle GPU/VRAM/RAM/storage | **Unknown** — account Notebook settings বা runtime খোলা যায়নি। Development host-এর GPU probe-এ `nvidia-smi` নেই; এটি Kaggle account-এ GPU নেই, তার প্রমাণ নয়। |
| Actual quota / session duration / Internet / libraries | **Unknown**। Documentation-এর সাধারণ quota/hardware owner-এর account value হিসেবে বসানো হয়নি। |
| GPU resource use | কোনো Kaggle session/GPU activate/reserve করা হয়নি। Paid/cloud fallback নেই। |

Access evidence: `verification/kaggle_model_selection/access_status.json`। দুটি **development-host** probe আলাদা JSON-এ; কোনোটি Kaggle resource report নয়।

## B. ২১-agent model selection matrix

নিচে **research priority**, নির্বাচিত winner নয়। সকল agent-এর current selection status: **Blocked — With Exact Reason**: Kaggle access/quota অজানা; নতুন exact model/license/download approvals এবং actual comparative output অনুপস্থিত। Existing Ollama history নতুন GPU evidence হিসেবে পুনর্লিখন করা হয়নি।

| Agent | Primary research candidate | Secondary / specialist candidates | Required capability |
|---|---|---|---|
| Director AI | Qwen/Qwen3.5-27B | Qwen/Qwen3.5-35B-A3B; Qwen/Qwen3.6-27B | Creative direction, grounded diagnosis, specialist delegation and independent visual review |
| Quality Control AI | Qwen/Qwen3.5-27B | Qwen/Qwen3.5-9B | Evidence-grounded criticism, calibrated abstention and deterministic checks |
| Story AI | Qwen/Qwen3.5-27B | google/gemma-3-27b-it; google/gemma-3-12b-it | Causal episodic story, character arcs, Bengali emotional narrative |
| Script AI | Qwen/Qwen3.5-27B | google/gemma-3-27b-it; Qwen/Qwen3.5-9B | Natural Bangladeshi dialogue, subtext, wit, visual scenes and exact rewrite |
| Character AI | Qwen/Qwen3.5-27B | black-forest-labs/FLUX.2-klein-4B | Psychology bible and consistent fictional identities |
| Art Director AI | black-forest-labs/FLUX.2-klein-4B | Qwen/Qwen3.5-27B; Tongyi-MAI/Z-Image-Turbo | Culturally grounded sets, props, palette and visual design |
| Location AI | black-forest-labs/FLUX.2-klein-4B | Qwen/Qwen3.5-27B | Reference locations and spatial/camera-access validation |
| Costume Designer AI | black-forest-labs/FLUX.2-klein-4B | Qwen/Qwen3.5-27B | Locked actor, costume/hair/makeup and chronological scene states |
| Storyboard AI | black-forest-labs/FLUX.2-klein-4B | Qwen/Qwen3.5-27B | Coverage, geography and visual continuity |
| Performance Director AI | Qwen/Qwen3.5-27B | Wan-AI/Wan2.2-Animate-2-14B | Playable acting intentions and actual performance assessment |
| Cinematographer AI | Qwen/Qwen3.5-27B | black-forest-labs/FLUX.2-klein-4B | Lens, light, blocking, screen direction and visual inspection |
| Motion & Physics AI | Wan-AI/Wan2.2-Animate-2-14B | Qwen/Qwen3.5-27B | Physical motion, interactions and temporal assessment |
| Video Generation AI | Wan-AI/Wan2.2-TI2V-5B-Diffusers | Lightricks/LTX-2.5; stabilityai/stable-video-diffusion-img2vid-xt | Native short cinematic clips; compare equivalent supported controls only |
| Voice & Dialogue AI | bodhan-ai/indic-speak | ai4bharat/IndicF5; ai4bharat/indic-parler-tts | Bengali intelligibility, accent, prosody, emotion and speaker continuity |
| Continuity Supervisor AI | Qwen/Qwen3.5-27B | black-forest-labs/FLUX.2-klein-4B | Cross-scene source/media state inspection; generator is not a critic |
| Music & SFX AI | ACE-Step/Ace-Step1.5 | stabilityai/stable-audio-open-small | Dramatic music fit, motivated SFX and listening evidence |
| Editing & VFX AI | Qwen/Qwen3.5-27B | Qwen/Qwen3.5-9B | Narrative edit guidance, actual receipt-bound FFmpeg assembly and A/V QC |
| Production Manager AI | Qwen/Qwen3.6-27B | Qwen/Qwen3.5-9B | Resource-aware scheduling, provenance, recovery and deterministic operations |
| Growth AI | Qwen/Qwen3.5-27B | black-forest-labs/FLUX.2-klein-4B | Truthful packaging and authorized measured analytics |
| YouTube AI | Qwen/Qwen3.5-9B | — | Read-only channel validation and local release preparation; never publish |
| Casting Director AI | Qwen/Qwen3.5-27B | black-forest-labs/FLUX.2-klein-4B; Wan-AI/Wan2.2-Animate-2-14B; bodhan-ai/indic-speak | Character fit, rights-authorized actor identity and actual acting/voice/chemistry evidence |

প্রতি agent-এর modalities, fallback rule, exact blocker ও unselected status machine-readable `assets/professional/phase3_candidates.json`-এ। একই model একাধিক role-এ research route হিসেবে reuse করা যায়; এতে independent QC বা Producer approval একীভূত হয় না।

## C. প্রকৃত benchmark ফল

| Evidence category | এই সেশনের ফল |
|---|---|
| Genuine Kaggle runtime canary | চালানো যায়নি; access unverified |
| Genuine model canary / Bengali writing output | ০ |
| Actual generated image / voice / music / video | ০ |
| Measured Kaggle generation speed / peak VRAM / model failure rate | নেই; denominator ০, 0% failure rate বলা যাবে না |
| Director/QC actual criticism accuracy | অজানা; কোনো নতুন model response নেই |
| New expert scores / artistic approval | নেই; কোনো score বানানো হয়নি |
| Software regression | Final result নিচের checkpoint section ও regression evidence-এ; creative quality-এর প্রমাণ নয় |

Source-controlled unseen test: `assets/professional/kaggle_bengali_cases.json`। কল্যাণপুরের রুবা–আদনান–সালমার নতুন original brief-এ ১১ task: premise, causal outline, natural dialogue/wit, emotional confrontation, written romantic chemistry, hook/cliffhanger, Director criticism, clean abstention, QC defect, targeted rewrite ও delegation। এগুলো **test specification**, AI output নয়। একই source, seed, context, token budget, temperature ও thinking setting দিয়ে পৃথক candidates চলবে; native rendered chat template-ও রাখা হবে।

Critic validation-এ planted objective defect, clean control, verbatim quotation, false positive/negative আলাদা। JSON success = artistic success নয়। Role-specific human comparison ছাড়া provisional winner নির্বাচন বন্ধ।

## D. Integration — কী আছে, কী যাচাই হয়নি

| অংশ | Implemented behavior | Genuine validation / blocker |
|---|---|
| Shared model services | Exact repo/revision, selected safetensors SHA256, tokenizer/config Git/LFS hashes, owner installation/license receipt, per-role development route, run snapshot, local-only loading | নতুন approved model installation নেই; inference unverified। Existing production route override নিষিদ্ধ। |
| Text worker | Fixed Qwen3.5/3.6 dense ও Gemma3 classes; NF4-on-load, FP16 compute; no remote code/download; bounded subprocess, raw response, rendered prompt, telemetry ও truncation/failure evidence | Prospective implementation; বাস্তব GPU class/API/numerics/quality যাচাই হয়নি। Giant generation budget নীরবে কমানো হয় না; staged bounded call লাগে। |
| FLUX.2 klein 4B / Z-Image worker | Fixed Diffusers classes, short native step budget; FLUX reference editing-এ current rights-authorized exact image IDs/versions; Z-Image text-only; stale references rejected | কোনো image তৈরি হয়নি। Identity/acting preservation প্রমাণিত নয়। FP16 fallback on non-BF16 hardware experimental/unverified। |
| Engine / Studio integration | Explicit shared development route থাকলে existing local Engine text path ব্যবহার করে; `shared_image` operation existing Character/Art/Location/Costume/Storyboard media path-এ যুক্ত | Model route কেবল consented exact installed checkpoint-এ configure করা যাবে। এই সেশনে কোনো real project/production route configure করা হয়নি। |
| Existing Wan / SVD / Parler / Stable Audio | আগের local adapters ও তাদের আলাদা approval ব্যবস্থা সংরক্ষিত | New shared profile binding/actual inference আলাদা pending; তাদের approval আগের evidence দিয়ে মিথ্যা পূরণ করা হয়নি। |
| LTX-2.5 / Animate-2 / Indic-Speak / IndicF5 / ACE-Step1.5 | Exact research profile, license/hardware requirement ও specialist contract | বর্তমান নতুন shared execution adapter নেই। পুরোনো LTX0.9.5/Animate14B/ACE3.5B-কে নতুন candidate বলে চালানো যাবে না। |
| Professional review | আগের ProfessionalLab ও feedback/QC gates অক্ষত। New writing comparison-এর actual samples/quotes + qualified independent human attestation ও explicit Producer decision পেলে provisional selection API | Writing comparison দিয়ে অন্যান্য বিভাগের visual/listening acceptance দেওয়া যায় না। Production promotion কখনো automatic নয়। |

Worker dependencies-এর prospective exact pins `experiments/kaggle_phase3/requirements.proposed.txt`-এ। এগুলো GPU-তে install/test করা হয়নি; Kaggle-এর torch/CUDA stack blindly replace করা যাবে না। Actual successful worker তার installed version ও telemetry লেখে। Kaggle permanent Render endpoint নয়; কোনো public server/tunnel বানানো হয়নি।

## E. Director multi-model architecture

Director-এর creative reasoning, coordination ও visual review আলাদা capability। Writing adapter text-only, যদিও Qwen publisher multimodal capability ঘোষণা করে। Text worker আছে বলেই visual/audio review যুক্ত হয়েছে বলা হয়নি। Approved shared model অন্য agent-ও reuse করতে পারে; prompt/source/task context পৃথক এবং casting identity/QC/Producer gates বহাল। Model-unavailable হলে shared benchmark fail closed; অন্য model-এর output primary model বলে চালানো হয় না। Existing digest-pinned Ollama fallback policy অপরিবর্তিত।

## F. Creative quality comparison ও selection

**কোন model বেশি ভালো লিখেছে, বলা যাচ্ছে না**—নতুন comparable raw sample নেই। কোনো বড়/newer model-কে শ্রেষ্ঠ ঘোষণা করা হয়নি। New selection guard পূর্ণ একই role-specific test set, matching model revision/settings/raw hashes, technical/grounded-critic pass, actual independent human findings/quotes এবং explicit Producer choice চায়। Accepted candidate-ও এই benchmark-এর provisional primary; ২১-agent professional/production acceptance আলাদা।

## G. Model / compute / license requirement

নিচের selected weights decimal GB। RAM/VRAM **unmeasured conservative engineering gate**, measured minimum নয়। Source configs/tokenizers/auxiliary models অতিরিক্ত; full repository inventory-র mutually exclusive weights একসঙ্গে download করার প্রস্তাব নয়। দুই T4-এর VRAM যোগ করে একটি বড় GPU ধরে নেওয়া নিষিদ্ধ।

| Exact repository | Selected weight GB | GPU GiB gate | Host RAM GiB gate | License / important condition |
|---|---:|---:|---:|---|
| Qwen/Qwen3.5-27B | 55.563 | 24 | 32 | Apache-2.0 obligations; no terms accepted here. |
| Qwen/Qwen3.5-35B-A3B | 71.904 | 32 | 64 | Apache-2.0; 3B active parameters do not mean 3B resident weights. |
| Qwen/Qwen3.6-27B | 55.563 | 24 | 32 | Apache-2.0; no Bengali superiority established. |
| Qwen/Qwen3.5-9B | 19.306 | 12 | 16 | Apache-2.0; native BF16 source quantized to NF4 only in memory. |
| google/gemma-3-27b-it | 54.865 | 24 | 48 | Gemma custom terms, use restrictions and explicit gated access acceptance required. |
| google/gemma-3-12b-it | 24.375 | 16 | 24 | Gemma custom terms and gated access acceptance required; not Apache-2.0. |
| black-forest-labs/FLUX.2-klein-4B | 15.964 | 16 | 24 | Apache-2.0; 4B distinguished from noncommercial 9B variants. Publisher mentions ~13GB VRAM; 16GiB is conservative unmeasured gate. |
| Tongyi-MAI/Z-Image-Turbo | 32.832 | 24 | 48 | Apache-2.0; text-to-image does not implement reference identity editing. |
| Wan-AI/Wan2.2-Animate-2-14B | 32.790 | 80 | 128 | Apache-2.0 base/distilled native checkpoints plus auxiliary components need exact audit. No old Animate substitution. |
| Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers | 45.921 | 64 | 96 | Apache-2.0; separately identified distilled Diffusers candidate, not silently substituted for native base. |
| Wan-AI/Wan2.2-TI2V-5B-Diffusers | 34.180 | 24 | 64 | Apache-2.0; existing Wan Diffusers recipe fit unmeasured; current BF16 worker requires capable GPU. |
| Lightricks/LTX-2.5 | 70.123 | 80 | 128 | LTX-2.x community terms: conditional free commercial use below entity/affiliate USD10m annual revenue; fine-tune transfer and components require review. Gated. NVFP4 needs Blackwell; Comfy int8 files are not PyTorch pipeline weights. |
| stabilityai/stable-video-diffusion-img2vid-xt | 4.509 | 12 | 32 | Stability Community terms, owner eligibility/registration/attribution and revenue conditions require review; no text prompt or acting control. |
| bodhan-ai/indic-speak | 7.069 | 12 | 24 | Indic Open Model License v1.0 plus Llama/SNAC/Vocos upstream audit. Self-hosting differs from serving others through an API; written permission/exceptions and scale thresholds apply. No cloning; style control preview quality. |
| ai4bharat/IndicF5 | 1.403 | 8 | 16 | MIT model metadata plus gated access, authorized voice reference/transcript and reviewed custom code required. |
| ai4bharat/indic-parler-tts | 3.751 | 8 | 16 | Apache-2.0 model metadata plus gated access. Existing preset worker; Bengali accent/emotion unverified. |
| ACE-Step/Ace-Step1.5 | 10.029 | 8 | 24 | MIT; ACE-Step 1.5 API/checkpoints differ from existing 3.5B worker. Component and generated-rights review required. |
| stabilityai/stable-audio-open-small | 1.677 | 8 | 16 | Stability Community license and gated access; entity eligibility and exact component terms require owner approval. |

পূর্ণ ৪০-character revision ও file bytes/hash: `assets/professional/phase3_candidates.json`; official metadata snapshot: `verification/kaggle_model_selection/official_metadata.json`। Public license file retrieval/hash ও inaccessible/gated status আলাদা নথিভুক্ত; ৬টি public license document পাওয়া গেছে। **সমস্ত custom/upstream licence eligibility বা owner acceptance সম্পন্ন দাবি নয়।**

বিশেষ সীমা: Wan TI2V 5B-এর publisher native offload example 24GB class হলেও বর্তমান Diffusers worker fit অমাপা। Native Animate-2 base weight file একাই ~32.790GB; auxiliary components অতিরিক্ত। LTX-2.5 selected distilled BF16 pack বড়; Comfy INT8 বা Blackwell NVFP4 file arbitrary PyTorch pipeline-এ ব্যবহার করা যাবে না। SVD-XT শুধু image-conditioned native video arm; text-directed acting model-এর সমতুল্য নয়।

### Consolidated download proposal — এখনো অনুমোদিত/শুরু নয়

Actual Kaggle GPU/RAM/disk/quota দেখা না পর্যন্ত এই proposal executable approval request নয়। প্রথম feasible shortlist হতে পারে নিচের তিনটি **ক্রমে, এক model at a time**। কোনটি fit করে এবং permitted session budget কত, তা মেপে owner-এর কাছে একইসঙ্গে exact approval চাইতে হবে।

| Candidate / exact revision | Transfer lower bound | Intended tests | Conditions / smaller alternative |
|---|---|---|
| Qwen/Qwen3.5-9B; `c202236235762e1c871ad0ccb60c8ee5ba337b9a` | 19.329GB known selected weights/configs; extra transfer headroom | Identical Bengali writing/Director/QC tasks, tiny canary first | NF4 runtime original full weights download কমায় না। Existing registry-তে Ollama Q4 alternative ~6.551GB আছে; সেটি আলাদা artifact/approval এবং এই benchmark-এ silently ব্যবহার করা হয়নি। |
| google/gemma-3-12b-it; `96b6f1eccf38110c56df3a15bffe176da04bfd80` | 24.414GB known selected weights/configs; extra transfer headroom | Identical Bengali writing/Director/QC tasks, tiny canary first | Gemma gate/terms owner acceptance দরকার। Ollama Q4 alternative ~8.164GB আগের research snapshot-এ; নতুন artifact approval ও measured GPU preflight আলাদা। |
| black-forest-labs/FLUX.2-klein-4B; `e7b7dc27f91deacad38e78976d1f2b499d76a294` | 15.980GB known selected weights/configs; extra transfer headroom | Fictional adult identity, angles/light/costume continuity; no acting claim | Apache-2.0 4B variant; actual multi-reference images এবং rights authorization দরকার। Z-Image Turbo reference-edit substitute নয়। |

একটিও download এখন চালানো হয়নি। 27B/35B, gated licence, LTX/Animate/audio bundles-এর জন্য পৃথক অনুমোদন ছাড়া resource ব্যয় হবে না। Actual quota/model timing না থাকায় workload-এর “কত ঘণ্টা লাগবে” নির্ভরযোগ্য অনুমান দেওয়া হয়নি; per-call upper bound 30–600s, preservation margin ও actual observed quota/session clock দিয়ে queue থামবে।

## H. Human review package

Blinded packet/export code আছে, কিন্তু নতুন বাস্তব samples **০**; তাই completed human review package বা artistic evaluation বলা যাবে না। Actual raw text এলে metadata-blind packet ও separate administrator key তৈরি হবে। Script review-তে exact quote, image review-তে actual image region এবং audio/video-তে time range ধরে আগের specialist evaluation চালাতে হবে। Reviewer identity/qualification software independently authenticate করে না; owner attestation আলাদা থাকে। Test fixtures/synthetic samples actual corpus-এ যায় না।

## I. Checkpoint, tests ও recovery

**আগের পূর্ণ regression: ৪১৮/৪১৮ tests PASS, ৩৮.৫৫৮ সেকেন্ড; তখনকার নতুন guard/integration tests: ২৫। Resume-এ অসম্পূর্ণ backend/retry validation শেষ হয়েছে: নতুন চারটি guard PASS। পূর্ণ suite পুনরায় চালানো হয়নি।** Final regression log ও source hashes `verification/kaggle_model_selection/`-এ। New tests শুধু safe integration/gates পরীক্ষা করেছে; simulated unit fixture-কে genuine AI output বা human review বলা হয়নি। আগের সফল creative outputs/benchmarks পুনরায় generate করা হয়নি; regression temporary fixture দিয়ে compatibility পরীক্ষা করেছে।

Recovery sequence:

1. Latest feature HEAD ও এই রিপোর্ট পড়ুন; Dashboard বা Casting redo করবেন না।
2. Owner-এর authenticated Kaggle tab-এর supported Work connection establish করুন। কোনো password/token/verification code chat-এ চাইবেন না।
3. Actual free accelerator, quota, RAM/VRAM/storage/session/Internet ও library versions মাপুন; generic documentation দিয়ে field পূরণ করবেন না।
4. Private runtime notebook, bounded tensor canary, separately approved installed model canary, saved private output থেকে verified retrieval—তারপর বড় benchmark। Default template GPU/Internet off।
5. Actual fit ও licence দেখে consolidated exact download permission নিন; তারপর identical tasks compare করুন। Running/failed job blindly restart নয়; investigate preserved evidence/new hypothesis।
6. Actual samples-এর owner/independent expert review নিন; তার আগে model winner বা professional readiness ঘোষণা নয়। Paid API/GPU, Render deploy বা YouTube operations করবেন না।

এই Work session বন্ধ হলে autonomous background continuation-এর প্রতিশ্রুতি নেই। Pending GPU experiments শুরুই হয়নি; কোনো idle GPU রাখা হয়নি।

## Sources

- Official repositories ও exact metadata URLs প্রতিটি profile/snapshot-এ রয়েছে। Model card advertisement আমাদের independently verified Bengali/visual quality নয়।
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md
- https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/auth.md
- https://huggingface.co/docs/transformers/model_doc/qwen3_5
- https://huggingface.co/docs/bitsandbytes/installation

Safety: শুধু feature branch; main unchanged; production DB/media untouched; no Render deploy/restart/migration, paid API/GPU/billing, public inference endpoint, licence acceptance, weight training, OAuth escalation বা YouTube publishing।

## Resume verification — interrupted validation completed

- Remote feature HEAD was still `13f45f3a98bf8015e4a027909c97060a6b0da081`; previous Phase 3 source/evidence had survived locally but was not committed. Completed research/development and 418-test regression were not repeated.
- Remaining backend guard fixed: each run now pins Ollama/shared backend before execution. Adding/changing a route cannot silently change a retry's backend; prior Ollama snapshots and initial production-route preference are preserved.
- Four new targeted guards passed. Initial targeted run had three passes plus one test-harness error caused by replacing a class with a mock; the constructor spy was corrected and only that failed test was rerun successfully. Both original and retest logs are retained. No model/creative inference occurred.
- Final source hashes are in the resume manifest. The 418-test full-suite evidence describes the earlier pre-resume implementation; final guard additions have the separate focused evidence, not a claimed fresh full-suite run.
- Fresh browser connection check returned the same originating-context error. Standard API token/legacy credential checks record presence only; no secrets were read or logged. Secure Kaggle access remains the exact blocker; GPU hardware/quota are still unknown.
