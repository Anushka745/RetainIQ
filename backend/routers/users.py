"""
routers/users.py
End-user analytics listing and CSV upload endpoint.
"""

import io
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_current_user
from database import get_db
from rate_limiter import general_rate_limiter, get_client_key
from services.segmentation import segment_all

logger = logging.getLogger("retainiq.users")
router = APIRouter(tags=["Users"])

REQUIRED_COLUMNS = {"external_id", "signup_date"}


@router.get("/users", response_model=List[schemas.EndUserOut])
def list_users(
    request: Request,
    segment: Optional[str] = Query(None, description="Filter by segment name"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    query = db.query(models.EndUser).filter(models.EndUser.owner_id == current_user.id)
    end_users = query.all()
    segment_all(end_users)
    db.commit()

    if segment:
        end_users = [u for u in end_users if u.segment.lower() == segment.lower()]

    return end_users


@router.post("/upload", response_model=schemas.UploadResponse)
def upload_users_csv(
    request: Request,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    general_rate_limiter.check(get_client_key(request))

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")

    try:
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        logger.error("Failed to parse uploaded CSV: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not parse CSV file") from exc

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV is missing required columns: {', '.join(missing)}",
        )

    rows_imported = 0
    for _, row in df.iterrows():
        try:
            signup_date = pd.to_datetime(row["signup_date"]).to_pydatetime()
        except Exception:
            continue

        last_active = None
        if "last_active_date" in df.columns and pd.notna(row.get("last_active_date")):
            try:
                last_active = pd.to_datetime(row["last_active_date"]).to_pydatetime()
            except Exception:
                last_active = None

        end_user = models.EndUser(
            owner_id=current_user.id,
            external_id=str(row["external_id"]),
            name=str(row.get("name")) if pd.notna(row.get("name")) else None,
            email=str(row.get("email")) if pd.notna(row.get("email")) else None,
            signup_date=signup_date,
            last_active_date=last_active,
            plan=str(row.get("plan", "free")) if pd.notna(row.get("plan", "free")) else "free",
            revenue=float(row.get("revenue", 0.0) or 0.0),
            sessions_count=int(row.get("sessions_count", 0) or 0),
            features_used=int(row.get("features_used", 0) or 0),
            is_churned=bool(row.get("is_churned", False)) if pd.notna(row.get("is_churned", False)) else False,
        )
        db.add(end_user)
        rows_imported += 1

    db.commit()
    logger.info("CSV upload by user_id=%s imported %d rows", current_user.id, rows_imported)

    return schemas.UploadResponse(message="Upload successful", rows_imported=rows_imported)
