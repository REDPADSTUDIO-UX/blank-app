# REDPAD AI Studio — Phase 2 specialist software delivery

বাকি ১৭ বিভাগের software workflow, contract, dashboard execution ও micro-test বাস্তবায়িত।
মোট এজেন্ট ২০/২০; Director, Story ও Script-এর বিদ্যমান কাজ সংরক্ষিত।
এটি real-model বা সিনেমার সৃজনশীল মান যাচাইয়ের ফল নয়। Phase 3 চালানো হয়নি।

Repository: REDPADSTUDIO-UX/blank-app. Branch: `feature/video-music-editing-studio`.
Creative baseline: `7c79f063f5c2afefcfed60432f8c2a110dc19144`.
Stage A checkpoint: `7217eb44e12a959e7a91ee9a2b5fc130527b4c40`.
Stage B checkpoint: `274f325ec3685dde76b81f961adf53c60a1e90f3`.
Stage C checkpoint: `d0b217549f88f800290e1c13419bffdd1ef708be`.
Stage D and final evidence are saved with this document; use the current feature-branch head.

## Implemented department matrix

All rows have positive execution, domain-specific negative/defect cases, missing-model blockers,
QC/owner boundaries, immutable revision/handoff tests and individual dashboard execution tests.

| Stage | Specialist | Implemented workflow | Negative micro-test |
|---|---|---|---|
| A | QC | Supplied review provenance/severity, source character-state comparisons, media specification rules, revision routes, approved-review routing to exact task version | Self-review rejected; inconsistent hair detected; invalid fps actionable blocker |
| A | Character | Versioned identity Bible, identity hashes, relationships, age/face/hair/personality/evolution, reference/state records and typed downstream links | Invalid age and unknown relationships rejected |
| A | Art Director | Set/prop/palette/culture/period/light specifications, scene briefs, targeted change impact | Invalid inventory rejected; changed prop identifies affected scenes |
| A | Location | Room graph, architecture/geography, openings, camera access, reference records | Asymmetric connections and contradictory destinations for the same door flagged |
| A | Costume | Character/scene wardrobe, color/material/weather/culture/accessory/reference records, justified changes | Unexplained outfit change flagged; documented change accepted |
| B | Storyboard | Approved structured screenplay → bounded coverage slots; shot IDs/order/action/purpose/composition/references/performance; existing Studio board export | Invalid order or scene IDs rejected; single-shot revision preserves other shots |
| B | Performance Director | Emotional transitions, subtext/gaze/body/micro-expression/blocking/pause/intensity, approved Character-state comparison | Intensity >10 rejected; conflicting emotional transition flagged |
| B | Cinematographer | Lens/height/angle/movement/light/exposure/color/framing/screen direction and scene-axis records | Unmotivated A/B axis change flagged; explicit reset accepted |
| B | Motion & Physics | Timed pose transitions, support/contact, object state/permanence, gravity/collision constraints | Unsupported sitting and contradictory pose/object actions flagged |
| B | Continuity | Episode/scene entity state, costume/prop/location/time/camera attributes, justified changes, impacted shots | Unexplained state drift flagged; documented change accepted |
| C | Video Generation | Provider capability/preflight interfaces, request lifecycle, local SVD native mapping, Wan/LTX contract boundaries, isolated file inspection and provenance | Unsupported modes rejected; missing runtime blocks; invalid synthetic clip rejected |
| C | Voice & Dialogue | Bengali NFC/whitespace preparation, speaker/character lock, pronunciation dictionary, emotion/pace/pauses, estimated lip-sync slots, local speech interface | Speaker remapping, invalid pauses rejected; missing local TTS blocks |
| C | Music & SFX | Emotion/motif/cue sheets, ambience/Foley/SFX, timing, mix/ducking constraints, asset/license/review metadata; existing local cue bridge | Escaping/remote asset paths rejected; unknown rights block readiness |
| C | Editing & VFX | Ordered contiguous EDL, source bounds, cut/fade/color/VFX metadata, subtitles and export profiles, existing isolated quality-gated renderer | Invalid source/subtitle timing rejected; missing media flagged; export path remains null until actual render |
| D | Production Manager | Resource-aware DAG/order/parallel batches/estimates, queue/inventory/approval monitoring, recovery, cost prohibition; actual 17-department queue with approved creative dependencies | Cycles/paid work rejected; absent GPU blocks related jobs while independent jobs continue |
| D | Growth | Bengali/English metadata, audiences/genre/thumbnail/trailer/campaign/calendar, objective concept comparison, existing marketing metric aggregation | Overlength title/invalid date/metrics rejected; no posting or campaign execution |
| D | YouTube | Channel profile/metadata/checklists, preparation-only action, fixed readonly scope, secure read-only analytics boundary | Upload/publish/schedule/scope escalation rejected; missing OAuth reported without credential exposure |

## Contracts and integration

The opt-in `specialist_v1` envelope has exactly `specialist_v1`, `project`, `records`,
`sources`, `base`, `targets`. Original fixtures are in `specialist_examples.py`; they are
manually authored Bengali production metadata, never model-generated samples.

`records` hold stable IDs and department fields. `sources` bind named departments to exact
current owner-approved artifacts through `$from` task IDs and paths. Source department/type,
version and transitive freshness are checked before execution and again before saving output.
Character, location and shot references are validated against supplied approved Bibles.

