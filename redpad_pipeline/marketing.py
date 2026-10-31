"""REDPAD Marketing Agent: deterministic/offline creative planning and human approval.

This module does not use AI APIs, advertising APIs, platform credentials,
network access, ad spend, auto publishing, scraping or impersonation.

Data is stored in additive SQLite tables so existing Studio data is not edited.
The Render Free filesystem is ephemeral; durable production storage remains a
separate, blocked migration while original database backup is incomplete.
"""
from __future__ import annotations

import csv
from datetime import datetime, date, time, timedelta, timezone
from hashlib import sha256
from io import StringIO
import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse
from zoneinfo import ZoneInfo

BD = ZoneInfo("Asia/Dhaka")
PLATFORMS = ("YouTube", "Facebook", "Instagram", "TikTok")
GOALS = ("Awareness", "Video Views", "Engagement", "Subscribers", "Website Visits")
CAMPAIGN_KINDS = ("Organic", "Paid Strategy Only")
ASSET_STATES = ("Draft", "Changes requested", "Approved")
MAX_ASSETS = 24

# These are platform-specific editorial recommendations, NOT platform-provided
# specifications, campaign statistics, reach forecasts or targeting guarantees.
FORMATS = {
    "YouTube": ("Short teaser (vertical)", "Community post"),
    "Facebook": ("Reel teaser (vertical)", "Feed post"),
    "Instagram": ("Reel teaser (vertical)", "Story sequence"),
    "TikTok": ("Vertical story hook", "Behind-the-scenes hook"),
}
TIME_SLOTS = {"YouTube": (19, 30), "Facebook": (20, 0), "Instagram": (18, 30), "TikTok": (21, 0)}
CTAS = {
    "Awareness": "গল্পটা কার সঙ্গে শেয়ার করবে?",
    "Video Views": "পুরো গল্পটি দেখতে চ্যানেলে যাও।",
    "Engagement": "শেষ দৃশ্যে কী ঘটবে বলে মনে হয়? কমেন্টে বলো।",
    "Subscribers": "এমন নতুন গল্প পেতে চ্যানেলটি সাবস্ক্রাইব করো।",
    "Website Visits": "বিস্তারিত জানতে দেওয়া লিংকটি দেখো।",
}
DEFAULT_TAGS = {
    "Horror": ["নিশিকথা", "ভৌতিকগল্প", "BanglaHorror", "বাংলাগল্প", "Suspense"],
    "Documentary": ["BanglaDocumentary", "বাংলাডকুমেন্টারি", "Bangladesh", "Documentary"],
    "Entertainment": ["বাংলাবিনোদন", "BanglaStory", "Entertainment"],
}


class MarketingError(ValueError):
    pass


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect(path):
    conn = sqlite3.connect(path, timeout=15)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


