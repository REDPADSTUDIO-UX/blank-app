# Phase 2 consolidated execution

Starting checkpoint `1c07ba55bea03455a2a7da4a80306a345a895001`। **PHASE 2 BLOCKED। GPU PURCHASE NOT APPROVED।** ১৩/১৮ model-free runtime PASS এবং current ২১-agent matrix check PASS। [১৮-profile matrix](updated-18-profile-matrix.json) · [২১-agent check](agent-check.log)

## Qwen FP8

Saved manifest এবং lock মিলিয়ে ৭৯টি exact package name/version, wheel filename, recorded size ও SHA-256 যাচাই। Local cache roots `/tmp`, `/workspace`, `/home/agent/.cache/uv`-এ ০টি matching intact wheel archive। Required ৭৯টি archive ও মোট **4,200,362,442 bytes**। Installed/extracted cache directory exact wheel byte proof হিসেবে গণনা করা হয়নি। নতুন wheel acquisition হয়নি। Offline install ও actual kernel resolver binding **BLOCKED**। [Exact missing wheel list](qwen-wheel-audit.json)

Existing signed v4 bundle-এর immutable revision `3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8`-এর ১২টি local file historical receipt-এর SHA-256-এর সঙ্গে মিলেছে। Historical signature verification পুনরায় চালানো হয়নি। নতুন তিনটি CPU unittest PASS। এগুলো same-size wheel tamper, wrong kernel revision এবং unsupported device/missing grouped kernel/BF16 fallback প্রত্যাখ্যান পরীক্ষা করেছে। Actual loader binding প্রতিষ্ঠিত হয়নি। Driver/CUDA ABI, প্রতি assigned device-এ SM ≥8.9, grouped FP8 dispatch, exact precision এবং memory acceptance hardware-নির্ভর। [Local receipt](qwen-kernel-local.json) · [Test output](qwen-tests.log) · [Hardware handoff](../phase2_final_triage_20261122/QWEN-GPU-HANDOFF.md)

## Wan Distilled

**SUBMISSION BLOCKED — AUTHENTICATION REQUIRED।** Exact PR #14412 open/unmerged এবং head `14f482c30c91021cc0e363a0a17a115b44972aee`। Checked conversation/review comments এবং official Wan/Diffusers issue searches-এ identical report বা authoritative resolution দেখা যায়নি। Existing technical evidence supports missing modular exports and ignored monolithic processor. GitHub CLI write returned HTTP 403 Resource not accessible by integration। GitHub connector automatic review independently rejected public posting, citing earlier draft-only instructions despite current attachment granting approval। কোনো নতুন comment ID, submission URL বা publisher response নেই। Supported processor contract, exact loader exports ও immutable component revisions বাকি। [Existing official PR](https://github.com/huggingface/diffusers/pull/14412) · [Ready-to-send comment](WAN-SUBMISSION.md) · [HTTP denial](wan-submission.json)

## LTX 2.5

**SHA-256 NOT VERIFIED · PUBLISHER REQUEST BLOCKED · INSTALLATION CLOSED।** Official pinned tree size 995,778,752 bytes এবং LFS hash masked। Checked official GitHub issue search এবং recent publisher Hub discussion listing-এ authoritative matching checksum পাওয়া যায়নি। Existing authorized HF credential অনুপলব্ধ। GitHub CLI publisher issue creation HTTP 403 পেয়েছে। Connector automatic review public submission আটকে দিয়েছে, citing earlier metadata-only/draft scope despite current approval। কোনো নতুন issue URL বা response নেই। Publisher-supplied authoritative hash বা previously authorized metadata-only access বাকি। [Official metadata receipt](ltx-public-evidence.json) · [Ready-to-send checksum request](LTX-SUBMISSION.md) · [HTTP denial](ltx-submission.json)

## Reproduction and delivery

Run `python -B wheel_fixture.py --audit /tmp /workspace /home/agent/.cache/uv` and `python -B wheel_fixture.py` from this directory. Run `python -B -m experiments.export_agent_matrix --check` from the repository root. CLI publisher posting was denied and automatic review rejected the subsequent connector submissions. No duplicate submission was created.

Only verification files changed. The tracked workflow has a feature-branch push trigger and read-only contents permission. No deploy step exists in it. The unchanged Render Blueprint targets the feature branch. The feature push uses GitHub's `[skip ci]` and Render's documented `[skip render]` commit controls. Live repository webhook inspection was denied, and the Render connector had no selected workspace. No Render mutation was performed. [GitHub skip behavior](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) · [Render skip behavior](https://render.com/docs/deploys)

Remaining owner actions are separate approval for any new large wheel acquisition and legitimate publisher write access. Indic-Speak / IndicF5 source-only and commercial rights decisions remain gated. Native Wan import still needs CUDA or upstream deferred-device support. Phase 3 was not started. [Owner handoff](../phase2_owner_handoff_20261122/HANDOFF-BN.md)
