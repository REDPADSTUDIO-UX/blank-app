# Phase 2 reproduction

Existing public dependencies only. Package startup loads no model weights. The
CPU wheel index is deliberately distinct from future accelerator packages.

## Host baseline and failure reproduction

```sh
export UV_CACHE_DIR=/tmp/redpad-phase2/cache
export UV_PYTHON_INSTALL_DIR=/tmp/redpad-phase2/python
uv python install 3.11
p=/tmp/redpad-phase2
for family in media speech modern; do
  uv venv --python "$p/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11" "$p/$family"
done
uv pip install --python "$p/media/bin/python" --index-url https://download.pytorch.org/whl/cpu 'torch==2.7.1'
uv pip install --python "$p/media/bin/python" -r assets/offline/requirements-media.txt
uv pip install --python "$p/modern/bin/python" --index-url https://download.pytorch.org/whl/cpu 'torch==2.7.1'
uv pip install --python "$p/modern/bin/python" -r experiments/kaggle_phase3/requirements.proposed.txt
uv pip install --python "$p/speech/bin/python" --index-url https://download.pytorch.org/whl/cpu 'torch==2.5.1' 'torchaudio==2.5.1'
uv pip install --python "$p/speech/bin/python" -r assets/offline/requirements-speech.txt
mkdir -p "$p/home"
for family in media speech modern; do
  uv pip check --python "$p/$family/bin/python"
  env -i PATH=/usr/bin:/bin HOME="$p/home" "$p/$family/bin/python" -B \
    verification/runtime_phase2_20261121/probe.py "$family"
done
.venv/bin/python -B verification/runtime_phase2_20261121/probe.py codec
```

The first historical speech run installed Torch CPU before resolving the
original speech requirements without the TorchAudio pin. The retained
`speech-initial.json` captures TorchAudio 2.11.0 failing to load
`libcudart.so.13`. The actual lock now uses the matching CPU wheel. The first
modern probe looked for a nonexistent marketing-version class. The pinned
Qwen 3.6 config hash verifies that the implementation class really is
`Qwen3_5ForConditionalGeneration`; the model is not loaded.

## Sandbox and binding

```sh
gh workflow run 396098651 --ref feature/video-music-editing-studio -f runtime_phase2=true
```

The workflow materializes three independent temporary prefixes from the
checked-in complete CPU package version lists. It seals a file and Linux ABI
manifest, checks each bound profile's committed model revision and worker
source digest, then uses the production mount/namespace builder with a
diagnostic Python payload. The child checks its interpreter, distribution
inventory and network namespace before running model-free imports. The
recorded source, file and ABI hashes are specific to that package build and
host. They must be recomputed and approved for a future installation.

## Targeted software contracts

```sh
.venv/bin/python -m unittest -v tests.test_native_local_execution \
  tests.test_native_professional tests.test_professional_readiness \
  tests.test_offline_six_preparation tests.test_offline_11_preparation \
  $(.venv/bin/python -c 'from tests.test_worker_isolation import WorkerIsolationTests; import unittest; print(" ".join("tests.test_worker_isolation.WorkerIsolationTests."+n for n in unittest.defaultTestLoader.getTestCaseNames(WorkerIsolationTests) if "test_kernel_private" not in n))')
```

`contracts-final.txt` records individual test IDs and counts. The known
managed-host Phase 1 kernel canary was excluded. The focused Phase 2 workflow
uses the proven Ubuntu 22.04 sandbox host and does not dispatch Phase 1.
