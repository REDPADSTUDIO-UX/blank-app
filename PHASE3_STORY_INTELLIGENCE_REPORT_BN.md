# Story AI — creative benchmark preparation ও runtime checkpoint

**Exact pinned Qwen3.5-27B এই session-এ চালানো হয়নি। কোনো actual candidate story তৈরি হয়নি।**
নতুন measured creative improvement, professional grade বা production readiness দাবি নেই।

Repository ও remote feature HEAD প্রথমে যাচাই: `REDPADSTUDIO-UX/blank-app`,
`feature/video-music-editing-studio`, baseline `6f5e3fda85710f0dd0a6d028c768de168f8915f1`।
Latest verified pushed commit SHA সমাপ্তির উত্তরে থাকবে। `main` modify/merge/push নয়।

## বাস্তব source পরিবর্তন

| ফাইল | কাজ |
|---|---|
| `assets/filmmaking/story_benchmark.json` | Existing `intelligence.story.v1` / `professional_story_v1`, exact selected model, Story instructions, research hypotheses, ১৫ anchored criteria, সাত adversarial specifications ও proposed bounded budget |
| `assets/filmmaking/story_benchmark.schema.json` | Three acts, ১২–১৬ beats, motivation/psychology, cause/state/knowledge, setup/payoff, emotion/humor, treatment/ending/filmability ও self-critique-এর strict versioned output contract |
| `redpad_pipeline/story_quality.py` | Existing Engine-এর Story-only extension: intake/validation, classified research, source-bound locks, exact-target revision comparison, review packet, lossless section assembly, approved Bible handoff, passive preflight ও non-overwriting CLI checkpoint |
| `redpad_pipeline/agent_engine.py` | Story request/result dispatch; selected benchmark runtime hard gate; exact system/prompt/input/output retention in existing ledgers; Story-specific quality packet ও independent review intake |
| `redpad_pipeline/story_bridge.py` | Existing Studio project-এর source-bound `queue_benchmark`; idempotency ও একই task-এ owner-requested revision |
| `redpad_pipeline/intelligence.py` | Optional Story benchmark rubric resolution; actual beat ID ও সেই beat-এর exact quotation যাচাই; অন্য role-এর default behavior বহাল |
| `tests/test_story_quality.py` | ২২টি authored CPU structural/safety/integration test; genuine inference নয় |
| `verification/story_intelligence/` | Preflight, canary/request/section schemas, research access results, scoped CPU logs, prior-evidence/preservation audit ও precise resume checkpoint |

নতুন model loader, agent registry, Story engine বা parallel database নেই। Existing task store,
Engine, StoryBridge, intelligence context, classified fact validation, professional brief,
creative attempt ledger, QC ও Producer approval guards reuse করা হয়েছে। অন্য agent-এর
capability development বা model benchmark করা হয়নি।

## Story intelligence ও deliverables

BRIEF → RESEARCH CONTEXT → PREMISE → CHARACTER MOTIVATIONS → CAUSAL BEATS →
EMOTIONAL ARC → STORY TREATMENT → SELF-CRITIQUE → INDEPENDENT QC →
TARGETED REVISION → OWNER REVIEW। Output-এ traceable deliverable hashes; pending QC/owner
review কখনো completed বলা হয় না। এটি model-এর private reasoning পড়া বা চিন্তাশক্তি মাপা নয়।

Central dramatic question, costly choice, wants/needs/fears/contradictions, relationship,
internal conflict, behavior ও emotional change explicit। Beat-এ actor, goal, choice, earlier
cause, consequence, visible action/location/sound, state before/after, required/new knowledge,
plants/payoffs, emotional investment এবং motivated humor থাকে। At least two subtle-emotion
moments, one humor opportunity, earlier setup থেকে earned reveal ও ordered তিন act লাগে।
Father-কে villain বা daughter-এর independence-কে selfishness ধরে লেখা নিষেধ; restrained action,
competing defensible motivations, escalating consequences ও meaningful ending চাওয়া হয়।

Technical checks unknown actor, forward causal reference, discontinuous state, unchanged state,
secret knowledge before disclosure, same-beat self-justified knowledge, unplanted/repeated payoff,
future emotional setup, duplicate IDs ও missing deliverables reject করে। Repeated choice,
missing emotional investment বা unmotivated humor structural findings হিসেবে চিহ্নিত হয়।
শুধু source quote বা metadata দিয়ে artistic quality প্রমাণ হয় না। A causal reference সত্যিই
বিশ্বাসযোগ্য কি না, humor হাসায় কি না বা emotion convincing কি না—স্বয়ংক্রিয়ভাবে জানা যায় না।

