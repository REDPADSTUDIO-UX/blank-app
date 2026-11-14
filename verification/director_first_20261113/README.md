# Director-first continuation, 2026-11-13

Resumed verified remote feature checkpoint `7f665cbbb819a5cb62750d62740160fffed25eea`.
No prior successful model call was repeated. The two new Gemma controls test a
previously untested Director role, motivated by the owner's A-over-B preference
and Qwen's observed false accusation on the clean control. The preference is not
professional acceptance or a controlled model ranking.

## Evidence boundaries

- `gemma_*_raw.txt`: verbatim UI Copy message output, including Markdown fences.
- `*_request.json`: original synthetic benchmark inputs; no private film material.
- Hosted model reported as Gemma 3 12B IT; exact weights, serving revision,
  temperature, seed, context, GPU and memory are unknown. A Space name is not an
  attestation of an exact checkpoint or commercial deployment license.
- UI token input 1024; slider displayed 1020. Effective cap and finish reason are
  unknown. Completion in the UI does not prove absence of model truncation.
- Any fence-stripped JSON is a derived artifact, never a replacement for raw
  output. Content checks are distinct from strict protocol/technical acceptance.
- New generations used an existing free Hugging Face Space, not a production
  model route. No local download, paid API or QC/owner approval was inferred.
- Director plan's first JSON-formatted input was rejected as an invalid
  `text/plain` attachment; this is an interface failure, not model output.
  A sequential-entry attempt timed out after partial input. A plain-text input
  recovery is separately recorded; never count an unobserved submission as a
  successful generation.

## Revision guard

`revision_gap_before_fix.json` reproduces the old checkpoint accepting changed
wardrobe/door state despite a camera-only note, using disposable software fixtures.
The existing Director backend now accepts owner-authored `allowed_changes` JSON
pointers on `Request revision`, persists them in existing review events, includes
them in the generation prompt and checks them inside the write transaction.
Example: `allowed_changes=['/scenes/0/camera']`. All other fields are locked;
scene IDs and order are preserved for every revision. Rejected output creates no
plan. Accepted revisions still await independent QC and owner approval.

The existing Dashboard is unchanged. Its free-text review does not set structured
field locks; free-text scope cannot safely be inferred. Existing callers remain
compatible. This guard is software validation, not evidence that a model follows
direction or understands drama. No hosted response is relabeled local inference.

## Resume rule

Read `results.json` and the Bengali report before any further call. Do not repeat
these two completed controls. Inspect any interrupted input/submission before
retrying. When Colab actually grants free GPU, inspect cache first, use the
previously verified prebuilt runtime (not another CUDA source build), then run
only the next unexecuted Director cases under the existing professional suite.
That suite still requires ten text samples and three actual generated shots with
independent text/visual review. No professional selection is justified yet.
