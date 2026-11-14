"""REDPAD Marketing & Growth Agent dashboard.

All integrations are OFF. Plans, approvals, editorial calendars, hypothetical
budgets, hand-entered performance metrics and exports only. No advertising,
no auto publishing, no fake realtime insights or claims of network AI.
"""
from __future__ import annotations

from datetime import date, datetime
import json
import sqlite3
from pathlib import Path

import streamlit as st

from .marketing import (
    PLATFORMS, GOALS, CAMPAIGN_KINDS, MarketingError,
    assets_for, budget_scenario, campaigns, create_campaign, export_csv,
    export_package, get_campaign, init_marketing, metric_summary, metrics_for,
    review_asset, save_metrics, source_current, update_asset, utm_link,
)


def _drafts(db_path):
    with sqlite3.connect(db_path) as db:
        try:
            rows=db.execute("""SELECT c.id,c.channel_id,c.title,c.topic,c.script,ch.name
              FROM content c JOIN channels ch ON c.channel_id=ch.id
              ORDER BY c.id DESC""").fetchall()
        except sqlite3.OperationalError:
            return []
    return [{"id":x[0],"channel_id":x[1],"title":x[2],"topic":x[3],
             "script":x[4],"channel":x[5]} for x in rows]


def _notice(error):
    st.error(str(error))


def _campaign_builder(db_path, demo_mode=False):
    st.subheader("🧭 Campaign Builder")
    st.caption("Create a 7-day editorial growth sprint. Copy uses local story-aware templates, NOT a live LLM.")
    drafts=_drafts(db_path)
    options=["New campaign idea"]+[f"Linked draft #{c['id']} · {c['title']}" for c in drafts]
    with st.form("marketing_builder",clear_on_submit=False):
        option=st.selectbox("Source content",options,key="mk_source")
        linked=drafts[options.index(option)-1] if options.index(option)>0 else None
        left,right=st.columns(2)
        with left:
            name=st.text_input("Campaign / title",value=linked["title"] if linked else "",
                               max_chars=140,placeholder="নিশিকথা — শেষ ট্রেনের যাত্রী")
            category=st.selectbox("Category",["Horror","Documentary","Entertainment","Education","Brand"])
            objective=st.selectbox("Growth objective",GOALS,index=1)
            audience=st.text_input("Target audience",value="Bangla-speaking mystery & story fans, 18+",
                                   max_chars=150)
        with right:
            kind=st.radio("Strategy type",CAMPAIGN_KINDS, horizontal=True)
            region=st.text_input("Target geography",value="Bangladesh",max_chars=100)
            start=st.date_input("Campaign start",value=date.today())
            platforms=st.multiselect("Channels (editorial plans only)",PLATFORMS,
                                      default=list(PLATFORMS), key="mk_platforms")
        topic=st.text_area("Story summary, hook or campaign brief",
                           value=(linked["topic"]+" "+linked["script"][:650]).strip() if linked else "",
                           height=120, max_chars=1200,
                           placeholder="Describe the trailer, mystery and desired audience.")
        url=st.text_input("Optional HTTPS video / landing link",max_chars=400)
        budget=st.number_input("Illustrative paid budget (BDT; NOT spent)",min_value=0,max_value=100000000,
                               value=0,step=1000,disabled=kind=="Organic")
        create=st.form_submit_button("Generate 7-Day Marketing Draft",disabled=demo_mode)
    if create:
        try:
            cid=create_campaign(db_path,name=name,topic=topic,audience=audience,region=region,
                         category=category,objective=objective,kind=kind,platforms=platforms,
                         start_date=start.isoformat(),landing_url=url,
                         budget_bdt=int(budget if kind!="Organic" else 0),
                         content_id=linked["id"] if linked else None,
                         channel_id=linked["channel_id"] if linked else None)
            st.session_state["mk_campaign"]=cid
            st.success(f"Campaign #{cid} created in Draft. No ads or posts were sent.")
            st.rerun()
        except MarketingError as e:
            _notice(e)
    if demo_mode:
        st.info("Read-only demo: generating/editing campaigns is disabled. Integrated Studio has the full workflow.")


