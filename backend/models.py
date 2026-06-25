"""
models.py
SQLAlchemy ORM models for RetainIQ: User, Session, Event, Prediction.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """Application user / account that can log in to RetainIQ (the SaaS customer)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    company_name = Column(String(120), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    subscription_plan = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)

    end_users = relationship("EndUser", back_populates="owner", cascade="all, delete-orphan")


class EndUser(Base):
    """
    A tracked end-user / customer record belonging to a RetainIQ account.
    This is the entity that analytics, churn prediction, and cohorts are computed on
    (distinct from the `User` table, which is who logs in to RetainIQ itself).
    """

    __tablename__ = "end_users"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    external_id = Column(String(100), index=True, nullable=False)
    name = Column(String(120), nullable=True)
    email = Column(String(255), nullable=True)
    signup_date = Column(DateTime, nullable=False)
    last_active_date = Column(DateTime, nullable=True)
    plan = Column(String(50), default="free")
    revenue = Column(Float, default=0.0)
    sessions_count = Column(Integer, default=0)
    features_used = Column(Integer, default=0)
    is_churned = Column(Boolean, default=False)
    segment = Column(String(50), default="New Users")

    owner = relationship("User", back_populates="end_users")
    sessions = relationship("UserSession", back_populates="end_user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="end_user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="end_user", cascade="all, delete-orphan")


class UserSession(Base):
    """A usage session for an end-user (login session inside the customer's product)."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    end_user_id = Column(Integer, ForeignKey("end_users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Float, default=0.0)
    pages_viewed = Column(Integer, default=0)

    end_user = relationship("EndUser", back_populates="sessions")


class Event(Base):
    """A funnel/product event performed by an end-user (visit, signup, activation, purchase, etc.)."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    end_user_id = Column(Integer, ForeignKey("end_users.id"), nullable=False)
    event_name = Column(String(100), nullable=False)
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(String(500), nullable=True)

    end_user = relationship("EndUser", back_populates="events")


class Prediction(Base):
    """A churn-risk prediction produced by the ML model for an end-user."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    end_user_id = Column(Integer, ForeignKey("end_users.id"), nullable=False)
    churn_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # High / Medium / Low
    predicted_at = Column(DateTime, default=datetime.utcnow)

    end_user = relationship("EndUser", back_populates="predictions")
