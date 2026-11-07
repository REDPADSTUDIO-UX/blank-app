# Free shared GPU image-to-video

Video Studio now calls a reviewed Hugging Face ZeroGPU Wan2.2 Space through gradio_client 1.14.0. It submits an uploaded image and an English motion prompt, receives an actual generated MP4, validates duration, and shows a preview/download. No GPU is added to Render. The shared remote worker runs the model.

The client explicitly sets hf_token=False, uses no account credentials, no hosted Inference Providers, no paid GPU provisioning, no subscription, no credits and no paid fallback. Anonymous quota and provider queue limit availability; this is not an always-on or production-SLA GPU. Generation is a single submission with a bounded result wait, no automatic retry. Failed/uncertain jobs remain marked as such and never appear as successful clips.

Images/prompts go to the public third-party Space zerogpu-aoti/wan2-2-fp8da-aoti-faster; do not upload confidential media without appropriate authorization. Only PNG/JPEG up to 10 MB/20 megapixels are accepted. Clips are about 3.56 seconds at 832x480 in the smoke test. Video has no narration/music. This does not implement a complete two-minute episode editor or generation of every shot.

Server-local clips/job records are temporary on Render Free. Download clips to retain them. Existing code is saved in GitHub; user-facing smoke artifacts are saved separately.

Official references:
https://huggingface.co/docs/hub/spaces-zerogpu
https://huggingface.co/docs/hub/spaces-api-endpoints
https://huggingface.co/spaces/zerogpu-aoti/wan2-2-fp8da-aoti-faster

Implementation note: a first raw REST integration returned a worker error. It was replaced with the supported SDK path. No output from that failed job is described as successful.

## Free personal account mode

A user-authorized token may be configured only in the hosting secret REDPAD_HF_FREE_TOKEN. Before GPU submission the backend calls whoami-v2 and requires type=user and isPro=false; missing/unknown/paid profiles fail closed. The token is passed to the SDK for the existing ZeroGPU Space, never to an Inference Provider or provisioned paid hardware. It is not saved in job metadata or shown in the UI. This enables the account's free quota; it does not remove quota or queue limits. With no token the original anonymous mode remains available. The connection check reports which mode is active.

A built-in geometric test image permits testing through the deployed Studio without transferring a local user image. This fixture is not AI-generated story artwork and must not be presented as a completed episode.
