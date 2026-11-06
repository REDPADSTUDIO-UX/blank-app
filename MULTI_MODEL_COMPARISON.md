> Latest unified continuation: [Master Studio checkpoint](MASTER_STUDIO_CHECKPOINT.md). Earlier results below remain historical evidence.

# Phase 3 — multi-model comparison and role routing

Continuation parent: `c5fe3262d6e39e0bc3fe49ad107b72dd1deb7803`.
Owner/client research date: 2026-11-06. Feature branch only.

## Verified outcome and honest limits

The Studio now has configurable, digest-pinned local model routes for all 20
registered agents, with up to two explicitly approved local fallbacks. The
existing task/dependency/QC/owner workflows remain in place. Production selection
requires role-specific real benchmark evidence plus an explicitly attested
independent human acceptance. No candidate has been selected as a creative winner.

**New alternative-model inference calls: 0. New model downloads: 0.**
The restored execution workspace contains an older dirty development checkout;
it was preserved without reset or edits. Work continued in a separate checkout
of the latest remote parent. Neither the prior Ollama binary nor weights are
present in this environment. Historical installation success is NOT current
availability. Large candidate downloads await the owner's explicit approval.

## Models researched (not tested here)

Exact fresh-pull layer sizes and full manifest digests were retrieved directly
from the public Ollama registry, without downloading model weights. Layer bytes
include the config and all layers, including projector layers where present;
shared local blobs can reduce a later network transfer. Registry tags can change:
verify the approved digest again before downloading; do not silently substitute.

| Exact local variant | Fresh-pull bytes | License / commercial use | Estimated CPU RAM at 4096 context | Decision |
|---|---:|---|---|---|
| `gemma3:4b-it-q4_K_M` | 3,350,272,403 | Custom Gemma terms; commercial use subject to terms, restrictions and redistribution obligations | 5–7 GiB | First different-family candidate; owner approval pending |
| `qwen3.5:4b-q4_K_M` | 3,324,173,934 | Apache 2.0; commercial use subject to license conditions | 5–7 GiB | Newer-family candidate; owner approval pending |
| `qwen3:8b-q4_K_M` | 5,225,388,164 | Apache 2.0; commercial use subject to license conditions | 8–10 GiB | Stronger-size investigation only; defer near/exceeding host limit |
| `ministral-3:3b-instruct-2512-q4_K_M` | 2,953,840,808 | Apache 2.0; commercial use subject to license conditions | 5–7 GiB | Third-family diagnostic option; Bengali writing unverified |

RAM values are engineering planning estimates, **not measured minimums or vendor
guarantees**. The current host reports 9.73 GiB total RAM. CPU trials require no
GPU/VRAM (0 dedicated VRAM). Optional full-GPU allocation would need roughly the
listed RAM range with headroom, but is unmeasured and NOT authorized. Use one
loaded model and bounded context, monitor RSS, stop on pressure/OOM, and never
rent a GPU or create a resource. Runtime compatibility must pass preflight after
restoring the previously approved Ollama 0.40.15; it is not asserted in advance.

Qwen3-4B-Instruct-2507 Q4_K_M remains the historical control, not a winner. The
previous reports preserve 17 actual attempts at `7a6b1ed`, then 10 at `c5fe326`.
Those were different contracts/experiments and MUST NOT be relabeled as results
of this new equivalent-task suite. The old installation included 2,497,293,803
bytes of Qwen layers; restoring that control and runtime, if absent, adds network
traffic beyond the new-candidate total. The existing owner permission covers
that control; no automatic restore/download was performed in this continuation.

Other investigations:
- Gemma 4 E2B IT: Apache 2.0, 2.3B effective but 5.1B including embeddings; defer
  until exact artifact/runtime and memory budget are separately approved.
- Aya Expanse 8B: CC-BY-NC-4.0; excluded from the commercial production shortlist
  because commercial permission has not been established.
- Ministral's promoted language list does not establish Bengali screenplay quality.
- Larger/newer/faster is never treated as evidence of a better Bengali writer.

Primary sources (read for this research):
- https://ollama.com/library/gemma3:4b-it-q4_K_M
- https://ai.google.dev/gemma/terms
- https://blog.google/innovation-and-ai/technology/developers-tools/gemma-open-models/
- https://ollama.com/library/qwen3.5:4b-q4_K_M
- https://huggingface.co/Qwen/Qwen3.5-4B
- https://ollama.com/library/qwen3:8b-q4_K_M
- https://huggingface.co/Qwen/Qwen3-8B
- https://ollama.com/library/ministral-3:3b-instruct-2512-q4_K_M
- https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512
- https://huggingface.co/CohereLabs/aya-expanse-8b
- https://huggingface.co/google/gemma-4-E2B-it

## Identical Bengali benchmark prepared

Six original tasks cover all ten requested dimensions:

| Task | Assigned role | What is tested |
|---|---|---|
| `story` | Story | Original conflict, costly choice, causality, psychology, emotion, opening hook, earned ending |
| `romance` | Script | Responsive Bangladeshi speech, romantic tension, subtext, action before dialogue |
| `humor` | Script | Character habits, warmth and wit without insult or generic punchlines |
| `revision` | Script | Preserve locked s1, change only s2; grounded targeted revision and continuity |
| `criticism` | Director | Evidence-grounded dramatic criticism; seeded source defect and false-positive tracking |
| `qc` | QC | Independently answer the same source check; no self-approval or invented quote |

