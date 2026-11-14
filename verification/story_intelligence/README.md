# Story-only CPU preparation evidence

No selected-model inference occurred. Synthetic controls in `tests/test_story_quality.py` are mechanical authored data, not an original candidate story or expert evaluation.

Final scoped command (58 tests pass):

```sh
python -m unittest tests.test_story_quality tests.test_creative tests.test_staged_writing tests.test_intelligence.IntelligenceTests.test_unseen_medium_abstains_and_score_rejected tests.test_intelligence.IntelligenceTests.test_review_independence_staleness_and_invalid_values tests.test_professional_readiness.ProfessionalTests.test_binding_must_precede_inference_and_requires_approved_candidate tests.test_professional_readiness.ProfessionalTests.test_injected_simulation_is_not_real_inference tests.test_professional_readiness.ProfessionalTests.test_actual_review_needs_minimum_samples_exact_quotes_and_qualification tests.test_professional_readiness.ProfessionalTests.test_source_revision_or_raw_tampering_invalidates_review -v
```

These are engineering regressions, not rerun model experiments. The prior 351-test baseline is preserved, not re-counted as current verification. Final scope excludes YouTube tests. An initial 113-test shared regression accidentally included pre-existing all-agent authored fixture loops; its log is retained. No YouTube API, upload or publish operation occurred. One later test selection used the wrong unittest class name; the loader error is retained separately and the final command corrected it.

Fresh, non-overwriting CPU resume checkpoint:

```sh
python -m redpad_pipeline.story_quality --output work/story-gpu-resume-new
```

This emits preflight inventory, existing professional brief request, full output contract, proposed budget, canary request and per-section schemas. It never launches inference. A repeated output folder is rejected. The CLI's `artifact: null` is intentionally not a generated candidate.

Proposed budget, requiring future explicit authorization: one 384-token canary, one primary story assembled from five sections (foundation, three acts, final treatment/reflection), at most one targeted revision; seven calls including failures; each primary section at most 1536 output tokens / 4096 total context / 240 seconds, fixed selected NF4 model, no thinking, no automatic retry. Reflection follows supplied story beats; compilation does not repair or rewrite output. Cache/tokenizer feasibility remains unmeasured. Existing shared workers reload per request, so loading overhead must be included before approving GPU time. This proposal does not allocate or authorize GPU resources.

`require_runtime` deliberately blocks the new benchmark before writer construction. The existing general shared worker does not establish this benchmark's scoped owner authorization or verified kernel-isolation binding. An executable GPU-launch path is **not** claimed ready. On a suitable explicitly approved GPU, first validate those gates and exact local source/component/license receipts, then bind the staged section requests to the existing shared worker/Engine evidence ledger. Preserve raw output, prompt hashes, runtime/device/quantization/telemetry and failures. Never remove the gate merely because a GPU appears. No replacement model, CPU inference or hosted fallback.

Review via `Engine.quality_packet` and `Engine.record_quality_review` uses the 15 Story criteria and exact beat-specific quotations. Scores cannot come from missing inspection or self-review. `StoryBridge.queue_benchmark` handles source-bound fixtures/requests and owner-requested beat revisions. `queue_bible_handoff` transforms only current owner-approved benchmark artifacts into the existing Bible-stage contract; it does not run Script or Director.
