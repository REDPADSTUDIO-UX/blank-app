# REDPAD Phase 3 — approved local model comparison

Continuation parent: `c3eab18e75fb82d500f2236c2cae4c13b9c08373`.
Branch: `feature/video-music-editing-studio`. Owner authorization:
`verification/approved_comparison/owner_authorization.json`.

**Two approved alternatives were installed and genuinely tested on CPU. No model
has reached professional Bengali creative acceptance. No production winner or
independent human review is claimed.** The prior six-case Qwen3 baseline is
reused unchanged, not regenerated.

## Exact models, installation and resources

| Model | License / commercial use | Newly downloaded layer bytes | Execution |
|---|---|---:|---|
| Qwen3 4B Instruct 2507 Q4_K_M | Apache 2.0, subject to its conditions | 0 this continuation; existing control reused | CPU, previous six-case baseline |
| `gemma3:4b-it-q4_K_M` | Custom Gemma terms; commercial use subject to restrictions and distribution duties; owner consent recorded | 3,350,272,403 | CPU, six identical cases |
| `qwen3.5:4b-q4_K_M` | Apache 2.0, subject to its conditions | 3,324,173,934 | CPU, default and explicitly non-thinking arms |

Both registry manifests were pinned to the previously requested digests and
rechecked before pulling. Every downloaded blob was independently SHA256/size
verified. Installation JSON contains the exact digests. The total approved new
layers are 6,674,446,337 bytes, including projector/config/license layers; this
is not a claim about transfer overhead or actual loaded text-model memory.
No extra model variant was downloaded. Ollama 0.40.15, one loaded model at a
time, context 4096, output cap 1024, temperature .35, seed 42, 180-second call
budget, schema-constrained streaming. No paid/hosted fallback or GPU was used.

| Arm | Complete/schema-valid | Failed | Observed total seconds |
|---|---:|---:|---:|
| Existing Qwen3 baseline, reused | 6/6 | 0/6 | 214.350 |
| Gemma3 | 6/6 | 0/6 | 107.266 |
| Qwen3.5 default thinking | 0/6 | 6/6 | 678.910 |
| Qwen3.5 explicit thinking off | 6/6 | 0/6 | 195.485 |

Eighteen new actual calls: twelve complete/schema-valid, six retained token-limit
failures. The six older control calls are not counted as new inference.

Host RAM is approximately 9.73 GiB. Per-case files measure sampled aggregate
RSS of the controller and owned Ollama descendants, with shared pages possibly
counted twice. This is not PSS, minimum required RAM, or total host use. GPU VRAM
requirements were not measured. Previous 5–7 GiB planning estimates remain
estimates. See [runtime measurements](verification/approved_comparison/RUNTIME_COMPARISON.md).

## Demonstrated operational fix

All six Qwen3.5 default calls ended at `finish_reason=length`, each consuming
1024 generated tokens and returning empty final content. `/api/show` reports
thinking enabled by default. The original adapter ignored `message.thinking`,
so those original reasoning traces are missing and cannot be reconstructed;
empty final content, original requests, counters, errors and timings remain.
We infer that default thinking exhausted this small budget before a final answer.

Added optional, strictly boolean `think` control, runtime capability checks,
separate capture of runtime-generated thinking, mode-specific benchmark identity
and immutable stage fingerprints. The explicit `think:false` arm uses the same
six original briefs, system, schemas and sampling settings. It is separately
labeled, not silently substituted for failed default calls. The results establish
bounded-call behavior only, not general superiority of non-thinking models.

Dashboard research routes can pin the primary model's mode; the API supports
different modes per approved fallback. Production routes inherit each model's
accepted benchmark mode and reject conflicting execution overrides. Existing
20 agents, workflows, approvals and transport-only local fallback remain.

Saved evidence is visible even in a project with no active model authorization;
viewing it does not authorize inference. Archived failures cannot be reset in
the Dashboard. A real archive UI regression exposed a download/session-state key
collision; separate widget keys fix it.

## Creative findings — engineer assessment, not independent editorial review

