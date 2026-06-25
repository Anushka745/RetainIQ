"""
services/insights_engine.py
Rule-based insights engine that turns raw analytics into plain-language
business recommendations. Optionally augmented by a local Ollama LLM call
if OLLAMA_ENABLED=true and an Ollama server is reachable.
"""

import logging
import os
from typing import List

import pandas as pd
import requests

logger = logging.getLogger("retainiq.insights_engine")

OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def generate_insights(
    churn_df: pd.DataFrame,
    funnel_stages: List[dict],
    segment_counts: dict,
) -> List[dict]:
    insights = []

    # --- Churn-related insight ---
    high_risk = churn_df[churn_df["risk_level"] == "High"] if not churn_df.empty else pd.DataFrame()
    if len(high_risk) > 0:
        pct = round(len(high_risk) / len(churn_df) * 100, 1)
        insights.append(
            {
                "category": "Churn Risk",
                "title": f"{len(high_risk)} users at high risk of churning",
                "description": (
                    f"{pct}% of your active user base shows behavioural patterns strongly "
                    "associated with churn, primarily extended inactivity and low feature engagement."
                ),
                "severity": "critical" if pct > 20 else "warning",
                "recommended_action": (
                    "Launch a targeted re-engagement campaign (email or in-app) for these users "
                    "within the next 7 days, and consider personal outreach for your highest-revenue accounts."
                ),
            }
        )

    # --- Funnel bottleneck insight ---
    if funnel_stages:
        worst_stage = max(funnel_stages[1:], key=lambda s: s["drop_off_pct"], default=None)
        if worst_stage and worst_stage["drop_off_pct"] > 30:
            insights.append(
                {
                    "category": "Conversion Bottleneck",
                    "title": f"High drop-off entering '{worst_stage['stage']}'",
                    "description": (
                        f"{worst_stage['drop_off_pct']}% of users who reach the prior stage do not "
                        f"continue to {worst_stage['stage']}. This is your biggest funnel leak."
                    ),
                    "severity": "warning",
                    "recommended_action": (
                        f"Review the UX and messaging leading into the {worst_stage['stage']} step. "
                        "Consider A/B testing a simplified flow or adding contextual onboarding hints."
                    ),
                }
            )

    # --- Onboarding insight ---
    new_users = segment_counts.get("New Users", 0)
    at_risk = segment_counts.get("At Risk Users", 0)
    if new_users > 0 and at_risk > 0 and at_risk >= new_users * 0.3:
        insights.append(
            {
                "category": "Onboarding",
                "title": "New users may not be reaching activation",
                "description": (
                    "A significant share of at-risk users signed up recently, suggesting onboarding "
                    "friction rather than long-term disengagement."
                ),
                "severity": "warning",
                "recommended_action": (
                    "Add a guided first-run checklist and trigger a check-in email at day 3 and day 7 "
                    "post-signup to drive early activation."
                ),
            }
        )

    # --- Upgrade opportunity insight ---
    power_users = segment_counts.get("Power Users", 0)
    if power_users > 0:
        insights.append(
            {
                "category": "Upgrade Opportunity",
                "title": f"{power_users} power users are strong upsell candidates",
                "description": (
                    "These users show high session counts and broad feature adoption, indicating "
                    "they are extracting strong value and may be ready for a higher-tier plan."
                ),
                "severity": "opportunity",
                "recommended_action": (
                    "Trigger a personalized upgrade offer or feature-unlock prompt for this segment, "
                    "highlighting premium features that match their usage patterns."
                ),
            }
        )

    # --- Growth opportunity insight ---
    loyal_users = segment_counts.get("Loyal Users", 0)
    if loyal_users > 0:
        insights.append(
            {
                "category": "Growth Opportunity",
                "title": f"{loyal_users} loyal users could become advocates",
                "description": (
                    "Long-tenured, consistently active users are your best source of referrals "
                    "and testimonials, and typically convert well in referral programs."
                ),
                "severity": "info",
                "recommended_action": (
                    "Invite this segment into a referral program or case-study/testimonial outreach."
                ),
            }
        )

    if not insights:
        insights.append(
            {
                "category": "Overview",
                "title": "No major risk signals detected",
                "description": "Current data does not show significant churn, funnel, or onboarding issues.",
                "severity": "info",
                "recommended_action": "Continue monitoring weekly; revisit once more usage data accumulates.",
            }
        )

    if OLLAMA_ENABLED:
        insights = _augment_with_ollama(insights)

    return insights


def _augment_with_ollama(insights: List[dict]) -> List[dict]:
    """Optionally rewrites insight descriptions using a local Ollama LLM for more natural language."""
    try:
        summary_text = "\n".join(f"- {i['title']}: {i['description']}" for i in insights)
        prompt = (
            "Rewrite each of the following SaaS analytics insights in one concise, "
            "professional sentence aimed at a startup founder. Keep the same order, "
            "return one sentence per line, no preamble:\n\n" + summary_text
        )
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=8,
        )
        if response.status_code == 200:
            text = response.json().get("response", "").strip()
            lines = [line.strip("- ").strip() for line in text.split("\n") if line.strip()]
            for i, line in enumerate(lines):
                if i < len(insights):
                    insights[i]["description"] = line
    except requests.RequestException as exc:
        logger.info("Ollama augmentation skipped (server unreachable): %s", exc)
    return insights
