# Agent registration audit and individual development roadmap

Scope: existing Streamlit/SQLite Studio at baseline cce16c9f533f528168ebe22c511b7a45fae7a132. No live database access. Related modules are reused by preserving their existing pages, not by pretending they are autonomous agents.

## Audit

| Existing module | Classification | Evidence and limitation |
|---|---|---|
| screenwriter.py | Partially implemented; model not connected in this session | LocalWriter and screenplay validation exist; no real inference tested |
| storyboard.py / storyboard_ui.py | Implemented software; offline regression tested | Versioned boards, reference images and approval; not automatic cinematic generation |
| drama_quality.py / drama_quality_ui.py | Implemented software; offline regression tested | Character Bible, dependency fingerprints, reviews, stage gates; no verified AI critic |
| engine.py / providers.py / local_animation.py | Partially implemented | Queue, mock/live interfaces and local animation adapter; no new model execution |
| marketing.py | Implemented software; offline regression tested | Campaign planning and human approval; not autonomous audience research |
| youtube.py | Partially implemented | OAuth and approval guards tested with mocks; no live connection or upload tested |
| Central registry before this change | Absent | Existing roles were scattered across modules |

## Foundation boundaries

Statuses are separate: Registered identity; Configured local identifier; Model Not Connected until inference evidence exists; Tested applies only to documented software tests; Ready is reserved for future verified execution. All 20 remain Blocked for autonomous execution. No Ready flag can be set by typing a model name.

Manual owner task assignment and approved-output handoffs work. Catalog dependencies describe the intended department graph; they are not a mandatory production scheduler in this phase. Concrete task references enforce current owner approval, exact versions and transitive freshness. QC reviews specialist tasks independently of Director. QC-authored tasks cannot self-recommend and remain blocked pending a future independent QC-review policy. The trusted owner UI manually records QC recommendations; there are no model-callable approval tools.

No replacement Character Bible, production records or publishing system was created. The new sidecar agent_control.sqlite3 contains only development records and must be backed up alongside existing data before any future deployment.

## Model evaluation sources

- Qwen3-8B planning candidate: https://huggingface.co/Qwen/Qwen3-8B (Apache-2.0 model card; Bengali quality must be evaluated).
- Wan compatibility candidate: https://github.com/Wan-Video/Wan2.2
- LTX compatibility candidate: https://github.com/Lightricks/LTX-Video

These are evaluation candidates, not installed models or quality claims. All registry operations need CPU only. Planning inference budget estimate: quantized 8B evaluation may need roughly 8–16 GB available RAM, depending on runtime and context; measure before approval. Video VRAM depends on checkpoint, resolution, offload and duration; use the selected official model instructions and measure on an approved existing GPU. No hardware rental or model download authorized here.

## Individual development order

