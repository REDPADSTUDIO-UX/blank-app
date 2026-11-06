> Next continuation: [multi-model research and role routing](MULTI_MODEL_COMPARISON.md). Historical inference evidence below remains unchanged.

# Phase 3 — staged Bengali writing correction checkpoint

Continued from `7a6b1ed1b82e3fd82500da05b739f098c147cb95`, 2026-11-06.
Working branch: `feature/video-music-editing-studio` only.

**সফটওয়্যার guard উন্নত হয়েছে; গ্রহণযোগ্য creative উন্নতি প্রমাণিত হয়নি।**
বর্তমান Qwen দিয়ে বাস্তব retest হয়েছে। গল্পের motivation, সংলাপের অর্থ,
ইমোশন, স্বাভাবিক humor ও Director-এর বিচার এখনও নির্ভরযোগ্য নয়। Phase 3
বা স্বাধীন human editorial evaluation সম্পন্ন বলে দাবি করা হচ্ছে না।

## Implemented changes and scope

- LocalWriter accepts a JSON schema in Ollama's `format` field, also validates
  the reply locally, retains raw responses and records schema/wire-prompt hashes.
  Existing callers without a schema retain their previous transport behavior.
- A resumable development pilot splits work into character plan, three individual
  causal choices, one short scene and one Director review. Each stage has its own
  immutable request/dependency hashes, bounded output/time and at most one
  explicit retry. Failed parents and changed cached replies cannot propagate.
- Fixed goals are authoritative brief data, not model inventions: Rashed's own
  office attendance and Tania's own interview. Current plan schema binds each
  name to that goal and refuses to resume the observed inverted legacy plan.
- State checks reject remote prop transfer, transfer plus simultaneous travel,
  and location changes skipping the established route. These checks do NOT prove
  that the free Bengali prose agrees with the state ledger or has good causality.
- Scene validation requires an INT./EXT. heading, action first, known speakers
  and actual dialogue beats. After observing Qwen tag every utterance as action,
  the final pilot uses fixed action/reply slots. The protocol adapter preserves
  every generated text exactly. It rejects narrated speaker prefixes in reply
  fields and quoted speech hidden in action fields, rather than laundering them
  into valid dialogue. This remains a narrow, two-character home-scene pilot.
- New Director output references existing line IDs in a pinned source snapshot.
  Software supplies the exact evidence quote. A changed source invalidates the
  review; feedback is hypothetical and cannot automatically authorize a rewrite.
- Existing production Director validation now binds quotes to the **target**
  scene/episode; quoting another scene or global metadata is rejected. Production
  Story/Script/Director prompts also end with specific causal, dialect, responsive
  dialogue, visual-action and conservative editorial instructions.
- Existing Phase 3 Studio UI exposes one opt-in short stage at a time, raw export,
  an explicit failed-stage retry and an unreviewed blind package download.
  No production approvals or existing completed departments were replaced.

## Real CPU inference evidence

The already installed Ollama and `qwen3:4b-instruct-2507-q4_K_M` were reused.
No installation or additional model download was needed. Runtime allocation logs
show CPU buffers; no GPU resource was enabled. Buffer sizes are not a fresh peak
aggregate RSS measurement.

| Experiment | Role | Runtime completed | Tokens | Wall seconds | Saved result |
|---|---|---:|---:|---:|---|
| First plan | Story | No | 768 | 121.415 | Length termination; raw retained |
| Shorter plan | Story | Yes | 413 | 65.844 | Old shape passed; fixed goals later reject it |
| Beat 1 | Story | Yes | 297 | 56.721 | State check passes; motivation still wrong |
| Beat 2 | Story | Yes | 271 | 56.187 | Strengthened route check rejects it |
| Beat 3 | Story | Yes | 266 | 63.227 | Strengthened route check rejects it |
| First home scene | Script | Yes | 603 | 121.672 | Stronger heading/dialogue checks reject it |
| First review | Director | Yes | 401 | 66.715 | Exact line references; judgment unreliable |
| Brief-only scene | Script | Yes | 367 | 84.345 | Local schema rejected action-only dialogue |
| Compact-slot retry | Script | Yes | 277 | 67.073 | Old slot shape passed; final attribution checks reject it |
| Compact scene review | Director | Yes | 206 | 40.602 | Grounded line reference; judgment still unreliable |

