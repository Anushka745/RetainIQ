"""
components/charts.py
Plotly chart builders themed to match the app's design tokens.
"""

from typing import List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ACCENT = "#2DD4BF"
RISK = "#FB7185"
WARNING = "#FBBF24"
INFO = "#60A5FA"


def _base_layout(dark_mode: bool, height: int = 360) -> dict:
    text_color = "#E6E9EF" if dark_mode else "#161A23"
    grid_color = "#262E3D" if dark_mode else "#E2E5EB"
    return dict(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=text_color, size=12),
        xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
        yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


def line_chart(dates: List[str], series: dict, dark_mode: bool = True, title: str = ""):
    """series: dict of {label: [values]} to plot as separate lines."""
    fig = go.Figure()
    colors = [ACCENT, INFO, WARNING, RISK]
    for i, (label, values) in enumerate(series.items()):
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name=label,
                line=dict(color=colors[i % len(colors)], width=2.5, shape="spline"),
                fill="tozeroy" if i == 0 else None,
                fillcolor=f"rgba(45, 212, 191, 0.08)" if i == 0 else None,
            )
        )
    fig.update_layout(**_base_layout(dark_mode), title=title)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(categories: List[str], values: List[float], dark_mode: bool = True, title: str = "", color: str = ACCENT):
    fig = go.Figure(go.Bar(x=categories, y=values, marker_color=color, marker_line_width=0))
    fig.update_layout(**_base_layout(dark_mode), title=title)
    st.plotly_chart(fig, use_container_width=True)


def pie_chart(labels: List[str], values: List[float], dark_mode: bool = True, title: str = ""):
    colors = [ACCENT, WARNING, RISK, INFO, "#A78BFA"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors[: len(labels)]),
            textfont=dict(color="#E6E9EF" if dark_mode else "#161A23"),
        )
    )
    layout = _base_layout(dark_mode, height=320)
    layout.pop("xaxis")
    layout.pop("yaxis")
    fig.update_layout(**layout, title=title)
    st.plotly_chart(fig, use_container_width=True)


def funnel_chart(stages: List[str], counts: List[int], dark_mode: bool = True):
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial",
            marker=dict(color=[ACCENT, INFO, WARNING, RISK][: len(stages)]),
        )
    )
    fig.update_layout(**_base_layout(dark_mode, height=380))
    st.plotly_chart(fig, use_container_width=True)


def heatmap_chart(df: pd.DataFrame, dark_mode: bool = True, title: str = ""):
    fig = go.Figure(
        go.Heatmap(
            z=df.values,
            x=df.columns.tolist(),
            y=df.index.tolist(),
            colorscale=[[0, "#1B2230" if dark_mode else "#F0F2F5"], [1, ACCENT]],
            text=df.values,
            texttemplate="%{text}%",
            textfont=dict(size=11),
            showscale=False,
        )
    )
    layout = _base_layout(dark_mode, height=max(320, 40 * len(df)))
    fig.update_layout(**layout, title=title)
    st.plotly_chart(fig, use_container_width=True)