def _asset_review(db_path,c,assets,demo_mode=False):
    st.subheader("✍️ Creative Studio & Human Approval")
    if not assets:
        st.info("No creative assets yet.")
        return
    st.caption("Each channel gets tailored hooks, short copy, CTA, local publishing suggestions, and production directions.")
    for platform in PLATFORMS:
        matched=[a for a in assets if a["platform"]==platform]
        if not matched:
            continue
        with st.expander(f"{platform} • {len(matched)} creative drafts",expanded=False):
            for a in matched:
                st.markdown(f"**{a['placement']}** — {a['status']}")
                st.write(a["headline"])
                st.caption(a["caption"][:350])
    choices={f"#{a['id']} · {a['platform']} · {a['placement']} · {a['status']}":a for a in assets}
    chosen=st.selectbox("Edit / review a creative",list(choices),key="mk_selected_asset")
    a=choices[chosen]
    current=source_current(db_path,c)
    if not current:
        st.error("Linked script or title has changed. This campaign is STALE; create a fresh plan before approval/export.")
    with st.form(f"mk_edit_{a['id']}_{a['revision']}"):
        headline=st.text_input("Headline / hook",value=a["headline"],max_chars=200)
        caption=st.text_area("Social caption (Bangla)",value=a["caption"],height=170,max_chars=1500)
        tags=st.text_input("Hashtags separated by comma",value=", ".join(a["hashtags"]))
        visual=st.text_area("Creative direction / cutdown prompt",value=a["visual_direction"],
                           height=100,max_chars=800)
        left,right=st.columns(2)
        with left: thumb=st.text_input("Thumbnail overlay",value=a["thumbnail_text"],max_chars=90)
        with right: cta=st.text_input("Call to action",value=a["cta"],max_chars=180)
        planned=st.text_input("Planned local time (ISO 8601, +06:00)",
                              value=a["planned_local"])
        edited=st.form_submit_button("Save Draft Changes",disabled=demo_mode or not current)
    if edited:
        try:
            update_asset(db_path,c["id"],a["id"],a["revision"],headline=headline,caption=caption,
                         tags=[x.strip() for x in tags.split(",") if x.strip()],
                         visual_direction=visual,thumbnail_text=thumb,cta=cta,planned_local=planned)
            st.success("Saved: human approval reset to Draft.")
            st.rerun()
        except MarketingError as e:
            _notice(e)
    st.code(a["caption"]+"\n\n"+" ".join("#"+x for x in a["hashtags"]),language=None)
    st.caption("Copy above is ready to manually paste after approval. No automated publishing.")
    url=utm_link(c,a)
    if url:
        st.text_input("Trackable link (manual copy, no external requests)",url,key="mk_utm")
    status_col,decision_col=st.columns([1,2])
    status_col.metric("Creative status",a["status"])
    with decision_col:
        review=st.radio("Human decision",["Approved","Changes requested","Draft"],
                         horizontal=True,key="mk_review_choice")
        if st.button("Save Marketing Review Decision",disabled=demo_mode or not current,
                     key="mk_review_submit"):
            try:
                review_asset(db_path,c["id"],a["id"],a["revision"],review)
                st.success("Review saved. This DOES NOT publish or boost the asset.")
                st.rerun()
            except MarketingError as e:
                _notice(e)


def _calendar(c,assets):
    st.subheader("🗓️ Content Calendar & Manual Release Queue")
    approved=sum(a["status"]=="Approved" for a in assets)
    st.info(f"{approved} of {len(assets)} assets human-approved. All posting is MANUAL; "
            "planned dates are suggestions, NOT active scheduled jobs.")
    if not source_current(st.session_state.get("mk_db_path"),c):
        st.error("Linked script changed; previous approvals should not be used.")
    display=[]
    for a in assets:
        display.append({
            "Bangladesh planned time":a["planned_local"].replace("T"," ")[:16],
            "Platform":a["platform"],"Format":a["placement"],"Headline":a["headline"][:75],
            "Approval":a["status"],"Posting":("Manual ready" if a["status"]=="Approved" else "Needs review"),
        })
    st.dataframe(display,hide_index=True,use_container_width=True)
    st.caption("After manually posting, record actual results in the Analytics tab. "
               "YouTube/Facebook/Instagram/TikTok publishing tokens are NOT used here.")


