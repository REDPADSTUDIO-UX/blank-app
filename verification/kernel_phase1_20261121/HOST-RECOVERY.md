# Phase 1 GitHub-hosted runner recovery

**BLOCKED — HOST LIMITATION.** The standard Ubuntu 24.04 runner used Linux
`7.0.0-1014-aws`. The permitted package manager successfully installed
Bubblewrap 0.9.0. The probe ran as the unprivileged runner user. The production
native launch command failed inside Bubblewrap before the dummy payload ran.

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
Phase 1 probe exit code: 1
```

This confirms a denial during sandbox loopback configuration. The log does
not identify the host policy responsible. User, mount, network, and PID
namespace separation were not independently proven by the payload. All of
A (private-file denial), B (read-only input), C (writable boundary),
D (network isolation), E (process cleanup), and F (native/shared parity)
are blocked. The shared path was not reached after the native startup
failure. No application defect was confirmed by this run.

## Reproduction and evidence

```sh
gh workflow run 396098651 --ref feature/video-music-editing-studio -f kernel_phase1=true
gh run view 44919361523 --log --job 136891833222
```

The command ran against `97eea4634dc5e60d6880d9ffc6da673ae666b20a`.
The full job log preserves the apt commands, package and kernel versions,
runner identity, mount arguments, and failure. The earlier run
`44918960679` lacked Bubblewrap entirely. There was one recovery run and
no retry after the namespace setup denial.

A different authorized free Linux host needs a dedicated standalone
Python prefix, distribution-supported Bubblewrap at `/usr/bin/bwrap`,
standard `ldd` and `findmnt`, working unprivileged UID/GID mappings,
user/mount/network/PID namespaces, and permission for Bubblewrap to
configure loopback inside its isolated network namespace under the
host's existing controls. Run the existing `probe.py` there.
