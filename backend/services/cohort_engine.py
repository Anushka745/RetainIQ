"""
services/cohort_engine.py
Builds monthly signup cohorts and computes retention rates for months 0-5.
"""

from typing import List

import pandas as pd

import models

RETENTION_MONTHS = 6


def compute_cohorts(end_users: List[models.EndUser]) -> List[dict]:
    if not end_users:
        return []

    rows = []
    for u in end_users:
        if not u.signup_date:
            continue
        cohort_month = u.signup_date.strftime("%Y-%m")
        last_active = u.last_active_date or u.signup_date
        months_active = _month_diff(u.signup_date, last_active)
        rows.append({"cohort_month": cohort_month, "months_active": months_active})

    if not rows:
        return []

    df = pd.DataFrame(rows)
    results = []

    for cohort_month, group in df.groupby("cohort_month"):
        cohort_size = len(group)
        row = {"cohort_month": cohort_month, "cohort_size": cohort_size}
        for m in range(RETENTION_MONTHS):
            retained = (group["months_active"] >= m).sum()
            row[f"month_{m}"] = round((retained / cohort_size) * 100, 1) if cohort_size else 0.0
        results.append(row)

    results.sort(key=lambda r: r["cohort_month"])
    return results


def _month_diff(start, end) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)
