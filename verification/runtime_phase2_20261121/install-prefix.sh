#!/bin/bash
# Ephemeral GitHub job only. Install exactly the model-free CPU receipt packages.
set -euo pipefail
family=$1
prefix=$2
lock=verification/runtime_phase2_20261121/$family.lock.txt
base=$(python -c 'import sys; print(sys.base_prefix)')
mkdir -p "$prefix"
cp -aL "$base/." "$prefix/"
site="$prefix/lib/python3.11/site-packages"
rm -rf -- "$site"
mkdir -p "$site"
find "$prefix" -type d -name __pycache__ -prune -exec rm -rf {} +
grep -E '^(torch|torchaudio)==' "$lock" > "$RUNNER_TEMP/torch.txt"
grep -vE '^(torch|torchaudio)==' "$lock" > "$RUNNER_TEMP/runtime.txt"
python -m pip install --no-deps --no-compile --target "$site" --index-url https://download.pytorch.org/whl/cpu -r "$RUNNER_TEMP/torch.txt"
python -m pip install --no-deps --no-compile --target "$site" --index-url https://pypi.org/simple -r "$RUNNER_TEMP/runtime.txt"
# Some wheels ship bytecode. Seal only reviewed source and native runtime files.
find "$prefix" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$prefix" -type f -name '*.pyc' -delete
