# Story AI — Colab secure-worker compatibility checkpoint

১৬ নভেম্বর ২০২৬, Asia/Dhaka।

**COLAB ACCESS OR SECURITY BLOCKED; NO REAL INFERENCE.**

এখানে browser access **VERIFIED**; blocked অংশটি secure execution। Current Free Colab-এ
নতুন read-only hardware/kernel/cache metadata নেওয়া হয়েছে। আগের failed bubblewrap mount
test, অন্য agent বা কোনো successful benchmark পুনরায় চালানো হয়নি। নতুন story/model
generation, creative improvement বা professional readiness দাবি নেই।

## A–N সমাপ্তি রিপোর্ট

| Item | যাচাইকৃত ফল |
|---|---|
| A — GitHub | Remote feature HEAD `2dac998dd2786e684136ca80b77bbea748876a25` থেকে resume; final verified feature commit সমাপ্তির উত্তরে। `main` অক্ষত |
| B — Browser | Chrome extension কাজ করেছে; owner-এর existing saved Colab notebook authenticated অবস্থায় খোলা গেছে। পুরোনো VM connected ছিল না; normal Connect-এ current T4 পাওয়া গেছে। Notebook শেষে All changes saved |
| C — Resources | Tesla T4, 15360 MiB total / 14913 MiB free VRAM; host RAM 12.67 GiB total / 11.44 GiB available; disk প্রায় 112.54 GiB free। Python 3.13.16, Torch metadata 2.14.1+cu130; driver 580.82.07, compute capability 7.5। No tensor/model compatibility test |
| D — Secure blocker | পুরোনো executable dependency ঠিক করার পরও fresh `/proc` mount-এ permission denied। Current VM-এ bwrap অনুপস্থিত; mount capability আবার verified নয়। Existing Story-specific runtime binding/gate এখনও fail-closed |
| E — Equivalent path | কোনো security-equivalent alternative VERIFIED নয়। শুধু Python চলা, namespace creation বা offline flags যথেষ্ট নয় |
| F — Research notebook | Reproducible read-only notebook ও concrete Option C boundary packet প্রস্তুত; execution disabled। Changed security boundary-এর explicit owner authorization pending। Alternate inference launcher নেই |
| G — Model used | এই run-এ কোনো model ব্যবহার হয়নি। Primary exact Qwen3.5-27B অপরিবর্তিত। Approved 9B GGUF-এর পুরোনো অনুমোদন বহাল; পুনরায় তা চাওয়া হয়নি |
| H — Canary | নতুন canary ০। পুরোনো actual canary-র JSON/knowledge-boundary technical success reuse; সেটি convincing dramatic choice বা creative pass নয় |
| I — Complete story | অনুপস্থিত। পুরোনো foundation `finish_reason=length`, 1536-token truncated JSON; acts/reflection নেই। Missing prose বানানো হয়নি |
| J — Fifteen-criterion QC | নতুন complete candidate নেই, তাই নতুন creative assessment/grades দেওয়া হয়নি। পুরোনো partial-defect triage ও blank/missing-evidence status অপরিবর্তিত |
| K — Improvement | Measured before/after creative improvement নেই; targeted revision চালানো হয়নি |
| L — CPU QA | শুধু নতুন probe/boundary checkpoint-এর **৭টি distinct check pass**: প্রথম ৬টি, পরে নতুন notebook-pause check একবার। পুরোনো regression/benchmark rerun নয় |
| M — Human / owner | Independent qualified review ও artistic owner acceptance PENDING। Model authorization retained; Option C changed-boundary authorization আলাদা pending |
| N — Next action | নিরাপত্তা বজায় রেখে প্রয়োজনীয় provider-supported mount/Story binding verified করতে হবে, অথবা owner-কে পৃথক research-only boundary নিয়ে সিদ্ধান্ত দিতে হবে। এরপরও exact local bundle/hash/dependency ও remaining call-budget feasibility লাগে |

Current UI: **not subscribed, zero compute units**, resources offered free of charge।
“Up to 4 hours 10 minutes” session estimate; guaranteed quota বা remaining GPU hours নয়।
পুরোনো ১৫ নভেম্বরের GPU ফল current বলে চালানো হয়নি। বর্তমান probe শুধু metadata/filename/
size পড়েছে; real weights read/hash/load/download করেনি। Known approved GGUF cache roots-এ
model এবং installation receipt নেই; global/private-account cache অনুসন্ধান করা হয়নি।

