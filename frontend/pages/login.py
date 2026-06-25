"""
pages/login.py
Login page: email + password, JWT token retrieval, remember-me option.
"""

import streamlit as st

from assets.theme import get_theme_css
from utils.api_client import api_get, api_post
from utils.helpers import is_logged_in

st.set_page_config(page_title="Log in | RetainIQ", page_icon="📊", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

if is_logged_in():
    st.success("You're already logged in.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

st.markdown('<div class="app-title" style="font-size:1.8rem;">Retain<span>IQ</span></div>', unsafe_allow_html=True)
st.subheader("Log in to your account")

with st.form("login_form"):
    email = st.text_input("Email address", placeholder="you@company.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    remember_me = st.checkbox("Remember me for 7 days")
    submitted = st.form_submit_button("Log in", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Please enter both email and password.")
    else:
        with st.spinner("Signing you in..."):
            result = api_post("/auth/login", {"email": email, "password": password, "remember_me": remember_me})

        if result.get("error"):
            st.error(result.get("message", "Login failed. Please check your credentials."))
        else:
            data = result["data"]
            st.session_state["access_token"] = data["access_token"]
            st.session_state["token_expires_minutes"] = data["expires_in_minutes"]

            profile_result = api_get("/auth/profile")
            if not profile_result.get("error"):
                st.session_state["user_profile"] = profile_result["data"]

            st.success("Logged in successfully!")
            st.switch_page("pages/dashboard.py")

st.markdown("---")
st.caption("Don't have an account?")
if st.button("Create one here", use_container_width=True):
    st.switch_page("pages/signup.py")

with st.expander("Demo credentials"):
    st.code("Email: admin@retainiq.com\nPassword: Admin@123", language="text")
    st.caption("Seeded demo admin account — change this password before any production use.")
