# REDPAD Storyboard Studio — offline MVP

Branch: `feature/video-music-editing-studio`. This release adds a standalone **🎬 Storyboard Studio** tab between AI Production and Video Studio. It does not change `main`, deploy to Render, provision services, connect YouTube, call paid APIs, or alter the existing video approval system.

## What is actually implemented

- Choose an existing REDPAD content draft with a nonempty script.
- **Create Offline Storyboard** splits Bangla/English narration into shot cards without a network request. Bangla danda punctuation is supported; long paragraphs are segmented and large inputs rejected. This deterministic split is an initial editorial suggestion, **not AI writing**.
- Display a **contact sheet of free schematic framing sketches** (wide, medium, close-up, insert, POV, over-shoulder) using Pillow, or display a manually uploaded JPEG/PNG/WEBP reference. Sketches are not AI-generated photography.
- Edit shot-by-shot narration, action/visual direction, camera size, camera movement, timing and director notes.
- Maintain character, location and cinematography continuity notes for consistent production prompts.
- Export a UTF-8 JSON contact sheet/shot plan with individual motion prompts, original narration and character/location/style continuity.
- Save all shot changes in an additive `storyboards` SQLite table keyed by content ID; use optimistic revision checks to reject stale edits.
- The storyboard is **Draft** until a human selects **Approve Storyboard**. All edited shots or continuity notes reset it to Draft. A changed source script invalidates the previous storyboard approval, blocks editing/export, and requires explicit confirmation before regenerating.
- Free uploaded image references are normalized, size-limited (5 MB), and restricted to the storyboard media directory.

## Deliberate limits

The sketches are local image compositions, **not AI-generated images**. Approved storyboards can now produce free **animated MP4 animatics** directly in this tab. Their hand-edited, English-translated shot plans can also be selected as source inputs in **Live AI Production**, but live generation remains disabled unless the existing explicit provider budget and owner consent gates are enabled. No paid generation or account connection has been tested or authorized.

The storyboard must be approved *again* after editing shots or continuity notes. Live model production requires a manually checked English translation, 4–10 seconds per shot, 30–600 seconds in total and a supported model. If an approved reference photo exists, the Gen-4.5 first-frame image-to-video provider adapter is available under paid-call gates. Without a real reference image the adapter uses text-to-video; schematic sketches are not submitted as AI-generated photos. Local reference photos and script are SHA/revision checked before billable requests.

Do not confuse the offline animatic (FFmpeg animation of static pictures) with generative moving AI footage. Automatic cinematic AI still-image generation, live provider account/credits verification, premium Bangla TTS verification and a true production run remain outstanding.

Data and reference images are still saved to the app's **existing local SQLite/media filesystem**. A Render free deployment may wipe these. No production Render deploy/migration may occur without independently checked backups and durable storage.

## Verification

`tests/test_storyboard.py` exercises offline Bangla splitting, shot planning and sketch sizes, JSON export, update conflicts, human approval/reapproval, stale-script handling, image upload sanitization, media containment, and the real Streamlit UI with all HTTP requests forbidden. It runs inside the existing video-studio GitHub Actions CI alongside previous video/YouTube tests. No live Google authorization, paid API or external database is needed.


## End-to-end video workflow added — 29 October 2026

1. **Script:** Create a content draft in Approval Dashboard, then generate an offline storyboard.
2. **Visual planning:** Edit shot durations, scene action, shot size, camera motion, sound cue, bilingual narration/translation, character/location/look continuity, and upload your own licensed/copyright-cleared image references if available.
3. **Storyboard approval:** Explicit human approval; all edits reset the storyboard to Draft.
4. **Free animatic:** **Render Approved Storyboard → MP4** animates reference images or clearly labelled schematic sketches with FFmpeg, burns Bangla captions, includes Bangla SRT tracks, procedural soundtrack, edit SFX, optional licensed music and optional uploaded spoken narration. Without voice upload, the output has **no spoken narration**, not a fake synthetic voice. The MP4 appears in the existing Approval Dashboard as **Awaiting review** and is downloadable.
5. **Live AI path, code-only:** In **AI Production**, choose **Live AI → Approved Storyboard**. After human-entered English subtitle translations and valid scene durations, the shot-exact plan uses storyboard continuity prompts. Approved images use Runway Gen-4.5 \`/v1/image_to_video\` first-frame data URI; other scenes use \`/v1/text_to_video\`. Existing owner spend switch, per-job USD approval, credentials and checkpoint safety gates remain mandatory. The assistant did **not** initiate a billed request, and real provider compatibility and footage quality remain unverified.
6. **Final review:** Saved script version, source storyboard revision and reference image hashes are checked again before approval. YouTube upload/publish remains disabled and unrelated to this production feature.

### Testing
- \`tests/test_storyboard_render.py\`: actual FFmpeg MP4 encode and decode, moving frames, soundtrack, Bangla subtitles, human final review, blocked stale sources, zero external calls.
- \`tests/test_storyboard_live.py\`: human-translation and duration validation, immutable storyboard source binding, fake/stubbed Runway image-to-video first-frame request and rejection of altered reference bytes; no paid requests.
- Existing full Video Studio, browser and YouTube mock tests continue running in GitHub Actions.

### Deployment and persistence
The existing original Render service has **not** been changed or redeployed. Its original SQLite database and media have **not** been fully backed up and restored. All new production files currently use local storage in a developer/test environment; a Render Free redeploy risks loss. Do **not** deploy, restart, migrate or enable paid calls until full backup and recovery checks are completed. A separate secure vault for real YouTube OAuth also remains pending.