`base` is either an exact approved dependency artifact or this task's immutable prior revision
following a recorded revision request. `targets` restrict changes to selected record IDs.
Derived hashes/analytics are excluded from comparisons. Approved versions are never overwritten.
Changes still await independent QC and owner approval. QC tasks are reviewed by the owner;
QC cannot self-recommend, approve other tasks or invoke publishing.

The existing owner-gated Agent Control Center has all 17 individual specialist forms, editable
contracts, approved source binding, execution modes, output tables/JSON/downloads, source data,
findings, errors, retry/recovery, model configuration and revision controls. The Storyboard workspace
can prepare coverage from a selected approved screenplay. Reference IDs from this deterministic
coverage draft must be mapped to the final approved Character/Location Bibles, and shot composition
needs Director review. Placeholder references never become rendered images.

Production Manager can queue the actual branched graph in `specialist_project.py`. Independent
software tasks use a bounded worker pool; model/media execution is explicit. Repeated identical
project requests use durable idempotency keys, including recovery mappings. The engine blocks
consumers until owner approval, not merely until a producer finishes. Earlier independent QC tasks
can be assigned through existing source/reference controls at any production stage.

Local text-provider responses are restricted to records, so they cannot remove source/revision
constraints. Raw attempts and hashes are retained. Model-authored QC observations are forced to
`unverified_model`; deterministic source/specification checks remain separately attributable.
All workflow-level artistic judgment remains subject to human review.

## Verification and reproducibility

Final acceptance: **230 tests passed, 0 failed, 0 skipped**; **8/8 standalone entry points passed**.
All 17 specialist workspaces passed Streamlit execution tests. Stage D is complete.

See `verification/specialists/tests.json`, `matrix.json`, `standalone.json`, `audit_summary.json`.
The matrix exporter reproduces 17 positive/domain-negative cases in temporary sidecars with network
calls prohibited. It confirms 20 registered agents and zero actual model inference.

Commands:

```bash
python -m unittest discover -s tests -p 'test_*.py' -q
python -m tests.export_specialist_evidence
```

`tests.test_specialists` verifies department rules and safe MP4 inspection.
`tests.test_specialist_integration` covers approved creative sources, exact/stale handoffs,
all-department revisions/approval boundaries, branched execution, idempotency/recovery, QC routing,
provider/scope boundaries and real-model absence.
`tests.test_specialist_ui` executes every specialist's actual Streamlit intake/run/inspection,
plus the approved-screenplay coverage button. This is Streamlit AppTest, not a browser visual audit.
Existing Director/Story/Script tests remain in the full regression suite.

Media tests use explicitly synthetic codec patterns, tone audio and temporary media roots.
The local ffprobe adapter checks real bytes, streams, dimensions, duration and content hashes;
it accepts bounded MP4/MOV/WAV only, rejects playlists/symlinks/escaping paths, uses no remote
protocol, and reports inspection as non-generation. Existing FFmpeg assembly tests exercise codecs,
layered audio/subtitles and quality gates; editorial gates mocked in the codec fixture are identified
as test-only. These tests establish software/media plumbing, not neural video, acting or music quality.

## Model and production limitations

- No actual writing-model inference, image generation, neural video, Bengali TTS or real-media artistic
  evaluation occurred in this phase. Injected provider responses are marked simulation.
- The local text runtime/model and CUDA/checkpoints are unavailable on this host. The current software
  connects through the existing fixed-loopback LocalWriter and never downloads checkpoints automatically.
- SVD retains its existing native 1024×576, 25 frames at 7 fps interface. The new adapter rejects other
  native requests, maps isolated reference/seed controls, and validates the actual output before QC.
  It is image-conditioned; a text prompt is editorial guidance, not a claimed conditioning capability.
  Face consistency, multi-character control, photorealism and acting remain unverified.
- Wan/LTX are future-compatible local provider contracts with explicit unavailable-backend states,
  not installed or benchmarked integrations. An approved actual backend/checkpoint is required.
- Bengali local TTS is unavailable; pronunciation and lip-sync plans do not prove speech quality or
  phoneme alignment. The adapter does not fall back to remote gTTS.
- Music planning and code-synthesized sketches require listening review. Motion rules are not a physics
  simulator. VFX/color entries are requirements metadata, not finished compositing/grading.
- Generation jobs, rendering and inspection remain isolated under `agent_media`; the existing gated
  renderer requires an actual approved isolated quality project and selected valid assets.
- Read-only OAuth must be verified in existing secure YouTube Connect; this workflow cannot assert a
  live connection. No upload scopes, upload, schedule or publish operation is available here.
- All departments remain blocked for production-quality readiness despite passing software tests.

## Safety and continuation

No Render deployment/restart/migration/upgrade, original database/media mutation, paid service,
model download, new cloud resource or YouTube write occurred. All three existing Render services
were read-only checked with autoDeploy=no / autoDeployTrigger=off. `main` remained
`c03550cb6facc27ba90c3f3286a5b0a0e69748a8`.

Continue from the latest actual feature-branch head; do not repeat Stages A–D. The agent sidecar and
isolated media need the same verified backup/restore policy before any future deployment.

Phase 3 prerequisites: an explicitly approved existing local/free runtime with selected licensed
checkpoints and measured RAM/VRAM; approved character/location references and voice rights;
secure read-only OAuth for any live read; independent Bengali creative/listening/visual reviewers.
Then run bounded real inference with provenance, blind Bengali script/acting/voice/music assessment,
short per-department media tests and one approved end-to-end production fixture. Repair failures
before expanding duration. Live deployment still requires full backup and independently verified
restoration. Phase 3 and live deployment were not executed.