| Task / dimensions | Actual observations |
|---|---|
| Story: originality, causality, motivation, emotional arc, hook/cliffhanger | Baseline garbles the costly choice. Gemma's “মায়ের চিকিৎসার জন্য নিজের কলেজের কিস্তি পরিশোধ করে দিল” contradicts the intended money dilemma, then invents an unearned admission cancellation. Qwen3.5 non-thinking changes the expense/illness outcome; its window-looking ending does not supply a consequential unresolved choice. The original Bengali brief also has a potentially ambiguous family reference; no model superiority is inferred from that ambiguity. |
| Romance / psychology / cinematic action | Gemma puts third-person narration in dialogue slots, with stray Chinese `试图`. Qwen3.5 mixes speaker attributions, reverses the requested reply roles, and puts quoted speech in closing action. Baseline inserts an unrelated golden-vessel image. No demonstrated professional romantic chemistry. |
| Natural Bangladeshi dialogue / character humor | Gemma's food exchange is more readable in fragments than the baseline, but generic; the mother describes “তোমার মায়ের হাতের খাবার” in an awkward third person. Qwen3.5's “বেশি চর্বি করবো তোমার জন্য” is unnatural and closing action contains dialogue. No validated witty exchange. |
| Targeted revision / episode continuity | Gemma copies both original lines unchanged; Qwen3.5 retains the father's original “আমি তোমার জন্য সব করেছি।” Both emit only the requested s2 object, but structural targeting alone does not mean the revision instruction was followed. Episode-length continuity is untested by these microtasks. |
| Director / QC accuracy | Exact per-arm TP/FP/FN and precision/recall are in the runtime report and summary JSON. These check strict line/category matching against one seeded umbrella contradiction; they do not certify semantic accuracy, editorial remedies or general dramatic intelligence. Gemma QC misses the expected defect label and adds three unmatched findings. Qwen3.5 Director adds unsupported objections about clear destinations and ordinary fare counting. Qwen3.5 QC does mention the bag/umbrella contradiction under L2/motivation, which this strict scorer marks unmatched rather than L3/continuity; treating that as wholly unrelated prose would be misleading. Its semantic partial credit requires independent adjudication. |

Full original outputs, not rewritten examples, are in each model's case JSON and
the blind review package. JSON/schema acceptance is explicitly separate from
creative acceptance. Faster complete output is not a winning screenplay.

## Role selection and human status

| Agent | Production selection | Reason |
|---|---|---|
| Story | None | Causal and earned-ending quality remains unacceptable/unreviewed |
| Script | None | Dialogue, role attribution, humor and revision defects remain |
| Director | None | False positives or weak remedies; narrow seed success is insufficient |
| QC | None | Inconsistent error detection; no independent human acceptance |

There is no automatic winner or production promotion. The dashboard supports
separate approved local models and safe local fallback per role; routes are
configurable without forcing all departments through one model. Research-use
installation consent is not artistic approval. Existing stronger-model research
remains in `MULTI_MODEL_COMPARISON.md` and `WRITING_MODEL_COMPARISON_PLAN.md`;
Qwen3 8B, Ministral 3 and newer Gemma variants remain untested here. Any further
large download needs a new exact variant/size/resource/license approval.

The [blind package](verification/approved_comparison/BLIND_REVIEW.md) has anonymous
candidate IDs, identical original tasks and unchanged outputs, with blank reviewer
fields. Withhold `blind-administrator-key.json` from reviewers. Human participants,
ratings and artistic sign-off: **none recorded**. Metadata blinding cannot conceal
every stylistic clue. One sample per category cannot support statistical ranking.

## Evidence and remaining blockers

Final full regression: **319 tests passed, zero failures/skips, 36.490 seconds**.
All **8 standalone checks passed**. Final archive Dashboard coverage includes
projects with active approvals and projects without any active model approval.
All 24 archived case records across the four arms pass the exporter's request,
raw-response and model-digest integrity checks; complete records also pass their
original JSON schema. No creative acceptance is inferred from these checks.

- `verification/approved_comparison/summary.json`: real case status, timing,
  sampling, digests, narrow critic metrics, limitations and null role selections.
- `regression.json`, `standalone.json`, `development_checks.json`: actual test
  results, including corrected development-time failures. These are software
  tests; synthetic fixtures are not represented as creative/media inference.
- CPU load was not isolated: some regression activity overlapped default-arm
  inference. Treat timing as observed performance, not a controlled speed ranking.
- Existing-free-GPU readiness remains unverified. Initial Kaggle settings
  navigation reached login; later observation was blocked by automatic approval
  review because it could observe a private Google origin outside the Kaggle-only
  authorization. No bypass, new account, terms acceptance, GPU session or resource
  activation occurred. Quota, GPU type and VRAM remain unknown.
- Independent Bengali editorial review, acceptable full scenes/episodes,
  30-episode staged completion, actual video/voice checkpoint approval and genuine
  media/listening/visual tests remain open. This milestone does not finish the
  entire autonomous Studio or label all 20 departments production-ready.
- Render auto-deploy was inspected as off. No main changes, Render deployment,
  restart/migration, production database/media access, YouTube publishing, paid
  API or new cloud resource occurred.

Primary technical/license sources checked for this continuation:
[Ollama thinking controls](https://docs.ollama.com/capabilities/thinking),
[Qwen3.5 model card](https://huggingface.co/Qwen/Qwen3.5-4B),
[Gemma terms](https://ai.google.dev/gemma/terms).
