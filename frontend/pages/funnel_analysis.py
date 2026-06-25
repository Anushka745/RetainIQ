"""
pages/funnel_analysis.py
Visit -> Signup -> Activation -> Purchase funnel visualization.
"""

import streamlit as st

from assets.theme import get_theme_css
from components.charts import funnel_chart
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import require_login

st.set_page_config(page_title="Funnel Analysis | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Conversion</div><h1>Funnel Analysis</h1>', unsafe_allow_html=True)
st.caption("Visit → Signup → Activation → Purchase")

with st.spinner("Loading funnel data..."):
    result = api_get("/funnel")

if result.get("error"):
    st.error(f"Could not load funnel: {result.get('message')}")
    st.stop()

stages = result["data"]["stages"]
if not stages or all(s["count"] == 0 for s in stages):
    st.info("No funnel event data yet.")
    st.stop()

col1, col2 = st.columns([1.3, 1])
with col1:
    st.markdown("##### Funnel Chart")
    funnel_chart(
        stages=[s["stage"] for s in stages],
        counts=[s["count"] for s in stages],
        dark_mode=st.session_state["dark_mode"],
    )

with col2:
    st.markdown("##### Stage Breakdown")
    for s in stages:
        st.markdown(
            f"""
            <div class="kpi-card" style="margin-bottom:10px;">
                <div class="kpi-label">{s['stage']}</div>
                <div class="kpi-value" style="font-size:1.5rem;">{s['count']:,} users</div>
                <div style="margin-top:6px; font-size:0.85rem; color:var(--text-muted);">
                    Conversion from top: <strong style="color:var(--accent);">{s['conversion_pct']}%</strong>
                    &nbsp;|&nbsp; Drop-off: <strong style="color:var(--risk);">{s['drop_off_pct']}%</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

worst = max(stages[1:], key=lambda s: s["drop_off_pct"], default=None)
if worst and worst["drop_off_pct"] > 25:
    st.warning(
        f"⚠️ Biggest leak: **{worst['drop_off_pct']}%** of users drop off before reaching "
        f"**{worst['stage']}**. Consider reviewing this step's UX."
    )
