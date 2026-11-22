# Exact-source Phase 2 verification

The workflow materializes public publisher source only by matching every
selected file to its complete public immutable Git tree and byte count.
The per-file SHA-256 manifests are checked again before the production
Bubblewrap launch. The probe imports entrypoints and resolves signatures.
The artifacts are diagnostic runtime locks, and create no owner approvals.

```sh
d=verification/runtime_phase2_exact_20261121
.venv/bin/python -B "$d/fetch-source.py" ltx25 /tmp/redpad-exact/ltx25
.venv/bin/python -B "$d/fetch-source.py" ace15 /tmp/redpad-exact/ace15
.venv/bin/python -B "$d/fetch-source.py" wan_animate2 /tmp/redpad-exact/wan_animate2
gh workflow run 396098651 --ref feature/video-music-editing-studio -f runtime_phase2_ltx=true
gh workflow run 396098651 --ref feature/video-music-editing-studio -f runtime_phase2_ace=true
gh workflow run 396098651 --ref feature/video-music-editing-studio -f runtime_phase2_wan=true
.venv/bin/python -B -m unittest -v tests.test_native_local_execution \
  tests.test_offline_six_preparation tests.test_selected_voice_binding
.venv/bin/python -B "$d/collect-receipts.py"
```

The CPU wheel index and actual complete dependency versions are in the
existing install-prefix script and the three exact lock files. The first
LTX run on Torch 2.7.1 is preserved as a host failure. Earlier GitHub
failures 44932637949 and 44932820301 preserve the initial missing account
database error. Successful LTX and ACE runs use the fixed sanitized
identity. The Wan run stops at the exact publisher CUDA default without
patching it. Full logs are compressed and the bound child receipts are
machine-readable.
