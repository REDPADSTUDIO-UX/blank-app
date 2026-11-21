# Director, Story and Script — Creative Intelligence development

Date: 2026-11-06 (Asia/Dhaka). Baseline: 484c7746d8deefa119588bc99b1ead6e3b523a25.
Branch: feature/video-music-editing-studio. No Render deployment.

## Acceptance and limits

**Software Working**: three creative contracts, existing-engine handoffs, source validation, UI, revisions and attributed evaluation are implemented and tested.

**Model Connected / Real Inference Verified**: no. Host inspection found no Ollama executable/server, installed local models, Torch or CUDA device. The existing app dependencies were restored locally so regression/UI tests could run; no model weights or cloud resources were installed.

**Creative Evaluation Completed** applies only after a named reviewer supplies evidence-backed scores. No independent human creative ratings were collected here. **Human Review Pending** remains the creative status. Premium emotional intelligence, Bengali fluency and production quality are not proved by software tests.

## A — Director AI

Added a scene/episode analysis contract covering dramatic purpose, objectives, concealment, conflict, emotional change, subtext, humor category/reason, visual opportunity, restrained performance/intensity, pacing, transition, audience effect and narrative contribution. Reviews must cover every source scene/episode, quote actual source text, and direct actionable revision notes only to Story or Script.

Natural, witty, situational and emotional humor are distinct from forced humor and intentional absence of humor. These are review fields and model instructions; deterministic code does not understand whether a joke is genuinely funny. Director self-review cannot become independent QC or owner approval.

The existing Director planning/dispatch page remains available. The new creative review appears inside the same Director workspace.

## B — Story AI

Complete season planning supports 1–100 episodes (including 5/10/20/30). It requires logline, premise, conflict, season arc, character biographies/wants/needs/internal conflicts/relationship arcs, ordered episode objectives and escalation, reveals, payoff/ending links, production feasibility, setup/payoff schedules and continuity facts.

Software checks reject incomplete seasons, invalid episode numbering, payoffs before plants, duplicate characters/setup IDs and malformed metadata. Unexplained continuity changes and repeated causal statements produce targeted findings. These are explicit-data checks, not proof that the plot is original or emotionally convincing.

Research guidance reuses the existing attributed CC-BY Sintel excerpt and original curriculum notes. Source/license/status notes accompany story research; absent research is flagged. No protected screenplay collection or fine-tuning dataset was assembled. Retrieval/in-context coaching is explicitly not model training.

## C — Script AI

Added treatment, screenplay and targeted rewrite operations. Treatment forbids dialogue; screenplay reuses the existing Bangla, speaker, action-first and timing validators. Scene fields add numbered INT./EXT. headings, location/time, purpose, subtext, performance, transition, continuity, action and pause budgets. Episode endings have payoff, consequential question, next-episode connection, ending type and real setup-scene references.

Estimated durations support 180–4200 seconds; unit fixtures cover short episodes, 15/30-minute formats and 70-minute totals. They do not establish exact performed runtime. The five-minute example is deliberately identified as a timing/contract fixture, not a finished premium episode.

Targeted rewrites replace exactly selected scene IDs. An ending rewrite requires an explicit `__ending__` target. Other scenes and metadata remain unchanged; source hashes and diffs are exported. Existing immutable task versions and stale-source checks remain in force.

## Collaboration, provenance and evaluation

Existing agent engine path: approved Story architecture -> Director review -> Script -> Director second review -> independent QC recommendation -> requested revision -> owner approval. The implementation intentionally retains owner-approved source gates between departments. Script generation requires both approved season and Director-review artifacts; a fabricated literal source is rejected. Creative outputs never grant approval.

New creative operations are additive (`creative_v1`); legacy Director/Story/Script input contracts and other 17 departments remain intact. All production tasks, reviews and raw model responses stay in the separate agent sidecar.