Research facts হলে exact current source hash/quote/attribution লাগে; interpretations,
assumptions ও proposals আলাদা। Source locks approved dependencies-এর exact paths থেকে resolve
হয়। Revision prior immutable artifact-এর exact target beats-এ সীমাবদ্ধ; অন্য beats, order,
character metadata বা treatment বদলালে reject। বৃহত্তর treatment revision চাইলে আলাদা explicit
scope দরকার। Existing Producer lock ও stale dependency rejection বহাল। Before/after hashes ও
technical findings তুলনা হয়; `measured_creative_improvement=null` থাকে human evidence না আসা পর্যন্ত।

## গবেষণা ও prior evidence

Fresh Banglapedia Film/Drama requests আবার proxy `403`-এ blocked। তাই নতুন storycraft principles
**authored hypotheses**, verified Bangladeshi cultural facts নয়। Existing allowed original craft
curriculum reuse; excluded/rights-uncertain source ingest নয়। Copyrighted script scrape, copied
plot, invented audience statistics/interview বা popularity ranking নেই।

আগের `PHASE3_APPROVED_GPU_WRITING_REPORT_BN.md` ও raw causal-outline evidence পর্যালোচনা:
Qwen 9B GGUF story sample structurally valid হলেও repeated beats, unearned knowledge এবং weak
agency ছিল; clean-control critique-এ false positive ছিল। Gemma dialogue sample-এর ভাষা/format
সমস্যাও আগে নথিভুক্ত। সেগুলো **selected Qwen3.5-27B NF4-এর ফল নয়** এবং নতুন session-এ rerun নয়।
Earlier CPU Story failure evidence-ও capability success হিসেবে নেওয়া হয়নি। Raw originals অক্ষত।
নতুন checks এই known failure classes লক্ষ্য করে; এগুলো model defect চিনতে/সংশোধন করতে পারে—এমন
নতুন বাস্তব পরীক্ষার দাবি করা হয়নি।

## Benchmark ও independent review

Original approved professional brief `ফিরতি টিকিট` অপরিবর্তিত: ঢাকার modest rental home,
নীরার অন্য জেলায় চাকরি, হাসানের outward support ও লুকানো একাকিত্বের ভয়। Primary artifact-এ
original logline, motivations, three acts, ১২–১৬ consequential beats, humor, subtle emotion,
escalation, reveal, ending ও filmability থাকতে হবে। Test fixture কোনো candidate story নয়।

সাত prepared adversarial case: A coincidence/lost payment; B secret knowledge;
C unsupported tragedy/forced emotion; D unrelated joke; E flat motivations;
F repetitive scenes; G owner-lock conflict। এগুলো specification ও authored software controls;
model adversarial pass count **০**। All seven expensive real generations শুরু করা হয়নি।

১৫ criteria: originality, causal logic, agency, psychological depth, relationship credibility,
emotional authenticity, organic humor, Bangladesh authenticity, hook/suspense, escalation,
setup/payoff, ending, filmability, consistency, audience-engagement hypothesis। প্রত্যেকটির
১/৩/৫ anchors ও exact beat evidence লাগে। Named reviewer inspection receipt, current source hash,
real beat ID এবং ঐ beat-এর quotation যাচাই হয়। Missing evidence-এ abstain; self-review independent
grade নয়। Technical validation, automated structural findings, human review ও owner acceptance
আলাদা। Independent qualified human reviewer **PENDING**; expert feedback বানানো হয়নি।

## GPU/model/cache preflight — read only

- Exposed queryable NVIDIA GPU: **নেই**; `nvidia-smi` tool/device পাওয়া যায়নি।
- Container memory limit: **৮ GiB**। Existing candidate planning gate **৩২ GiB host RAM** ও
  আনুমানিক **২৪ GiB GPU**; measured minimum বা fit guarantee নয়।
- Checked known workspace cache paths-এ exact snapshot পাওয়া যায়নি; global/private cache
  search বা weight read করা হয়নি। Known workspace-এ existing agent sidecar পাওয়া যায়নি;
  approved installation/license receipt প্রদর্শিত নয়। CLI-তে store না দিলে receipt status
  `null/not inspected`, fabricated absence claim নয়।
- Metadata-only check-এ torch, transformers, bitsandbytes, accelerate, safetensors পাওয়া যায়নি।
  GPU/model packages install বা import হয়নি।
- Kernel namespace identity পড়া হয়েছে; network isolation **verified নয়**। Session quota
  environment-এ exposed নয়; free GPU quota ব্যবহার বা GPU session activate করা হয়নি।
- Exact candidate: `Qwen/Qwen3.5-27B@fc05daec18b0a78c049392ed2e771dde82bdf654`,
  `hf_text_nf4`, proposed NF4 double quantization/FP16 compute; actual compatibility unverified।

## Executable resume checkpoint ও bounded scope

```sh
python -m redpad_pipeline.story_quality --output work/story-gpu-resume-new
```