**10 attempts: 9 complete runtime replies, 1 incomplete reply; 743.801 measured
wall seconds in total.** Eight passed the mechanical schema/checks available
when generated; that is NOT eight accepted creative drafts. The latest guards
were reapplied to the original replies without another model call; failures are
recorded in `verification/phase3_staged/postcheck.json`. The saved request in each
attempt records the exact schema/task used, including earlier weaker versions.
The complete but schema-rejected attempt is separate from the truncated attempt.

One initially truncated plan completed after shorter fields and a 1024-token
budget. All later runtime replies completed, but some strings stop mid-thought
inside otherwise complete JSON. Therefore JSON completion does not establish
finished prose, and no general timeout/truncation solution or speedup is claimed.
The tasks/budgets/constraints differ from the old checkpoint; this is diagnostic
comparison, not a controlled statistical quality win.

## Actual creative findings — assistant assessment, not human review

- Baseline Story had arbitrary umbrella denial and unexplained travel. The new
  plan instead assigns Tania a want to arrange Rashed's office attendance and
  Rashed a want to keep Tania at home. That violates the brief. Beat 2 sends her
  straight from home to interview while the action says she takes the umbrella
  and the state puts it on the table. Beat 3 returns her without travel. Merely
  adding cause IDs and motivation fields did not produce sound causal writing.
- The first new scene puts all dialogue in action fields, contains cut-off speech,
  a missing scene-heading prefix and artificial expressions such as
  `রাশেদ হাসি মানে বলে`. There is no accepted emotional/humor improvement.
- The brief-only retry has simpler fragments such as `তুমি যাবে, আমি অফিসে যাবো,
  ছাতা নিয়ে যাও।` However, the model places `তানিয়া বলে...` in the field assigned
  to Rashed's reply, and puts speech inside the closing action. The prop also
  changes from table to Tania's possession without an intervening visible action.
  It is not a validated playable scene or evidence of successful witty dialogue.
- Director no longer needs to invent a quoted string in the new protocol; quotes
  are copied from the cited source line. But it still falsely treats the umbrella
  as invisible merely because it is later put beside someone, and suggests
  unclear reactions. Grounding fixes attribution, not editorial intelligence.
  No Director instruction was applied as a rewrite.

## Tests, review package and remaining blockers

- Final full regression: **274 tests passed**, 0 failures, 0 skipped,
  33.534 seconds. This is 16 meaningful new tests beyond the 258-test checkpoint.
- All **8 standalone checks passed**. Existing simulated/synthetic media tests
  establish software behavior, not new neural acting, speech or cinematic quality.
- Evidence: `verification/phase3_staged/summary.json`, `tests.json`,
  `standalone.json`, `postcheck.json`, `runtime_reuse.json`, individual raw stage
  records, and `verification/phase3_grounded/` including rejected attempts.
- `blind_review.json` contains five anonymous candidates, the common brief,
  blank reviewer/ratings and comparison limitations. `blind_admin_mapping.json`
  is the separate administrator key; do not send that file to a blind reviewer.
  **No human has reviewed or scored these candidates.** No reviewer was contacted.
- `WRITING_MODEL_COMPARISON_PLAN.md` records official-source research and a
  resource-bounded, blind comparison protocol. No alternative model was downloaded
  or tested; no better-model claim is made. Approval is required before another
  large model download.
- Blockers: reliable causal/emotional writing, natural responsive Bengali and
  organic wit, trustworthy editorial judgment, and independent human evaluation.
  A fresh end-to-end six-stage creative run passing all strengthened guards and
  human review is still pending. No production-ready episode or artistic signoff.

No main change/merge, Render deployment/restart/migration, paid API, GPU rental,
new cloud resource or YouTube publishing. Existing production data was untouched.
The CPU server owned by each experiment was stopped on context exit.
