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
