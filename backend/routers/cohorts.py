"""
routers/cohorts.py
Cohort analysis endpoint.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_current_user
from database import get_db
from rate_limiter import general_rate_limiter, get_client_key
from services.cohort_engine import compute_cohorts

logger = logging.getLogger("retainiq.cohorts")
router = APIRouter(prefix="/cohorts", tags=["Cohort Analysis"])


@router.get("", response_model=schemas.CohortResponse)
def get_cohorts(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    end_users = db.query(models.EndUser).filter(models.EndUser.owner_id == current_user.id).all()
    cohorts = compute_cohorts(end_users)
    logger.info("Cohort analysis computed for user_id=%s (n_cohorts=%d)", current_user.id, len(cohorts))

    return schemas.CohortResponse(cohorts=[schemas.CohortRow(**c) for c in cohorts])
