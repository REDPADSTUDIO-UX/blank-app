"""Run unique unittest IDs and preserve per-test outcomes and the test environment."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import unittest

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent


def test_id(test):
    identifier = unittest.TestCase.id(test)
    return identifier.removeprefix('tests.')


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test_id(test)] = 'pass'

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test_id(test)] = 'error'

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test_id(test)] = 'failure'

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test_id(test)] = {'skipped': reason}

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcomes[test_id(test)] = 'expected_failure'

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcomes[test_id(test)] = 'unexpected_success'

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            self.outcomes[test_id(test)] = 'subtest_failure'


def main():
    # Script invocation places its own folder on sys.path. Put the repository first
    # for package imports and keep the same discovery root as the original run.
    sys.path.insert(0, str(ROOT))
    unique, duplicates = {}, []
    for test in flatten(unittest.defaultTestLoader.discover('tests')):
        identifier = test_id(test)
        if identifier in unique:
            duplicates.append(identifier)
        else:
            unique[identifier] = test

    sources = {}
    for path in (
        *sorted(Path('redpad_pipeline').glob('*.py')),
        *sorted(Path('tests').glob('*.py')),
        Path('requirements.txt'), Path('uv.lock'), HERE / 'run_cpu_regression.py',
    ):
        sources[str(path.relative_to(ROOT) if path.is_absolute() else path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {
        'base_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'python': sys.version,
        'interpreter': sys.executable,
        'interpreter_realpath': str(Path(sys.executable).resolve()),
        'platform': platform.platform(),
        'sqlite': sqlite3.sqlite_version,
        'dependencies': sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions()),
        'test_environment': {key: os.environ.get(key) for key in ('PYTHONHASHSEED', 'PYTHONWARNINGS')},
        'duplicate_discovery_ids': duplicates,
        'source_sha256': sources,
    }
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(unittest.TestSuite(unique.values()))
    receipt.update(tests_run=result.testsRun, successful=result.wasSuccessful(), outcomes=result.outcomes,
                   missing_outcomes=sorted(unique.keys() - result.outcomes.keys()))
    (HERE / 'regression-receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    return 0 if result.wasSuccessful() and not receipt['missing_outcomes'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