def _analytics(db_path,c,assets,demo_mode=False):
    st.subheader("📊 Analytics & Growth Review")
    st.caption("All metrics are OWNER-ENTERED, not pulled from social networks. No invented platform statistics.")
    rows=metrics_for(db_path,c["id"])
    summary=metric_summary(rows)
    cards=st.columns(5)
    for card,field,title in zip(cards,["impressions","views","clicks","engagements","conversions"],
                               ["Impressions","Views","Clicks","Engagements","Conversions"]):
        card.metric(title,f"{summary[field]:,}")
    more=st.columns(3)
    more[0].metric("CTR (manual)",f"{summary['ctr_percent']}%" if summary["ctr_percent"] is not None else "No data")
    more[1].metric("Engagement rate",f"{summary['engagement_rate_percent']}%" if summary["engagement_rate_percent"] is not None else "No data")
    more[2].metric("Recorded spend",f"৳{summary['spend_bdt']:,.2f}")
    if rows:
        st.dataframe([{
            "Date":r["date_local"],"Platform":r["platform"],"Impressions":r["impressions"],
            "Views":r["views"],"Clicks":r["clicks"],"Engagements":r["engagements"],
            "Conversions":r["conversions"],"Spend ৳":r["spend_bdt"],
            "Source":"Manual input",
        } for r in rows],hide_index=True,use_container_width=True)
        by_platform={}
        for r in rows:
            key=r["platform"]
            by_platform[key]=by_platform.get(key,0)+r["views"]
        if any(by_platform.values()):
            st.bar_chart([{"Platform":k,"Views":v} for k,v in by_platform.items()],
                         x="Platform",y="Views")
    else:
        st.info("No measured results yet. Enter authentic post statistics below; zeros are not a live platform report.")
    if not assets:
        return
    choices={f"#{a['id']} · {a['platform']} · {a['headline'][:40]}":a["id"] for a in assets}
    with st.form("mk_metrics_form"):
        chosen=st.selectbox("Creative being measured",list(choices))
        day=st.date_input("Metric date",value=date.today())
        a,b,c1=st.columns(3)
        impressions=a.number_input("Impressions",min_value=0,value=0,step=1)
        views=b.number_input("Views",min_value=0,value=0,step=1)
        clicks=c1.number_input("Clicks",min_value=0,value=0,step=1)
        d,e,f=st.columns(3)
        engagements=d.number_input("Engagements",min_value=0,value=0,step=1)
        conversions=e.number_input("Conversions",min_value=0,value=0,step=1)
        spend=f.number_input("Actual spend (BDT; manually reported)",min_value=0.0,
                             value=0.0,step=100.0)
        notes=st.text_input("Report source / internal notes",max_chars=300,
                            placeholder="YouTube Studio manual export — 29 Oct")
        save=st.form_submit_button("Save Manual Performance Record",disabled=demo_mode)
    if save:
        try:
            save_metrics(db_path,choices[chosen],day.isoformat(),
                impressions=int(impressions),views=int(views),clicks=int(clicks),
                engagements=int(engagements),conversions=int(conversions),
                spend_bdt=float(spend),attribution_note=notes)
            st.success("Manual stats saved. No advertising API was called.")
            st.rerun()
        except MarketingError as err:
            _notice(err)
    st.subheader("Growth Recommendations")
    if summary["impressions"]:
        if summary["ctr_percent"] is not None and summary["ctr_percent"]<1.5:
            st.write("**Hypothesis to test:** Try a stronger first-frame hook and thumbnail variation. "
                     "The 1.5% threshold here is an editable editorial heuristic, NOT a platform benchmark.")
        else:
            st.write("Continue comparing hook variants and viewer retention using actual platform data.")
    else:
        st.write("Once manual metrics are added, compare captions and thumbnails by platform. "
                 "Do not infer winners from an empty dataset.")


def _budget(c):
    st.subheader("💸 Budget Scenario Lab — arithmetic only")
    st.warning("This page does NOT buy ads. CPM is whatever YOU enter; estimated impressions "
               "are not real reach forecasts, platform quotations or guarantees.")
    amount=st.number_input("Illustrative total spend (৳)",min_value=0,max_value=100000000,
                           value=int(c["budget_bdt"]),step=1000,key="mk_scenario_bdt")
    cpm=st.number_input("Hypothetical CPM (৳ per 1,000 impressions)",
                        min_value=1.0,max_value=1000000.0,value=300.0,step=10.0)
    try:
        scenario=budget_scenario(int(amount),float(cpm))
        st.metric("Arithmetic impression count",f"{scenario['assumed_impressions']:,}")
        st.caption(scenario["warning"])
    except MarketingError as e:
        _notice(e)