## Root cause — dependency বনাম kernel policy বনাম application binding

Authoritative prior evidence:
`verification/story_isolation_20261115/execution_requirement.json`।

- **Executable:** আগের official Ubuntu `bubblewrap 0.9.0-1ubuntu0.3` install সফল। তাই পুরোনো
  failure শুধু “bwrap নেই” ছিল না। Fresh VM-এ সেটি এখন নেই; পুনঃইনস্টল করলেই kernel
  restriction মিটেছে বলা যাবে না। এই run-এ install হয়নি।
- **User/PID/network namespaces:** পূর্বের `unshare --user --map-root-user --pid --fork --net`
  এবং network-only commands return code 0 দিয়েছিল। User namespaces universally blocked—
  এমন দাবি ভুল হবে। এই successful checks আবার চালানো হয়নি।
- **Mount boundary:** architecture-required bwrap command-এর exact error:
  `bwrap: Can't mount proc on /newroot/proc: Permission denied`। এটি fresh proc mount denial;
  সব mount operation বা mount-namespace creation নিষিদ্ধ প্রমাণ নয়। Kernel/provider/LSM/
  seccomp-এর কোন নির্দিষ্ট rule দায়ী তা evidence থেকে আলাদা করা যায়নি।
- **Current kernel metadata:** `6.6.159+`; Seccomp mode 2, এক filter; LSM profile `kernel
  (enforce)`। CAP_SYS_ADMIN effective bit present হলেও তা unrestricted host capability,
  mount permission বা policy change প্রমাণ নয়। পুরোনো comparable metadata নেই; নতুন VM
  হওয়া একা failed privileged test rerun-এর justification নয়।
- **Network:** পূর্বে network namespace তৈরি হওয়া সম্পূর্ণ secure worker-এর প্রমাণ নয়।
  Localhost binding, environment offline flags বা Python audit hooks kernel egress isolation
  প্রতিস্থাপন করে না।
- **Filesystem/seccomp scope:** existing native supervisor user/PID/network namespaces,
  read-only root, temporary `/tmp`, fresh `/proc` এবং explicit writable output bind চায়।
  আলাদা dedicated `--seccomp` filter সেট করে না। Read-only `/` write আটকায়, কিন্তু সব readable
  host file থেকে confidentiality isolation প্রমাণ করে না; clean research environment জরুরি।
- **Story binding:** `story_quality.require_runtime()` এখনও unconditional fail-closed।
  Native six-role supervisor সরাসরি Story GGUF worker নয়। Generic shared text route বা
  পুরোনো standalone runner দিয়ে এই gate bypass করা হয়নি।
- **Lifecycle/evidence:** timeout, process-group cancellation, PID reuse protection,
  recovery, source fingerprints এবং immutable raw-evidence controls অপরিবর্তিত। আগের
  relevant CPU evidence reuse হয়েছে; model process চালিয়ে নতুন verification নয়।

এই audit browser failure-কে GPU/kernel failure বলে না। Browser এবং actual current GPU access
কাজ করেছে; required secure launch এখনও প্রমাণিত নয়। Unavailable/unknown capability-কে
বিশ্বের সব Colab runtime-এ অসম্ভব বলা হচ্ছে না।

## A / B / C / D সিদ্ধান্ত

| Option | সিদ্ধান্ত |
|---|---|
| A — unchanged Studio worker | BLOCKED / NOT VERIFIED: current dependency absent, required mount support এবং Story-specific secure binding verified নয় |
| B — equivalent restricted worker | NOT VERIFIED। Host `/proc` bind করা, `--proc`/PID isolation বাদ দেওয়া, hooks-only execution গ্রহণ করা নিষিদ্ধ। Same restricted mount লাগা unshare-only wrapper সমাধান নয়। Provider-supported অন্য sandbox/VM এখানে demonstrated নয় |
| C — separate research-only notebook | Boundary review packet প্রস্তুত; owner-এর নতুন explicit decision ছাড়া execute নয়। এটি Studio-equivalent security বা Studio production integration নয় |
| D — stop safely | এই checkpoint-এ কার্যকর সিদ্ধান্ত। সব বর্তমান observation/code/tests সংরক্ষণ; নতুন inference বন্ধ |

