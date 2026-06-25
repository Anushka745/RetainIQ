"""
routers/insights.py
AI insights endpoint: combines churn, funnel, and segmentation data into
business recommendations.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_current_user
from database import get_db
from rate_limiter import general_rate_limiter, get_client_key
from services.churn_model import train_and_predict
from services.cohort_engine import compute_cohorts
from services.funnel_engine import compute_funnel
from services.insights_engine import generate_insights
from services.segmentation import segment_all

logger = logging.getLogger("retainiq.insights")
router = APIRouter(prefix="/insights", tags=["AI Insights"])


@router.get("", response_model=schemas.InsightsResponse)
def get_insights(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    end_users = db.query(models.EndUser).filter(models.EndUser.owner_id == current_user.id).all()
    end_user_ids = [u.id for u in end_users]
    events = (
        db.query(models.Event).filter(models.Event.end_user_id.in_(end_user_ids)).all() if end_user_ids else []
    )

    if not end_users:
        return schemas.InsightsResponse(insights=[])

    churn_df, _ = train_and_predict(end_users)
    funnel_stages = compute_funnel(events)
    segment_all(end_users)
    db.commit()

    segment_counts = {}
    for u in end_users:
        segment_counts[u.segment] = segment_counts.get(u.segment, 0) + 1

    insights = generate_insights(churn_df, funnel_stages, segment_counts)
    logger.info("Generated %d insights for user_id=%s", len(insights), current_user.id)

    return schemas.InsightsResponse(insights=[schemas.InsightCard(**i) for i in insights])
