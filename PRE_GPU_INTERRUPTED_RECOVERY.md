# Pre-GPU implementation — interrupted workspace recovery

**Historical interruption record — superseded by full workspace recovery.**

The complete implementation, original logs, authored outputs and labeled codec artifacts were recovered unchanged and saved at `b459290568a880da15a8c7dd4ad67eaf071782e8`. The formerly unfinished fixture-provenance guard is now implemented; see `verification/pre_gpu/fixture_provenance_retest.json` and `verification/pre_gpu/recovery_regression.json`. The record below describes the earlier outage and is retained as history. Current report: [PRE_GPU_COMPLETION_REPORT_BN.md](PRE_GPU_COMPLETION_REPORT_BN.md).

Base: e43bf25eefe95565c91a535fb84d4c18b41a5707.
Authorized branch: feature/video-music-editing-studio.
The development environment became unavailable before the full new workspace
could be read, committed or uploaded. Do not claim the full implementation or
raw evidence is present in this branch.

## What this recovery commit actually preserves

Ten independently recoverable source-file patches, reproduced with strict
single-match edits against the same e43bf25 base inspected at session start:

- AgentStore transaction connections close; current-source traversal memoizes
  approved DAG ancestors within one transaction and rejects cycles/stale refs.
- Explicit empty subtitles are accepted for silent shots; non-string subtitle
  fields still fail.
- LocalSpeechAdapter requires an explicit supported preset/style, uses the
  normalized pronunciation cue, preserves original speaker/transcript and does
  not pretend arbitrary pace/pause/reference controls are implemented.
- An OS-held, reentrant-within-one-owned-pipeline resource lease serializes local
  text, image, video, speech and legacy SVD entry points across projects.
- Engine blocks an additional local/media worker in the same project and reports
  global compute contention as a resource blocker requiring explicit retry.

These source changes were exercised in the expanded local workspace before
the outage. The reduced recovery tree has NOT been run again after recovery,
because there is no usable execution environment. This is not the complete
tree on which the expanded 368-test run was observed.

## Observed results before the outage

The tool results showed:

- Full expanded local suite: 368 tests in 67.164s, OK.
- Eight standalone workflow checks: all exit codes 0.
- An isolated original “ফিরতি টিকিট” project exercised all 20 roles through
  54 authored software stages, including 30 episode outlines.
- Separate tests exercised 30 bounded Director critiques followed by compilation,
  per-scene screenplay assembly and raw/source tampering rejection.
- Actual codec canary retained locally: 18-second assembly of gray frames and
  digital silence, 46,620 bytes. Input pattern: 2,033 bytes; PCM silence:
  32,044 bytes. These were NOT model-generated filmmaking assets.
- New actual model calls: 0. New actual human artistic reviews: 0.
- New weights, GPU resources, paid APIs, license acceptance and YouTube actions: 0.
- Main was c03550cb6facc27ba90c3f3286a5b0a0e69748a8.
- Read-only Render inspection found all three services autoDeploy=no,
  autoDeployTrigger=off.

The new raw logs, output JSON, source hash manifest and codec binaries could not
be retrieved after the outage. Counts above are observations from completed tool
responses, NOT a replacement raw-evidence bundle. No independent artistic
acceptance or professional readiness was established.

## Local implementation to recover before recreating work

Former root:
    /workspace/scratch/19aa449d4f91/studio-intelligence

Do not overwrite any surviving files. Inspect actual latest feature HEAD and
git status first. Preserve the older dirty “studio” checkout as well.

New modules written and exercised locally, but NOT included by this recovery:

- story_bridge.py: bible/arcs, one episode at a time, knowledge/state and
  setup/payoff validation, approved season/sequence bridge, ledger import.
- grounded_review.py: observation/interpretation/confidence/abstention,
  exact source quotations, clean/defect calibration and critic compilation.
- episode_scenes.py: bounded raw scene records, immutable draft versions,
  unchanged assembly, pinned source/sequence/time budgets.
- production_execution.py: shared approved shot specifications, exact voice
  segmentation/lexicon/preset binding, feedback, source-bound release preparation.
