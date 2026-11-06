> Latest continuation: [staged Bengali correction checkpoint](PHASE3_STAGED_CHECKPOINT.md). Earlier results below are retained as historical evidence.

> Newer authorized CPU installation and real inference evidence: [QWEN_CPU_PROGRESS.md](QWEN_CPU_PROGRESS.md). The original no-runtime audit below is historical.

# REDPAD AI Studio — Phase 3 checkpoint: actual inference blocked

Phase 3 শুরু হয়েছে। Hardware/model audit, primary-source research, bounded benchmark integration,
raw response evidence, dashboard controls এবং recovery উন্নয়ন সংরক্ষিত। **Phase 3 সম্পন্ন হয়নি।**
বাস্তব AI inference: **০**। Local runtime preflight blocked: **২**। প্রকৃত cinematic MP4: **তৈরি হয়নি**।
কোনো creative score, acting/voice/music quality pass বা independent human review বানানো হয়নি।

Branch: `feature/video-music-editing-studio`.
Starting checkpoint: `5cf3ac36e5a8aae89bbf6ff7abd790c59b938065`.
Continue from the current feature-branch HEAD. Preserve all 20 existing departments and Phase 2 work.

## Completed safe work

- Audited this host: x86_64, 9 logical CPUs, about 9.73 GiB total RAM, roughly 59.7 GiB free disk.
  Exact measured values, available RAM, Python/package versions and local runtime inventory are in
  `verification/phase3/hardware.json`. FFmpeg/FFprobe and Streamlit are available. There is no detected
  NVIDIA device, nvidia-smi, Torch/Transformers/Diffusers, Ollama executable/server or installed model
  in reviewed cache/model locations. CUDA/VRAM cannot be validated without an available GPU.
- Researched exact model variants and license labels through original model cards/repos. The candidate
  registry is `assets/phase3/model_candidates.json`; nothing was downloaded, installed or selected
  as a Bengali-quality winner.
- Added isolated experiment workspaces under ignored `phase3_runs/`, using the existing AgentStore
  and Engine rather than a replacement Studio. Production database/media are never opened.
- Added original Bengali benchmark briefs for family romance, 30-episode horror, Director analysis,
  approximately five-minute screenplay, targeted weak-script repair and continuity review.
  Contract examples have previous narrative prose redacted; they are schema guidance, not samples
  to pass off as model output. Source-dependent tasks require actual owner-approved source records.
  Director/Script inherit the selected source's real brief, keeping genre/episode context consistent.
- Bound each queued comparison to its exact model identifier so later configuration changes do not
  silently change the candidate under test. Existing fixed-loopback inference is retained; no cloud,
  hosted API, download, paid fallback or new model runtime starts automatically.
- Preserved raw runtime text even when JSON is invalid or an output fails structural validation.
  Evidence includes model metadata hash, reported quantization, settings, finish reason, timing and
  available token/duration counters. Responses are bounded to 2 MiB; cloud-backed model metadata,
  reported identity mismatch, incomplete output and non-object JSON are rejected.
- Added explicit generation budgets: six distinct queued experiments per lab, at most two execution
  attempts per experiment. Existing source/version approval and QC separation remain enforced.
- Added experiment idempotency and interrupted-worker recovery, including repair of an interrupted
  mapping update. Models cannot remove source constraints or approve outputs.
- Added dashboard audit, isolated queue/run/error/retry/recovery controls, evidence download,
  actual-output-only blind editorial export and attributed human rubric input with no prefilled scores.
  A blind package omits model identity; the research ledger retains it. Software cannot certify the
  reviewer's identity or independence, so that status remains unverified.

## Model research and conditional choices

All entries are research candidates, not installed or quality-verified models. License labels do not
clear rights to every input, voice, dependent component or output. No terms were accepted on behalf
of the owner. Dependency/variant compatibility must be pinned before actual loading.

