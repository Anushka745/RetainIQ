"""
components/navbar.py
Sidebar navigation, account info, theme toggle, and logout control.
"""

import streamlit as st

from utils.helpers import logout


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="app-title">Retain<span>IQ</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("AI-powered retention intelligence")
        st.markdown("---")

        profile = st.session_state.get("user_profile")
        if profile:
            st.markdown(f"**{profile.get('full_name', 'User')}**")
            st.caption(profile.get("company_name") or profile.get("email", ""))
            st.markdown("---")

        st.toggle("Dark mode", key="dark_mode", value=st.session_state.get("dark_mode", True))

        st.markdown("---")
        if st.button("Log out", use_container_width=True):
            logout()
            st.rerun()
