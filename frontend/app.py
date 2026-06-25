"""
app.py
RetainIQ Streamlit frontend entrypoint.

Run with:
    streamlit run app.py
"""

import streamlit as st

from assets.theme import get_theme_css
from components.navbar import render_sidebar
from utils.helpers import is_logged_in

st.set_page_config(
    page_title="RetainIQ | Retention Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded" if is_logged_in() else "collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

if not is_logged_in():
    st.markdown('<div class="app-title" style="font-size:2.2rem; text-align:center; margin-top:60px;">Retain<span>IQ</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:var(--text-muted); font-size:1.05rem; margin-bottom:36px;">'
        "AI-powered analytics that explain <em>why</em> users churn, <em>where</em> they drop off, "
        "and <em>what</em> to do about it.</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["Log in", "Create account"])
        with tab_login:
            st.info("Click below to go to the login page.")
            if st.button("Go to Login", use_container_width=True):
                st.switch_page("pages/login.py")
        with tab_signup:
            if st.button("Go to Signup", use_container_width=True):
                st.switch_page("pages/signup.py")

    st.stop()

# --- Logged in: show landing/overview with sidebar nav ---
render_sidebar()

profile = st.session_state.get("user_profile", {})
st.markdown(
    f'<div class="section-eyebrow">Welcome back</div>'
    f'<h1>{profile.get("full_name", "there")} 👋</h1>',
    unsafe_allow_html=True,
)
st.write(
    "Use the navigation in the sidebar to explore your **Dashboard**, **User Analytics**, "
    "**Funnel Analysis**, **Churn Prediction**, **Cohort Analysis**, and **AI Insights**."
)

st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("##### 📈 Start with the Dashboard")
    st.caption("See your core KPIs: users, revenue, conversion, and churn risk at a glance.")
with c2:
    st.markdown("##### 🤖 Check AI Insights")
    st.caption("Get plain-language recommendations on what to fix first.")
with c3:
    st.markdown("##### ⚙️ Manage your account")
    st.caption("Update your profile or password in Settings.")
