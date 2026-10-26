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
