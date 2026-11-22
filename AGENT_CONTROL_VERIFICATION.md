# 20-agent registration verification

Date: 2026-11-06 Asia/Dhaka (execution host UTC 2026-11-05).
Baseline: cce16c9f533f528168ebe22c511b7a45fae7a132.
Authorized branch: feature/video-music-editing-studio.

## Delivered

Exactly 20 stable, source-versioned agent identities and department responsibilities in agent_catalog.json; individual workspaces in the existing authenticated Streamlit dashboard. Independent local model identifiers persist across restarts. Configuration does not perform inference. No agents are reported Ready.

Separate agent_control.sqlite3 development sidecar: assignments, approved-version handoffs, output revisions, rejection/revision records, independent QC recommendations, explicit owner approval, transactional audit history and downloadable records. Existing production DB/media are not used by the new registry. Old pages and systems remain available.

Existing archive UI now handles absent episode plan files without crashing the entire dashboard. This was exposed by isolated regression fixtures. No archived content or media was altered.

## Executed evidence

- `python -m unittest tests.test_agents tests.test_agents_ui -v`: **7 tests passed**. Includes all 20 output contracts, dependency DAG, stable unique identities, independent configuration and restart, no network routing, stale/transitive handoff guards, targeted revisions, false inference rejection, QC self-review/Director bypass rejection, all 20 dashboard workspace selections, task/output/configuration controls and QC-to-owner review controls.
- `python -m unittest discover -s tests -p 'test_*.py'`: **125 tests passed** (includes six new contract tests; executed before adding the separate UI test). Existing Character Bible/quality, script, storyboard, media, marketing and YouTube unit/integration checks included. Offline/mocked provider tests are not real AI tests.
- Standalone existing checks: smoke_streamlit_ui, test_production_ui, test_drama_quality_ui, test_marketing_ui, test_youtube_ui, test_private_preview, test_storyboard and test_production_pipeline all passed. Initially missing archived fixture files crashed smoke/marketing/private preview; reruns passed after the guard. Drama quality UI was rerun as a module to resolve its existing direct-script import path assumption.
- Python compilation and `git diff --check`: passed.
- Chromium browser suite not executed: Playwright is absent. Streamlit AppTest exercised the dashboard instead.
- Actual model inference tests: **0**. Verified model-connected agents: **0**. Registered agents: **20**. Missing registrations: **0**.

## Security and remaining boundaries

Read-only Render inspection confirmed all three repository services have autoDeploy=no and autoDeployTrigger=off. Existing GitHub workflow contains test jobs only, no Render deployment action. Commit includes skip directives as an additional precaution. No Render mutation, deployment, restart, migration, paid calls, GPU rental, model downloads, YouTube upload or new resources were performed.

Main reference observed: c03550cb6facc27ba90c3f3286a5b0a0e69748a8. Only the authorized feature branch is updated. No live data backup or recovery verification is claimed; that remains a prerequisite to any future deployment.

Manual routing foundation only: department dependency maps are planning contracts, not an autonomous scheduler. Model configuration records identifiers only. Generic output envelopes need future agent-specific media validators. QC-authored task outputs cannot self-approve and remain blocked pending an independent reviewer policy. Actor strings are trusted in-process values supplied by the existing single-owner dashboard, not authentication credentials or a public API. Model agents must never receive direct owner review access in future integrations. Audit history is local transactional history, not a tamper-proof external ledger.

All future individual agent work remains pending. Begin with Director AI, then QC, Story, Script and Character only after owner instruction. See AGENT_DEVELOPMENT_ROADMAP.md for all 20 roles.
