"""
pages/cohort_analysis.py
Monthly cohort retention table and heatmap.
"""

import pandas as pd
import streamlit as st

from assets.theme import get_theme_css
from components.charts import heatmap_chart
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import require_login

st.set_page_config(page_title="Cohort Analysis | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Retention</div><h1>Cohort Analysis</h1>', unsafe_allow_html=True)
st.caption("Monthly signup cohorts tracked across their first 6 months.")

with st.spinner("Computing cohorts..."):
    result = api_get("/cohorts")

if result.get("error"):
    st.error(f"Could not load cohorts: {result.get('message')}")
    st.stop()

cohorts = result["data"]["cohorts"]
if not cohorts:
    st.info("Not enough signup history yet to build cohorts.")
    st.stop()

df = pd.DataFrame(cohorts)
month_cols = [c for c in df.columns if c.startswith("month_")]
heatmap_df = df.set_index("cohort_month")[month_cols]
heatmap_df.columns = [f"M{c.split('_')[1]}" for c in heatmap_df.columns]

st.markdown("##### Retention Heatmap (%)")
heatmap_chart(heatmap_df.fillna(0), dark_mode=st.session_state["dark_mode"])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### Cohort Table")
display_df = df.rename(columns={"cohort_month": "Cohort Month", "cohort_size": "Cohort Size"})
display_df.columns = [c if not c.startswith("month_") else f"Month {c.split('_')[1]} %" for c in display_df.columns]
st.dataframe(display_df, use_container_width=True, hide_index=True)
