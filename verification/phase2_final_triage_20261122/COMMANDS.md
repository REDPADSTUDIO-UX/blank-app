# New evidence

Wan used the prior immutable PR source archive, overlay and pinned Docker image. Run `timeout 90 bash wan-modular-command.sh` from this directory. Only the exact public modular index is copied into the private temporary directory. There are no model weights or component folders. The first fixture attempt assumed a top-level generic export. The corrected fixture imports generic classes from the Wan submodule and verifies the named Distilled exports required by the actual loader. Public metadata URLs and digests are recorded in wan-publisher-receipt.json.

Qwen fetched only the 12 immutable public CUDA bundle files at the base URL in ../phase2_cpu_gaps_20261122/qwen-kernel-v4.json. Compare SHA-256 with the previous receipt before staging files under /tmp/redpad-triage-kernel/torch-cuda, preserving relative paths. No bundle code is imported. Run the following CPU-only metadata check with the publisher verifier.

```sh
XDG_CACHE_HOME=/tmp/redpad-triage-xdg XDG_DATA_HOME=/tmp/redpad-triage-data \
  uv --cache-dir /tmp/redpad-uv-cache run --no-project --no-python-downloads \
  --python /tmp/redpad-exact/wan-env/bin/python \
  --with 'kernels==0.17.2' --with 'sigstore==4.5.1' \
  python -c 'from pathlib import Path; from kernels.verify import VerificationResult, verify_variant; result = verify_variant(Path("/tmp/redpad-triage-kernel/torch-cuda")); print(result); assert isinstance(result, VerificationResult.Success)'
```

The earlier attempts could not initialize the trust metadata cache under the read-only home directory. The successful invocation used writable XDG paths. Trust policy and exact identity are defined by the versioned upstream verifier. Temporary Python verifier dependencies were permitted CPU-only packages. No CUDA packages, model weights or GPU were used. LTX was not queried. Publisher requests are drafts.

[Versioned verifier](https://github.com/huggingface/kernels/blob/v0.17.2/kernels/src/kernels/verify.py)
