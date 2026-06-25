"""
routers/auth.py
Authentication endpoints: signup, login, logout, profile management.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ACCESS_TOKEN_EXPIRE_MINUTES_REMEMBER,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import get_db
from rate_limiter import auth_rate_limiter, get_client_key

logger = logging.getLogger("retainiq.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.SignupRequest, request: Request, db: Session = Depends(get_db)):
    auth_rate_limiter.check(get_client_key(request))

    existing = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if existing:
        logger.warning("Signup attempt with duplicate email: %s", payload.email)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    new_user = models.User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        company_name=payload.company_name.strip() if payload.company_name else None,
        password_hash=hash_password(payload.password),
        created_at=datetime.utcnow(),
        subscription_plan="free",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("New user signed up: %s (id=%s)", new_user.email, new_user.id)

    token = create_access_token({"sub": str(new_user.id)})
    return schemas.TokenResponse(access_token=token, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    auth_rate_limiter.check(get_client_key(request))

    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning("Failed login attempt for email: %s", payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated")

    user.last_login = datetime.utcnow()
    db.commit()

    expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES_REMEMBER if payload.remember_me else ACCESS_TOKEN_EXPIRE_MINUTES
    token = create_access_token({"sub": str(user.id)}, expires_minutes=expire_minutes)

    logger.info("User logged in: %s (id=%s)", user.email, user.id)
    return schemas.TokenResponse(access_token=token, expires_in_minutes=expire_minutes)


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(current_user: models.User = Depends(get_current_user)):
    # Stateless JWT: logout is enforced client-side by discarding the token.
    # Logged here for audit purposes.
    logger.info("User logged out: %s (id=%s)", current_user.email, current_user.id)
    return schemas.MessageResponse(message="Logged out successfully")


@router.get("/profile", response_model=schemas.UserProfile)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserProfile)
def update_profile(
    payload: schemas.ProfileUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
    if payload.company_name is not None:
        current_user.company_name = payload.company_name.strip()

    db.commit()
    db.refresh(current_user)
    logger.info("Profile updated for user id=%s", current_user.id)
    return current_user


@router.post("/change-password", response_model=schemas.MessageResponse)
def change_password(
    payload: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    logger.info("Password changed for user id=%s", current_user.id)
    return schemas.MessageResponse(message="Password updated successfully")


@router.delete("/delete-account", response_model=schemas.MessageResponse)
def delete_account(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    db.delete(current_user)
    db.commit()
    logger.info("Account deleted: id=%s", user_id)
    return schemas.MessageResponse(message="Account deleted successfully")
