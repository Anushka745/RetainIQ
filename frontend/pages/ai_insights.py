"""
pages/ai_insights.py
AI-generated business recommendation cards.
"""

import streamlit as st

from assets.theme import get_theme_css
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import require_login, severity_color

st.set_page_config(page_title="AI Insights | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Recommendations</div><h1>AI Insights</h1>', unsafe_allow_html=True)
st.caption("Plain-language analysis of what's working, what's not, and what to do about it.")

with st.spinner("Generating insights..."):
    result = api_get("/insights")

if result.get("error"):
    st.error(f"Could not load insights: {result.get('message')}")
    st.stop()

insights = result["data"]["insights"]

if not insights:
    st.info("No insights available yet — upload more user data to generate recommendations.")
    st.stop()

severity_icons = {"critical": "🔴", "warning": "🟠", "opportunity": "🟢", "info": "🔵"}

for insight in insights:
    color = severity_color(insight["severity"])
    icon = severity_icons.get(insight["severity"], "🔵")
    st.markdown(
        f"""
        <div class="insight-card" style="--accent-border: {color};">
            <div class="insight-category">{icon} {insight['category']}</div>
            <div class="insight-title">{insight['title']}</div>
            <div class="insight-desc">{insight['description']}</div>
            <div class="insight-action"><strong>Recommended action:</strong> {insight['recommended_action']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
