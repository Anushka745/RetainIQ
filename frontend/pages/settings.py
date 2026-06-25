"""
pages/settings.py
Account settings: profile update, password change, account deletion, CSV upload.
"""

import streamlit as st

from assets.theme import get_theme_css
from components.navbar import render_sidebar
from utils.api_client import api_delete, api_get, api_post, api_put
from utils.helpers import logout, require_login

st.set_page_config(page_title="Settings | RetainIQ", page_icon="⚙️", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

require_login()
render_sidebar()

st.markdown('<div class="section-eyebrow">Account</div><h1>Settings</h1>', unsafe_allow_html=True)

tab_profile, tab_password, tab_data, tab_danger = st.tabs(
    ["Profile", "Password", "Import Data", "Danger Zone"]
)

profile = st.session_state.get("user_profile", {})

with tab_profile:
    st.markdown("##### Update your profile")
    with st.form("profile_form"):
        full_name = st.text_input("Full name", value=profile.get("full_name", ""))
        company_name = st.text_input("Company name", value=profile.get("company_name", "") or "")
        submitted = st.form_submit_button("Save changes")

    if submitted:
        result = api_put("/auth/profile", {"full_name": full_name, "company_name": company_name})
        if result.get("error"):
            st.error(result.get("message", "Could not update profile."))
        else:
            st.session_state["user_profile"] = result["data"]
            st.success("Profile updated.")
            st.rerun()

with tab_password:
    st.markdown("##### Change your password")
    with st.form("password_form"):
        current_password = st.text_input("Current password", type="password")
        new_password = st.text_input("New password", type="password")
        confirm_new_password = st.text_input("Confirm new password", type="password")
        submitted_pw = st.form_submit_button("Update password")

    if submitted_pw:
        if new_password != confirm_new_password:
            st.error("New passwords do not match.")
        elif len(new_password) < 8:
            st.error("New password must be at least 8 characters.")
        else:
            result = api_post(
                "/auth/change-password",
                {"current_password": current_password, "new_password": new_password},
            )
            if result.get("error"):
                st.error(result.get("message", "Could not change password."))
            else:
                st.success("Password updated successfully.")

with tab_data:
    st.markdown("##### Import user data")
    st.caption("Upload a CSV with columns: external_id, name, email, signup_date, last_active_date, plan, revenue, sessions_count, features_used, is_churned")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        if st.button("Upload"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            result = api_post("/upload", files=files)
            if result.get("error"):
                st.error(result.get("message", "Upload failed."))
            else:
                st.success(f"Imported {result['data']['rows_imported']} rows successfully.")

with tab_danger:
    st.markdown("##### Delete your account")
    st.warning("This action is permanent and cannot be undone. All your data will be deleted.")
    confirm_delete = st.checkbox("I understand this action is permanent.")
    if st.button("Delete my account", type="primary", disabled=not confirm_delete):
        result = api_delete("/auth/delete-account")
        if result.get("error"):
            st.error(result.get("message", "Could not delete account."))
        else:
            st.success("Account deleted.")
            logout()
            st.switch_page("app.py")
