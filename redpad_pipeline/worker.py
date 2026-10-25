"""Optional durable worker entry point for the private Codespaces/server deployment."""
import argparse
import os
import sqlite3
import tomllib
from contextlib import closing
from pathlib import Path
from .models import Config
from .providers import LiveGateway
from .media import MockGateway
from .engine import load_state, run_job


def main():
    parser = argparse.ArgumentParser(description='Run one saved REDPAD job; never prints credentials.')
    parser.add_argument('--db', type=Path, default=Path(__file__).resolve().parents[1] / 'redpad_studio.db')
    parser.add_argument('--job', required=True, help='Existing production job ID, not a new generation request')
    args = parser.parse_args()
    with closing(sqlite3.connect(args.db)) as db:
        row = db.execute('SELECT job_dir FROM production_jobs WHERE job_id=?', (args.job,)).fetchone()
    if not row:
        raise SystemExit('Saved job not found.')
    secrets_path = args.db.parent / '.streamlit/secrets.toml'
    secrets = tomllib.loads(secrets_path.read_text()) if secrets_path.is_file() else {}
    config = Config.load(lambda key: os.environ.get(key) or secrets.get(key, ''))
    root = Path(row[0])
    state = load_state(root)
    import json
    plan = json.loads((root / 'plan.json').read_text())
    gateway = LiveGateway(config, plan['seconds'], state['approved_usd']) if state['mode'] == 'live' else MockGateway()
    result = run_job(args.db, root, gateway)
    print(result['job_id'], result['phase'])
    raise SystemExit(0 if result['phase'] in ('complete', 'waiting') else 1)


if __name__ == '__main__':
    main()