Every candidate receives the exact same task data, system prompt and schema for
each case. The suite has a version/content hash. Settings: CPU-only intended,
context 4096, output limit 1024 tokens, temperature 0.35, seed 42, streaming,
180-second budget per call. Model-specific sampling/template differences must be
reported rather than hidden. One explicit case per click; at most one explicit
retry after a stopped failure. No fallback during benchmarking, so a candidate
cannot inherit another model's output. Save unsuccessful replies too.

The seeded criticism test has one concrete umbrella continuity contradiction at
L3. Both logic and continuity descriptions can identify it; precision/recall
normalize that same defect. This is a narrow deterministic calibration and does
NOT establish general editorial judgment, semantic correctness of a suggestion,
or an independent human assessment. Human review must judge the prose itself.

After download approval, propose six tasks per candidate plus the same six for
the restored control. Three models = 18 initial calls, with a generation wall-time
budget up to 54 minutes before preflight/loading and explicit retries. CPU can be
slow; a complete JSON reply may still be poor writing. Do not expand the budget,
download more models or change compute without the applicable permission.

## Actual samples and findings currently available

Only the existing Qwen control has real archived Bengali creative outputs:

- `verification/phase3_cpu/BENGALI_SAMPLES.md` retains original baseline text.
- `verification/phase3_staged/` retains the next ten-call experiment and postchecks.
- `verification/phase3_grounded/scene.json` includes the literal fragment
  `তুমি যাবে, আমি অফিসে যাবো, ছাতা নিয়ে যাও।` inside a misattributed dialogue
  field. This is a recorded defect, not an accepted screenplay sample.
- Story inverted the characters' wants and skipped travel; dialogue sometimes
  narrated speech inside action fields, lacked organic wit and cut off mid-thought.
- Director cited source line IDs but still gave unjustified visual criticism.
- Staged calls completed 9/10 runtime replies (one truncation). Completion is
  separate from schema/continuity/editorial acceptance; see the earlier report.

No new writing samples exist for Gemma, Qwen3.5, Qwen8B or Ministral. Runtime,
failure rate and Director/QC accuracy for them are **unmeasured**, not zero.
No result from a unit-test fake is presented as actual model inference.

## Selection and Dashboard behavior

| Role | Selected production model | Supporting status |
|---|---|---|
| Story | None | Qwen baseline weak; alternatives not benchmarked |
| Script | None | Authentic dialogue/emotion/humor not accepted |
| Director | None | Judgment unreliable; grounding alone is insufficient |
| QC | None | No accepted role-specific independent benchmark |
| Other 16 roles | No automatic new assignment | Existing workflows retained; research routes configurable, relevant evidence still needed for production use |

The owner-only Dashboard can inspect local inventory, approve an already installed
model by full digest/license/owner confirmation, configure separate ordered routes,
revoke a model, run one benchmark case, export raw candidate evidence and export
stable metadata-blind packages. The administrator identity key is separate and
must be withheld from blind reviewers. The package includes task/source data and
blank ratings; self-identifying prose can still reveal a model, so metadata-blind
is the precise claim. No independent human reviews have occurred.

Production routes for Story/Script/Director/QC require complete actual matching
role-case records, unchanged request/raw hashes, model digest, suite/settings,
valid schema, seeded critic accuracy where applicable, and an owner-attested
independent human review with all ten dimensions, exact quotes and explicit
acceptance. Scores are never prefilled and no numeric auto-winner is computed.
Other roles need a relevant capability benchmark before production acceptance;
the software does not assume writing evidence validates video, speech or music.
A production model route never grants approval to an individual task artifact.

Execution uses a pinned policy snapshot per run. Runtime/unavailable-model errors
may try only the next installed owner-approved digest; invalid JSON/schema,
model-identity/digest change, revoked permission or bad creative content never
silently switches model. Every attempted model's raw text, error and evidence is
logged in the existing sidecar. Outputs and run history name the actual successful
model. The existing no-route single-model path is retained for compatibility.
No route can call a hosted/paid endpoint, pull models, or grant QC/owner approval.

## Remaining blockers and concrete approval proposal

1. Approve the two exact candidate variants/digests in
   `verification/model_comparison/registry_metadata.json`: Gemma3 4B and Qwen3.5 4B.
   Combined new layers: **6,674,446,337 bytes (~6.67 GB)** before any existing-model
   and runtime restoration. No new GPU environment proposed.
2. Restore the previously approved runtime/control as necessary, verify checksums,
   preflight local compatibility and measure actual RSS before each small trial.
3. Run identical tasks and retain actual failures/samples/latency; no winner now.
4. Obtain independent Bengali human review before final creative acceptance.
5. Commit subsequent verified results only to the existing feature branch.

No paid API, GPU rental, new cloud resource, Render deployment/restart, production
DB/media change, main merge or YouTube publishing occurred.

## Final software verification

291 regression tests passed, 0 failed, 0 skipped (39.010 seconds); all eight
standalone checks passed. Seventeen new tests cover route isolation, production
acceptance, revoked/mutated models, fallback identity/partials, actual-engine
integration, equivalent-task evidence, failed-run retention and Dashboard safety.
These tests use explicitly labeled fixtures/mocks and are not alternative-model
inference or artistic-quality results. Raw test evidence is in
`verification/model_comparison/tests.json` and `standalone.json`.
