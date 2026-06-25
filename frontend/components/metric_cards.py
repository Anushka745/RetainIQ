"""
components/metric_cards.py
Renders KPI metric cards in a responsive grid.
"""

from typing import List, Optional

import streamlit as st


def render_kpi_row(cards: List[dict]):
    """
    cards: list of dicts like:
        {"label": "Total Users", "value": "1,204", "delta": "+4.2%", "delta_positive": True}
    """
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            render_kpi_card(
                label=card["label"],
                value=card["value"],
                delta=card.get("delta"),
                delta_positive=card.get("delta_positive", True),
            )


def render_kpi_card(label: str, value: str, delta: Optional[str] = None, delta_positive: bool = True):
    delta_html = ""
    if delta:
        delta_class = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{delta_class}">{arrow} {delta}</div>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
