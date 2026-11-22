# CPU software verification, not model evaluation

Baseline: ce9a235530f4a500482dbf056bbf8e03c5adcff8.

Use an isolated virtualenv and repository requirements. Exact focused command:

```sh
python -m unittest tests.test_intelligence tests.test_agents tests.test_agent_foundation tests.test_specialists tests.test_specialist_integration tests.test_no_gpu_staging tests.test_native_local_execution tests.test_selected_voice_binding tests.test_offline_11_preparation tests.test_offline_six_preparation tests.test_voice_casting_integration tests.test_professional_readiness tests.test_creative tests.test_staged_writing tests.test_director tests.test_agent_execution_ui -q
```

Tests use temporary sidecars, authored controls, mock workers and injected providers. No actual models or weights. Repeated runs are regression reruns, not independent creative trials. Logs retain failures and final corrections; fixture consent is never actual human consent.

Corrections: per-attempt snapshot compatibility with corrected-input retries; project-local installation of missing development dependencies; stale ACE native-worker assertion; one WAV fixture missing the existing explicit scoped-consent test helper; canonical intelligence profile hash shared between Engine and ProfessionalLab. Existing professional sample hashes were not migrated or altered.

`audit.json` records registry completeness and byte preservation of ten baseline components. `future_evaluation_queue.json` is a disabled plan using unchanged pinned candidates, not a list of executed jobs or installed models. `research_access.json` records blocked public-page requests; no fresh source verification claimed.

Trusted review intake is `Engine.record_quality_review`, separate from model output handling. `Engine.quality_packet` checks exact current source revision. `Engine.enqueue_targeted_revision` uses existing requested-revision state and dependency scheduler. Existing Producer guards still apply on save. Neither method grants owner approval. Modality receipts are named reviewer attestations, not automated perception or verified expert identities.
