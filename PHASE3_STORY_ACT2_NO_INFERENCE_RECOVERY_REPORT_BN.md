# Story Act2 recovery checkpoint ও স্বাধীন অগ্রগতি

২১ নভেম্বর ২০২৬, Asia/Dhaka। Latest remote feature HEAD প্রথমে `a3d6252d2886827d7028ef328eff3fbf967901e4` যাচাই করা হয়েছে। এই checkpoint-এ GPU/inference/download **০**। মূল Budget11 ledger **9/11 consumed,2 remaining** অপরিবর্তিত। Foundation v2 ও Act1 v3 শুধু structural handoff-এর জন্য accepted; পুনরায় generate বা repair নয়।

## ১. সাতটি exact Act2 defect ও recovery requirement

| # | Beat/field | প্রকৃত ত্রুটি | নতুন generation input-এর শর্ত |
|---|---|---|---|
|1|B5 cause|B4 choice-এর prose লিখেছে; beat ID নয়|B1–B4 থেকে actual causal beat ID; ID valid হওয়ার পাশাপাশি অর্থপূর্ণ কারণ থাকতে হবে|
|2|B5 requires.H|TICKET_BOX_HIDDEN unknown knowledge|এটি B2 plant; H-এর প্রতিষ্ঠিত fact TICKET_HIDDEN। Fact/plant alias নয়|
|3|B6 cause|আবার prose|শুধু পূর্বের B1–B5 থেকে causal ID|
|4|B7 cause|B5.after state string|শুধু পূর্বের B1–B6 থেকে causal ID|
|5|B7 before|B5.after কপি করে B6-এর পরের state হারিয়েছে|নতুন output-এ ঠিক আগের beat.after আক্ষরিকভাবে কপি করতে হবে|
|6|B7 requires.H|একই plant-versus-fact ভুল|স্থির knowledge ledger মানতে হবে; কৃত্রিম learns যোগ করে pass নয়|
|7|B8 cause|B7.after prose|শুধু পূর্বের B1–B7 থেকে actual causal ID|

B5-এর entry state অপরিবর্তিত: `{"progress":"খাবার_হাতে,_মেয়ে_স্বপ্নে_আছে"}`। N-এর জানা facts JOB_RAJ ও তিন room fact; ticket কেনা/লুকানো এখনও অজানা। H জানেন TICKET_HIDDEN। Act1-এ কোনো learns নেই। B2-এর unresolved plant TICKET_BOX_HIDDEN আলাদা namespace। Discovery দেখানোর আগে N-এর secret reaction/required knowledge চলবে না; একই beat-এর learns দিয়ে আগের requires বৈধ করা যাবে না।

`act2_recovery_prompt_v1.json` সম্পূর্ণ versioned candidate এবং `prompt_before_after.md` exact addendum diff। শুধু addendum পরিবর্তন; original system/brief/prior context/schema/section instruction unchanged। N/H, B5–B8, causal ID ranges, immediate state copy, known fact/plant distinction ও plain Bengali নির্দেশ স্পষ্ট। মূল output বদলায়নি; নতুন beat/story বানিয়ে pass করানো হয়নি। Runtime-এ install বা call reserve হয়নি।

সাত finding-এর প্রকৃত values ও predecessor sources `diagnosis.json`-এ আছে। “বাতাসের_ধারে_প্লেট_হয়নি”, “প্লেটের_ঘর_কাঁচা_বেশেছে” coherent Bengali নয়। Actor N-এর consequence-এ “মেয়েকে_জানালেন” সম্পর্কগত অসংগতির hypothesis। Act1-এর frozen language দুর্বলতাও পরের context-এ রয়ে গেছে। এই prompt ভালো গল্প দেবে—এমন প্রমাণ নেই।

## ২. কী পরীক্ষা হয়েছে

১১টি JavaScript static/source comparison PASS: captured সাত finding-এর source projection, unchanged Foundation/Act1/failedAct2/ledger, only-addendum replacement, actual context-এর knowledge ও literal last_state match, fact/plant separation এবং no-submission। এটি Python guard/unit-test run বা model benchmark নয়। Selected development environment **UNAVAILABLE**; তাই নতুন Python tests, schema execution বা app verification দাবি নেই। পুরোনো successful tests/inference পুনরায় চালানো হয়নি।

Original2420 prompt tokens-এ output1536 মিলে3956 ছিল; new prompt6221 বনাম6109 character। Character length token-fit প্রমাণ করে না। Existing exact runtime/template দিয়ে <=4096 eligibility ভবিষ্যৎ preflight-এ পরীক্ষা করতে হবে; এখন **NOT MEASURED**। Limits4096/1536/240sec, seed117/temp0.7/repeat_penalty1.08/thinking=false অপরিবর্তিত।

## ৩. মূল আট-ধাপের source recovery — নামের পার্থক্য

`assets/phase3/master_scope.md`, SECTION18, lines1133–1140-এ মূল আটটি **readiness status** পাওয়া গেছে। এটি আলাদা আট-development-phase roadmap নয়। Feature tree1220entries,61 root Markdown,162 feature commit messages, master scopes ও GitHub issue/PR context inspect করা হয়েছে। আলাদা আট-development-phase তালিকা reviewed source-এ যাচাই হয়নি; কথোপকথনেই থাকা কোনো পুরোনো plan নেই—এমন প্রমাণও নয়। অজানা ধাপের নাম/সমাপ্তি বানানো হয়নি।

