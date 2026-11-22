# Reproduction commands

Commands run from the repository root. The pre-existing `targeted-regression.txt`
contains 116 invocations from the interrupted worktree. The new 49-test focused
log and 707-ID regression overlap and should be counted separately.

```sh
d=verification/runtime_phase2_targeted_20261121
.venv/bin/python -B -m unittest -v tests.test_native_local_execution \
  tests.test_worker_isolation.WorkerIsolationTests.test_only_explicit_files_are_mounted_and_environment_is_allowlisted \
  tests.test_worker_isolation.WorkerIsolationTests.test_shared_kernel_block_preserves_terminal_evidence_and_never_launches_fallback
PYTHONHASHSEED=0 PYTHONWARNINGS=default .venv/bin/python -B "$d/run_cpu_regression.py"
.venv/bin/python -B -m experiments.export_agent_matrix --check
.venv/bin/python -B "$d/source-inventory.py"
.venv/bin/python -B "$d/ltx-publisher-check.py"
.venv/bin/python -B "$d/export-matrix.py"
gh workflow run 396098651 --ref feature/video-music-editing-studio -f kernel_phase1=true
```

The local LTX prefix is a model-free support probe. The three CPU wheels
were installed from `https://download.pytorch.org/whl/cpu` at Torch 2.7.1,
TorchAudio 2.7.1 and TorchVision 0.22.1. The separate prefix uses
Transformers 5.14.1. Exact resolved dependencies are in
`ltx-cpu-support.lock.txt`. No LTX model or pipeline package was installed.

```sh
env -i PATH=/usr/bin:/bin HOME=/tmp/redpad-phase2/home HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES= \
  /tmp/redpad-phase2/modern/bin/python -B "$d/moe-fp8.py"
env -i PATH=/usr/bin:/bin HOME=/tmp/redpad-phase2/home \
  /tmp/redpad-remain/ltx-targeted/bin/python -B "$d/ltx-cpu-probe.py"
```

The deduplicated full-suite receipt captures actual interpreter and
dependency metadata, source SHA-256 values, test IDs and outcomes. It was
collected from the worktree immediately before the engineering commit.
