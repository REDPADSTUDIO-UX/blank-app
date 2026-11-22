# CPU security verification

Run from the repository root. The concurrency, media and model-facing tests here use CPU processes, mocks and synthetic fixtures. The Linux filesystem canary skips with a recorded reason if the host refuses the namespace. A skip is excluded from the pass count.

## Full runs and retry history

| Order | Command | Logs | Result |
|---:|---|---|---|
| 1 | `PYTHONHASHSEED=0 PYTHONWARNINGS=default .venv/bin/python -m unittest discover -s tests -v` | `regression.log.gz` | 738 invocations, one kernel skip. Stock discovery repeated imported test classes. |
| 2 | `PYTHONHASHSEED=0 PYTHONWARNINGS=default .venv/bin/python verification/pre_gpu_security_20261121/run_cpu_regression.py` | `regression-receipt-runner-first.log.gz` | Receipt runner aborted because a test instance sets an `id` string, shadowing the method. The runner was corrected to call `unittest.TestCase.id(test)`. |
| 3 | Same receipt-runner command | `regression-dedup-intermediate.log.gz`, `regression-dedup-intermediate-receipt.json` | 699 distinct tests, 698 passes and one kernel skip. Intermediate source before the shared reference-rights check. |
| 4 | Same receipt-runner command | `regression-final.log.gz`, `regression-receipt.json` | See final receipt for distinct IDs and outcomes. The last CI fixture-only portability adjustment was also tested separately, as recorded below. |

The receipt contains the exact interpreter, SQLite version, installed distributions, distinct test IDs, duplicates removed, per-ID outcomes and hashes of the application/test Python sources at the start of each recorded run. The full logs retain warning and skip lines. No result is counted twice.

## Targeted checks

| Command | Log |
|---|---|
| `.venv/bin/python -m unittest -v tests.test_worker_isolation tests.test_native_local_execution` | `targeted-first.log.gz` |
| `.venv/bin/python -m unittest -v tests.test_worker_isolation tests.test_native_local_execution tests.test_professional_readiness tests.test_kaggle_model_services` | `targeted-artifact-receipts.log.gz` |
| `.venv/bin/python -m unittest -v tests.test_worker_isolation tests.test_native_local_execution tests.test_professional_readiness` | `targeted-shared-lifecycle.log.gz` |
| `.venv/bin/python -m unittest -v tests.test_worker_isolation` | `targeted-abi.log.gz`, `targeted-rights.log.gz`, `targeted-ci-portability.log.gz` |
| `.venv/bin/python -m experiments.export_agent_matrix --check` | `matrix-check.log.gz` |

The last targeted run used the CI-compatible fixture that omits interpreter-local libraries from the host ABI fixture manifest. This was a test-only edit during the final full run. The final checkout hash of that fixture is in `fixture-ci-portability.sha256`.
