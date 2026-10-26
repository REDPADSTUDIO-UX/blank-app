"""Real Chromium/Streamlit smoke test in a disposable, credential-free workspace.

This browser only visits its own local test app. It never logs in or calls providers.
"""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

SOURCE = Path(__file__).resolve().parents[1]


def main():
    artifacts = SOURCE / 'ci_artifacts'
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='redpad-browser-') as directory:
        root = Path(directory)
        for name in ('streamlit_app.py', 'redpad_video_studio.py'):
            shutil.copy2(SOURCE / name, root / name)
        for name in ('redpad_pipeline', 'assets'):
            shutil.copytree(SOURCE / name, root / name)
        env = dict(os.environ)
        for key in ('RUNWAY_API_KEY', 'OPENAI_API_KEY', 'AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION'):
            env.pop(key, None)
        env['REDPAD_ENABLE_PAID_GENERATION'] = 'false'
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        with (root / 'server.log').open('w') as log:
            process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
                '--server.headless', 'true', '--server.address', '127.0.0.1', '--server.port', str(port),
                '--browser.gatherUsageStats', 'false'], cwd=root, env=env, stdout=log, stderr=log)
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                for _ in range(60):
                    try:
                        opener.open(f'http://127.0.0.1:{port}/_stcore/health', timeout=1).close()
                        break
                    except OSError:
                        if process.poll() is not None:
                            raise RuntimeError('Test app stopped before startup')
                        time.sleep(.25)
                else:
                    raise RuntimeError('Test app startup timeout')
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(channel='chrome', headless=True)
                    page = browser.new_page(viewport={'width': 1440, 'height': 1200})
                    try:
                        page.goto(f'http://127.0.0.1:{port}', wait_until='domcontentloaded')
                        expect(page.get_by_role('heading', name='🎬 REDPAD AI Studio', exact=True)).to_be_visible(timeout=30000)
                        expect(page.get_by_text('Total Channels', exact=True)).to_be_visible()
                        page.screenshot(path=str(artifacts / 'dashboard.png'))
                        page.get_by_role('tab', name='🎞️ Video Studio', exact=True).click()
                        page.get_by_role('button', name='🧪 Start free demo workspace', exact=True).click()
                        model = page.get_by_role('combobox', name='Video generation model', exact=True)
                        expect(model).to_be_visible(timeout=30000)
                        model.scroll_into_view_if_needed()
                        model.click()
                        for family in ('Grok Imagine', 'Kling', 'WAN', 'Runway', 'Seedance'):
                            expect(page.get_by_role('option').filter(has_text=family).first).to_be_visible()
                        page.screenshot(path=str(artifacts / 'multi-model-selection.png'))
                        page.keyboard.press('Escape')
                        topic = page.get_by_role('textbox', name='Topic / story / existing Bangla script', exact=True)
                        topic.fill('শেষ ট্রেন — free browser test')
                        topic.press('Tab')  # Streamlit commits a textarea edit on blur.
                        expect(page.get_by_role('button', name='🧪 Create offline production test', exact=True)).to_be_enabled(timeout=30000)
                        page.get_by_role('button', name='🧪 Create offline production test', exact=True).click()
                        expect(page.get_by_text('Status: complete', exact=False)).to_be_visible(timeout=180000)
                        output = page.get_by_role('button', name='Download production MP4', exact=True)
                        output.scroll_into_view_if_needed()
                        with page.expect_download() as transfer:
                            output.click()
                        destination = artifacts / 'browser-downloaded-MOCK.mp4'
                        transfer.value.save_as(str(destination))
                        assert destination.stat().st_size > 10000
                        expect(page.get_by_role('button', name='Download BN subtitles', exact=True)).to_be_visible()
                        expect(page.get_by_role('button', name='Download EN subtitles', exact=True)).to_be_visible()
                        page.wait_for_function("() => { const all = document.querySelectorAll('video'); const v = all[all.length - 1]; return v && v.readyState >= 2 && v.duration >= 29; }", timeout=30000)
                        page.screenshot(path=str(artifacts / 'production-complete.png'))
                        live_mode = page.get_by_role('radio', name='Live AI — paid providers', exact=True)
                        live_mode.press('Space')  # Native keyboard selection avoids the custom radio's covered input.
                        expect(live_mode).to_be_checked()
                        expect(page.get_by_role('button', name='🎬 Create AI production job', exact=True)).to_be_disabled()
                        assert page.locator('[data-testid="stException"]').count() == 0
                    except Exception:
                        diagnostics = page.locator('video').evaluate_all("els => els.map(v => ({readyState:v.readyState, networkState:v.networkState, duration:Number.isFinite(v.duration)?v.duration:null, error:v.error?.code, mp4:v.canPlayType('video/mp4; codecs=\"avc1.42E01E, mp4a.40.2\"')}))")
                        (artifacts / 'video-diagnostics.json').write_text(__import__('json').dumps(diagnostics))
                        page.screenshot(path=str(artifacts / 'browser-failure.png'))
                        (artifacts / 'browser-dom.html').write_text(page.content(), encoding='utf-8')
                        raise
                    browser.close()
                    print('PASS: real Chrome dashboard, all model families, free end-to-end job, MP4 download, subtitles, paid gate')
            finally:
                process.terminate()
                process.wait(timeout=15)


if __name__ == '__main__':
    main()
