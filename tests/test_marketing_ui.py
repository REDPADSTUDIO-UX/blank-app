"""Real Streamlit Growth Engine and isolated read-only preview smoke tests."""
from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

SOURCE = Path(__file__).resolve().parents[1]


def assert_ok(at, stage):
    messages=[str(x) for x in at.exception]
    assert not messages, f"{stage}: {messages}"


def first(items,label):
    return next(x for x in items if x.label == label)


def main():
    with tempfile.TemporaryDirectory(prefix="redpad-growth-ui-") as folder:
        root=Path(folder)
        for file in ("streamlit_app.py","redpad_video_studio.py"):
            shutil.copy2(SOURCE/file,root/file)
        shutil.copytree(SOURCE/"redpad_pipeline",root/"redpad_pipeline")
        shutil.copytree(SOURCE/"assets",root/"assets")
        db=root/"redpad_studio.db"
        with patch("requests.Session.request",
                   side_effect=AssertionError("Marketing UI attempted external API request")):
            at=AppTest.from_file(str(root/"streamlit_app.py"),default_timeout=120).run()
            assert_ok(at,"app loads")
            assert "📣 Growth Engine" in [x.label for x in at.tabs]
            assert first(at.button,"Generate 7-Day Marketing Draft") is not None
            first(at.text_input,"Campaign / title").set_value("নিশিকথা — শেষ ট্রেন")
            first(at.text_area,"Story summary, hook or campaign brief").set_value(
                "শেষ ট্রেনের যাত্রী অদ্ভুত এক রহস্যের সাক্ষী হয়। "
                "স্টেশনের আলো নিভে যায়, আর দরজায় দেখা যায় ছায়ামূর্তি।"
            )
            first(at.button,"Generate 7-Day Marketing Draft").click().run()
            assert_ok(at,"campaign creation")
            with sqlite3.connect(db) as conn:
                count=conn.execute("SELECT COUNT(*) FROM marketing_campaigns").fetchone()[0]
                assets=conn.execute("SELECT COUNT(*) FROM marketing_assets").fetchone()[0]
            assert (count,assets)==(1,8),f"Expected one campaign and 8 assets, got {(count,assets)}"
            first(at.button,"Save Marketing Review Decision").click().run()
            assert_ok(at,"asset approval")
            with sqlite3.connect(db) as conn:
                status=conn.execute(
                    "SELECT status FROM marketing_assets ORDER BY id LIMIT 1").fetchone()[0]
            assert status=="Approved"
            first(at.text_area,"Social caption (Bangla)").set_value(
                "এই ভয়ানক রাতের রহস্য সামনে আসবে খুব শিগগিরই। "
                "পুরো বাংলা ভৌতিক গল্পটি দেখতে প্রস্তুত তো?"
            )
            first(at.button,"Save Draft Changes").click().run()
            assert_ok(at,"asset revision")
            with sqlite3.connect(db) as conn:
                status=conn.execute(
                    "SELECT status FROM marketing_assets ORDER BY id LIMIT 1").fetchone()[0]
            assert status=="Draft","Edited approved copy retained approval"
            first(at.number_input,"Impressions").set_value(3000)
            first(at.number_input,"Views").set_value(1200)
            first(at.number_input,"Clicks").set_value(90)
            first(at.number_input,"Engagements").set_value(200)
            first(at.button,"Save Manual Performance Record").click().run()
            assert_ok(at,"manual analytics")
            with sqlite3.connect(db) as conn:
                rows=conn.execute("SELECT impressions,clicks,source FROM marketing_metrics").fetchall()
            assert rows==[(3000,90,"manual")],rows
            assert any(x.proto.label=="Download Editorial Calendar CSV (UTF-8)"
                       for x in at.get("download_button"))
            print("PASS: Streamlit Growth Engine campaign → 8 assets → approval → edit reset → analytics → export")

    # Dedicated marketing-only preview runs in separate temporary fixture
    # and must disable every state-changing button in its public browser.
    with patch("requests.Session.request",
               side_effect=AssertionError("Public marketing preview contacted an API")):
        at=AppTest.from_file(str(SOURCE/"marketing_preview.py"),default_timeout=120).run()
        assert_ok(at,"isolated read-only demo")
        assert "READ-ONLY PUBLIC DEMO" in " ".join(x.message for x in at.warning)
        for label in ("Generate 7-Day Marketing Draft","Save Draft Changes",
                      "Save Marketing Review Decision","Save Manual Performance Record"):
            button=first(at.button,label)
            assert button.disabled, f"{label} was enabled in public preview"
        print("PASS: isolated read-only dashboard contains fictional fixtures, no ad calls")


if __name__=="__main__":
    main()
