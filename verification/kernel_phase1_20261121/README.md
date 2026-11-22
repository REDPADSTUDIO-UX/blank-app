# Phase 1 kernel isolation verification

Run from the repository root on an authorized Linux host with Bubblewrap at
`/usr/bin/bwrap`, standard Linux tools (`findmnt`, `ldd`) and a dedicated
standalone Python prefix containing no private files.

```sh
python3 verification/kernel_phase1_20261121/probe.py
sh verification/kernel_phase1_20261121/run-fixtures.sh python3
```

The first command exercises the production launcher configuration for both
worker names with fixed synthetic payloads substituted for inference. It
checks namespace identity, file denial, read-only inputs, writable paths,
host-loopback denial, timeout, cancellation, and descendant teardown after
controller death. The live host listener uses loopback and receives no
external requests. The second command separately exercises existing supervisor
state/recovery and launch-policy tests. These fixtures include real local
processes, but do not supply kernel-isolation evidence.

This package emits launch arguments and the allowlisted environment. Preserve
the exit status and full log. Exit 2 means the local procfs preflight detected a
read-only UID-map mount. A failure or unavailable host cannot establish a pass.
The existing user/mount/net/PID namespace IDs are host observations only.

## Result on 21 November 2026

**BLOCKED — HOST LIMITATION.** The managed Debian 13.6 host has kernel
6.18.57 and Bubblewrap 0.12.0. A read-only procfs backs the UID map, matching the
prior recorded UID-map error. The current preflight exited before launch.
The standard GitHub-hosted Ubuntu 24.04 runner reached the focused job but
lacked `/usr/bin/bwrap`. Its failed-step log is preserved. The diagnostic now
reports this case explicitly as blocked.

GitHub commands from the repository checkout:

```sh
gh workflow run 396098651 --ref feature/video-music-editing-studio -f kernel_phase1=true
gh run view 44918960679 --log-failed
```

Six standalone CPU fixture tests passed. The actual namespace canaries A–F
remain pending, including the writable boundary at the sandbox root and
lifecycle cleanup across the PID namespace. No working worker code was changed
and no kernel-level defect could be confirmed on either host.
