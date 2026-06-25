"""
pages/signup.py
Signup page: full name, email, company, password + confirm, with validation.
"""

import streamlit as st

from assets.theme import get_theme_css
from utils.api_client import api_get, api_post
from utils.helpers import is_logged_in

st.set_page_config(page_title="Create account | RetainIQ", page_icon="📊", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

if is_logged_in():
    st.success("You're already logged in.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

st.markdown('<div class="app-title" style="font-size:1.8rem;">Retain<span>IQ</span></div>', unsafe_allow_html=True)
st.subheader("Create your account")
st.caption("Start uncovering why your users churn — free, no credit card required.")

with st.form("signup_form"):
    full_name = st.text_input("Full name", placeholder="Jordan Lee")
    email = st.text_input("Email address", placeholder="you@company.com")
    company_name = st.text_input("Company name", placeholder="Acme Inc.")
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type="password", placeholder="At least 8 characters")
    with col2:
        confirm_password = st.text_input("Confirm password", type="password")
    st.caption("Password must contain at least one uppercase letter, one lowercase letter, and one digit.")
    submitted = st.form_submit_button("Create account", use_container_width=True)

if submitted:
    errors = []
    if not full_name or len(full_name.strip()) < 2:
        errors.append("Please enter your full name.")
    if not email or "@" not in email:
        errors.append("Please enter a valid email address.")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if password != confirm_password:
        errors.append("Passwords do not match.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Creating your account..."):
            result = api_post(
                "/auth/signup",
                {
                    "full_name": full_name.strip(),
                    "email": email.strip(),
                    "company_name": company_name.strip() if company_name else None,
                    "password": password,
                    "confirm_password": confirm_password,
                },
            )

        if result.get("error"):
            st.error(result.get("message", "Could not create account."))
        else:
            data = result["data"]
            st.session_state["access_token"] = data["access_token"]
            st.session_state["token_expires_minutes"] = data["expires_in_minutes"]

            profile_result = api_get("/auth/profile")
            if not profile_result.get("error"):
                st.session_state["user_profile"] = profile_result["data"]

            st.success("Account created! Taking you to your dashboard...")
            st.switch_page("pages/dashboard.py")

st.markdown("---")
st.caption("Already have an account?")
if st.button("Log in instead", use_container_width=True):
    st.switch_page("pages/login.py")