এটি শুধু preflight, original request, schemas, canary ও proposed budget লেখে; inference করে না।
Existing output overwrite নিষিদ্ধ। Existing `StoryBridge.queue_benchmark`/Engine path software
artifact validate করতে পারে; genuine `local` benchmark writer তৈরির আগেই Blocked হয়।

Full metadata-rich story এক ১৫৩৬-token response-এ ধরবে ধরে নেওয়া হয়নি। Lossless assembly-র
five bounded sections প্রস্তুত: foundation, act 1, act 2, act 3, শেষে actual supplied beats-এর
reflection/treatment। কোনো prose repair, manual candidate substitution বা নতুন generation নেই।

**Proposed, not authorized:** এক ৩৮৪-token canary, এক primary story-এর পাঁচ section,
প্রয়োজনে এক targeted revision—সর্বোচ্চ **৭ calls including failures**। প্রতিটি primary section
≤১৫৩৬ output tokens, ≤৪০৯৬ context, ≤২৪০ seconds; এক selected model/এক Story evaluation;
no thinking, no automatic retry/substitution। Exact approved tokenizer দিয়ে প্রতিটি request-এর
feasibility এখনও যাচাই করতে হবে। Existing shared worker প্রতি call-এ reload করে; loading overhead
সহ budget পুনরায় পর্যালোচনা জরুরি। এটি সাতটি repeated story experiment নয়; এক story-এর bounded
sections। Truncation/context overflow হলে fail/stop, নিজে budget বাড়ানো নয়।

GPU-start-এর আগে এখনো বাকি: নির্দিষ্ট available GPU/resource/quota, approved exact bundle ও
component/source hashes/license receipts, dependency/precision compatibility, scoped owner
runtime authorization এবং verified kernel-isolated shared-worker binding। `require_runtime`
ইচ্ছাকৃত hard gate; **launch integration ready দাবি করা হয়নি**, এবং শুধু GPU উপস্থিত হলেই gate
সরানো যাবে না। Existing generic shared worker-কে authorization/isolation bypass হিসেবে ব্যবহার নয়।
এই gate future verified scoped runner-এর সঙ্গে bind করার পরই canary; authentic canary pass-এর
পর primary, তারপর grounded defects ও remaining authorized budget থাকলে targeted revision।

## CPU QA ও preservation

Final Story/support scoped run: **৫৮ tests pass, ০ failures/errors**। এর মধ্যে **২২ new Story tests**।
Compile এবং diff whitespace checks pass। আগের ৩৫১-test baseline artifacts/test files অপরিবর্তিত;
পুরো suite rerun করে unrelated work পুনরাবৃত্তি করা হয়নি। Prior evidence ও candidate/source locks
byte-preservation audit-এ সংরক্ষিত। Test count creative intelligence-এর প্রমাণ নয়।

প্রথম shared regression-এ ভুল করে pre-existing all-agent authored fixture loops অন্তর্ভুক্ত হয়েছিল,
যেখানে offline YouTube metadata fixture-ও ছিল। সেটি Story-only testing scope-এর বাইরে; final run
narrow করা হয়েছে। কোনো YouTube API, smoke workflow, upload বা publish চালানো হয়নি। সেই ১১৩-test
log রাখা হয়েছে। পরে এক test selector-এর ভুল class name loader error দিয়েছিল; final command-এ
সঠিক class নিয়ে pass। কোনো production safety gate শিথিল করে test pass করানো হয়নি।

## Status ও exact next action

| স্তর | অবস্থা |
|---|---|
| CPU-safe Story software preparation | Implemented and verified within the described scope |
| Selected-model runtime | **BLOCKED / NOT RUN** |
| Real generated story quality evaluation | **NOT PERFORMED** |
| Before/after measured creative improvement | **NOT MEASURED** |
| GPU time / VRAM telemetry | **Not measured; no GPU execution** |
| Independent qualified review | **PENDING** |
| Owner acceptance / professional readiness | **PENDING / NOT ACCEPTED** |

পরবর্তী কাজ: available GPU ও exact local bundle নির্ধারণ; metadata-only preflight ও source/rights
receipts যাচাই; cached tokenizer দিয়ে section budgets মেলানো; scoped authorization/isolation
binding সম্পন্ন করে owner-এর কাছে **সেই নির্দিষ্ট resource/model/maximum call budget**-এর অনুমোদন
নেওয়া। তারপর অনুমোদিত canary। এই session-এর নির্দেশকে সেই future GPU approval ধরা হয়নি।

কোনো GPU/CPU model inference, selected-weight download/load, alternate model/hosted generation,
paid resource/API, fine-tuning, Render deployment/restart/migration, production DB/media change,
YouTube publication বা `main` change হয়নি। নতুন actual story বা quality improvement দাবি নেই।
