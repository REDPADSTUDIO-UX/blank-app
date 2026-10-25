# REDPAD AI Studio: Video + Background Sound + Editing (prototype)

This branch adds `redpad_video_studio.py` and a **Video Studio** tab to the existing Streamlit app. The original channel settings, script agent, Azure voice agent and approval dashboard are preserved.

## What it really does

- Select a channel and create a template-based demo idea, or use an existing draft.
- Render four original abstract storyboard scenes to a real MP4 with FFmpeg.
- Produce a synthetic, original ambient soundtrack (horror/calm mood).
- Optionally mix in an MP3 recording you upload (e.g. a previous narration test).
- Save output as `redpad_media/video/*.mp4`, display preview and offer a download.
- Leave the draft in the existing **Approval Dashboard**. Absolutely no auto-posting.

**Important limitations:** No live topic research; demo ideas are templates, not generative AI. Scene images are stylized procedural cards, not cinematic generative video; the ambient track is not an AI music model. No API credits needed for this part. Render time and storage are limited. Save downloads because Codespaces/Streamlit local storage is not a permanent media library.

## How to run

GitHub Codespaces: switch to the feature branch, allow its environment to sync dependencies, then run the Streamlit app. In case the auto-sync did not install Pillow and imageio-ffmpeg, run `uv sync`. The app also has `requirements.txt` for Streamlit Cloud. FFmpeg can be supplied by the `imageio-ffmpeg` package.

Then choose the **🎞️ Video Studio** tab, select **AI-free demo idea**, keep MP3 empty for the first smoke test, and click **Generate demo MP4**. Confirm the four-scene MP4 plays and appears in the review queue. Uploaded voices should be legitimate recordings with permission to use.

## Next phases

Integrate properly licensed stock assets or premium text-to-video APIs, higher quality Bangladeshi narration, a fully permission-cleared music catalog, script + storyboarding agents, production queue, cloud object storage, and optional publishing *only after explicit human approval*.

**Security:** Never commit `.streamlit/secrets.toml` to GitHub. 


## Verification and approval fixes (25 October 2026)

- The generated video can now be played and downloaded inside Approval Dashboard.
- Rendering a new version resets that draft to Awaiting review and uses a unique media filename.
- Editing or AI-regenerating a script invalidates the linked old video. Editing a script while selecting Approve saves it as Awaiting review.
- Narration longer than 79 seconds is rejected with an explanation instead of silently truncating speech.
- The isolated Streamlit AppTest creates a channel, clicks Generate, checks both media/download widgets, exercises correction/review/approval, and tests rerender and stale-script behavior. It copies source into a temporary workspace and never touches the deployed database.
- Codec tests decode real MP4 output and test synthetic MP3 mixing plus malformed/oversized-duration input rejection. The synthetic tone is not a Bangla voice quality test.
- CI keeps the 30-second demo and UI-generated MP4 as downloadable workflow artifacts.

### Verified scope and remaining work

The sample is 30 seconds, 360×640, H.264 video and AAC audio. Four abstract stills with cuts and a synthesized drone are expected; these are not cinematic scenes, animated AI footage, subtitles, or spoken Bangla narration. Basic landscape rendering is also tested. Download widgets are verified with AppTest; a signed-in Codespaces browser download has not been tested.

Cloud Browser was signed out of GitHub during this audit. The feature branch was checked and executed in an alternative isolated environment; the user's running Codespace, installed dependencies, secrets, existing drafts and provider quotas were not inspected. No production records were changed and no paid API calls or social uploads were made.

The script model and Azure Bangla TTS integrations exist, but need working credentials/quota and real provider tests. Video Studio currently accepts narration by manual MP3 upload; the stored Azure recording is not automatically connected to rendering. Channel creation only stores local settings: it does not authorize a YouTube channel or Facebook Page. Publishing has no OAuth flow, token storage, upload client, scheduler, queue, retry logic or remote publish-status tracking. Preferred publishing time and videos-per-day are settings only.

To complete production: connect script-to-scene planning and licensed visual sources, integrate narration/subtitles and higher-resolution editing, add durable database/media storage and a background job queue, implement YouTube/Facebook OAuth and upload adapters, then add scheduling in Asia/Dhaka, approval bound to the rendered version, retries/idempotency, upload status logs and private/test-channel end-to-end publishing tests. Agree provider budgets before enabling paid generation. Old unlinked renders need a retention/cleanup policy.


## New AI Film Production beta

The additive production section now has live Runway/Azure/OpenAI adapters, checkpointed scene editing and bilingual captions. See [AI_PRODUCTION_README.md](AI_PRODUCTION_README.md) for current capabilities, cost guards, offline/live distinctions and unverified live-provider limitations. Earlier audit notes above describe the original preview module.
