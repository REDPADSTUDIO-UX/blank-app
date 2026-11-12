# Private Kaggle handoff

Prepared, not submitted or executed. No account is connected yet. The assistant fills the authenticated owner slug only after supported Browser/API access is established. Metadata is private, GPU-off and Internet-off by default. No arbitrary tunnel, API server, paid accelerator, public notebook or secret attachment is permitted.

1. Inspect actual Notebook settings and quota through the connected owner session.
2. Run the read-only environment inventory; preserve JSON outside the temporary session through an approved artifact export.
3. If a free GPU is actually available/authorized, activate only during the bounded runtime/model test. Observe updated runtime/library/VRAM and quota values. Do not add VRAM from separate GPUs as if one device.
4. Run the tiny tensor canary, then one already approved exact model canary with a 32-token limit. No weights are embedded/downloaded by this notebook.
5. Use `KaggleLab` with the same source-controlled Bengali cases across separately approved candidates. Raw outputs, settings, hashes, telemetry, validation and failures persist per job. Failed/interrupted calls never automatically repeat.
6. Export completed evidence before stopping the session. No permanent Kaggle-to-Render inference endpoint exists.

Official workflow sources: https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md and https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md . API credentials are absent in this environment; none were requested or logged. Never publish or commit credentials/model weights.
