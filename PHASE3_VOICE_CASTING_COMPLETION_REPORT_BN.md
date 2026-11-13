# REDPAD Phase 3 — Voice ও Casting offline engineering

১৩ নভেম্বর ২০২৬, বাংলাদেশ সময়। Remote feature HEAD
`c649d5f5f3f4c4de2e98722d70ad7821b2d7eb49` যাচাই করে সেখান থেকে কাজ হয়েছে।
এই রিপোর্টসহ পরবর্তী verified feature commit নতুন resume checkpoint।

**Engineering complete ১৮/১৯। Casting Director complete; Voice PARTIAL।**
Current selected candidate bindings-এর runtime **MODEL/GPU VALIDATION BLOCKED**;
creative status **HUMAN REVIEW PENDING**। Professionally accepted/production-ready
০/২১। আগের Qwen/Gemma evidence বা Director/Script checkpoints বদলায়নি।

## দুই agent-এর প্রকৃত ফল

**Casting Director — NO-GPU ENGINEERING COMPLETE।** Existing Character Bible, casting
proposal, portraits, voice/performance references, pair assessment, Voice handoff,
Director inspection, independent QC ও Producer identity-lock workflow যুক্ত। Missing
voice model/source হলে explicit abstention; অন্য candidate নিজে বেছে নেয় না। এই task-এর
Casting completion criterion অনুযায়ী unavailable Voice binding-কে সঠিকভাবে blocked
রাখা হয়েছে; এটি acting/voice/chemistry বা professional acceptance নয়।

**Voice — PARTIAL।** Existing Indic-Parler worker audition workflow-এ যুক্ত। Official
public Indic-Speak engine-এর reviewed local adapter ও safe codec loaders বাস্তবায়িত।
কিন্তু exact selected checkpoint-এর gated inference/token/speaker/decoder contract
যাচাই হয়নি। IndicF5-এর exact gated `model.py` loader-ও অপরিহার্য এবং unavailable।
এই নির্দিষ্ট selected loaders বন্ধ আছে। Public engine implementation-কে selected
checkpoint integration বা বাস্তব বাংলা voice capability বলা হয়নি।

## Source/access যাচাই — Chrome সংযুক্ত, repository agreement বাকি

Connected Chrome extension-এ existing Hugging Face session ব্যবহার করে দুই exact
revision-এর file-list preview দেখা গেছে। দুইটিতেই **Agree and access repository**
gate ছিল; code/file content access granted নয়। কোনো form পূরণ, agreement, CAPTCHA,
credential সংগ্রহ, gated-file retrieval বা bypass হয়নি।

| Selected candidate | Public official source | এখনও gated / minimum owner action |
|---|---|---|
| `bodhan-ai/indic-speak@76e0814f189321efe550011850cd288dae366aad` | `Bodhan-AI/bodhan_genai@62090c5e8f77588f1adb1dd745af1b9b8530dfb7` — native IndicTTSEngine, HF backend, tokenizer/template, SNAC/Vocos code | Selected `inference.py`, `voices.md`, `token_contract.md`, config/tokenizer metadata এবং matching Vocos source/config review বাকি। Owner license পড়ে Organization, Country, Intended Use দিয়ে নিজে agreement/request করবেন। HF email ও username publisher-এর সঙ্গে share হবে। |
| `ai4bharat/IndicF5@fb652a96e508091045890dae5bb99fe511facbcf` | `AI4Bharat/IndicF5@13f7c4d627cc10111aea8fe9c0039462cacacdc7` — README, generic local F5 inference utilities | Exact `model.py`, `config.json`, matching `f5_tts` ও vocabulary source বাকি। Owner নিজে repository agreement/contact-sharing review ও access দেবেন; তারপর code-only inspection। |
| Existing Indic-Parler | Existing selected profile ও `speech_worker.py` অপরিবর্তিত | Approved exact local model/component/license bundle ও actual listening validation বাকি; reference cloning অনুমান করা হয়নি। |

Public Indic-Speak source সরাসরি একই model repository নাম ব্যবহার করে, তবে selected
token/speaker equivalence প্রমাণ করে না। Model-card-এর preview-v2 example বা voice
name থেকে trained speaker ID বানাইনি। Public IndicF5 README এখনও gated custom loader
দেখায়; generic Gradio-র default আলাদা SWivid checkpoint, তাই সেটি substitute নয়।