## Option C-তে owner-এর সামনে concrete proposal

একই আগে অনুমোদিত **`unsloth/Qwen3.5-9B-GGUF`**, revision
`3885219b6810b007914f3a7950a8d1b469d598a5`, file `Qwen3.5-9B-Q4_K_M.gguf`,
5,680,522,464 bytes, SHA256
`03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`।
পুরোনো reviewed llama binary hash/runtime receipt-ও বিদ্যমান evidence-তে আছে; current local
bytes/loader compatibility এখনও verified নয়। Primary `Qwen/Qwen3.5-27B` revision
`fc05daec18b0a78c049392ed2e771dde82bdf654` অপরিবর্তিত; T4-তে fit/tested দাবি নয়।

প্রস্তাবিত পৃথক boundary: owner-এর fresh research-only Colab, trusted exact local model/
runtime, শুধুমাত্র existing fictional Story brief, no Drive mount/production secrets/database/
private media, no hosted/public inference endpoint, no automatic downloads বা substitutions।
Original prompts, raw responses, finish reason, runtime/resource receipts ও hashes থাকবে;
research artifacts quarantined থাকবে। Studio import/QC/Director/owner gates বহাল থাকবে।

**এই boundary Studio worker-এর verified kernel PID/mount/network guarantees দেয় না।**
Offline flags/loopback/source hashes residual read/egress risk দূর করার প্রমাণ নয়। Owner-কে
এই সীমাবদ্ধতাসহ পৃথক research execution স্পষ্টভাবে অনুমোদন করতে হবে। JSON/boolean flag
নিজে অনুমোদন নয়। এই checkpoint-এ alternate launcher enable/implement করা হয়নি; তাই owner
decision-এর পরে concrete reviewed continuation এখনও দরকার।

## Budget ও incomplete Story-র বাস্তব সীমা

পুরোনো same benchmark evidence-তে দুই actual call আছে: narrow successful canary এবং failed
foundation। সাত-call ceiling conservative ভাবে ধরলে **পাঁচ slot অবশিষ্ট**। Fresh canary
এবং পাঁচটি নতুন section = ছয় call; পাঁচ slot-এ প্রতিশ্রুতি দেওয়া যাবে না। Eligible পুরোনো
evidence reuse/failed section-এর justified retry এবং overall budget review দরকার; ledger reset
করে failure লুকানো বা অনুমতি ছাড়া ceiling বাড়ানো হবে না।

পুরোনো foundation-এ repeated assumptions ও truncation-এর evidence আছে। তা থেকে নির্দিষ্ট
bounded correction hypothesis/retry বিবেচনা করা যায়; নতুন output ছাড়া improvement দাবি নয়।
Canary-র সরু schema pass পূর্ণ dramatic intelligence pass নয়। ১৫-criterion rubric,
StoryBridge → Story Evidence → independent QC → Director/Script → Owner path অপরিবর্তিত;
genuine full result না থাকায় নতুন end-to-end import/acceptance NOT TESTED।

## Deliverables ও preservation

- `experiments/story_colab_readonly.py`: standard-library metadata helper; no mount/unshare,
  installer/network/model execution path। Caller নিজে Colab account certify করতে পারে না।
- `tests/test_story_colab_readonly.py`: সাত new fixture safety checks; fake GPU metadata,
  tiny manual files, no model data।
- `verification/story_colab_compatibility_20261116/`: current raw stdout/JSON, browser free-tier
  observation, A–J security audit, A–D decisions, exact Option C proposal, CPU receipt,
  reproduction notebook এবং actual screenshots।
- `STORY_COLAB_READONLY_AND_BOUNDARY_REVIEW.ipynb`: reproducible **preflight + paused
  boundary review**, inference launcher নয়; outputs/counters খালি। Run-all থেকেও generation
  enabled হয় না। পুরোনো download/setup বা research runner স্বয়ংক্রিয় import নয়।
- ২৬টি protected Story/shared-worker/registry/schema/previous-result/report file baseline-এর
  সঙ্গে byte-identical; hashes `preservation.json`-এ। কোনো completed architecture পুনর্নির্মাণ নয়।

নতুন inference/download/unsafe model code/privileged isolation retry/paid service/Render/
production DB/media/YouTube/main changes **সব ০**। Kaggle বা অন্য provider এই task-এ খোলা হয়নি।
