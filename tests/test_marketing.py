"""Marketing agent unit tests; all planning/approval/metrics remain offline."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from redpad_pipeline.marketing import (
    MarketingError, assets_for, budget_scenario, campaigns, create_campaign,
    export_csv, export_package, get_campaign, init_marketing, metric_summary,
    metrics_for, review_asset, save_metrics, source_current, update_asset, utm_link,
)


class MarketingAgent(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="redpad-marketing-ci-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "studio.sqlite"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE channels(id INTEGER PRIMARY KEY,name TEXT)")
            db.execute("INSERT INTO channels VALUES(1,'নিশিকথা')")
            db.execute("""CREATE TABLE content(
                id INTEGER PRIMARY KEY, channel_id INTEGER,
                title TEXT,topic TEXT,script TEXT,status TEXT
            )""")
            db.execute("""INSERT INTO content VALUES
                (1,1,'শেষ ট্রেন','এক রহস্যময় যাত্রী',
                 'শেষ ট্রেনে এক রহস্যময় যাত্রী উঠে বসে। সে হঠাৎ অদৃশ্য হয়।','Draft')""")
        init_marketing(self.path)
        self.kwargs = dict(
            name="নিশিকথা — শেষ ট্রেন", topic="শেষ ট্রেনে এক রহস্যময় যাত্রী উঠে বসে। অদ্ভুত কিছু ঘটে।",
            audience="বাংলাদেশি প্রাপ্তবয়স্ক রহস্যপ্রেমী", region="Bangladesh",
            category="Horror", objective="Subscribers", kind="Organic",
            start_date="2026-10-30", platforms=list(("YouTube","Facebook","Instagram","TikTok")),
            landing_url="https://www.youtube.com/channel/UCtbHkj0GwJxjXZWbItDAyuQ",
            content_id=1,channel_id=1,
        )

    def test_zero_api_organic_7_day_plan_and_export(self):
        with patch("requests.Session.request",side_effect=AssertionError("network attempted")):
            cid=create_campaign(self.path,**self.kwargs)
            creative=assets_for(self.path,cid)
            self.assertEqual(len(creative),8)
            self.assertEqual(len(set(a["platform"] for a in creative)),4)
            self.assertTrue(all(a["status"]=="Draft" for a in creative))
            self.assertTrue(all("+06:00" in a["planned_local"] for a in creative))
            self.assertIn("ভৌতিকগল্প",creative[0]["hashtags"])
            self.assertTrue(source_current(self.path,get_campaign(self.path,cid)))
            self.assertEqual(campaigns(self.path)[0]["approved_count"],0)
            exported=export_package(self.path,cid)
            self.assertEqual(len(exported["assets"]),8)
            self.assertIn("no social post",exported["disclaimer"])
            csv_data=export_csv(self.path,cid)
            self.assertTrue(csv_data.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"YouTube",csv_data)
            link=utm_link(get_campaign(self.path,cid),creative[0])
            self.assertIn("utm_source=youtube",link)
            self.assertIn("utm_medium=social",link)
        print("PASS: eight platform-specific English/Bangla editorial drafts, Dhaka calendar, UTF-8 exports")

    def test_manual_review_revision_and_stale_script(self):
        cid=create_campaign(self.path,**self.kwargs)
        creative=assets_for(self.path,cid)
        a=creative[0]
        review_asset(self.path,cid,a["id"],a["revision"],"Approved")
        with self.assertRaises(MarketingError):
            review_asset(self.path,cid,a["id"],a["revision"],"Approved")
        self.assertEqual(assets_for(self.path,cid)[0]["status"],"Approved")
        # Any editing resets approval and requires a new human sign-off.
        revision=assets_for(self.path,cid)[0]["revision"]
        update_asset(self.path,cid,a["id"],revision,
            headline="নতুন রহস্য", caption="এই গল্পের শেষটা জানার আগে সাবস্ক্রাইব করো।",
            tags=["নিশিকথা","বাংলাগল্প"],visual_direction="Cinematic light & shadow",
            thumbnail_text="শেষ ট্রেন",cta="গল্প শুনুন",
            planned_local=a["planned_local"])
        self.assertEqual(assets_for(self.path,cid)[0]["status"],"Draft")
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE content SET script='Changed source script' WHERE id=1")
        self.assertFalse(source_current(self.path,get_campaign(self.path,cid)))
        with self.assertRaisesRegex(MarketingError,"changed"):
            review_asset(self.path,cid,a["id"],revision+1,"Approved")
        with self.assertRaisesRegex(MarketingError,"changed"):
            export_package(self.path,cid)
        print("PASS: manual approval, stale review lock, edited approval reset and source hash protection")

    def test_manual_only_metrics_no_fake_platform_data(self):
        cid=create_campaign(self.path,**self.kwargs)
        aid=assets_for(self.path,cid)[0]["id"]
        self.assertEqual(metrics_for(self.path,cid),[])
        self.assertIsNone(metric_summary([])["ctr_percent"])
        save_metrics(self.path,aid,"2026-10-30",impressions=10000,views=5000,
                     clicks=400,engagements=640,conversions=8,spend_bdt=0,
                     attribution_note="Manual YouTube Studio copy")
        save_metrics(self.path,aid,"2026-10-30",impressions=11000,views=5500,
                     clicks=440,engagements=700,conversions=10,spend_bdt=100,
                     attribution_note="Updated by owner")
        rows=metrics_for(self.path,cid)
        self.assertEqual(len(rows),1)
        stats=metric_summary(rows)
        self.assertEqual(stats["ctr_percent"],4)
        self.assertEqual(stats["spend_bdt"],100)
        self.assertAlmostEqual(stats["cpc_bdt"],100/440,places=2)
        with self.assertRaisesRegex(MarketingError,"Clicks"):
            save_metrics(self.path,aid,"2026-10-31",impressions=5,views=2,
                         clicks=6,engagements=1,conversions=0,spend_bdt=0)
        self.assertEqual(budget_scenario(12000,300)["assumed_impressions"],40000)
        print("PASS: owner entered performance only, safe replacements and budget arithmetic")

    def test_invalid_campaign_and_urls_rejected(self):
        broken=[dict(platforms=["YouTube","YouTube"]),
                dict(platforms=[]),dict(platforms=["Spam"]),
                dict(kind="Organic",budget_bdt=1000),
                dict(landing_url="http://example.com"),
                dict(landing_url="https://localhost/private"),
                dict(content_id=1,channel_id=99),
                dict(name=""),
                dict(topic="bad")]
        for fields in broken:
            with self.subTest(fields=fields):
                with self.assertRaises(MarketingError):
                    create_campaign(self.path,**{**self.kwargs,**fields})
        self.assertFalse(campaigns(self.path))

    def test_human_approval_never_sends_post_or_ads(self):
        cid=create_campaign(self.path,**self.kwargs)
        assets=assets_for(self.path,cid)
        for a in assets:
            review_asset(self.path,cid,a["id"],a["revision"],"Approved")
        self.assertEqual(get_campaign(self.path,cid)["status"],"Approved")
        self.assertEqual(len(export_package(self.path,cid,approved_only=True)["assets"]),8)
        self.assertFalse(any(a["status"]=="Published" for a in assets_for(self.path,cid)))
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM marketing_metrics").fetchone()[0],0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
