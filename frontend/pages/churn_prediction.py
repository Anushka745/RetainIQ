"""
pages/churn_prediction.py
ML-driven churn prediction: probability scores, risk tables, charts.
"""

import pandas as pd
import streamlit as st

from assets.theme import get_theme_css
from components.charts import bar_chart
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import require_login

st.set_page_config(page_title="Churn Prediction | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Machine Learning</div><h1>Churn Prediction</h1>', unsafe_allow_html=True)
st.caption("Powered by a Scikit-learn Random Forest model trained on your usage data.")

with st.spinner("Running churn model..."):
    result = api_get("/churn")

if result.get("error"):
    st.error(f"Could not load churn predictions: {result.get('message')}")
    st.stop()

data = result["data"]
predictions = data["predictions"]

if not predictions:
    st.info("Not enough user data yet to run predictions.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">High Risk</div>'
        f'<div class="kpi-value" style="color:var(--risk);">{data["high_risk_count"]}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Medium Risk</div>'
        f'<div class="kpi-value" style="color:var(--warning);">{data["medium_risk_count"]}</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Low Risk</div>'
        f'<div class="kpi-value" style="color:var(--accent);">{data["low_risk_count"]}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
col4, col5 = st.columns([1, 1.4])
with col4:
    st.markdown("##### Risk Distribution")
    bar_chart(
        ["High", "Medium", "Low"],
        [data["high_risk_count"], data["medium_risk_count"], data["low_risk_count"]],
        dark_mode=st.session_state["dark_mode"],
        color="#FB7185",
    )

with col5:
    st.markdown("##### At-Risk Users")
    risk_filter = st.multiselect("Filter by risk level", ["High", "Medium", "Low"], default=["High", "Medium"])
    df = pd.DataFrame(predictions)
    filtered = df[df["risk_level"].isin(risk_filter)] if risk_filter else df

    filtered = filtered.copy()
    filtered["churn_probability"] = (filtered["churn_probability"] * 100).round(1).astype(str) + "%"
    st.dataframe(
        filtered[["name", "email", "churn_probability", "risk_level"]].rename(
            columns={"churn_probability": "Churn Probability", "risk_level": "Risk Level"}
        ),
        use_container_width=True,
        hide_index=True,
    )
