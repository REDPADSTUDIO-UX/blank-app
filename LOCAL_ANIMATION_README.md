# Local neural image animation

Video Studio now includes an optional local SVD-XT image-to-video panel before the channel requirement. It accepts an uploaded PNG/JPEG, exposes seed/motion controls, and produces 25 genuinely model-generated frames at 7 fps (about 3.57 seconds), with an MP4 download and provenance sidecar. It does not send images to any API. The existing procedural renderer and paid providers remain separate.

## Runtime

A CUDA GPU host must have optional `requirements-animation.txt` installed and an SVD-XT Diffusers checkpoint directory provisioned under its applicable license. Set `REDPAD_SVD_CHECKPOINT` to that directory containing model_index.json. The web app does not install packages, download weights, rent GPUs or accept license terms. Inference uses `local_files_only=True`, FP16, CPU offload, forward chunking and decode chunks of two frames. No inference endpoint or API credential is needed. CPU-only hosts display an unavailable status and disable generation.

Optional packages are deliberately excluded from the normal web requirements. Use a separate compatible GPU Python/PyTorch environment; the main app currently declares Python >=3.14, whose compatibility with optional ML wheels must be checked before provisioning. This change does not modify Render, deploy, restart or migrate anything.

## Scope and validation

This generates individual silent landscape clips, not a complete narrated two-minute film. Music, speech and multi-shot editing remain separate steps. Successful clips are for human review and are not published or marked approved. Failures remove incomplete job files. Inputs are bounded by format, byte size and pixel count. Metadata records image checksum, inference controls, engine, frame count and review requirement.

Contract tests use a fake pipeline to verify local-only loading, inference arguments, metadata, validation and failed-job cleanup. They do not prove visual quality or real GPU inference. The implementation environment has no CUDA device; a real checkpoint/GPU smoke test is still required before calling this production-ready.

Reference: https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/svd

## Consumer Google voice panel

Video Studio includes a separate Google Bengali voice panel using gTTS consumer Translate TTS. It never uses Google Cloud billing or Gemini, and cannot promise expressive acting or a specific voice gender. Only spoken text is submitted, with timeouts, default certificate verification, no automatic retries and no substitution. Failed or rate-limited requests do not register output. The panel has a voice-only preview/download: completing it is NOT an end-to-end film test. Import reviewed narration into the existing Storyboard Studio for assembly. The earlier work-environment Translate request returned 429; no successful Google voice is claimed.
