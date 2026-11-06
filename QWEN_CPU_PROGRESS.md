# REDPAD — authorized Qwen CPU inference and Bengali quality results

**Runtime/model installation and genuine Story/Script/Director inference are verified. Bengali creative
quality has not passed. Phase 3 and autonomous cinematic production remain incomplete.**

The owner explicitly authorized Ollama plus only Qwen3-4B-Instruct-2507 Q4_K_M on this development host.
Started from feature checkpoint `21574648dac4f9b8006020dd693c3d61444ce98b`; preserved Phase 1/2 work.
Verified installation/smoke checkpoint: `ba6ca005e6561db235b77240ad51996802ff02bd`.
Verified Unicode correction/baseline evidence checkpoint: `2163e048f819a6eab2e67a91a86d8ec19f0fff84`.
Use the latest actual `feature/video-music-editing-studio` HEAD for the final evidence with this report.

## Installed and measured

| Item | Actual result |
|---|---|
| Runtime | Official Ollama **0.40.15**, development directory; no system service |
| Runtime checksum | Official release archive SHA256 `628c018404a4206493efd38e46251c154ede5141b8b8dc85c659b3b027c47379` verified before extraction |
| Model | `qwen3:4b-instruct-2507-q4_K_M`, **2,497,293,803 bytes**, GGUF Q4_K_M |
| Model manifest | `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0` |
| License | Apache-2.0 model label and exact authorized tag; no other model downloaded |
| Model architecture | Runtime reports Qwen3, Instruct, 4,022,468,096 parameters |
| Compute | Existing CPU only; reported **VRAM=0** |
| Host | 9 logical CPUs, about 9.73 GiB total RAM; exact audit in hardware_after_install.json |
| Sampled peak aggregate RSS | **4,537,593,856 bytes** (~4.23 GiB), including caller and server/runner; not unique model allocation |
| First small inference | 127 output tokens; **23.697 seconds** including cold load/prefill, ~13.7 decoded tokens/second |
| Aggregate measured decode | **8.11 tokens/second** across replies with decode counters; different contexts/output lengths, not a universal speed guarantee |
| Additional downloads | No additional model, GPU library extraction, rented GPU or cloud resource. The official runtime bundle was downloaded; CUDA/ROCm/Vulkan directories were excluded from extraction. |

Command environments isolate loopback. Installed runtime and client therefore run in the same owned
`local_cpu_session` context, cloud disabled, one model/worker, CPU forced. The context starts no system
service, never downloads anything and stops only its own runtime. Installed model files remain cached
under ignored `phase3_models/`. They must not be committed or copied into production storage.

## Actual model attempts — not software test counts

| Result | Count / meaning |
|---|---|
| Actual model calls | **17**: 13 creative research calls, 3 small controls/smokes, 1 actual task-engine roundtrip |
| Complete runtime replies | **13**; a completed reply is not necessarily correct or useful |
| Incomplete/failed runtime attempts | **4**: one request failed at 420.146 seconds; three replies exhausted their token allowance |
| Initial contract rejection despite complete reply | **2**: invented Director quote; Script returned a single target object instead of the requested array |
| Accepted experimental micro-contracts | **7**; field/timing/speaker validity only, no artistic approval |
| Target-wrapper postcheck | One object can be wrapped as the single requested s2 without modifying s1. No new inference or creative improvement is claimed for this normalization. |
| Actual task engine | Genuine local inference persisted through Engine/AgentStore and ended **Awaiting QC**, not Approved |
| Task-engine content | Repeated input instructions rather than writing original material; now flagged as an input-echo warning |
| Independent human review / owner output approval | **0 / 0** |
| Genuine image/video/speech/audio assets | **0 / 0 / 0 / 0** in this text-only benchmark |
| Genuine cinematic MP4 | **None** |

The complete record manifest, counters, timings, failures and raw-response hashes are in
`verification/phase3_cpu/summary.json`. Original full and partial replies are saved per call.
The first non-streamed 420-second failure produced no received raw text or decode counters; those
cannot be reconstructed and are not fabricated. Subsequent streaming preserves partial responses.
Mocked transport/unit fixtures are temporary software tests and are not counted among these 17 calls.

