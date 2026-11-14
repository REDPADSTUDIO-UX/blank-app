# REDPAD Growth Engine — Marketing Agent (Offline Safe Release)

Feature-branch application module: Growth Engine tab in REDPAD AI Studio.
Dedicated public read-only entrypoint: marketing_preview.py.
No real campaign, brand/client content or secret is included in the public fixture.

## Shipped, actual behavior

- 7-day creative sprint from a standalone idea or an existing content draft.
- Four editorial platform variants: YouTube Shorts/Community, Facebook Reel/Feed, Instagram Reel/Story, TikTok story/BTS.
- Campaign objectives: awareness, video views, engagement, subscribers, website visits.
- Horror/other category adaptations, Bangla hook/captions, per-platform placement, thumbnail text, hashtags, visual/cutdown directions, recommended Bangladesh-local scheduling times.
- Human-editable creative cards with per-asset approvals and optimistic revisions. Any copy change resets its prior approval.
- Original source title, topic and script are SHA-256-bound; changed linked scripts block approval and export until a fresh campaign is created.
- A planned editorial calendar, human-ready queue and approval-filtered JSON/CSV exports. UTF-8 BOM and spreadsheet formula safety in CSV.
- A hypothetical budget simulator using USER-ENTERED CPM (arithmetic only; no ad-rate quotes or reach guarantees).
- Manually entered and labelled campaign metrics: impressions, views, clicks, engagements, conversions and reported spend. Actual CTR/engagement calculations only with data. No invented platform analytics.
- UTM link planning for approved/manual posting; no auto navigation to advertiser payment, no social tokens or credentials.
- SQLite-only additive tables: marketing_campaigns, marketing_assets, marketing_metrics. Existing Studio data is not migrated, erased or overwritten.
- A completely separate read-only public dashboard preview using fictional Nishikotha horror marketing campaigns. The preview disables generation, edits, approvals and manual metrics write actions. Its demo filesystem can reset on Render Free.

## What is NOT shipped and MUST NOT be claimed

This is a deterministic, rule-based **offline marketing planning agent**, not an LLM generating unpredictable new ideas. No external AI inference is used because the owner has forbidden paid APIs.

It does NOT do:
- Automatically post content to YouTube, Facebook, Instagram or TikTok.
- Purchase/boost campaigns on Meta Ads or Google Ads.
- Scrape or retrieve real-time audience data, performance metrics or trends.
- Spend, charge billing accounts, create actual ad sets, or optimize bids.
- Maintain always-on publish queues, background schedules, API tokens, or producer impersonation.

A real autonomous marketing agent would require separate connected platform accounts, platform approval/eligibility, durable job/metric storage, true live analytics and the owner's explicit campaign/spend approvals. Those are separate future integrations, NOT part of this safe version.

## Operational release constraints

- The existing Render Free service redpad-ai-studio-private-preview holds original ephemeral SQLite and media which have NOT been fully backed up and restored.
- Absolutely do not restart, redeploy, migrate or change old service settings.
- Use a **different, isolated Free Render showcase service** for marketing_preview.py. Enable autoDeploy=false and provide NO access tokens, OAuth keys, production database or advertising secrets. Since it has only fiction/sample data, a public read-only link is acceptable.
- This preview demonstrates the Marketing Growth Engine UI, not production persistence or real Google/Meta integration.
- The integrated feature is separately available in the Studio's Growth Engine tab and through PR #2. Production deployment is gated on the original data backup/isolated restore.
- No YouTube upload/publication/scheduling, paid generation, main branch update or GitHub merge is permitted.

## Tests

- tests/test_marketing.py — 8 platform assets, UTF-8 Bangla, local calendar, zero-API, source revisions, approvals, metrics, exports, bad URLs and budget safety.
- tests/test_marketing_ui.py — real Streamlit dashboard campaign creation and review; isolated public-demo controls explicitly disabled.
- GitHub Actions: runs these alongside current Video Studio, Storyboard, YouTube and full Render backup tests on a throwaway test database.

## Manual owner workflow

1. Open integrated REDPAD AI Studio → Growth Engine.
2. Choose an existing approved/editable content draft or standalone marketing idea.
3. Create 7-day content sprint, review every platform creative, edit copy and visual notes, approve each one.
4. Export CSV and paste approved copy into social channels yourself.
5. Enter actual platform metrics manually and review which hooks or placements worked.
6. Use Budget Scenario Lab only for hypothetical arithmetic. No live ad spend can occur.

Production owner must separately authorize platform integrations. Marketing dashboard does not imply live marketing automation.

Owner controls remain: no paid API, no live ads, no video posts, no Render-old deployment, no main merge.
