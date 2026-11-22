# Confirm a revision-locked processor and loader for Wan Animate 2 Distilled

We are checking `Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers@59e4141466bcb1bf9733eca1bc78be6891c9fbdf` with Diffusers PR #14412 head `14f482c30c91021cc0e363a0a17a115b44972aee`. The standard model index declares seven components, including a `CLIPImageProcessor` in `image_processor/`. The exact monolithic class has six constructor components. Its local loader emits a warning and drops the processor declaration and an explicit processor override. `encode_image` constructs a default processor. That default matched the published preprocessing on the synthetic RGB case in our fixture.

We also tried the published modular index via `ModularPipeline.from_pretrained(local_dir, local_files_only=True, trust_remote_code=False)`. The directory contained only the exact modular index. The pinned Diffusers source provides generic Wan modular classes in its Wan submodule. The index requests `WanAnimate2DistilledModularPipeline` and `WanAnimate2DistilledBlocks`. It omits the processor and refers to scheduler and transformer through `refs/pr/1`. That ref resolved to `ff28d41a9c0c331137691847cc8700593d785593` during this review. The two public config files matched the pinned model revision byte-for-byte. Checkpoint tensors were outside this reproduction.

## Minimal CPU reproduction

1. Use Python 3.11 with the exact Diffusers PR checkout above. Our diagnostic used Torch 2.7.1+cpu, Transformers 5.22.2, Hub 1.31.0 and Safetensors 0.8.0.
2. Fetch only `modular_model_index.json` from the exact published model revision into an otherwise empty local directory. Disable networking or set Hub offline. From that checkout, run:

   ```python
   from diffusers import ModularPipeline

   ModularPipeline.from_pretrained(
       "/path/to/local-metadata", local_files_only=True, trust_remote_code=False
   )
   ```

   Observed `AttributeError: module diffusers has no attribute WanAnimate2DistilledModularPipeline`.
3. For the standard route, use the pinned `model_index.json` in a separate local directory. Intercept Diffusers' `load_sub_model` in the diagnostic and provide a synthetic scheduler. Call `WanAnimate2Pipeline.from_pretrained(local_dir, local_files_only=True)` with and without an explicit `image_processor` argument. The dispatch records six constructor components and warns that `image_processor` is ignored in both cases.

Could you confirm whether the monolithic processor entry is intentionally unused, and specify which processor contract is normative for this checkpoint? If its published configuration must load, please identify the exact released or reviewed source commit, class, loader invocation and revision-locked component mapping. For the modular route, please provide the exact exports and immutable component revisions, or confirm its support status. A weight-free loader dispatch or preprocessing contract test would make the intended behavior reproducible.

[Pinned model repository](https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B-Distilled-Diffusers/tree/59e4141466bcb1bf9733eca1bc78be6891c9fbdf)
