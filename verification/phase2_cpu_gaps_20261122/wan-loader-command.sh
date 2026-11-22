#!/bin/bash
set -eu
base=/tmp/redpad-phase2/python/cpython-3.11.18-linux-x86_64-gnu
venv=/tmp/redpad-exact/wan-env
probe=/tmp/redpad-approved
docker run --rm --pull never --network none --ipc none --read-only --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m,mode=1777 --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 64 --user "$(id -u):$(id -g)" \
  -v "$probe/os-libs:/os-libs:ro" -e LD_LIBRARY_PATH=/os-libs -e HOME=/nonexistent -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 \
  -v "$base:/tmp/redpad-phase2/python/cpython-3.11-linux-x86_64-gnu:ro" -v "$venv:$venv:ro" -v "$probe/wan-src:/source:ro" \
  -v "$probe/overlay:/overlay:ro" -v "$PWD:/diagnostic:ro" \
  debian@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2 \
  "$venv/bin/python" -I -B /diagnostic/wan_loader_fixture.py
