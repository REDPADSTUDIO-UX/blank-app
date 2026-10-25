"""Exercise production widgets with a synchronous test worker and real offline codecs."""
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from redpad_pipeline.engine import run_job
from redpad_pipeline.media import MockGateway


def main():
    with tempfile.TemporaryDirectory(prefix='redpad-production-ui-') as directory:
        root = Path(directory)
        for name in ('streamlit_app.py', 'redpad_video_studio.py'):
            shutil.copy2(SOURCE / name, root / name)
        for name in ('redpad_pipeline', 'assets'):
            shutil.copytree(SOURCE / name, root / name)
        at = AppTest.from_file(str(root / 'streamlit_app.py'), default_timeout=240).run()
        assert not at.exception
        next(w for w in at.text_input if w.label == 'Channel Name').set_value('Production test')
        next(w for w in at.text_input if w.label == 'Content Category / Niche').set_value('Horror')
        next(b for b in at.button if b.label == '➕ Save Channel').click().run()
        assert not at.exception
        at.radio(key='prod_mode').set_value('Live AI — paid providers').run()
        at.text_area(key='prod_topic').set_value('শেষ ট্রেনের গল্প').run()
        assert at.button(key='prod_create').disabled, 'Paid calls available without server approval/credentials'
        at.radio(key='prod_mode').set_value('Offline mock test — free').run()
        # Only worker scheduling is replaced; real engine, FFmpeg and database run.
        def test_worker(db, job, config):
            result = run_job(db, job, MockGateway())
            assert result['phase'] == 'complete', result
        with patch('redpad_pipeline.ui.launch', side_effect=test_worker), patch('requests.Session.request', side_effect=AssertionError('No network permitted')):
            at.button(key='prod_create').click().run()
        assert not at.exception, [e.message for e in at.exception]
        labels = [w.proto.label for w in at.get('download_button')]
        for label in ('Download production MP4', 'Download BN subtitles', 'Download EN subtitles',
                      'Download review MP4', 'Review BN subtitles', 'Review EN subtitles'):
            assert label in labels, (label, labels)
        assert any('MOCK' in w.value for w in at.warning), 'Mock output needs an explicit disclosure'
        assert len(at.get('video')) >= 3
        next(r for r in at.radio if r.label == 'Review Decision').set_value('Approve')
        next(b for b in at.button if b.label == '💾 Save Review Decision').click().run()
        assert not at.exception
        with sqlite3.connect(root / 'redpad_studio.db') as db:
            assert db.execute('SELECT status FROM content').fetchone()[0] == 'Approved'
            assert db.execute('SELECT mode FROM production_exports').fetchone()[0] == 'mock'
        print('PASS: paid UI gated, offline job button, MP4/SRT downloads, previews, mock disclosure and human approval')


if __name__ == '__main__':
    main()
