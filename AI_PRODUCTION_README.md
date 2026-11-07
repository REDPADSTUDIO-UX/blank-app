# REDPAD AI Film Production — beta

Built on `2ea1190` without changing `main` or removing the original studio.

## What is implemented

The new section inside Video Studio accepts a topic/story (or script) and a channel. In live mode, a structured OpenAI scene planner writes Bangladeshi Bangla narration, matching English translations, continuity-aware motion prompts and sound-effect cues. Azure Speech synthesizes Pradeep or Nabanita per scene. Runway Gen-4.5 supplies actual text-to-video footage through `POST /v1/text_to_video`, with checkpointed task IDs and status polling.

FFmpeg normalizes each clip, crops to portrait/landscape, fits the narration without silently truncating speech, ducks background audio under speech, adds original synthetic transition effects, and concatenates scenes. A bundled OFL Noto Sans Bengali font and Pillow RAQM shape Bangla captions. The final H.264/AAC MP4 has burned bilingual captions, selectable Bengali/English subtitle tracks, and downloadable UTF-8 SRT files.

The MP4 and subtitles appear in Production Jobs and Approval Dashboard. All renders enter **Awaiting review**. A draft edited during production cannot be published to the review row as if it matched the old render. Existing script changes invalidate the previous preview as before. No YouTube/Facebook upload was added.

## Modes: do not confuse them

| Mode | Network / payment | Output |
| --- | --- | --- |
| Original preview | None | Existing abstract stills and ambient soundtrack |
| Offline production mock | None | Moving codec test patterns, synthetic test tone, music/SFX, Bangla/English captions; visible MOCK banner |
| Live production | OpenAI + Azure Speech + Runway API credits | Model-planned story, neural Bangla narration, generated moving footage, mixed audio and captions |

Mock mode always uses a fixed fictional railway story. The topic names the test; it does not turn that fixture into generated content. Mock tone is **not spoken Bangla**. No credentials, spend approval, or successful live test are implied by a passing mock.

## Spending and secrets

Required secret names: `RUNWAY_API_KEY`, `OPENAI_API_KEY`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`. Read them from the environment or the existing untracked Streamlit secrets file. The tracked `.streamlit/secrets.toml.example` contains only empty placeholders.

Live UI additionally requires the owner switch `REDPAD_ENABLE_PAID_GENERATION=true`, a sufficient `REDPAD_MAX_JOB_USD`, and a per-job checkbox showing the current estimate. Changing the topic, voice, ratio, duration, channel or music resets consent; starting a job clears it. Resume uses only that saved job's approval. Server flags are not an authorization to create unlimited jobs. Keep the deployment private; app-level multiuser authentication and role-based billing permissions are not implemented.

On 25 October 2026, Runway lists Gen-4.5 at 12 credits/second and $0.01/credit: 30 seconds costs $3.60 for video alone. The UI uses a $0.25 allowance per 30 seconds for planning/speech ($3.85 total estimate). This allowance is approximate; region, taxes, provider price changes and manual regenerations can change billing. This is a request/estimate guard, **not a hard provider invoice cap**. Set provider-side billing limits before deployment. Runway consumer subscriptions do not replace developer API credits. No paid calls were run in this implementation session.

## Checkpoints and long-video architecture

- Scene durations are 2–10 seconds. The topic planner currently uses 6-second scenes; UI targets are 30, 60, 120, 300 and 600 seconds.
- Each scene has separate source video, WAV narration, captions, effects and normalized MP4. Processing is sequential and disk-backed; the full film is not loaded into a movie-editing object.
- `plan.json` is hash-bound to `state.json`. The job saves task IDs before polling and reuses completed media. File locks prevent two workers charging the same job concurrently.
- Provider submission POSTs are never automatically retried. A crash/timeout before recording a returned ID leaves an uncertain submission blocked for operator reconciliation. HTTP polling/download retries use the same task; resuming does not blindly regenerate video. A rejected/uncertain voice submission may likewise require operator reconciliation/new approved job.
- The UI starts a worker thread and refreshes progress; Resume restarts an interrupted worker. `redpad_pipeline.worker` is also available for a supervised private deployment worker on an existing job ID. Secrets never appear in process arguments.
- Task results are downloaded only from approved HTTPS CDN hosts; redirects are checked, private addresses rejected, no auth headers forwarded, downloads capped at 500 MB/scene. FFmpeg's local inputs restrict protocols to file/pipe.
- The live job uses 720p at 24 fps; mocks intentionally use low resolution. The 600-second timeline and SRT boundaries are tested, but a 10-minute live film, provider concurrency, cinema-quality continuity and production load are not validated.

## Subtitle and audio limits

Captions are timed to each narration scene, not word-aligned transcription. Long narration is sped up only within a bounded range; text that cannot fit is rejected before video submission for that scene. Human review must check pronunciation, translation, timing, visual continuity and audio levels. The soundtrack/effects are procedural, not premium AI music. An optional licensed MP3/WAV music upload is supported (20 MB). Footage's original audio is intentionally replaced by the narration/music/effects mix.

## Tests and verification

`tests/test_production_pipeline.py` covers paid-call gating, credential-safe errors, OpenAI/Runway/Azure HTTP contracts with mocks, malformed plans, 10-minute caption boundaries, sound-effect waveforms, SSRF rejection, checkpoint resume, unknown submissions, exclusive worker locks, and edited-script rejection. It also renders and decodes a real 30-second offline MP4, checks changing frames, extracts both embedded subtitle tracks and verifies review records. The optional music upload path is exercised.

`tests/test_production_ui.py` exercises the live button's locked state, offline job button, real offline renderer, preview/download/SRT widgets, visible MOCK disclosure and human approval. Only worker scheduling is made synchronous for the test. The existing UI/codec regression tests remain in CI. Test databases are temporary; user data and production secrets are not touched. CI publishes MP4/SRT artifacts for seven days.

## Remaining before claiming production readiness

1. Supply credentials securely and approve the first paid budget; execute the entire live 30-second story and inspect actual footage, Bangla pronunciation, translated captions and mix. Provider contract mocks do not prove account access or live API compatibility.
2. Deploy a supervised worker with durable database/object storage, backup/retention and monitoring. Current files and job paths are local to one machine. Queue concurrency, cancellation, quota reconciliation and high-volume operation need further work.
3. Improve character continuity, scene-specific sound design and subtitle word alignment; support chapter planning beyond the current 10-minute limit.
4. Add authentication/roles before exposing paid controls publicly. Add YouTube/Facebook OAuth, token protection, approval-bound publishing, schedules, idempotent retries and remote upload-status tracking as a separate phase.

## Primary integration references

- Runway API and version: https://docs.dev.runwayml.com/api/
- Runway pricing: https://docs.dev.runwayml.com/guides/pricing/
- Azure TTS REST: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech
- OpenAI structured output: https://developers.openai.com/api/docs/guides/structured-outputs
- Bundled font source: https://github.com/google/fonts/tree/main/ofl/notosansbengali (retrieved 25 October 2026); redistribution license: `assets/fonts/OFL.txt`.
