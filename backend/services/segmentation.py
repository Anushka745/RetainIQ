"""
services/segmentation.py
Rule-based user segmentation: classifies end-users into New, Loyal, Power, or At Risk.
"""

from datetime import datetime
from typing import List

import models


def classify_segment(end_user: models.EndUser) -> str:
    now = datetime.utcnow()
    days_since_signup = (now - end_user.signup_date).days if end_user.signup_date else 0
    days_since_active = (
        (now - end_user.last_active_date).days if end_user.last_active_date else days_since_signup
    )

    if days_since_active > 21:
        return "At Risk Users"
    if days_since_signup <= 14:
        return "New Users"
    if (end_user.sessions_count or 0) >= 30 and (end_user.features_used or 0) >= 8:
        return "Power Users"
    if days_since_signup > 60 and days_since_active <= 14:
        return "Loyal Users"
    return "Loyal Users" if days_since_signup > 30 else "New Users"


def segment_all(end_users: List[models.EndUser]) -> List[models.EndUser]:
    """Updates the `.segment` attribute on each end_user in-place and returns the list."""
    for u in end_users:
        u.segment = classify_segment(u)
    return end_users
