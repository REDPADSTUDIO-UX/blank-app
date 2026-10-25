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

Then choose the **🎞️ Video Studio** tab, select **Auto demo idea**, keep MP3 empty for the first smoke test, and click **Produce preview MP4**. Confirm the four-scene MP4 plays and appears in the review queue. Uploaded voices should be legitimate recordings with permission to use.

## Next phases

Integrate properly licensed stock assets or premium text-to-video APIs, higher quality Bangladeshi narration, a fully permission-cleared music catalog, script + storyboarding agents, production queue, cloud object storage, and optional publishing *only after explicit human approval*.

**Security:** Never commit `.streamlit/secrets.toml` to GitHub. 