## Demonstrated issues and fixes

### 1. Canonical Bengali Unicode input

The exact-copy control passed arithmetic and object transfer but returned `তানি<tool_call>া` instead
of the supplied Bengali name. Repeating the identical semantic prompt with canonical **NFC** text,
the same model, seed, context, temperature and output allowance returned the correct `তানিয়া`.
The marker was text, never an executed tool call.

This paired observation justified normalization in the actual LocalWriter adapter. System/prompt text
is normalized before sending; normalization status and normalized wire prompt hash are recorded.
Raw responses and original request snapshots remain unchanged. Text evidence matching accepts
canonical-equivalent spelling while still rejecting invented words. ASCII task/scene IDs remain intact.
This corrects a measured identity/input problem; it does not prove all Bengali output is good.

Four explicit post-fix retests used the same approved model. Correct canonical names appeared in the
new Story and Script. The downstream script/critic consumed the newly generated upstream candidate,
so this is a pipeline retest, not an isolated claim that every downstream change is caused only by NFC.

### 2. Failure/output preservation and resource bounds

Large structured architecture did not finish within the 420-second experiment bound. Streaming now
preserves incomplete output, enforces a response-size/wall-time bound and rejects truncated drafts.
CPU timeouts are configurable only within 30–600 seconds; the default remains 180. The installed CPU
UI mode uses a measured 4096-token context and bounded output allowance instead of blindly using
large generic defaults. Endpoint/model override through runtime settings is rejected.

The finite creative pilot expanded explicitly from eight calls to nine for a prompt-order control,
then thirteen for four post-normalization retests. Three small runtime/control calls and one actual
Engine roundtrip are separately identified. There is no automatic further regeneration or paid fallback.

### 3. Rewrite and evidence integrity

The local transport accepts structured object or array JSON, enabling targeted scene-array replies.
A single s2 object can be normalized only to a one-element target list; scene ID, timing, speakers
and unchanged s1 are checked. Original raw/model rejection records remain preserved.

The initial Director inserted a name into an alleged exact quote; it was absent from the actual script
and the evidence validator rejected it. Canonical matching does not make such invented content valid.
Later Director replies were truncated and were not promoted to accepted QC. The model's own praise
was not used as a quality pass.

### 4. Input copying is not creative generation

The actual Engine call completed, validated department fields and stored a version for independent QC.
However, the model copied the supplied instructions. A canonical input-echo warning now makes that
limitation visible. Echoing may preserve intentionally supplied facts, so it does not automatically
invalidate every preservation task; it establishes no new creative material. Nothing bypasses owner
approval because a model returned JSON or because a runtime call succeeded.

## Bengali creative findings

These are **Codex assistant/model-based editorial observations**, not independent human review.
No numeric quality scores were invented. `editorial_review.json` links each finding to actual output;
`BENGALI_SAMPLES.md` presents original model samples without manually improving their wording.

| Area | Observed result |
|---|---|
| Story logic | Still weak after identity correction. Rain, travel and umbrella possession do not form a sufficiently clear causal progression. |
| Natural dialogue | Remains unnatural; the corrected breakfast request still returned “আমি বাবার চোখে দেখি না।” The requested meaning and gentle wit were not demonstrated. |
| Emotion / warmth | Not established by these short lines and repetitive behavior; no actor performance was generated or judged. |
| Humor | No reliable character-based humor improvement demonstrated. |
| Hook / ending | Repeated umbrella possession questions do not establish a convincing earned family-drama ending. |
| Character identity | Specific Unicode-name corruption improved in the controlled probe and post-fix Story/Script. Narrative identity/continuity still requires editorial review. |
| Director criticism | Not reliable enough to replace independent QC: an invented quote, questionable language advice and incomplete replies were observed. |
| Targeted revision | Untouched-scene preservation can be verified mechanically; the generated revision did not fix the main causal/language issues. |
| Music/SFX text | Some fields describe visual or ambiguous events rather than a motivated sound plan. No audio was generated/listened to, so audio quality is unverified. |