def show_marketing(db_path: str | Path, demo_mode: bool=False):
    db_path=Path(db_path)
    init_marketing(db_path)
    st.header("📣 REDPAD Growth Engine")
    st.caption("AI Marketing Agent workspace • Organic content strategy, campaign planning, copy, approvals, analytics")
    if demo_mode:
        st.warning("READ-ONLY PUBLIC DEMO — fictional sample content only. "
                   "No account connection, live metrics, data persistence guarantee or paid advertising.")
    else:
        st.info("OFFLINE STRATEGY ENGINE — creates editable editorial drafts without an AI model or API. "
                "No automatic posting, boosting, paid Meta/Google Ads, or billed API calls. "
                "Owner approval is required for every creative.")
    rows=campaigns(db_path)
    total_assets=sum(row["asset_count"] for row in rows)
    approved_assets=sum(row["approved_count"] for row in rows)
    a,b,c,d=st.columns(4)
    a.metric("Campaigns",len(rows))
    b.metric("Creative assets",total_assets)
    c.metric("Approved creatives",approved_assets)
    d.metric("Live ad spend", "৳0 — system disabled")
    tabs=st.tabs(["🧭 Campaign Builder","✍️ Creative Studio","🗓️ Content Calendar",
                  "📊 Analytics","💸 Budget Lab","📦 Export Center"])
    with tabs[0]:
        _campaign_builder(db_path,demo_mode)
    if not rows:
        with tabs[1]: st.info("Create a campaign to edit assets.")
        with tabs[2]: st.info("Calendar will appear after creating a campaign.")
        with tabs[3]: st.info("No measured campaign data.")
        with tabs[4]: st.info("Create a campaign to explore a hypothetical budget.")
        with tabs[5]: st.info("No marketing package yet.")
        return
    c_choices={f"#{c['id']} · {c['name']} · {c['status']}":c["id"] for c in rows}
    campaign_id=st.selectbox("Marketing campaign dashboard",list(c_choices),
                             index=list(c_choices.values()).index(
                                 st.session_state["mk_campaign"]
                             ) if st.session_state.get("mk_campaign") in c_choices.values() else 0,
                             key="mk_active_campaign")
    selected_id=c_choices[campaign_id]
    c=get_campaign(db_path,selected_id)
    assets=assets_for(db_path,selected_id)
    with tabs[1]: _asset_review(db_path,c,assets,demo_mode)
    with tabs[2]:
        st.session_state["mk_db_path"]=db_path
        _calendar(c,assets)
    with tabs[3]: _analytics(db_path,c,assets,demo_mode)
    with tabs[4]: _budget(c)
    with tabs[5]:
        st.subheader("📦 Strategy, Copy & Calendar Export")
        st.caption("Exporting does NOT publish, schedule, boost or contact any platform.")
        if not source_current(db_path,c):
            st.error("Source draft changed. Export blocked for stale campaign.")
            return
        full=export_package(db_path,selected_id)
        st.download_button("Download Full Campaign JSON",
                           json.dumps(full,ensure_ascii=False,indent=2).encode("utf-8"),
                           file_name=f"redpad-campaign-{selected_id}.json",
                           mime="application/json",key="mk_full_json")
        st.download_button("Download Editorial Calendar CSV (UTF-8)",
                           export_csv(db_path,selected_id),
                           file_name=f"redpad-calendar-{selected_id}.csv",
                           mime="text/csv",key="mk_full_csv")
        if any(a["status"]=="Approved" for a in assets):
            st.download_button("Download ONLY Approved Creatives CSV",
                               export_csv(db_path,selected_id,approved_only=True),
                               file_name=f"redpad-approved-{selected_id}.csv",
                               mime="text/csv",key="mk_approved_csv")
        st.code(
            "Human delivery checklist:\n"
            "1. Verify licensed visuals, music and brand/legal claims.\n"
            "2. Confirm platform aspect ratio and accessibility captions.\n"
            "3. Copy approved caption and hashtags; upload manually.\n"
            "4. Log actual performance in Analytics.\n"
            "5. Never spend or publish without a separate explicit owner approval.",
            language=None
        )
