"""
routers/funnel.py
Funnel analysis endpoint.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_current_user
from database import get_db
from rate_limiter import general_rate_limiter, get_client_key
from services.funnel_engine import compute_funnel

logger = logging.getLogger("retainiq.funnel")
router = APIRouter(prefix="/funnel", tags=["Funnel Analysis"])


@router.get("", response_model=schemas.FunnelResponse)
def get_funnel(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    end_user_ids = [
        u.id for u in db.query(models.EndUser.id).filter(models.EndUser.owner_id == current_user.id).all()
    ]
    events = (
        db.query(models.Event).filter(models.Event.end_user_id.in_(end_user_ids)).all() if end_user_ids else []
    )

    stages = compute_funnel(events)
    logger.info("Funnel computed for user_id=%s (n_events=%d)", current_user.id, len(events))

    return schemas.FunnelResponse(stages=[schemas.FunnelStage(**s) for s in stages])