### 1. Director AI
- Existing: redpad_pipeline/ui.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Creative vision, Scene interpretation, Department coordination, Task assignments and revisions.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit direction; prerequisites production_manager; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for creative vision, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 2. Quality Control AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Independent technical and creative review, Evidence-based rejection, Compliance, Quality recommendations.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit quality_review; prerequisites owner brief; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for independent technical and creative review, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 3. Story AI
- Existing: redpad_pipeline/screenwriter.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Research, Original premises, Plot, Character arcs, Dramatic structure.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit story; prerequisites director; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for research, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 4. Script AI
- Existing: redpad_pipeline/screenwriter.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Screenplay, Visual action first, Natural Bengali dialogue, Scene construction, Revisions.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit screenplay; prerequisites story; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for screenplay, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 5. Character AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Identity, Appearance, Character Bible, Facial references, Consistency.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit character_bible; prerequisites script; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for identity, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 6. Art Director AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Sets, Props, Production design, Color palettes, Visual style.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit art_plan; prerequisites director, script; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for sets, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 7. Location AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Bangladeshi architecture, Environment, Room layout, Location references and continuity.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit location_bible; prerequisites script, art; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for bangladeshi architecture, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 8. Costume Designer AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Wardrobe, Costume Bible, Styling, Character and art collaboration.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit costume_bible; prerequisites character, art; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for wardrobe, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 9. Storyboard AI
- Existing: redpad_pipeline/storyboard.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Shot breakdown, Compositions, Camera references, Shot lists, Director review.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit storyboard; prerequisites script, character, location; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for shot breakdown, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 10. Performance Director AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Restrained expression, Acting, Emotional performance, Body language.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit performance_plan; prerequisites script, character; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for restrained expression, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 11. Cinematographer AI
- Existing: redpad_pipeline/storyboard.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Lenses, Framing, Camera movement, Lighting, Composition.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit camera_plan; prerequisites storyboard, art; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for lenses, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 12. Motion & Physics AI
- Existing: redpad_pipeline/local_animation.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Walking, Sitting, Object interaction, Physical realism, Motion errors.
- Candidate: Qwen3-8B locally for structured planning only; evaluate Wan/LTX separately for video, never a physics guarantee.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit motion_plan; prerequisites performance, storyboard; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for walking, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 13. Video Generation AI
- Existing: redpad_pipeline/local_animation.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Cinematic video, Future Wan and LTX adapters, GPU interface, Controlled generation.
- Candidate: Qwen3-8B locally for structured planning only; evaluate Wan/LTX separately for video, never a physics guarantee.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit video_manifest; prerequisites cinematographer, motion, continuity; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for cinematic video, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 14. Voice & Dialogue AI
- Existing: redpad_pipeline/free_voice.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Bengali pronunciation, Emotional voices, Synchronization, Lip-sync planning.
- Candidate: Qwen3-8B locally for structured planning only; Bengali speech synthesis and lip-sync model remains unselected until pronunciation/license review.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit voice_manifest; prerequisites script, performance; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for bengali pronunciation, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 15. Continuity Supervisor AI
- Existing: redpad_pipeline/drama_quality.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Character, Wardrobe, Props, Location, Shot and episode continuity.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit continuity_review; prerequisites character, costume, location, storyboard; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for character, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 16. Music & SFX AI
- Existing: redpad_pipeline/drama_free.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Score, Atmosphere, Foley, Sound effects, Mix requirements.
- Candidate: Qwen3-8B locally for structured planning only; use existing local composition tooling for fixtures; production music model remains unselected.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit sound_plan; prerequisites script, storyboard; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for score, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 17. Editing & VFX AI
- Existing: redpad_pipeline/drama_finish.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Shot selection, Pacing, Transitions, Color, VFX, Subtitles, MP4 assembly.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit edit_manifest; prerequisites video, voice, music; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for shot selection, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 18. Production Manager AI
- Existing: redpad_pipeline/engine.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Schedule, Queue, GPU planning, Costs, Assets, Workflow status.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit production_plan; prerequisites owner brief; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for schedule, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 19. Growth AI
- Existing: redpad_pipeline/marketing.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Audience analysis, SEO, Campaign planning, Promotion, Growth.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit growth_plan; prerequisites editing; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for audience analysis, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

### 20. YouTube AI
- Existing: redpad_pipeline/youtube.py; Partially implemented — related module exists; autonomous agent not verified.
- Missing: verified execution for Channel connection, Metadata, Approval-based upload preparation, Analytics planning.
- Candidate: Qwen3-8B locally for structured planning only.
- Hardware: Registry: CPU only. Inference RAM/VRAM must be measured for selected model before installation.
- Integration: consume {'schema_version': 1, 'brief': 'non-empty string', 'references': 'list of approved task IDs'}; emit youtube_package; prerequisites editing, growth; preserve existing source IDs and hashes.
- Test: invalid/missing inputs, stale dependencies, realistic Bengali examples for channel connection, human blinded quality comparison, failure recovery and no-paid-network guard.
- Completion: Real representative Bengali fixtures, recorded inference evidence, human quality review, regression and safety tests pass

