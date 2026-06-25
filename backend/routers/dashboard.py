"""
routers/dashboard.py
Dashboard summary endpoint: KPIs and trend series.
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_current_user
from database import get_db
from rate_limiter import general_rate_limiter, get_client_key

logger = logging.getLogger("retainiq.dashboard")
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=schemas.DashboardSummary)
def get_dashboard(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    end_users = db.query(models.EndUser).filter(models.EndUser.owner_id == current_user.id).all()

    total_users = len(end_users)
    now = datetime.utcnow()
    active_cutoff = now - timedelta(days=14)
    active_users = sum(1 for u in end_users if u.last_active_date and u.last_active_date >= active_cutoff)
    churn_risk_users = sum(1 for u in end_users if u.is_churned)
    total_revenue = round(sum(u.revenue or 0.0 for u in end_users), 2)

    purchasers = sum(1 for u in end_users if (u.revenue or 0) > 0)
    conversion_rate = round((purchasers / total_users) * 100, 2) if total_users else 0.0

    trend_dates, trend_active, trend_signups, trend_revenue = _build_trend(end_users, now)

    logger.info("Dashboard summary computed for user_id=%s (n_end_users=%d)", current_user.id, total_users)

    return schemas.DashboardSummary(
        total_users=total_users,
        active_users=active_users,
        churn_risk_users=churn_risk_users,
        total_revenue=total_revenue,
        conversion_rate=conversion_rate,
        trend_dates=trend_dates,
        trend_active_users=trend_active,
        trend_new_signups=trend_signups,
        trend_revenue=trend_revenue,
    )


def _build_trend(end_users, now, days_back: int = 30):
    dates = [(now - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(days_back, -1, -1)]
    active_counts = []
    signup_counts = []
    revenue_counts = []

    for date_str in dates:
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
        active_counts.append(
            sum(1 for u in end_users if u.last_active_date and u.last_active_date.date() == day)
        )
        signup_counts.append(sum(1 for u in end_users if u.signup_date and u.signup_date.date() == day))
        revenue_counts.append(
            round(sum(u.revenue or 0.0 for u in end_users if u.signup_date and u.signup_date.date() == day), 2)
        )

    return dates, active_counts, signup_counts, revenue_counts
