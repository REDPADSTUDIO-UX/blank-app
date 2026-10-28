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

This is a **storyboard planning/review module**. The sketches are local image compositions and are not outputs of AI image models. The exported shot plan is **not yet consumed shot-for-shot by the Runway video worker**; existing production functionality remains unchanged. The module does not initiate AI imagery, generation, video export, upload, publishing or scheduling. Real AI storyboard stills and direct approved-board-to-video dispatch require separate budget and integration review.

Data and reference images are still saved to the app's **existing local SQLite/media filesystem**. A Render free deployment may wipe these. No production Render deploy/migration may occur without independently checked backups and durable storage.

## Verification

`tests/test_storyboard.py` exercises offline Bangla splitting, shot planning and sketch sizes, JSON export, update conflicts, human approval/reapproval, stale-script handling, image upload sanitization, media containment, and the real Streamlit UI with all HTTP requests forbidden. It runs inside the existing video-studio GitHub Actions CI alongside previous video/YouTube tests. No live Google authorization, paid API or external database is needed.
