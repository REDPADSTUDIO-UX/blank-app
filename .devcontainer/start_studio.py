"""No dotfiles: install this checkout's dependencies and launch its private Streamlit port."""
import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8503


def main():
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != 'feature/video-music-editing-studio':
        raise SystemExit('Studio startup skipped: the expected feature branch is not checked out. No branch was changed.')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')], cwd=ROOT, check=True)
    # Only boolean presence is emitted; values never leave the process.
    print('RUNWAY_API_KEY available:', bool(os.environ.get('RUNWAY_API_KEY')))
    with socket.socket() as connection:
        occupied = connection.connect_ex(('127.0.0.1', PORT)) == 0
    if occupied:
        print('Port 8503 already has a listener; existing process preserved.')
        return
    folder = ROOT / 'redpad_media'
    folder.mkdir(exist_ok=True)
    # Current owner instruction: no paid generation, even if an older config enabled it.
    os.environ['REDPAD_ENABLE_PAID_GENERATION'] = 'false'
    with (folder / 'streamlit.log').open('ab') as log:
        process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', str(ROOT / 'streamlit_app.py'),
            '--server.headless', 'true', '--server.address', '0.0.0.0', '--server.port', str(PORT),
            '--browser.gatherUsageStats', 'false'], cwd=ROOT, stdout=log, stderr=log, start_new_session=True)
    print('Streamlit launched on private forwarded port', PORT, 'process', process.pid)


if __name__ == '__main__':
    main()
