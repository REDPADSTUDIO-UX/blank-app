"""Public, read-only and fictional REDPAD Growth Engine dashboard showcase.

This entrypoint never connects to old Render data, Google accounts, paid AI,
Meta/Google Ads, YouTube publishing or real client analytics. Synthetic demo
fixtures live in a temporary demo-only SQLite file which may reset on free
instance spin-down. This route cannot mutate campaigns from the browser.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import gettempdir
import sqlite3

import streamlit as st

from redpad_pipeline.marketing import (
    campaigns, create_campaign, init_marketing, assets_for, review_asset,
)
from redpad_pipeline.marketing_ui import show_marketing

st.set_page_config(
    page_title="REDPAD Growth Engine • Read-only Demo",
    page_icon="📣", layout="wide", initial_sidebar_state="collapsed",
)
st.markdown(
    """<style>
    div[data-testid="stAppViewContainer"] { background: #0c1018; }
    div[data-testid="stHeader"] { background: #0c1018; }
    .block-container { padding-top: 2.2rem; }
    div[data-testid="stMetric"] { border:1px solid #283040;
      border-radius:14px; padding:15px 18px;background:#131a26; }
    </style>""", unsafe_allow_html=True
)
st.markdown("##### REDPAD AI STUDIO / PRIVATE PRODUCT PROTOTYPE")
st.title("📣 Growth Engine — Marketing Agent Dashboard")
st.caption("Preview of the new marketing workflow • Absolutely no paid API, social posting or ad spend")

# Private data is intentionally absent from this disposable public showcase.
DB = Path(gettempdir()) / "redpad_public_marketing_demo_v1.sqlite3"
init_marketing(DB)
with sqlite3.connect(DB) as conn:
    created = conn.execute("SELECT COUNT(*) FROM marketing_campaigns").fetchone()[0]
if not created:
    ids = []
    ids.append(create_campaign(
        DB, name="নিশিকথা — শেষ ট্রেনের যাত্রী",
        topic="গভীর রাতে একটি শেষ ট্রেন। এক অচেনা যাত্রী বারবার একই স্টেশনের নাম বলতে থাকে। "
              "হঠাৎ কামরার আলো নিভে যায়, আর জানালায় দেখা যায় অদ্ভুত একটি মুখ।",
        audience="Bangla-speaking horror-story viewers, adults 18+",
        category="Horror", objective="Video Views", kind="Organic",
        region="Bangladesh", platforms=["YouTube", "Facebook", "Instagram", "TikTok"],
        start_date=date.today().isoformat(),
        landing_url="https://www.youtube.com/channel/UCtbHkj0GwJxjXZWbItDAyuQ",
    ))
    ids.append(create_campaign(
        DB, name="Behind the Fear — Nishikotha Teaser Week",
        topic="কেন রাত তিনটায় ঘড়ির কাঁটা থেমে যায়? অদৃশ্য ছায়া ও পুরোনো রেলস্টেশনের রহস্য "
              "নিয়ে একটি নতুন বাংলা থ্রিলার সিরিজের টিজার প্রচারণা।",
        audience="Bangladesh-based mystery and thriller audiences, 18–34",
        category="Horror", objective="Subscribers", kind="Paid Strategy Only",
        region="Bangladesh", platforms=["YouTube", "Facebook", "Instagram"],
        start_date=date.today().isoformat(), budget_bdt=12000,
        landing_url="https://www.youtube.com/channel/UCtbHkj0GwJxjXZWbItDAyuQ",
    ))
    for asset in assets_for(DB, ids[0])[:3]:
        review_asset(DB,ids[0],asset["id"],asset["revision"],"Approved")

st.sidebar.title("REDPAD")
st.sidebar.markdown("**Growth Engine**")
st.sidebar.caption("Marketing intelligence • editorial approvals • organic plans")
st.sidebar.divider()
st.sidebar.info("Public demonstration with entirely fictional campaign records. "
                "No real user data, paid platform account, AI provider token or marketing API.")
show_marketing(DB,demo_mode=True)
st.divider()
st.caption("© REDPAD AI Studio • Read-only fictional preview. "
           "Demo data may reset on Render Free spin-down; live campaigns and performance are not connected.")
