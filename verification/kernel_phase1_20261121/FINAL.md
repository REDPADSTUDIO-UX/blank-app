# Phase 1 final verification — PASS

The free GitHub-hosted Ubuntu 22.04 image passed the genuine kernel canaries with Linux
`6.8.0-1070-azure` and distribution Bubblewrap `0.6.1`. The normal runner user
launched the production Bubblewrap configuration with synthetic worker payloads.
Both launch paths proved separate user, mount, network, and PID namespaces.
The workflow and probe exited successfully at tested commit
`8eedb6b1666683d705f2298b6ac2e318430e005d`.

| Test | Native | Shared | Evidence |
|---|---|---|---|
| A | PASS | PASS | Private read, enumeration, traversal and synthetic symlink denied. |
| B | PASS | PASS | Approved input read; write, unlink, and replacement denied; host input intact. |
| C | PASS | PASS | Output and temporary storage writable. Regular file creation denied at the sandbox root, runtime, input, model, source, device and proc paths. Existing device I/O through /dev/null worked. |
| D | PASS | PASS | Independent network namespace, no IPv4 routes, synthetic host loopback unreachable. |
| E | PASS | PASS | Timeout, cancellation and controller loss closed the pipe inherited by the sandbox child and detached grandchild. Persisted restart/recovery and deduplication were verified separately as software contracts. |
| F | PASS | PASS | Both production launch configurations passed the same kernel probes; synthetic ambient credential markers were absent. Runtime pins, source/version and evidence integrity were verified separately through software contracts. |

The probe exposed two launcher gaps. The sandbox root and the synthetic
`/dev` filesystem accepted regular-file writes. Remounting both read-only
after installing the writable output and temporary mounts corrected that
behavior. A separate canary defect rejected Linux's `EBUSY` response for
unlinking a bind-mounted file. The unlink assertion now recognizes that
kernel denial. The 64 targeted software contract tests passed after the
last launcher correction; the six earlier fixture results are separate
supporting evidence with overlapping tests.

Historical host blockers remain specific to those environments. The managed
Debian 13.6 host had read-only procfs at the UID map. The Ubuntu 24.04
runs first lacked Bubblewrap, then failed isolated loopback setup with
`RTM_NEWADDR: Operation not permitted` after installation. The authorized
Codespaces inventory was empty. Ubuntu 22.04 used the existing free workflow
with the stock host controls; only the temporary runner package was installed.

```sh
gh workflow run 396098651 --ref feature/video-music-editing-studio -f kernel_phase1=true
gh run view 44921166025 --log
sh verification/kernel_phase1_20261121/run-fixtures.sh .venv/bin/python
.venv/bin/python -m unittest -v \
  tests.test_native_local_execution tests.test_professional_readiness \
  tests.test_worker_isolation.WorkerIsolationTests.test_runtime_receipt_binds_exact_interpreter_dependencies_and_source \
  tests.test_worker_isolation.WorkerIsolationTests.test_shared_source_pin_and_terminal_receipt_detect_changes \
  tests.test_worker_isolation.WorkerIsolationTests.test_shared_supervisor_rechecks_exact_versions_and_rights \
  tests.test_worker_isolation.WorkerIsolationTests.test_shared_text_handoff_denies_artifact_changes
```

[Successful verification](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44921166025)
· [Initial Ubuntu 22.04 run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44920850005)
· [Root write finding](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44920918959)
· [Device filesystem write finding](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44921086770)

The evidence is for synthetic Phase 1 worker isolation. Real model runtimes
and GPU device bindings remain outside its scope. Phase 2 was not started.
