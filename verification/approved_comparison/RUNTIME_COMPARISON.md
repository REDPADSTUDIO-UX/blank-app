# Observed CPU results
Six identical cases per arm. Original baseline reused; eighteen new calls. No human creative acceptance.
| Model / thinking mode | Complete + schema valid | Failed | Total call seconds | Peak sampled aggregate RSS, GiB |
|---|---:|---:|---:|---:|
| qwen3:4b-instruct-2507-q4_K_M / runtime default | 6/6 | 0/6 | 214.350 | not sampled |
| gemma3:4b-it-q4_K_M / runtime default | 6/6 | 0/6 | 107.266 | 4.250 |
| qwen3.5:4b-q4_K_M / runtime default | 0/6 | 6/6 | 678.910 | 4.700 |
| qwen3.5:4b-q4_K_M / false | 6/6 | 0/6 | 195.485 | 4.603 |

| Model / mode | Critic task | TP | FP | FN | Precision | Recall |
|---|---|---:|---:|---:|---:|---:|
| qwen3:4b-instruct-2507-q4_K_M / default | criticism | 1 | 0 | 0 | 1.0 | 1.0 |
| qwen3:4b-instruct-2507-q4_K_M / default | qc | 1 | 0 | 0 | 1.0 | 1.0 |
| gemma3:4b-it-q4_K_M / default | criticism | 1 | 0 | 0 | 1.0 | 1.0 |
| gemma3:4b-it-q4_K_M / default | qc | 0 | 3 | 1 | 0.0 | 0.0 |
| qwen3.5:4b-q4_K_M / default | criticism | — | — | — | no completed answer | no completed answer |
| qwen3.5:4b-q4_K_M / default | qc | — | — | — | no completed answer | no completed answer |
| qwen3.5:4b-q4_K_M / off | criticism | 1 | 2 | 0 | 0.3333333333333333 | 1.0 |
| qwen3.5:4b-q4_K_M / off | qc | 0 | 3 | 1 | 0.0 | 0.0 |

Only one seeded defect; strict line/category matches do not validate semantic correctness or editorial remedies. Qwen3.5 QC mentions the contradiction under L2/motivation, which this scorer penalizes; semantic partial credit needs independent review.
Default Qwen3.5 failure is token exhaustion, not a measured timeout. Each failed call generated 1024 tokens with empty final content.
Sampled aggregate RSS double-counts shared pages; it is not a minimum RAM requirement. CPU load was not isolated.

## Per-case timings
| Model / mode | Case | Wall seconds | Generated tokens | Finish reason | Status |
|---|---|---:|---:|---|---|
| qwen3:4b-instruct-2507-q4_K_M / None | story | 52.605 | 301 | stop | validated_stage |
| qwen3:4b-instruct-2507-q4_K_M / None | romance | 37.44 | 237 | stop | validated_stage |
| qwen3:4b-instruct-2507-q4_K_M / None | humor | 31.543 | 241 | stop | validated_stage |
| qwen3:4b-instruct-2507-q4_K_M / None | revision | 27.704 | 192 | stop | validated_stage |
| qwen3:4b-instruct-2507-q4_K_M / None | criticism | 36.324 | 219 | stop | validated_stage |
| qwen3:4b-instruct-2507-q4_K_M / None | qc | 28.734 | 203 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | story | 22.354 | 121 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | romance | 17.546 | 119 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | humor | 15.74 | 95 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | revision | 10.153 | 51 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | criticism | 14.127 | 79 | stop | validated_stage |
| gemma3:4b-it-q4_K_M / None | qc | 27.346 | 224 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / None | story | 120.998 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / None | romance | 109.878 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / None | humor | 109.574 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / None | revision | 109.433 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / None | criticism | 117.206 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / None | qc | 111.821 | 1024 | length | failed |
| qwen3.5:4b-q4_K_M / False | story | 41.368 | 176 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / False | romance | 27.155 | 193 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / False | humor | 26.024 | 167 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / False | revision | 17.184 | 90 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / False | criticism | 46.212 | 344 | stop | validated_stage |
| qwen3.5:4b-q4_K_M / False | qc | 37.542 | 293 | stop | validated_stage |
