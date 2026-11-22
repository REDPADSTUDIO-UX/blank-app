# Sign-off reproduction

From the feature-branch checkout, with the existing CPU-only diagnostic
prefixes. No profile startup workflow is dispatched or rerun.

```sh
d=verification/phase2_signoff_20261122
.venv/bin/python -B "$d/audit-receipts.py"
.venv/bin/python -B "$d/gate-audit.py"
.venv/bin/python -B -m experiments.export_agent_matrix --check
/tmp/redpad-exact/ltx-env/bin/python -B "$d/oiio-lifecycle.py"
env -i PATH=/usr/bin:/bin HOME=/tmp LOGNAME=redpad-worker CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /tmp/redpad-phase2/modern/bin/python -B "$d/fp8-gate-probe.py"
```

The auditor decompresses committed logs, independently matches import and
runtime receipts, and re-reads GitHub Actions metadata. The file hashes
and tested commits remain attached to the original runs. The pinned LTX
and Modern package version lists are in the previous verification folders.
