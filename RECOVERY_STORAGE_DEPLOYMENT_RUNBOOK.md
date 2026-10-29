# REDPAD — Backup → Durable Storage → New Studio → Live Video release gate

Status: BLOCKED AT FULL ORIGINAL RENDER BACKUP (2026-10-29).
This is an engineering handoff, not authorization to deploy or pay.

## Verified baseline

- Existing Render Free app: redpad-ai-studio-private-preview, service ID srv-dbfiesvb9u1s73d2qblg.
- Last recorded old live commit 06915ba. The newer Studio is preserved in feature/video-music-editing-studio, PR #2; do not merge into main.
- Private recovery ZIP REDPAD_PARTIAL_RECOVERY_AND_MIGRATION_PLAN_2026-10-28.zip: one visible channel, one draft, complete visible script, valid recovered-file hashes. No original SQLite file, no audio, no MP4/media directory, and no source DB integrity proof.
- Render Free has no SSH/Shell/one-off jobs, ephemeral filesystem, and may lose local changes on redeploy/restart/idle spin-down. Verify whether the original database and media still exist; a browser snapshot alone does not prove it.
- redpad_pipeline/backup.py can capture a WAL-safe SQLite snapshot, all media and SHA-256 manifest, and verify an isolated restore. CI exercises this only with synthetic data. It has NOT been run against original Render. ZIP is unencrypted; private files must never be uploaded to public GitHub or unencrypted external storage.

## Stage 1 — Full original recovery (NO deployment)

1. Only read-only reconnaissance of the original service. Check current live deployment, counts, accessible old media, and supported data-export options. Avoid restarts, builds or config updates. Do not claim a cached browser page is an up-to-date database inspection.
2. Obtain source filesystem access or a provider-assisted non-restarting export. Do not assume upgrading plan or changing settings preserves the old ephemeral instance.
3. Export using SQLite online backup API, not a blind file copy ignoring WAL. Include every original table, version, row, ID, timestamp and media file, not just visible UI fields.
4. Require integrity_check=ok, no foreign-key violations, table row hashes/counts, file checksums, independent archive verification and an isolated restore. Confirm no concurrent app changes; a SQLite snapshot alone cannot atomically freeze video files.
5. Keep two encrypted private copies in separate locations, retained without GitHub commits. Prepare a signed-off recovery report. Only then evaluate migration.
6. If the old instance has already lost the data or free export is impossible, STOP. Get explicit owner decision on (A) strict preservation/provider support, versus (B) a newly isolated Studio from the verified partial recovery with explicit acceptance that missing media/original DB cannot be recovered. Do not silently substitute B for A.

## Stage 2 — Durable data and media (requires owner's separate permission)

Recommend evaluating Neon Free as a candidate, NOT an already-provisioned resource:
- Official Neon update dated 2026-10-02: 1 GB PostgreSQL, 100 CU-hours per project monthly, 5 GB S3-compatible object storage; actual account eligibility and free limits must be confirmed inside the provider UI.
- Use PostgreSQL as source-of-truth for channels, drafts, approvals, storyboards, production metadata, idempotent jobs and an encrypted separate OAuth-token vault. Media files belong in private object storage, not a free Render local folder or token table.
- Convert SQLite-specific SQL and transaction logic explicitly. Never claim setting REDPAD_YOUTUBE_DATABASE_URL alone migrates the main app tables/media.
- Keep encryption keys exclusively in the deployment platform's private environment; tokens encrypted with Fernet and isolated by real YouTube ID. Do not copy secrets into backups, commits or chat.
- Media uploads require private object ACLs, checksum verification, bounded filenames, separate worker-safe retry/resume, and signed download URLs with appropriate expiry. Retain a second encrypted backup outside the provider.
- Database and object storage quotas are prototype limits; free is not production SLA. Do not create a Neon account/project, accept terms, configure payment, or activate paid services without a separate owner approval. Do not use Render Free Postgres as a permanent vault: its free databases expire.

## Stage 3 — New Studio deployment (still gated)

1. Deploy the feature branch to an isolated, nonproduction preview first after source recovery has passed. Keep the old service untouched and auto-deploy off.
2. Verify stable media and records surviving a deliberate preview-only restart, after explicit owner permission. Compare recovered row counts/hashes and media SHA-256 against Stage 1.
3. Check real browser sign-in, original channel, draft, Storyboard Studio, MP4 review, subtitles, no billing, mock vs Google-verified OAuth, and no video upload.
4. Do not switch production URL or destroy old service until owner reviews restored samples and explicitly approves a cutover.

## Stage 4 — Explicitly authorized Live AI Video Test (never implicit)

1. Obtain new specific owner consent to a named model, exact duration, estimated USD maximum, provider access and billable request. Current no-paid-API policy otherwise remains active. Observe vendor billing caps and restrictions.
2. Prefer a short approved scripted horror shot set with real storyboard visual references, voice, music, subtitle and human approval. One paid request at a time; do not retry uncertain POST.
3. Verify video integrity, Bangla pronunciation, cinematic continuity, scene transitions, exact duration and download. Do not upload/publish/schedule to YouTube.
4. Separate staging success from production-ready claims and report true costs and remaining risks.

## Invariant rules

- No changes to main, no merge.
- No paid API, new cloud resource, deployment, restart, migration, Google OAuth consent, YouTube upload or public disclosure without appropriate explicit approval and safety gates.
- No owner Terminal/Coding required.
- A mock MP4, test ZIP or UI record export is not full source recovery.
- Exports may contain private scripts/content: encrypt and treat as restricted artifacts.

Official references:
- https://render.com/docs/free
- https://render.com/docs/ssh
- https://neon.com/blog/neon-free-plan-1-gb-per-project