| Task | Variant and decision | Evidence / remaining condition |
|---|---|---|
| First text comparison | Qwen3-4B-Instruct-2507, Apache-2.0; conditional first trial | [Original card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507); [Ollama tags](https://ollama.com/library/qwen3/tags) lists `qwen3:4b-instruct-2507-q4_K_M` at 2.5 GB. CPU RAM/latency and Bengali quality unmeasured. Full weight digest must be recorded after approved download. |
| Small text smoke | Qwen3-0.6B, Apache-2.0 | [Card](https://huggingface.co/Qwen/Qwen3-0.6B). Small runtime test candidate; not evidence of premium creative writing. |
| Newer text comparisons | Qwen3.5-2B and Gemma-4-E2B-it, Apache-2.0 labels | [Qwen](https://huggingface.co/Qwen/Qwen3.5-2B), [Gemma](https://huggingface.co/google/gemma-4-E2B-it). Runtime support, quantization and effective/total-memory differences require measurement. No assumption that newer wins. |
| Older text alternative | Gemma-3-4b-it, custom Gemma terms | [Card](https://huggingface.co/google/gemma-3-4b-it). Separate terms; not automatically covered by Gemma 4's label. Deferred. |
| Image reference generation | FLUX.1-schnell, Apache-2.0 | [Card](https://huggingface.co/black-forest-labs/FLUX.1-schnell). Large image model; absent GPU/weights. No character-consistency result. |
| Reference editing | Qwen-Image-Edit-2509, Apache-2.0 | [Card](https://huggingface.co/Qwen/Qwen-Image-Edit-2509). Multi-image candidate, but no identity or Bangladeshi-environment evaluation. |
| Pose conditioning | ControlNet SD1.5 OpenPose variant, OpenRAIL label | [Card](https://huggingface.co/lllyasviel/control_v11p_sd15_openpose). Requires compatible base and annotator terms; not a FLUX plug-in by assumption. |
| Video comparison | Wan2.2-TI2V-5B, Apache-2.0 | [Card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B). Official 1280×704 offload command documents at least 24 GB VRAM. No such GPU here. Native lip-sync, exact expression/camera control and identity lock are not claimed. |
| Lighter video alternative | LTX 2B 0.9.8 distilled | [Card](https://huggingface.co/Lightricks/LTX-Video), [variant license](https://huggingface.co/Lightricks/LTX-Video/blob/main/LTX-Video-Open-Weights-License-0.X.txt). Custom Open Weights terms; no blanket Apache claim. Device fit and exact control pipeline remain untested. |
| Initial Bengali speech comparison | Indic Parler-TTS, Apache-2.0 | [Card](https://huggingface.co/ai4bharat/indic-parler-tts) lists Bengali and emotion prompting. Local package/weights missing; Bangladeshi pronunciation and naturalness untested. |
| Speech alternatives | IndicF5 (MIT label; gated/custom code); Indic-Speak (custom Indic Open Model License v1.0) | [IndicF5](https://huggingface.co/ai4bharat/IndicF5), [Indic-Speak](https://huggingface.co/bodhan-ai/indic-speak). Access/conditions need owner consent. Newer recommendation does not inherit older license terms. No real-person voice cloning. |
| Music model | MusicGen-small not selected for commercial default | [Card](https://huggingface.co/facebook/musicgen-small) labels weights CC-BY-NC-4.0. No neural score generated. Existing original procedural sketches remain explicitly procedural. |
| Music/SFX alternative | Stable Audio Open 1.0 deferred | [Card](https://huggingface.co/stabilityai/stable-audio-open-1.0) uses custom community terms. Eligibility/usage and compute need review; no listening result. |
| Lip-sync | MuseTalk candidate; Wav2Lip public pretrained path rejected for commercial default | [MuseTalk](https://github.com/TMElyralab/MuseTalk) distinguishes MIT code/model permission, dependent-model terms and non-commercial testdata. [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) restricts the open-source pretrained use to non-commercial purposes. No actual lip synchronization tested. |

## Free runtime strategy

1. First proposed action: install one local Ollama runtime and one explicitly approved 2.5 GB Qwen
   model on this development host, not the owner's personal computer. No GPU or paid account is
   needed for a bounded CPU text trial. Actual memory/latency may still make it unsuitable; measure.
2. Compare equivalent bounded tasks, retain actual model/digest/settings/output evidence, reject
   truncation/contract failures and obtain independent Bengali editorial review before choosing a winner.
3. Only after useful text results, consider separately authorized free GPU media experiments.
   Existing shared remote GPU code remains retained but was not called in this phase.

[Kaggle Notebook docs](https://www.kaggle.com/docs/notebooks) currently describe up to 12-hour CPU/GPU
sessions, GPU availability/queue restrictions and 20 GB saved working storage.
[GPU usage docs](https://www.kaggle.com/docs/efficient-gpu-usage) describe nominal weekly quota around
30 hours, varying with demand/resources. This is not a guaranteed allocation or one uninterrupted
30-hour session. The current account's eligibility, quota, phone verification, accelerator/VRAM,
internet access and export permissions have not been inspected. No account, terms acceptance, GPU
session, notebook, schedule, GCP integration or cloud resource was created. Kaggle is an experimental
runtime, not a permanent server. Work usage limits and GPU quotas are separate.

## Actual execution and readiness

`tests.export_phase3_readiness` used no injected provider. It ran two bounded localhost preflights
for the family and horror architecture cases. The absent local runtime blocked both. There were:

- 0 completed model inference replies; 0 structurally accepted AI drafts.
- 2 blocked preflights; no actual model-generation failure to attribute to a model.
- 0 generated reference frames, video clips, speech takes or neural audio assets.
- 0 editorial scores, independent human reviews, owner approvals or production-ready outputs.
- No genuine cinematic MP4; duration/resolution/acting/voice quality are unavailable, not zero-quality scores.

Director, Script, weak-script revision and continuity benchmarks await real approved upstream sources.
Visual/art/costume/location experiments await genuine references. Performance/camera/motion media
assessment and video generation await approved weights/compute. TTS/lip-sync await approved local
backends and consented references. Audio finishing, continuity media review, QC and the 15–30-second
benchmark await genuine validated input assets. Growth/YouTube preparation remains software-ready;
no new live OAuth read or metadata posting was attempted. No new creative artifact was produced by
any of the 20 departments in this checkpoint.

Readiness stays separate: software extension tested; model installed=false; connected=false;
real inference=false; technically validated generated output=false; independent creative/media
review=false; end-to-end cinematic integration=false; owner approval=false; production ready=false.
A completed runtime response that later fails JSON validation is counted separately from an accepted
creative artifact. Mocked transport tests exercise that distinction and do not enter actual host results.

## Verification and resume

**246 automated tests passed, 0 failed, 0 skipped; 8/8 standalone checks passed.**
There are 16 new Phase 3 software tests. Exact current totals and log digest: `verification/phase3/tests.json`.
Actual host evidence: `hardware.json`, `status.json`, `approval_request.json` in that directory.
Model sources/decisions: `assets/phase3/model_candidates.json`.

```bash
python -m unittest discover -s tests -p 'test_*.py' -q
python -m tests.export_phase3_readiness
```

New tests cover localhost absence, no fake artifact/score, budgets, cloud/identity/truncation/response-size
rejection, raw invalid-response retention, same-case idempotency, exact model snapshot, genre inheritance,
lab isolation, interrupted-worker recovery, checkpoint repair and actual Streamlit controls. Transport
fixtures are explicitly mocks. Existing real-codec test patterns remain infrastructure tests, not a
Phase 3 filmmaking sample.

No deployment/restart/migration/upgrade, original SQLite/media access, paid resource, download,
external inference, account creation, broader OAuth scope or YouTube write occurred.
Render's three services were read-only checked with autoDeploy=no and trigger=off; their observed
updatedAt values stayed unchanged. Main remains `c03550cb6facc27ba90c3f3286a5b0a0e69748a8`.

Resume after the necessary owner approval recorded in `approval_request.json`. Do not repeat Phase 2,
reinstall unrelated dependencies or retry blocked inference before its prerequisite changes. Download
only the approved candidate, verify its exact digest/license/runtime, then run the first bounded local
text trial. Archive actual raw creative artifacts safely without committing weights/private media.
Apply attributed review and targeted revision before expanding to 30 episodes or expensive video.
Never call this checkpoint completed Phase 3 or completed autonomous filmmaking.
