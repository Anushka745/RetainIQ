"""
utils/helpers.py
Small shared helpers for formatting and session-state checks.
"""

import streamlit as st


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def require_login():
    """Call at the top of any protected page. Stops rendering if not logged in."""
    if not is_logged_in():
        st.warning("Please log in to access this page.")
        st.stop()


def logout():
    for key in ["access_token", "user_profile", "token_expires_minutes"]:
        st.session_state.pop(key, None)


def severity_color(severity: str) -> str:
    return {
        "critical": "#e53935",
        "warning": "#f59e0b",
        "opportunity": "#10b981",
        "info": "#3b82f6",
    }.get(severity, "#3b82f6")