This evidence does not support declaring Qwen3 4B Q4_K_M a suitable production Bengali head writer,
Director or autonomous critic in the tested configuration. It also does not establish that other
models/quantizations, prompts or larger compute budgets cannot work. No further large model was
silently substituted or downloaded.

## Studio integration and boundaries

- All **20 registered departments** remain. Only the existing Story, Script and Director were configured
  to share the approved writing model; no extra agents or twenty separate models were created.
- These three have integrity-checked historical local-inference evidence. Current API availability is
  distinct and depends on the owned local context; typing a model name alone is not inference proof.
- Research candidates can be inspected/downloaded in the existing Phase 3 dashboard. They consume
  unapproved experimental sources only in that research ledger. Production handoffs retain current
  approved-version/QC/owner guards. No candidate was silently promoted to an approved source.
- The true task-engine roundtrip uses existing department validation and immutable output storage.
  Its single Story artifact remains Awaiting QC; content echo is disclosed separately from connection.
- The one-minute script has estimated 30+30-second scene slots. It is not a table-read timing result,
  a five-minute episode, a complete 30-episode season or proof of reliable end-to-end filmmaking.
- Software regression includes clearly labeled synthetic codec fixtures. Those MP4 test patterns are
  infrastructure tests, not this Phase 3 cinematic benchmark.

## Verification and recoverable evidence

**258 automated tests passed; 0 failed; 0 skipped. 8/8 standalone checks passed.**
New safeguards cover Unicode wire normalization, canonical evidence, streaming/partial replies,
array transport, bounded settings, input echoes, archive integrity and installed manifest detection.
Existing Director/Story/Script, department, approval, recovery, UI and media regression remains intact.
Exact command, counts and log digest are in `verification/phase3_cpu/tests.json`.

Key files:

- `installation.json`, `hardware_after_install.json`: exact model/runtime/hardware facts.
- `cpu_smoke.json`, `control_probe.json`, `nfc_control_probe.json`: measured controls.
- `trial_*.json`: immutable request, actual raw reply, parsed result, model settings, timing and validation.
- `engine_roundtrip.json`, `engine_echo_postcheck.json`: actual Engine call and content limitation.
- `script_revision_postcheck.json`: scope-preserving wrapper normalization, no new model call.
- `summary.json`, `editorial_review.json`, `BENGALI_SAMPLES.md`: case manifest and attributed findings.
- `development_agent_configuration.json`: recoverable approved development configuration.

```bash
python -m experiments.export_qwen_evidence
python -m unittest discover -s tests -p 'test_*.py' -q
```

Completed trial names are immutable/cache-checked. Do not rerun them or redownload weights if the
approved installation is present. Interrupted partial responses require inspection and an explicitly
named retry. Restore only the three approved agent configurations if the development sidecar is lost.
Weights/private runtime logs remain outside git. Raw original fictional text/evidence is committed.

## Remaining Phase 3 work and safety

The full coherent 30-episode writing test, independently accepted five-minute screenplay and reliable
script repair benchmark remain pending. The bounded larger architecture failed; smaller complete
outputs still fail creative quality. More broad generation with the same setup was stopped after the
observed limited improvement, rather than treating structural passes as success.

Necessary next steps are a source-aware Bengali editorial evaluation and a separately approved
comparison with another suitable writing model/configuration. Any additional large model download
requires owner approval. No model winner, premium-writing score or weight training is claimed.

Visual identity references, realistic acting/motion, video and local Bengali speech experiments require
approved compatible weights and compute that are not available/authorized in this checkpoint. No GPU
was rented or enabled; no new cloud resources were created. Voice rights/consented references and
independent listening/visual review remain prerequisites. The 15–30-second genuine MP4 benchmark
must wait for validated genuine inputs and approvals; nothing was replaced with a slideshow or test bars.

Only the feature branch was written. Main remains `c03550cb6facc27ba90c3f3286a5b0a0e69748a8`.
No Render deployment/restart/migration/upgrade or original production database/media operation
occurred. All three Render services were read-only checked with auto-deploy off. No paid API/billing,
OAuth scope change or YouTube upload/publish/schedule occurred. Future deployment still requires
full backup and independently verified restoration.
