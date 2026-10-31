# REDPAD AI Studio — Multi-Model Video Generation (beta)

GitHub branch: `feature/video-music-editing-studio`. Main remains untouched.

## What changed

The Video Studio > **AI Production** section now offers:

- **Automatic — lowest estimated cost:** resolves to the cheapest listed supported 720p model **before** the owner reviews and approves a paid job. This does not try alternative models after failure.
- **Manual model selection:** Grok Imagine 1.5 Lite, Kling 3 Standard, WAN 3.0, Runway Gen-4.5, Seedance 2 Mini, Seedance 2 Fast, and Seedance 2.
- 720p portrait/landscape 6-second scenes, from the existing 30s+ structured planner; music/narration/editing/review workflow unchanged.
- Model-specific video quote is included in the job estimate and approval fingerprint. The **actual resolved model** is saved in the plan for resumed worker jobs; changing it invalidates the old consent and is refused when trying to resume the same job as a different model.
- Credential and paid-generation switches remain **OFF** by default; no background, silent or auto-retry billing. This feature was built and tested with mocks—no real paid model requests.

All providers listed above are accessed **through one Runway Developer API key**. This does not provide separate direct-provider keys or independent vendor invoices. Direct integrations may be added later if they prove cheaper.

## Planning prices (720p, video only; 26 Oct 2026)

| Model | USD per generated second | 30s video only |
| --- | ---: | ---: |
| Grok Imagine 1.5 Lite | $0.03 | $0.90 |
| Kling 3 Standard, audio=false | $0.09 | $2.70 |
| WAN 3.0 | $0.10 | $3.00 |
| Runway Gen-4.5 | $0.12 | $3.60 |
| Seedance 2 Mini | $0.16 | $4.80 |
| Seedance 2 Fast | $0.29 | $8.70 |
| Seedance 2 | $0.36 | $10.80 |

*The app adds a planning allowance of $0.25 for every 30 seconds of voice and script, so the Auto 30s **estimate** is $1.15, not a bill promise. Prices can change. Actual bills can include input media, other tiers, taxes, retries or regeneration. Follow provider limits and dry-run before spending.*

Official pricing: https://docs.dev.runwayml.com/guides/pricing/
Official models: https://docs.dev.runwayml.com/guides/models/
Supported ratios/inputs: https://docs.dev.runwayml.com/assets/inputs/

## Safe testing while the owner's laptop is off

CI uses only mock HTTP calls for all provider selections; no API key or paid credits are needed. The existing 30-second offline video, subtitles, approval, and UI tests are retained. GitHub Actions results appear on the PR.

**Do not enable paid mode until** the owner approves spend and configures their own private API credentials with server-side usage/billing limits. The first live job should validate API payload fields, real video quality, Bangla narration and video alignment. Current pricing is a *local estimate*, not a hard provider invoice cap. Keep the app private—authentication/RBAC, durable storage, and automatic social publishing are not production-ready.

## Next work

Validate with provider dry-runs where supported; compare direct vendor API pricing; add per-channel model policies, robust persistent quota accounting, cost reconciliation, and optional licensed stock footage for low-cost long-form content. YouTube/Facebook APIs remain disconnected; no automatic uploads occur.

## Dashboard and deployment verification — 26 Oct 2026

The dashboard now shows credential **presence only**, a public model/price catalog even before a channel exists, and a labelled free-demo workspace button. Presence is not key validity or account credit verification. Official Runway SDK request types were checked for all seven model IDs against `runwayml/sdk-python/src/runwayml/types/text_to_video_create_params.py`; this app uses the documented 720p pixel ratios and integer 6-second scenes. Gen-4.5 prompt validation counts UTF-16 code units correctly. Seedance Mini's 64-credit minimum is covered by the pipeline's 6-second clips (96 credits each).

Codespaces is configured to forward private port **8503**. The attach script installs this checkout's requirements and starts Streamlit without dotfiles or terminal work by the user. It refuses to change branches, preserves an existing listener, and forces paid generation **off** for this free-testing deployment profile. It reports only whether RUNWAY_API_KEY is present; it never prints, exports to a file, or tests the key against a paid endpoint. An occupied port is not proof that the listener runs the latest code.

The separate `browser-smoke-test` CI job uses real Chromium against a disposable Streamlit app with all provider secrets removed. It captures the actual Dashboard, opened multi-model selector and completed mock job, clicks the MP4 download, and confirms the live-generation button is disabled. These screenshots represent a CI test workspace, not the user's running Codespace. CI artifacts are downloadable for seven days.

Cloud Browser GitHub sign-in was not completed in this session. Therefore the user's Codespace restart, actual Codespaces secret injection and a user-accessible live Preview URL cannot be claimed verified. The isolated runtime is a different environment; absence of a Codespaces User Secret there or in Actions is expected and does not invalidate the user's secret setup. No paid provider call or credit purchase was performed.