১৪টি reviewed public file-এর exact Git blob SHA1 ও canonical SHA256 সংরক্ষিত:
`verification/voice_casting/public_source_metadata.json` এবং
`assets/professional/phase3_voice_public_source_lock.json`। Full source বা model weights
commit করিনি। Source access আর weight-download approval আলাদা; access পাওয়া গেলেও
এই task কোনো model download অনুমোদন করে না।

Owner access pages:
- https://huggingface.co/bodhan-ai/indic-speak/tree/76e0814f189321efe550011850cd288dae366aad
- https://huggingface.co/ai4bharat/IndicF5/tree/fb652a96e508091045890dae5bb99fe511facbcf

## বাস্তব source changes

- **`native_voice_worker.py`**: official public engine-এর constructor/injection seams,
  fixed local Llama/tokenizer loader, explicit local SNAC, bounded weights-only Vocos
  loading, no upstream automatic download/decoder fallback, original/NFC text ও mono
  PCM-16 WAV validation। Exact source gate model imports-এর আগেই বন্ধ করে। Tests শুধু
  injected fake classes/codec state; কোনো public upstream code বা real model চালানো হয়নি।
- **`voice_source_policy.py`**: public adapter বনাম selected binding আলাদা; repo/revision
  drift reject। Indic-Speak/IndicF5 selected loaders disabled। Parler explicit candidate
  হিসেবে reuse; missing primary থেকে silent fallback নয়। Unsupported pronunciation/
  emotion/style annotations selected engine-তে স্বয়ংক্রিয়ভাবে প্রয়োগ হয় না।
- **`voice_consent.py`**: actor, exact audio/document versions+hashes, transcript hash,
  intended use, task/revision ও named reviewer-সহ explicit owner-confirmed review
  declaration; revocation ও stale evidence checks। Document upload consent verification
  নয়; legal authenticity বা voice quality নিজে certify করে না। Model delegation দিয়ে
  consent grant করা যায় না। এই সেশনের records শুধু temporary software fixtures।
- **`casting_voice.py`**: existing agent store-এর একই casting tables/workflows থেকে
  immutable/idempotent audition drafts, approved Character identity, candidate/actor,
  pair/performance/voice assessment, read-only Voice task handoff ও native preparation।
  Assessment একই `casting_evaluations` store reuse; নতুন casting database নয়।
- **Existing Casting/Engine hooks**: Director packet-এ blocked voice/assessment status;
  voice plan বা evidence বদলালে inspection stale। Generic text/model execution audition
  task চালাতে পারে না—exact prepared native worker path লাগে। Existing independent QC,
  Director inspection ও Producer identity-lock controls অক্ষত।
- **Native result attachment**: exact prepared/run binding, real non-fixture supervisor
  result ও original WAV/hash থাকতে হবে। Missing/changed/unrelated/mock artifact reject;
  attachment-ও artistic acceptance নয়। Character/casting/revision/consent/assessment
  references staging এবং later inspection-এ revalidate হয়।
- **Privacy**: Voice/Casting native jobs-এর upstream stdout/traceback capture বন্ধ;
  safe typed status থাকে। Raw dialogue/reference evidence শুধু private local inputs ও
  provenance store-এ; diagnostic/event logs-এ actor audio/transcript লেখা হয় না।

একটি shared compatibility bug সংশোধিত: আগের upstream source artifact writer একটি
display newline যোগ করেছিল। ফলে ১৬টি expected source checksum আসল checkout bytes-এর
সঙ্গে মিলত না। Pinned revision-এর authoritative Git blob hash দিয়ে canonical bytes
মিলিয়ে checksum ঠিক হয়েছে। কোনো source revision/model/profile বদলায়নি; historical
retrieved-text receipts মুছিনি। Correction manifest আলাদা রাখা হয়েছে।

## CPU QA ও second-pass audit

