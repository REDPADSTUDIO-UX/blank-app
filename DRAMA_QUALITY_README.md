# Strict realistic-drama quality workflow

This feature adds a reusable, no-paid-API production workflow to the existing Streamlit Video Studio. It does not claim a new five-minute photorealistic episode has been produced. The older 2D episode remains an archived prototype, not a passing realistic-drama result.

## Implemented

- Versioned research, season, character/location bibles, scene objectives/conflicts/turns/consequences, individual Bangla dialogue, pronunciation lexicon, variable shot coverage, music spotting and action-specific sound cues in SQLite.
- Compare-and-swap edits, immutable source history and content-addressed read-only media copies, so a producer temporary file cannot overwrite a stored take. Source-linked screenplay stages, current script binding to the existing content row, and explicit agent/human review evidence without numerical quality claims.
- Selective invalidation: voice selection/lexicon edits do not force unrelated footage regeneration; appearance/reference changes invalidate affected shots. Selected take/reference bytes bind the final render. Changed bytes, scripts or selected takes revoke final approval.
- Explicitly separate technical integrity, project editorial review, asset editorial review, representative scene, resource/quota/rights preflight and final picture/sound review.
- No cartoon/mock/still fallback in this workflow. Imports must identify their real engine and rights; references/footage/voices need explicit review. Labels alone do not prove photorealism or acting quality.
- Existing anonymous ZeroGPU adapter plus a bounded Indic Parler audition adapter. Discovery is not inference and never establishes quota. Full batches require verified rights, sufficient evidenced quota and an accepted paired sample. Uncertain/blocked submissions are not blindly retried.
- Explicit revision/destination disclosure records before sending project images, directions or dialogue to public inference services. A disclosure check cannot be treated as owner consent unless the owner actually authorizes the transmission.
- Original local melodic/harmonic score sketches and event-specific practical-sound approximations, independently replaceable by licensed recordings. Sketches are not automatically judged musical, realistic or final.
- Finishing from accepted media: distinct footage, no looping/stretching a short clip into a scene, separate dialogue/music/Foley/ambience stems, event offsets, subtitles, music ducking and limiting. Actual decode, freeze/black/silence, clipping and resolution checks. Source resolutions remain in provenance; upscaling is not described as native HD generation.
- Approval Dashboard and YouTube snapshot boundaries call the same strict-project guard. No new YouTube API publication or automated schedule is enabled.

## UI

Video Studio opens the Quality Workbench first. Earlier paid/mocked/2D experiments remain in a clearly labelled collapsed Legacy section. No-code forms edit research, scripts, performances, references and cues. Media auditions/imports, actual reviewer evidence, selected takes, blockers, checkpoints and gated render controls are available. New projects link to the existing channel/content architecture.

## Current demonstration

`productions/ghor_117_quality/seed.py` checkpoints an authored original revision: 7 scenes, 34 dialogue lines, 70 varied shots over 300 seconds, the existing 30-episode season, stable character/location notes and six intentional music/ambience intervals. Model and technical source checks are recorded separately from fictional choices. Rafi's existing photographic project reference is available for an internal sample, not as a blanket claim that all image-generation rights were independently reverified.

No new voice or video inference completed in this upgrade run. Read-only checks found an unavailable expressive-voice public endpoint and unproven usable video quota/access. Automatic approval review separately rejected transmitting private project references/dialogue to public generation services without destination-specific owner authorization. The code and creative checkpoint were preserved; no workaround, paid fallback or cartoon replacement was used.

## Honest scope

This implements authoring, persistence, correction, orchestration and review/finishing boundaries. It is not an unattended free research/LLM service. The actual assistant-authored research/script revision is included; no server-side research crawler or screenplay-generation model is claimed to have run. A representative realistic visual-and-performance result still has to succeed. No passing test implies commercial suitability, perfect Bangla pronunciation, premium acting, adequate GPU quota or completed five-minute footage.

The codec integration test uses explicitly artificial test patterns and a tone in a temporary directory solely to test editing/stems/subtitles/QA. They are not demo drama assets.

## Safety / recovery

All implementation is on the existing local feature branch. The original Render database/media and main branch are unchanged. Do not push a watched branch until its auto-deployment safety or verified backup/recovery is established. Use the saved Git checkpoint to recover this local work. The isolated owner-private review preview is an export of actual backend state, not a new Render deployment or a claim that Streamlit is running on the static host.