| মূল readiness ধাপ | প্রকৃত current evidence | বাকি dependency |
|---|---|---|
|1 Software Implemented|Recorded19/19 no-GPU engineering;21 registry retained; Director/Script পৃথক|Actual runtime-specific defect থাকলে তখন fix; duplicate engineering নয়|
|2 Model Configured|Pinned candidate/profile/routing আছে; winner নয়|Role-wise বাস্তব capability comparison ও review|
|3 Model Installed|এক approved research GGUF/runtime bundle আগে hash-verified|সব agent bundle/auxiliary/dependencies/licenses নেই; current VM এই no-inference task-এ probe নয়|
|4 Actual Inference Verified|Story/Director/Script/QC-এর কিছু research output; সব21 নয়|প্রতিটি role-এর নিজস্ব authorized model/output; StoryGGUF-কে YouTubeNF4 বলা যাবে না|
|5 Technical Output Validated|Foundation/Act1 PASS; Act2 handoff FAIL|Targeted Act2 recovery ও বাকি full-story checks; অন্য role-এর standalone validation স্বাধীন|
|6 Creative Quality Reviewed|Packets আছে; independent review PENDING|Qualified Bengali editorial ও actual visual/listening review|
|7 Owner Approved|Resources/structural prefix অনুমোদিত; artistic output approval নয়|Source-bound QC/Director ও actual owner artistic decision|
|8 Production Ready|Professionally accepted0/21|সকল runtime/media/rights/review/owner/E2E gate; deployment নিষিদ্ধ|

আরও দুটো আলাদা eight-item list `verification/intelligence/completion_20261115/sequential_evaluation_plan.json`-এ আছে: আট model batch এবং আট execution phase। পূর্ণ exact lists/dependencies `studio_eight_status_dependency_map.json`-এ preserved; primary27B batch, approved9B GGUF research ও YouTubeNF4 একই model/evidence নয়। Stages1–3 notebook হলো YouTube/Music/Voice benchmark sequence, Studio development phase নয়। Story Budget11/consumed9 কোনো stage number নয়।

Recorded development: Phase1 foundation/Director work এবং Phase2 StageA–D software history retained; Phase3 বাস্তব model/creative acceptance এখনও IN PROGRESS। Phase4 optimization শুরু হয়নি। আলাদা Phase5–8 নাম reviewed source দিয়ে যাচাই হয়নি। কোনো নতুন phase শুরু করা হয়নি।

## ৪. Story থেকে স্বাধীন কাজ—বাস্তবে কী এগিয়েছে

Existing `intelligence.qc.v1 / professional_qc_v1` review form/rubric reuse করে নতুন source-bound genuine-text diagnostic extension প্রস্তুত: `verification/intelligence/qc_handoff/story_budget11_diagnostic_v1/`। Q1-এ original Foundation/Act1 prefix, Q2-এ original Act2 continuation; raw strings অপরিবর্তিত। Reviewer packet, blank form/instructions ও আলাদা owner expectations রয়েছে। পুরোনো Story A/B packet বা QC engine পুনর্নির্মাণ নয়; নতুন actual failure evidence-এর QC handoff।

Q1 structural pass মানে clean artistic control নয়। Q2-এর সাত symbolic finding recorded truth; semantic criticisms preliminary, expert-adjudicated truth নয়। এটি balanced clean/defect বা full text10/video3/audio3 benchmark-এর বিকল্প নয়। No precision/recall, reviewer identity, score বা acceptance বানানো হয়নি।

Partial text-এর actual human QC inspection এবং existing Director/Script outputs-এর review, independent reference/consent preparation, standalone music/voice/visual evaluation preparation full Story success-এর জন্য অপেক্ষা করে না। কিন্তু new media/model inference-এর জন্য নিজস্ব exact bundle, rights, compute ও authorization লাগে; Story budget সেই অনুমতি নয়। Recorded Stages1–3-তে calls0; RAM/cache/isolation blockers পড়া হয়েছে, পুনরায় run করা হয়নি।

এই turn-এ সম্পন্ন স্বাধীন কাজ: QC source packet, factual structural expectations ও neutral blank review handoff। Current execution environment unavailable থাকায় app engineering/runtime test শুরু করা হয়নি; পুরোনো software পুনর্নির্মাণ নয়। Existing 21 agents, routing, schema, approvals ও production worker unchanged।

## ৫. পরের inference-এর আগে অনুমোদন ও eligibility

এই prompt **Act2 retry অনুমোদন করে না**। বাকি2 call শুধু Act3/Reflection-এর historical allocation। Act2 recovery+Act3+Reflection-এর জন্য অন্তত3 নতুন call দরকার: historical9 ধরে total অন্তত12 হবে, যদি প্রত্যেকটি প্রথম চেষ্টায় সফল হয়। Owner-এর explicit retry allocation এবং পূর্ণ completion চাইলে total12-এর scoped approval প্রয়োজন; **এখন ceiling11 বা কোনো ledger record বদলানো হয়নি**। বিকল্পে owner দুই remaining call reallocate করলে full story শেষ করা যাবে না—সেটিও আগাম স্পষ্ট হওয়া দরকার।

Approval পেলেও exact template token-fit, current Free T4/RAM/cache full hashes, immutable9-call history, original source/OptionC research boundary এবং নতুন unique reservation আগে যাচাই; তারপর original schema+unchanged handoff। ব্যর্থ হলে stop; automatic retry নয়। New model/download/license/paid resource approval এই checkpoint দেয় না। Human/Owner artistic acceptance এখনও PENDING।

No inference/GPU/download, no main/Render/deploy/production data/security bypass/YouTube changes। Safe feature commit শেষে remote SHA আলাদাভাবে যাচাই করা হবে।
