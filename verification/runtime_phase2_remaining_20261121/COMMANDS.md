# Remaining Phase 2 reproductions

Run from the repository root. None of the probes acquires model weights.

```sh
.venv/bin/python -B verification/runtime_phase2_remaining_20261121/source-audit.py
gh workflow run 396098651 --ref feature/video-music-editing-studio -f runtime_phase2_stable=true
gh run view 44924150354 --log
```

The final job uses the versioned `stable.lock.txt` and production sandbox
launcher. The earlier Python 3.11 install failure is in
`github-44923915956.log.gz`. With the already installed isolated Python 3.10
CPU prefix, the exact host probe was:

```sh
env -i HOME=/tmp/redpad-phase2/home PATH=/usr/bin:/bin PYTHONPATH="$PWD" \
  /tmp/redpad-remain/stable310/bin/python -B verification/runtime_phase2_remaining_20261121/probe.py stable
env -i HOME=/tmp/redpad-phase2/home PATH=/usr/bin:/bin \
  /tmp/redpad-phase2/modern/bin/python -B verification/runtime_phase2_remaining_20261121/moe-meta-probe.py
env -i HOME=/tmp/redpad-phase2/home PATH=/usr/bin:/bin PYTHONPATH="$PWD" \
  /tmp/redpad-phase2/modern/bin/python -B verification/runtime_phase2_remaining_20261121/probe.py modern-symbols
env -i HOME=/tmp/redpad-phase2/home PATH=/usr/bin:/bin PYTHONPATH="$PWD" \
  /tmp/redpad-remain/voice/bin/python -B verification/runtime_phase2_remaining_20261121/probe.py voice-support
```

The voice-support inventory is intentionally incomplete for diagnosis. Its
dependency checker exits nonzero because Encodec was removed. It is unsuitable
for installation as a production runtime.

```sh
.venv/bin/python -m unittest -v tests.test_native_local_execution \
  tests.test_selected_voice_binding tests.test_offline_six_preparation \
  $(.venv/bin/python -c 'from tests.test_worker_isolation import WorkerIsolationTests; import unittest; print(" ".join("tests.test_worker_isolation.WorkerIsolationTests."+n for n in unittest.defaultTestLoader.getTestCaseNames(WorkerIsolationTests) if "test_kernel_private" not in n))')
.venv/bin/python -B verification/runtime_phase2_remaining_20261121/export-completion.py
```
