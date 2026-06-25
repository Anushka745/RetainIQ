"""
pages/user_analytics.py
User activity, session counts, feature usage, retention metrics, and segments.
"""

import pandas as pd
import streamlit as st

from assets.theme import get_theme_css
from components.charts import bar_chart, pie_chart
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import require_login

st.set_page_config(page_title="User Analytics | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Behavior</div><h1>User Analytics</h1>', unsafe_allow_html=True)

with st.spinner("Loading user data..."):
    result = api_get("/users")

if result.get("error"):
    st.error(f"Could not load users: {result.get('message')}")
    st.stop()

users = result["data"]
if not users:
    st.info("No user data yet. Upload a CSV from the Settings page to get started.")
    st.stop()

df = pd.DataFrame(users)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg. Sessions / User", f"{df['sessions_count'].mean():.1f}")
with col2:
    st.metric("Avg. Features Used", f"{df['features_used'].mean():.1f}")
with col3:
    retained_pct = (1 - df["is_churned"].mean()) * 100
    st.metric("Retention Rate", f"{retained_pct:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    st.markdown("##### Segment Distribution")
    seg_counts = df["segment"].value_counts()
    pie_chart(seg_counts.index.tolist(), seg_counts.values.tolist(), dark_mode=st.session_state["dark_mode"])
with col5:
    st.markdown("##### Plan Distribution")
    plan_counts = df["plan"].value_counts()
    bar_chart(plan_counts.index.tolist(), plan_counts.values.tolist(), dark_mode=st.session_state["dark_mode"])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### Filter by Segment")
segment_filter = st.selectbox("Segment", ["All"] + sorted(df["segment"].unique().tolist()))
filtered = df if segment_filter == "All" else df[df["segment"] == segment_filter]

st.dataframe(
    filtered[["external_id", "name", "email", "plan", "sessions_count", "features_used", "segment", "is_churned"]],
    use_container_width=True,
    hide_index=True,
)