**৩৭টি নতুন + ৯টি affected existing check = ৪৬টি distinct successful check।**
প্রথম run-এ ৩০টির ২৯টি pass, ১টি error: revision-এর output অনুপস্থিত হলে existing
Casting proposal reader `TypeError` দিচ্ছিল। এখন deterministic `AgentError`; শুধু ওই
failed check আবার pass। পরে new source/consent/assessment/security checks এবং affected
compatibility checks pass। Targeted rerun নতুন distinct test হিসেবে গোনা হয়নি।

Coverage: exact source/version gate, no generic model fallback, document-only consent
rejection, actor/transcript/task/revision spoofing, consent withdrawal, stale media,
Character-source integrity, persistent handoff, Director/QC/Producer controls, dummy
native result rejection, WAV constraints, safe codec config এবং source-lock correction।
Affected existing supervisor cancellation/environment privacy checks শুধু fixed CPU
dummy process দিয়ে হয়েছে; native model/MPI নয়। Other ১৭ agent ও Director/Script
records, ১৮ pinned profiles ও `models.json` preservation যাচাই হয়েছে।

Fresh environment-এর missing `requests`-এর জন্য import-only no-transport shim ব্যবহৃত;
package download বা HTTP transport validation নয়। GPU/model imports ও generation
paths guarded। Fixtures-এ tiny manual images, header-only video, PCM silence ও fake
tensor/class আছে—actual generated voice, model output বা human review নয়।

Second automated code-level audit আলাদা pass; একই assistant, independent human reviewer
নয়। Ordinary CPU-safe finding open নেই। Remaining exact Voice loader work genuinely
gated-source access/review-dependent; inference অনুপস্থিত বলে PARTIAL করা হয়নি।

## Final ১৯-agent readiness matrix

Runtime column-এর **BLOCKED = MODEL/GPU VALIDATION BLOCKED**। Creative column-এর
**PENDING = HUMAN REVIEW PENDING**। এগুলো current selected bindings-এর অবস্থা;
পূর্বের অন্য candidate benchmark evidence বাতিল বা পুনরায় চালানো হয়নি।

| Agent | Engineering | Runtime | Creative |
|---|---|---|---|
| QC | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Story | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Character | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Art Director | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Location | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Costume / Hair & Makeup | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Storyboard | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Performance | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Cinematographer | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Motion & Physics | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Video | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Voice | PARTIAL — exact gated selected source binding | BLOCKED | PENDING |
| Continuity | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Music & SFX | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Editing & VFX | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Production Manager | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Growth | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| YouTube Channel | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |
| Casting Director | NO-GPU ENGINEERING COMPLETE | BLOCKED | PENDING |

Machine-readable matrix: `verification/voice_casting/readiness_19.json`। Director ও
Script পৃথক unchanged workstreams। Professionally validated/production-ready ০/২১।

## Safety ও exact resume

GPU/CUDA execution, CPU/GPU model inference, real model-weight read/load/download,
hosted/paid inference, billing/new paid resource ও license acceptance **সব ০**। Main,
Render deployment/restart/migration, production SQLite/media ও YouTube অপরিবর্তিত।
Dashboard redesign বা Phase 4 হয়নি। অন্য ১৭ agent আবার develop/test/generate করা হয়নি;
shared changes শুধু justified source-lock/privacy/voice-handoff compatibility fixes।

পরবর্তী resume এই feature commit এবং `verification/voice_casting/access_blockers.json`
থেকে: owner নিজে দুই repository agreement/access শেষ করলে **শুধু exact gated code,
token/speaker/config/vocabulary/decoder review**। কোনো weights নয়। Matching local
binding verified হলে disabled loader/installation recipe পূরণ, affected CPU QA ও
১৯/১৯ audit। Runtime বা artistic completion দাবি নয়।

প্রথম separately authorized GPU checkpoint: kernel isolation এবং approved exact
local bundle/cache/dependency checks; তারপর **QC-এর bounded clean/seeded visual controls**।
আগের unresolved kernel-isolation failure এই সেশনে আবার চালানো হয়নি; GPU phase-এর
আগে owner hardware-এ verify করতে হবে। Voice পরে এক bounded fictional Bengali sample,
raw WAV/provenance, technical validation ও independent listening review; তারপর actual
Casting audition/pair review। Successful পুরোনো inference আবার নয়; automatic model
promotion বা publishing নয়।