The local adapter is still fixed-loopback, proxy-free, redirect-rejecting and without paid fallback. Creative calls use bounded 8192 context/output budgets with seed 42 and temperature 0.65. Original returned JSON, prompt hash, model identity and provenance are recorded before structural validation; successful real responses also record runtime/model metadata hash and timing/count metadata. An injected test provider is always simulation. Invalid or truncated responses are not promoted to accepted drafts. Very long season/script generations may need staged drafting on the eventual selected model; no long-context performance was verified here.

Eight evaluation weights total 100: logic/originality 15, emotion/psychology 15, Bengali dialogue 15, visual storytelling 10, hooks/endings 15, humor/warmth 10, continuity 10, pacing/feasibility 10. Scores require reviewer identity, human/model/simulation provenance, strengths, weaknesses, an exact draft quote and targeted improvement. The weighted result and deltas are computed; scores are never invented from field presence. Numerical score fixtures in tests are synthetic and are not artistic ratings.

## D — Model investigation

See `assets/writing/creative/model_candidates.json` for source URLs, licenses, weights/memory distinctions and limitations. Official documentation was checked for Qwen3-4B-Instruct-2507, Qwen3.5-2B, Gemma 4 E2B and Gemma 3 4B IT. Older Gemma 3 terms were not conflated with Gemma 4's Apache-2.0 card.

Provisional first trial: Qwen3 4B Instruct Q4_K_M, based on documented footprint and existing adapter compatibility. It is **not a measured Bengali quality winner**. Selected production model: **none**. Cross-model comparison: **Blocked — Real Model Prerequisite**. Future tests must use identical tasks, recorded model/configuration metadata and anonymized drafts with independent evidence-backed review; self-scores alone cannot select a winner.

## E — Bengali scenarios and evidence

`verification/creative/MANUAL_BENGALI_EXAMPLES.md` contains original manually authored fixtures, never labeled model-generated:

- A: five-episode family-romance architecture, plausible professional re-encounter and relationship boundaries.
- B: complete 30-episode horror outline with a planted key and scheduled payoff, plus Episode 1 fixture.
- C: approximately five-minute scene budget, visual hook, restrained dialogue, ending and setup references.
- D: deliberately weak dialogue-first/expository/coincidence/ending fixture repaired with supplied replacements. Structural failures are removed; independent proof of better humor/emotion is absent.
- E: three-episode continuity fixture; changing the key's location without an explanation produces a targeted episode-3 finding.

`verification/creative/evidence.json` records software outcomes, exact collaboration tasks/audit, and blocked local requests. Reproduce with `python -m tests.export_creative_evidence`.

## Tests

- Final full regression discovery: 181 passed, 0 failed, 0 skipped.
- New creative unit/UI tests: 15 passed (included in full count).
- Focused creative + legacy screenplay adapter tests: 24 passed (overlapping, not additive).
- Existing standalone suites: 8 passed: dashboard, production, quality, marketing, YouTube, private login, storyboard and production pipeline.
- First UI attempt was blocked by missing Streamlit in the refreshed environment. Existing requirements were installed and the UI tests then passed.
- Successful real AI inference tests: 0. Three configured-agent execution attempts blocked at missing-model prerequisite. Live runtime probe independently confirms the local server is unavailable.
- Model simulation: explicitly injected provider used only to verify raw-response storage and provenance.
- Human-reviewed creative results: 0. Artistic improvement scores: not assessed.
- Python compile and git whitespace checks passed. No real browser/Chromium test claimed; Streamlit AppTest was used.

## Protected state and next step

Only the feature branch is changed. Main remains c03550cb6facc27ba90c3f3286a5b0a0e69748a8. All three repository Render services had autoDeploy=no / trigger=off when checked before the checkpoint. No restart, deployment, migration, original database/media access, paid inference, GPU rental, billing, model training, cloud provisioning or YouTube action occurred.

Next step: make an approved compatible local runtime/model available, run identical A–E creative tasks, retain raw outputs and obtain independent Bengali editorial evaluation. Individual artistic optimization and production deployment do not automatically follow this software checkpoint.
