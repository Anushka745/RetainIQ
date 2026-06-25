"""
pages/dashboard.py
Main dashboard: KPI cards, trend charts, revenue breakdown.
"""

import streamlit as st

from assets.theme import get_theme_css
from components.charts import bar_chart, line_chart, pie_chart
from components.metric_cards import render_kpi_row
from components.navbar import render_sidebar
from utils.api_client import api_get
from utils.helpers import format_currency, format_percent, require_login

st.set_page_config(page_title="Dashboard | RetainIQ", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Overview</div><h1>Dashboard</h1>', unsafe_allow_html=True)

with st.spinner("Loading dashboard data..."):
    result = api_get("/dashboard")

if result.get("error"):
    st.error(f"Could not load dashboard: {result.get('message')}")
    st.stop()

data = result["data"]

render_kpi_row(
    [
        {"label": "Total Users", "value": f"{data['total_users']:,}"},
        {"label": "Active Users", "value": f"{data['active_users']:,}"},
        {"label": "Churn Risk Users", "value": f"{data['churn_risk_users']:,}", "delta": "needs attention", "delta_positive": False},
        {"label": "Revenue", "value": format_currency(data["total_revenue"])},
        {"label": "Conversion Rate", "value": format_percent(data["conversion_rate"])},
    ]
)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### 30-Day Activity Trend")
    line_chart(
        dates=data["trend_dates"],
        series={"Active Users": data["trend_active_users"], "New Signups": data["trend_new_signups"]},
        dark_mode=st.session_state["dark_mode"],
    )

with col2:
    st.markdown("##### Revenue Trend")
    bar_chart(
        categories=data["trend_dates"][-10:],
        values=data["trend_revenue"][-10:],
        dark_mode=st.session_state["dark_mode"],
    )

st.markdown("<br>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    st.markdown("##### User Status Breakdown")
    pie_chart(
        labels=["Active", "Churn Risk"],
        values=[max(data["active_users"], 0), max(data["churn_risk_users"], 0)],
        dark_mode=st.session_state["dark_mode"],
    )
with col4:
    st.markdown("##### What's next?")
    st.info("Head to **Churn Prediction** to see exactly which users are at risk and why.")
    st.info("Visit **AI Insights** for plain-language recommendations based on this data.")