def init_marketing(path):
    with _connect(path) as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS marketing_campaigns(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          channel_id INTEGER,
          content_id INTEGER,
          source_sha256 TEXT NOT NULL,
          name TEXT NOT NULL,
          objective TEXT NOT NULL,
          category TEXT NOT NULL,
          kind TEXT NOT NULL,
          audience TEXT NOT NULL,
          region TEXT NOT NULL,
          landing_url TEXT NOT NULL,
          start_date TEXT NOT NULL,
          platforms_json TEXT NOT NULL,
          budget_bdt INTEGER NOT NULL DEFAULT 0,
          status TEXT NOT NULL DEFAULT 'Draft',
          revision INTEGER NOT NULL DEFAULT 1,
          created_utc TEXT NOT NULL,
          updated_utc TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS marketing_assets(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          campaign_id INTEGER NOT NULL REFERENCES marketing_campaigns(id) ON DELETE CASCADE,
          platform TEXT NOT NULL,
          placement TEXT NOT NULL,
          headline TEXT NOT NULL,
          caption TEXT NOT NULL,
          hashtags_json TEXT NOT NULL,
          visual_direction TEXT NOT NULL,
          thumbnail_text TEXT NOT NULL,
          cta TEXT NOT NULL,
          planned_local TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'Draft',
          revision INTEGER NOT NULL DEFAULT 1,
          approved_utc TEXT,
          created_utc TEXT NOT NULL,
          updated_utc TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS marketing_metrics(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          asset_id INTEGER NOT NULL REFERENCES marketing_assets(id) ON DELETE CASCADE,
          date_local TEXT NOT NULL,
          impressions INTEGER NOT NULL,
          views INTEGER NOT NULL,
          clicks INTEGER NOT NULL,
          engagements INTEGER NOT NULL,
          conversions INTEGER NOT NULL,
          spend_bdt REAL NOT NULL,
          attribution_note TEXT NOT NULL DEFAULT '',
          source TEXT NOT NULL DEFAULT 'manual',
          updated_utc TEXT NOT NULL,
          UNIQUE(asset_id,date_local)
        );
        CREATE INDEX IF NOT EXISTS idx_marketing_asset_campaign ON marketing_assets(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_marketing_metric_asset ON marketing_metrics(asset_id);
        """)


def _src_hash(title: str, topic: str, script: str) -> str:
    payload = json.dumps([title, topic, script], ensure_ascii=False, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _get_content(db, content_id: int | None):
    if content_id is None:
        return None
    row = db.execute(
        "SELECT id,channel_id,title,topic,script FROM content WHERE id=?", (content_id,)
    ).fetchone()
    if not row:
        raise MarketingError("Source draft is missing. Please select a current content draft.")
    return dict(zip(("id", "channel_id", "title", "topic", "script"), row))


def source_current(db_path, campaign: dict):
    if campaign["content_id"] is None:
        return True
    with _connect(db_path) as db:
        source = _get_content(db, campaign["content_id"])
    return (
        source is not None
        and _src_hash(source["title"], source["topic"], source["script"])
        == campaign["source_sha256"]
    )


def _safe_tags(category: str, name: str) -> list[str]:
    canonical = category.strip().title()
    raw = DEFAULT_TAGS.get(canonical, DEFAULT_TAGS["Entertainment"]).copy()
    words = re.findall(r"[\w\u0980-\u09FF]+", name.replace(" ", ""))
    if words:
        tag = words[0][:30]
        if tag not in raw:
            raw.insert(0, tag)
    return raw[:6]


def _validate_url(url: str):
    if not url:
        return ""
    if len(url) > 400:
        raise MarketingError("Campaign destination URL is too long.")
    p = urlparse(url.strip())
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise MarketingError("Use a public HTTPS destination link without credentials or a custom port.")
    if p.hostname in ("localhost", "127.0.0.1") or p.hostname.endswith(".local"):
        raise MarketingError("A local or private URL cannot be used for promotions.")
    return url.strip()


def _planning_inputs(name, topic, audience, region, category, objective,
                     kind, platforms, start_date, landing_url, budget_bdt):
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 140:
        raise MarketingError("Campaign title must contain 2–140 characters.")
    if not isinstance(topic, str) or not 5 <= len(topic.strip()) <= 1200:
        raise MarketingError("Provide a 5–1200 character story, summary or content hook.")
    if not isinstance(audience, str) or not 2 <= len(audience.strip()) <= 150:
        raise MarketingError("Audience description must contain 2–150 characters.")
    if not isinstance(region, str) or not 2 <= len(region.strip()) <= 100:
        raise MarketingError("Target geography must contain 2–100 characters.")
    if objective not in GOALS or kind not in CAMPAIGN_KINDS:
        raise MarketingError("Choose a supported campaign goal and planning type.")
    if not isinstance(platforms, (list, tuple)) or not platforms or len(set(platforms)) != len(platforms):
        raise MarketingError("Choose one or more distinct platforms.")
    if any(p not in PLATFORMS for p in platforms):
        raise MarketingError("One campaign platform is not supported.")
    try:
        day = date.fromisoformat(str(start_date))
    except (TypeError, ValueError) as exc:
        raise MarketingError("Enter a valid campaign start date.") from exc
    if type(budget_bdt) is not int or budget_bdt < 0 or budget_bdt > 100_000_000:
        raise MarketingError("Planning budget must be between 0 and 100 million BDT.")
    if kind == "Organic" and budget_bdt:
        raise MarketingError("An organic plan cannot allocate paid media spend.")
    return day, _validate_url(landing_url)


def _make_assets(name, topic, objective, category, platforms, start_date, link):
    tags = _safe_tags(category, name)
    snippet = " ".join(topic.split())[:165].strip("।,. ")
    hook = ("এই গল্পের শেষটা আপনি অনুমান করতে পারবেন?"
            if category.lower() == "horror" else
            "এই গল্পটা অন্যভাবে দেখার সময় এসেছে।")
    assets = []
    for n, platform in enumerate(platforms):
        hour, minute = TIME_SLOTS[platform]
        for variation, placement in enumerate(FORMATS[platform]):
            day = start_date + timedelta(days=n + (variation * 3))
            planned = datetime.combine(day, time(hour, minute), BD).isoformat(timespec="minutes")
            headline = (f"{name[:85]} | {hook}" if not variation
                        else f"{name[:85]} — পর্দার আড়ালের রহস্য")
            caption = (
                f"{hook}\n\n{snippet}।\n\n{CTAS[objective]}"
                if not variation else
                f"প্রতিটা দৃশ্যের আড়ালে আছে একটা প্রশ্ন।\n{snippet}।\n"
                f"{CTAS[objective]}"
            )
            if link:
                caption += f"\n{link}"
            assets.append({
                "platform": platform,
                "placement": placement,
                "headline": headline[:200],
                "caption": caption[:1500],
                "hashtags": tags,
                "visual_direction": (
                    f"9:16 vertical cinematic hook; ominous opening in first 2 seconds; "
                    f"focus on the story's key visual, clean Bangla typography, "
                    f"no copied footage; {category} mood. Show curiosity without spoilers."
                    if variation == 0 else
                    f"Behind-the-scenes or intriguing still from licensed footage, "
                    f"safe Bangla overlays, curiosity-led narrative; {category} mood."
                ),
                "thumbnail_text": ("শেষটা কী হবে?" if not variation else "রহস্য এখনো বাকি"),
                "cta": CTAS[objective],
                "planned_local": planned,
                "status": "Draft",
            })
    if len(assets) > MAX_ASSETS:
        raise MarketingError("Campaign exceeds 24 assets.")
    return assets


def create_campaign(db_path, *, name, topic, audience, region="Bangladesh",
                    category="Horror", objective="Video Views",
                    kind="Organic", platforms=("YouTube", "Facebook", "Instagram", "TikTok"),
                    start_date=None, landing_url="", budget_bdt=0, content_id=None,
                    channel_id=None):
    """Create *drafts only*. No post, ad buy or external marketing action."""
    init_marketing(db_path)
    day, link = _planning_inputs(
        name, topic, audience, region, category, objective, kind, platforms,
        start_date or date.today().isoformat(), landing_url, budget_bdt
    )
    assets = _make_assets(name.strip(), topic.strip(), objective, category, platforms, day, link)
    now = _stamp()
    with _connect(db_path) as db:
        db.execute("BEGIN IMMEDIATE")
        content = _get_content(db, content_id)
        if content and (channel_id is not None and channel_id != content["channel_id"]):
            raise MarketingError("Selected content belongs to a different channel.")
        if content:
            channel_id = content["channel_id"]
            source_sha = _src_hash(content["title"], content["topic"], content["script"])
        else:
            source_sha = _src_hash(name.strip(), topic.strip(), "")
        cursor = db.execute("""INSERT INTO marketing_campaigns(
            channel_id,content_id,source_sha256,name,objective,category,kind,audience,
            region,landing_url,start_date,platforms_json,budget_bdt,created_utc,updated_utc
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            channel_id, content_id, source_sha, name.strip(), objective, category,
            kind, audience.strip(), region.strip(), link, day.isoformat(),
            json.dumps(list(platforms)), budget_bdt, now, now
        ))
        campaign_id = cursor.lastrowid
        for asset in assets:
            db.execute("""INSERT INTO marketing_assets(
                campaign_id,platform,placement,headline,caption,hashtags_json,
                visual_direction,thumbnail_text,cta,planned_local,created_utc,updated_utc
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (
                campaign_id, asset["platform"], asset["placement"], asset["headline"],
                asset["caption"], json.dumps(asset["hashtags"], ensure_ascii=False),
                asset["visual_direction"], asset["thumbnail_text"], asset["cta"],
                asset["planned_local"], now, now
            ))
    return campaign_id


def _rows(cursor):
    columns = [field[0] for field in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def campaigns(db_path):
    init_marketing(db_path)
    with _connect(db_path) as db:
        return _rows(db.execute(
            """SELECT c.*, (SELECT COUNT(*) FROM marketing_assets a WHERE a.campaign_id=c.id)
                AS asset_count,
               (SELECT COUNT(*) FROM marketing_assets a WHERE a.campaign_id=c.id AND a.status='Approved')
                AS approved_count
               FROM marketing_campaigns c ORDER BY c.id DESC"""
        ))


def get_campaign(db_path, campaign_id):
    init_marketing(db_path)
    with _connect(db_path) as db:
        data = _rows(db.execute("SELECT * FROM marketing_campaigns WHERE id=?", (campaign_id,)))
    if not data:
        raise MarketingError("Marketing campaign not found.")
    return data[0]


def assets_for(db_path, campaign_id):
    init_marketing(db_path)
    with _connect(db_path) as db:
        result = _rows(db.execute(
            "SELECT * FROM marketing_assets WHERE campaign_id=? ORDER BY planned_local,id", (campaign_id,)
        ))
    for r in result:
        r["hashtags"] = json.loads(r["hashtags_json"])
    return result


def update_asset(db_path, campaign_id, asset_id, expected_revision, *,
                 headline, caption, tags, visual_direction, thumbnail_text,
                 cta, planned_local):
    if (not isinstance(headline, str) or not 3 <= len(headline.strip()) <= 200 or
            not isinstance(caption, str) or not 10 <= len(caption.strip()) <= 1500 or
            not isinstance(visual_direction, str) or not 5 <= len(visual_direction.strip()) <= 800 or
            not isinstance(thumbnail_text, str) or len(thumbnail_text) > 90 or
            not isinstance(cta, str) or len(cta) > 180):
        raise MarketingError("Invalid copy length. Check headline, caption, visual and CTA.")
    if not isinstance(tags, (list, tuple)) or len(tags) > 12:
        raise MarketingError("Hashtags must contain at most twelve entries.")
    cleaned_tags = [re.sub(r"[^\w\u0980-\u09FF]", "", str(t).lstrip("#")) for t in tags]
    if any(not t or len(t) > 45 for t in cleaned_tags):
        raise MarketingError("One or more hashtags are invalid or too long.")
    try:
        dt = datetime.fromisoformat(planned_local)
        if dt.utcoffset() != timedelta(hours=6):
            raise ValueError("Not a Dhaka-local timestamp")
    except ValueError as exc:
        raise MarketingError("Use an Asia/Dhaka +06:00 planning timestamp.") from exc
    init_marketing(db_path)
    now = _stamp()
    with _connect(db_path) as db:
        db.execute("BEGIN IMMEDIATE")
        c = _rows(db.execute("SELECT * FROM marketing_campaigns WHERE id=?", (campaign_id,)))
        if not c:
            raise MarketingError("Campaign no longer exists.")
        if not source_current(db_path, c[0]):
            raise MarketingError("Linked script changed; create a new marketing campaign.")
        cur = db.execute("""UPDATE marketing_assets SET
            headline=?, caption=?, hashtags_json=?, visual_direction=?, thumbnail_text=?,
            cta=?, planned_local=?, status='Draft',approved_utc=NULL,
            revision=revision+1,updated_utc=?
            WHERE id=? AND campaign_id=? AND revision=?""",
            (headline.strip(), caption.strip(), json.dumps(cleaned_tags,ensure_ascii=False),
             visual_direction.strip(), thumbnail_text.strip(), cta.strip(),
             planned_local, now, asset_id,campaign_id,expected_revision))
        if cur.rowcount != 1:
            raise MarketingError("Asset changed or has disappeared. Refresh the dashboard.")
        db.execute("""UPDATE marketing_campaigns SET status='Draft', revision=revision+1,
            updated_utc=? WHERE id=?""", (now,campaign_id))


def review_asset(db_path,campaign_id,asset_id,expected_revision,decision):
    if decision not in ("Approved", "Changes requested", "Draft"):
        raise MarketingError("Unsupported human review decision.")
    init_marketing(db_path)
    with _connect(db_path) as db:
        db.execute("BEGIN IMMEDIATE")
        source = _rows(db.execute("SELECT * FROM marketing_campaigns WHERE id=?", (campaign_id,)))
        if not source:
            raise MarketingError("Campaign not found.")
        if not source_current(db_path, source[0]):
            raise MarketingError("Linked content changed. Refresh the campaign before approval.")
        now = _stamp()
        cur = db.execute("""UPDATE marketing_assets SET status=?,approved_utc=?,
            revision=revision+1,updated_utc=?
            WHERE id=? AND campaign_id=? AND revision=?""",
            (decision, now if decision=="Approved" else None, now,
             asset_id,campaign_id,expected_revision))
        if cur.rowcount!=1:
            raise MarketingError("Asset changed while reviewing. Refresh first.")
        stats = _rows(db.execute(
            "SELECT status,COUNT(*) AS count FROM marketing_assets WHERE campaign_id=? GROUP BY status",
            (campaign_id,)))
        all_approved = all(row["status"] == "Approved" for row in stats)
        count = sum(row["count"] for row in stats)
        campaign_state = "Approved" if all_approved and count else "Draft"
        db.execute("""UPDATE marketing_campaigns SET status=?,revision=revision+1,
            updated_utc=? WHERE id=?""",(campaign_state,now,campaign_id))
    return campaign_state


def save_metrics(db_path,asset_id,day,*,impressions,views,clicks,engagements,
                 conversions,spend_bdt=0,attribution_note=""):
    """Only user-entered metrics. No claims of platform verification."""
    try:
        on_date = date.fromisoformat(str(day)).isoformat()
    except (TypeError,ValueError) as exc:
        raise MarketingError("Invalid analytics date.") from exc
    data = (impressions,views,clicks,engagements,conversions)
    if any(type(n) is not int or n<0 or n>1_000_000_000 for n in data):
        raise MarketingError("Manual metric counts must be nonnegative integers.")
    if type(spend_bdt) not in (float,int) or not 0<=spend_bdt<=100_000_000:
        raise MarketingError("Manual spend must be between 0 and 100 million BDT.")
    if clicks>impressions and impressions>0:
        raise MarketingError("Clicks cannot exceed a positive impression count.")
    if len(attribution_note)>300:
        raise MarketingError("Notes cannot exceed 300 characters.")
    init_marketing(db_path)
    with _connect(db_path) as db:
        if not db.execute("SELECT id FROM marketing_assets WHERE id=?",(asset_id,)).fetchone():
            raise MarketingError("Marketing asset is missing.")
        db.execute("""INSERT INTO marketing_metrics(
            asset_id,date_local,impressions,views,clicks,engagements,conversions,
            spend_bdt,attribution_note,updated_utc
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(asset_id,date_local) DO UPDATE SET
              impressions=excluded.impressions,views=excluded.views,
              clicks=excluded.clicks,engagements=excluded.engagements,
              conversions=excluded.conversions,spend_bdt=excluded.spend_bdt,
              attribution_note=excluded.attribution_note,updated_utc=excluded.updated_utc""",
            (asset_id,on_date,*data,float(spend_bdt),attribution_note.strip(),_stamp()))


def metrics_for(db_path,campaign_id):
    init_marketing(db_path)
    with _connect(db_path) as db:
        return _rows(db.execute("""SELECT a.platform,a.headline,a.id AS asset_id,m.*
          FROM marketing_metrics m JOIN marketing_assets a ON a.id=m.asset_id
          WHERE a.campaign_id=? ORDER BY m.date_local DESC,m.id DESC""",(campaign_id,)))


def metric_summary(rows):
    fields=("impressions","views","clicks","engagements","conversions","spend_bdt")
    total={k:sum(row[k] for row in rows) for k in fields}
    impressions=total["impressions"];clicks=total["clicks"]
    total["ctr_percent"]=round(100*clicks/impressions,2) if impressions else None
    total["engagement_rate_percent"]=round(100*total["engagements"]/impressions,2) if impressions else None
    total["cpc_bdt"]=round(total["spend_bdt"]/clicks,2) if clicks else None
    return total


def budget_scenario(spend_bdt:int, hypothetical_cpm_bdt:float):
    """Illustrative arithmetic using USER-ENTERED CPM, not fetched platform rates."""
    if spend_bdt<0 or spend_bdt>100_000_000 or hypothetical_cpm_bdt<=0 or hypothetical_cpm_bdt>1_000_000:
        raise MarketingError("Enter a valid hypothetical spend and CPM.")
    return {"assumed_impressions":round(spend_bdt*1000/hypothetical_cpm_bdt),
            "assumed_cpm_bdt":hypothetical_cpm_bdt,
            "spend_bdt":spend_bdt,
            "warning":"Hypothetical planning arithmetic only; NOT a Meta/Google quote or performance guarantee."}


def export_package(db_path,campaign_id,approved_only=False):
    c=get_campaign(db_path,campaign_id)
    if not source_current(db_path,c):
        raise MarketingError("Linked source script changed. Regenerate the marketing plan.")
    records=assets_for(db_path,campaign_id)
    if approved_only:
        records=[row for row in records if row["status"]=="Approved"]
        if not records:
            raise MarketingError("No human-approved assets are ready to export.")
    clean=[]
    for item in records:
        clean.append({k:item[k] for k in (
            "id","platform","placement","headline","caption","hashtags",
            "visual_direction","thumbnail_text","cta","planned_local","status","revision"
        )})
    return {
        "format":"REDPAD-MARKETING-PLAN-V1","source":"Offline rules-based drafts; no live provider data",
        "disclaimer":"EXPORT ONLY — no social post, boost or paid advertising is triggered",
        "campaign":{k:c[k] for k in (
            "id","name","objective","category","kind","audience","region",
            "landing_url","start_date","budget_bdt","status"
        )},
        "assets":clean,
    }


def export_csv(db_path,campaign_id,approved_only=False):
    data=export_package(db_path,campaign_id,approved_only)
    columns=["id","platform","placement","headline","caption","hashtags",
             "visual_direction","thumbnail_text","cta","planned_local","status","revision"]
    buffer=StringIO()
    writer=csv.DictWriter(buffer,fieldnames=columns)
    writer.writeheader()
    for item in data["assets"]:
        row={**item,"hashtags":" ".join("#"+h for h in item["hashtags"])}
        # Spreadsheet formula injection guard for text fields in exports.
        for key,value in row.items():
            if isinstance(value,str) and value.lstrip().startswith(("=","+","-","@")):
                row[key]="'"+value
        writer.writerow(row)
    return ("\ufeff"+buffer.getvalue()).encode("utf-8")


def utm_link(campaign,asset):
    url=campaign["landing_url"]
    if not url:
        return ""
    p=urlparse(url)
    params=dict(parse_qsl(p.query,keep_blank_values=True))
    params.update({
        "utm_source":asset["platform"].lower(),
        "utm_medium":"social" if campaign["kind"]=="Organic" else "planned_paid",
        "utm_campaign":re.sub(r"[^\w-]+","-",campaign["name"].lower()).strip("-")[:80],
        "utm_content":str(asset["id"]),
    })
    return urlunparse(p._replace(query=urlencode(params)))
