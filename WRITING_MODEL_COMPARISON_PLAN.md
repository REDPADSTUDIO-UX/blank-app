# Writing model comparison — research only, 2026-11-06

No alternative model has been downloaded, executed or selected as a winner.
The installed control remains Qwen3-4B-Instruct-2507 Q4_K_M. General vendor
benchmarks do not establish the quality of Bangladeshi Bengali dramatic writing.

| Candidate | Official license / characteristics | Reason to compare | Unresolved constraint |
|---|---|---|---|
| Qwen3-4B-Instruct-2507 | Apache 2.0, 4.0B, non-thinking | Existing measured CPU control; no download | Demonstrated causal/dialogue/editorial weaknesses |
| Qwen3.5-2B | Apache 2.0; non-thinking by default | Smaller candidate for a bounded text-only trial | Exact compatible quantization, bytes, runtime version, CPU RSS and Bengali creative quality untested |
| Gemma 3 4B IT | Gemma license; multilingual model family | Different model family for dialogue comparison | License terms, exact quantized artifact and CPU support must be checked; multilingual coverage is not dramatic-quality evidence |
| Gemma 4 E2B IT | Apache 2.0; 2.3B effective, 5.1B including embeddings | Another model family designed for local use | E2B does not mean a 2B memory footprint; artifact size, runtime support and Bengali quality untested |

Sources read on 2026-11-06 (primary model cards):
- https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- https://huggingface.co/Qwen/Qwen3.5-2B
- https://huggingface.co/google/gemma-3-4b-it
- https://huggingface.co/google/gemma-4-E2B-it
- Structured output implementation reference: https://docs.ollama.com/capabilities/structured-outputs

## Protocol proposed for later approval

1. Identify the exact local-runtime artifact, license, SHA/digest, download bytes,
   estimated resident memory plus context/cache, and compatible runtime. Ask the
   owner before any additional large model download. No remote/paid inference.
2. Reuse the same umbrella brief, initial state, causal-beat and scene contracts.
   Keep canonical NFC, context 4096, seed 42, per-stage output/time budget and
   hardware fixed. Report any model-specific template/sampling differences.
3. One short pilot per candidate, then (only if feasible) three paired seeds per
   task. Limit each stage to two explicit attempts; save unsuccessful attempts,
   raw replies, request/schema hashes, model digest, stop reason, timing, tokens
   and peak RSS. Do not silently increase context, buy compute or change models.
4. Separate JSON/schema completion, state consistency and evidence grounding
   from actual literary merit. Do not use field presence as a logic/emotion score.
5. Give independent fluent Bangladeshi Bengali readers randomized anonymous
   candidates and a blank rubric. Record exact quoted evidence, causal
   contradictions, motivation, emotional progression, scene payoff, earned
   ending, responsive dialogue, character wit, filmability and pronunciation.
   Ideally use two readers and adjudicate disagreement; model self-review is
   never counted as independent human review.
6. Include both an open-brief test and a state-constrained test. The current
   staged pilot has stronger constraints and different budgets from the old
   checkpoint; it is diagnostic evidence, not a controlled model-quality win.
7. Choose only after blind ratings, failure rate and CPU cost are available.
   Keep all drafts outside production approval until existing QC/owner gates pass.

## Current status

Research and comparison protocol prepared. Downloads: zero. Alternative-model
inference: zero. Independent human evaluations: zero. No winner claimed.
