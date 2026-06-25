"""
assets/theme.py
Custom CSS injected into the Streamlit app. Implements a "signal room" visual
identity: deep charcoal/near-black base, a single electric-teal accent used
only for the metric that matters most (risk/retention signal), and tabular
monospace numerals for all KPI figures so the eye can compare digits cleanly
the way you would on a trading desk. Supports both dark and light modes.

Design tokens:
  Dark mode background: #0B0E14 (near-black, slightly blue)
  Dark mode surface:     #141925
  Light mode background: #F7F8FA
  Light mode surface:    #FFFFFF
  Accent (signal):       #2DD4BF (electric teal - "healthy" signal)
  Risk accent:           #FB7185 (coral - "at risk" signal)
  Warning accent:        #FBBF24 (amber)
  Text primary (dark):   #E6E9EF
  Text muted (dark):     #8B93A7
  Display face: 'Space Grotesk' (characterful, geometric, built for data UIs)
  Body face:    'Inter'
  Numeric face: 'JetBrains Mono' (tabular figures for KPI cards)
"""

DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
    --bg: #0B0E14;
    --surface: #141925;
    --surface-hover: #1B2230;
    --border: #262E3D;
    --text-primary: #E6E9EF;
    --text-muted: #8B93A7;
    --accent: #2DD4BF;
    --accent-dim: rgba(45, 212, 191, 0.14);
    --risk: #FB7185;
    --risk-dim: rgba(251, 113, 133, 0.14);
    --warning: #FBBF24;
    --warning-dim: rgba(251, 191, 36, 0.14);
    --info: #60A5FA;
}

.stApp {
    background: var(--bg);
    color: var(--text-primary);
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.01em;
}

body, p, div, span, label {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text-primary);
}

/* KPI Card */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 22px;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(45, 212, 191, 0.08);
}

.kpi-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
    margin-bottom: 6px;
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
}

.kpi-delta-up { color: var(--accent); font-size: 0.85rem; font-weight: 500; }
.kpi-delta-down { color: var(--risk); font-size: 0.85rem; font-weight: 500; }

/* Insight Card */
.insight-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-border, var(--accent));
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    animation: fadeSlideIn 0.4s ease both;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.insight-category {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.insight-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 6px;
}

.insight-desc {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 10px;
    line-height: 1.5;
}

.insight-action {
    background: var(--accent-dim);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.insight-action strong { color: var(--accent); }

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.risk-high { background: var(--risk-dim); color: var(--risk); }
.risk-medium { background: var(--warning-dim); color: var(--warning); }
.risk-low { background: var(--accent-dim); color: var(--accent); }

/* Segment badge */
.segment-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    background: var(--surface-hover);
    color: var(--text-primary);
    border: 1px solid var(--border);
}

/* Buttons */
.stButton button {
    border-radius: 8px;
    font-weight: 500;
    border: 1px solid var(--border);
    transition: all 0.2s ease;
}

.stButton button:hover {
    border-color: var(--accent);
    color: var(--accent);
}

div[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
}

/* Section divider label */
.section-eyebrow {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 4px;
}

.app-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.4rem;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.app-title span { color: var(--accent); }

hr {
    border-color: var(--border) !important;
}
</style>
"""

LIGHT_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
    --bg: #F7F8FA;
    --surface: #FFFFFF;
    --surface-hover: #F0F2F5;
    --border: #E2E5EB;
    --text-primary: #161A23;
    --text-muted: #6B7280;
    --accent: #0D9488;
    --accent-dim: rgba(13, 148, 136, 0.1);
    --risk: #E11D48;
    --risk-dim: rgba(225, 29, 72, 0.08);
    --warning: #D97706;
    --warning-dim: rgba(217, 119, 6, 0.1);
    --info: #2563EB;
}

.stApp { background: var(--bg); color: var(--text-primary); }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }
body, p, div, span, label { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

.kpi-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 20px 22px; transition: all 0.25s ease;
}
.kpi-card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(13,148,136,0.08); }
.kpi-label { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; margin-bottom: 6px; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.kpi-delta-up { color: var(--accent); font-size: 0.85rem; font-weight: 500; }
.kpi-delta-down { color: var(--risk); font-size: 0.85rem; font-weight: 500; }

.insight-card {
    background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent-border, var(--accent));
    border-radius: 10px; padding: 18px 20px; margin-bottom: 14px; animation: fadeSlideIn 0.4s ease both;
}
@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.insight-category { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
.insight-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; }
.insight-desc { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 10px; line-height: 1.5; }
.insight-action { background: var(--accent-dim); border-radius: 8px; padding: 10px 12px; font-size: 0.85rem; color: var(--text-primary); }
.insight-action strong { color: var(--accent); }

.risk-badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.risk-high { background: var(--risk-dim); color: var(--risk); }
.risk-medium { background: var(--warning-dim); color: var(--warning); }
.risk-low { background: var(--accent-dim); color: var(--accent); }

.segment-badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 500; background: var(--surface-hover); color: var(--text-primary); border: 1px solid var(--border); }

.stButton button { border-radius: 8px; font-weight: 500; border: 1px solid var(--border); transition: all 0.2s ease; }
.stButton button:hover { border-color: var(--accent); color: var(--accent); }

div[data-testid="stForm"] { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 28px; }

.section-eyebrow { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); font-weight: 600; margin-bottom: 4px; }
.app-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.4rem; color: var(--text-primary); letter-spacing: -0.02em; }
.app-title span { color: var(--accent); }
hr { border-color: var(--border) !important; }
</style>
"""


def get_theme_css(dark_mode: bool = True) -> str:
    return DARK_THEME_CSS if dark_mode else LIGHT_THEME_CSS