- delivery.py: genuine isolated asset receipts, actual duration/hash inspection,
  approved EDL binding, sequential two-decoder FFmpeg assembly and delivery receipt.
- audio_post.py: receipt-bound real PCM mixing, dialogue-window ducking,
  limiter and source recheck.
- offline_audio.py / audio_worker.py: prospective fixed offline ACE-Step v1
  and Stable Audio Open Small interfaces; no real compatibility/inference claim.
- offline_vision.py / vision_worker.py: prospective offline Qwen2.5-VL image
  criticism, source-frame extraction and original response evidence.
- pre_gpu_project.py / pre_gpu_acceptance.py: one original manually authored
  20-role/54-stage exercise and read-only resume verification.
- pre_gpu_ui.py: additions inside the existing three-primary-agent Dashboard.
- tests/test_pre_gpu_completion.py: 19 targeted functional/safety cases.
- Additional Engine, creative, ProfessionalLab and StudioProgram integration
  patches; these are NOT replaced by the reduced Engine patch in this commit.

Locally generated paths to inspect if the workspace returns:

- PRE_GPU_COMPLETION_REPORT_BN.md
- assets/pre_gpu/{owner_scope.md,writing_cases.json,review_controls.json}
- verification/pre_gpu/{acceptance.json,acceptance_artifacts.json,
  shot_execution_packets.json,episode1_screenplay.md,completion_matrix.json,
  gpu_human_handoff.json,regression.json,regression_initial_failed.json,
  standalone.json,targeted.log,environment.json,development_checks.json,
  reviewed_runtime_interfaces.json,resume_check.json,safety.json,manifest.json}
- verification/pre_gpu/codec_fixtures/
- phase3_runs/studio_program/pre-gpu-fixture-e43-completion/

All approvals in the authored exercise were explicitly SIMULATED SOFTWARE
FIXTURE actions; never relabel them as owner/expert artistic approval.
No weights were trained or new Bengali creative improvement demonstrated.

## Important unfinished final audit item

The outage occurred while attempting an additional fixture-taint correction.
That patch failed before it could read delivery.py; do NOT assume it applied.

Before shipping recovered delivery/audio code:
1. Require type(evaluation_only) is bool in Delivery.render.
2. Propagate evaluation_only/contains_fixture_inputs when importing a derived
   assembly receipt, so fixtures cannot be laundered into production provenance.
3. Mark an audio mix with fixture inputs as evaluation-only.
4. Add the corresponding rejection/taint assertions and rerun affected checks.

The current recovery does not publish those unrecovered modules.

## Recovery order

1. Restore access to the same workspace, locate and preserve surviving files.
2. Compare with this partial recovery commit; do not overwrite newer verified work.
3. Recover source/evidence hashes and apply the unfinished audit correction.
4. Run relevant tests, then the full required suite on the actual recovered tree.
5. Commit verified implementation and genuine evidence only to the feature branch.
6. Keep source-model/creative evaluation separate from software/fixture success.
7. Never run unchanged weak 4B generations merely to show progress.

If files are absent, use the original owner assignment (Pasted text(9).txt in this
conversation) and recorded implementation steps to reconstruct work in bounded
verified groups, committing each group before continuing. Do not claim an
unretrieved implementation was saved.

## Model/GPU/human handoff remains unchanged

The existing PROFESSIONAL_READINESS_REPORT.md and assets/professional/models.json
at e43bf25 retain exact candidate versions, sizes, license and planning memory
information. No production winner has been selected.

Primary candidates remain Qwen3.5-9B Q4_K_M (~6.55 GB complete layers),
Gemma3-12B-it Q4_K_M (~8.16 GB complete layers), Gemma4-E4B-it (15.99 GB selected
weights); none were newly downloaded or tested. Exact existing registry hashes
must be rechecked before any owner-approved installation.

A shared 24 GiB CUDA / 64 GiB host / phasewise 200 GiB free SSD station is an
unmeasured planning envelope, not a fit guarantee. Model-specific runtime,
component licenses, actual outputs, qualified Bengali editorial evaluation and
actual visual/listening review remain necessary. No new download/GPU/license
acceptance is authorized by this note.

Main, Render, production data, billing and YouTube must remain untouched.
No background work is promised after the session ends.
