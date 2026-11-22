# REDPAD screenplay agent upgrade

The original AI Script Agent explicitly prohibited stage directions and wrote voiceover only. The new screenplay desk in AI Production provides a separate visual-first drama workflow while retaining legacy narration.

## Implemented
- Versioned curriculum: eight craft lessons, three original Bangla weak/strong examples, one licensed two-scene screenplay opening, and three attributed craft references.
- Every writing call receives the lessons and actual Sintel opening, not just links. Genre lessons are selected by genre. This is in-context instruction, not weight training or an exhaustive screenplay collection.
- Four bounded model calls: opening/causal planning, draft, editorial critique, rewrite. The rewrite also receives deterministic structural failures.
- Action and dialogue remain ordered beats. Validation checks action-first openings, declared speakers, Bangla prose, causal scene fields, motivated sound notes, timeline totals and rough speech density.
- No model score or structural test can grant artistic approval. Outputs remain needs_revision or needs_editorial_review.
- UI saves separate versioned draft files and exposes reload/download. It never overwrites existing content, feeds stage directions to narration TTS, or publishes.
- Existing paid narration generation now respects REDPAD_ENABLE_PAID_GENERATION.

## Runtime and honest limits
The adapter uses an already-installed local Ollama model selected by REDPAD_LOCAL_WRITER_MODEL. It calls fixed loopback only, disables proxies, rejects cloud model names and remote model metadata, and never downloads a model or falls back to a paid provider. A capable Bangla local model and adequate RAM/GPU are required. No local writer is installed/configured in this execution environment; actual model generation and artistic improvement have NOT been measured. Render's free instance is not assumed capable of hosting a writing model.

The complete prompt is downloadable without a model. Configuring a model is an engineering task, not an instruction for the owner to use a terminal. Deployment remains pending verified backup/recovery of the live database/media. No deployment, restart, migration, billing or publication was performed.

## Source provenance
Sintel Draft 4 revision 2 (2009-11-06), Esther Wouda with revisions by Colin Levy. Only the two opening scenes are included, extracted with pdftotext; whitespace changed, words unedited.
© copyright Blender Foundation | durian.blender.org
CC BY 3.0: https://creativecommons.org/licenses/by/3.0/
Source: https://durian.blender.org/wp-content/uploads/2009/11/1stminute_script_11-61.pdf
License evidence: https://durian.blender.org/sharing/
Other sources and original summaries are in assets/writing/curriculum.json. Public availability is not treated as permission to copy entire scripts. Future additions require source, author, scope, license and attribution verification.

## Verification
2026-11-05: nine offline unit tests passed, including malformed drafts, action/dialogue ordering, unknown speakers, invalid durations, complete four-pass prompt delivery and no-config/cloud blocking. Python compilation passed. Injected test completions are fixtures, not actual LLM output. No production records used or modified.

## Next acceptance step
Run the configured free local writer on the same unseen horror, family and romance briefs with/without curriculum. Blindly review hook, action readability, causality, Bangla dialogue, emotional progression and continuity with scene-specific evidence. Record actual model/version, drafts and reviews. Do not label the agent trained/perfect before this test.
