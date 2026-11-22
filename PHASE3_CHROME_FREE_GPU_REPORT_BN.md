# Chrome free GPU access — ১২ নভেম্বর ২০২৬

সর্বশেষ remote/local feature checkpoint `3ef4dac7aa259ceeec9d364570aca146a6b54f38` মিলিয়ে continuation। Existing ২১ agents, candidates, model selection gates, Dashboard ও Casting অপরিবর্তিত। পূর্বের সফল benchmarks,418 regression,4 retry ও8 ledger tests পুনরায় চালানো হয়নি। নতুন engineering/test pass দাবি নেই।

## এখন যা প্রকৃত যাচাইকৃত

| Provider | Chrome-এ প্রত্যক্ষ ফল |
|---|---|
| Lightning AI | “Coming soon — Lightning hasn't expanded to your area yet.” Region restriction; bypass নয়। Account credits বা GPU অযাচাইকৃত। |
| Hugging Face | Owner account signed in। Existing Gemma3 12B Space Running on Zero এবং input UI দেখা গেছে। নতুন prompt submit বা আগের unknown request poll করা হয়নি। Personal quota অযাচাইকৃত। |
| Google Colab | Owner account signed in; Python3 T4 runtime সত্যিই connected; standard notebook cell দিয়ে নিচের tensor canary সফল। Resources pane: not subscribed, zero compute units, resources free of charge/not guaranteed। |

Chrome extension connection এখন **সফল**; এটি পূর্বের আলাদা cloud browser নয়। Login/verification handoff এইবার প্রয়োজন হয়নি। কোনো password/token/OTP পড়া বা সংগ্রহ করা হয়নি।

## প্রকৃত Colab runtime result — model inference নয়

- GPU: **Tesla T4**, total **15360 MiB /15 GiB**, free14910MiB at query; driver580.82.07।
- Host MemTotal:13286932KiB ≈**12.67GiB**; available11623284KiB at capture।
- `/content` disk: total120942624768bytes ≈112.64GiB; free120839057408bytes।
- Python3.13.16, Torch2.14.1+cu130, CUDA13.0 reported by actual cell।
- CUDA512×512 matrix multiplication: finite=True, result shape512×512; timed section **0.368457018s**; peak Torch allocation12451840bytes। This includes initial CUDA/tensor overhead; not model speed or general GPU throughput benchmark। Cell UI whole duration4s।
- Resources pane said runtime **may last up to5h10m**; maximum/remaining access is not guaranteed or a reserved quota।
- **New model generation0; new weights downloaded0; paid compute0; human artistic reviews0।** Previous actual hosted image retained unchanged; not generated again।

Raw result: `verification/chrome_free_gpu/colab_runtime_canary.json`। [Saved owner notebook](https://colab.research.google.com/drive/150YpQztfxOZY9q8hX4ixCOEJqX8RDeev) retains code/output, no sharing change। Notebook name `REDPAD_Phase3_Free_GPU_Preflight.ipynb`। No SSH, remote desktop, background daemon, public endpoint or free-tier bypass। GPU cell stopped; no keepalive। Runtime remained connected at last observation: reset/delete confirmation was cancelled, so notebook/runtime-local data were not silently deleted. Free runtime may expire normally; do not claim it was released or will remain available next turn।

## কেন existing model benchmark চালানো হয়নি

Existing source-to-NF4 Qwen3.5-9B gate is12GiB GPU/**16GiB host RAM**, source weights19.31GB; Gemma3-12B gate16GiB GPU/24GiB host RAM, source weights24.37GB plus gated custom terms। Actual Colab host RAM12.67GiB is below these conservative unmeasured engineering gates। Those gates were not lowered to force a test. Neither source-model download has current exact approval।

Previous hosted Gemma request remains completion-unknown after automatic approval review rejected external benchmark/source egress and hosted fallback। New Chrome login is not specific approval for that payload disclosure. No alternate access or retry bypassed that rejection. The existing exact outbound-payload consent request remains pending. This does not turn authenticated free Space access into a verified writing output or equivalent checkpoint benchmark।

## Concrete next approval — low-memory writing variant

New GGUF variant investigation is justified by **new measured RAM constraint**, not repeat of earlier broad model research. Exact metadata captured directly from Hugging Face publisher repository, no weights fetched:

| Field | Requested scope |
|---|---|
| Model | `unsloth/Qwen3.5-9B-GGUF` / `Qwen3.5-9B-Q4_K_M.gguf` |
| Exact repository revision | `3885219b6810b007914f3a7950a8d1b469d598a5` |
| Exact file bytes | **5680522464bytes —5.68GB /5.29GiB**; runtime dependencies/build artifacts extra |
| Exact expected SHA256 | `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8` |
| License | Publisher metadata Apache-2.0, ungated; license/notices must be preserved. No new terms accepted. |
| Environment | Only owner's verified free Colab T4; no paid fallback |
| Planning memory |8–10GiB VRAM,4–8GiB host RAM for short text-only2048 context; estimates, not measured model peak or guaranteed fit |
| Intended tests | First one bounded GPU load/generation canary; then existing causal/dialogue and grounded Director/QC controls, one at a time, max512 new tokens,180s first-call budget. No weak4B reruns. |
| Specialist workflow | Story/Script/Director/QC exploratory candidate only; other17 agents/selections unchanged |

This is **not installed or integrated yet**. Exact supported llama.cpp CUDA build and adapter still need validation after approval; existing NF4 worker is not silently reused or relabeled. No vision/mmproj/other model download is included. Changed precision/context/token cap must use a distinct experiment variant; equivalent comparisons require the same bounded settings across candidates and independent Bengali review. One9B candidate alone cannot choose the best model for all roles।

Next: obtain owner approval for this exact5.68GB file + free-runtime text test; recheck available T4/session; verify pinned runtime/hash; canary first; preserve raw output before continuing existing suite. No creative improvement, quality score, model winner, all21-agent completion or Phase4 claim is supported by a tensor test।

## Safety / evidence

Only `feature/video-music-editing-studio` may be updated. Main remains `c03550cb6facc27ba90c3f3286a5b0a0e69748a8` at verification. No Render mutation/deployment/restart, production DB/media access, billing, large weights, paid API/GPU or YouTube publishing. New files are access/canary evidence and the concrete approval proposal; model service/engine/Dashboard code unchanged।
