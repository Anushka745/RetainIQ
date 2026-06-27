"""
routers/churn.py
Churn prediction endpoint, powered by services/churn_model.py.
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

logger = logging.getLogger("retainiq.churn")
router = APIRouter(prefix="/churn", tags=["Churn Prediction"])


@router.get("", response_model=schemas.ChurnSummary)
def get_churn_predictions(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    end_users = db.query(models.EndUser).filter(models.EndUser.owner_id == current_user.id).all()

    if not end_users:
        return schemas.ChurnSummary(high_risk_count=0, medium_risk_count=0, low_risk_count=0, predictions=[])

    df, accuracy = train_and_predict(end_users, current_user.id)
    logger.info("Churn predictions generated for user_id=%s (model_accuracy=%.3f)", current_user.id, accuracy)

    predictions = [
        schemas.ChurnPredictionOut(
            end_user_id=int(row["id"]),
            name=row.get("name"),
            email=row.get("email"),
            churn_probability=round(float(row["churn_probability"]), 4),
            risk_level=row["risk_level"],
        )
        for _, row in df.iterrows()
    ]

    # Persist latest predictions for historical tracking (upsert pattern)
    from datetime import datetime
    for _, row in df.iterrows():
        user_id = int(row["id"])
        prob = float(row["churn_probability"])
        risk = row["risk_level"]
        
        existing_pred = db.query(models.Prediction).filter(models.Prediction.end_user_id == user_id).first()
        if existing_pred:
            existing_pred.churn_probability = prob
            existing_pred.risk_level = risk
            existing_pred.predicted_at = datetime.utcnow()
        else:
            db.add(
                models.Prediction(
                    end_user_id=user_id,
                    churn_probability=prob,
                    risk_level=risk,
                )
            )
    db.commit()

    high = sum(1 for p in predictions if p.risk_level == "High")
    medium = sum(1 for p in predictions if p.risk_level == "Medium")
    low = sum(1 for p in predictions if p.risk_level == "Low")

    return schemas.ChurnSummary(
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        predictions=sorted(predictions, key=lambda p: p.churn_probability, reverse=True),
    )
