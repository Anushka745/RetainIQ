"""
schemas.py
Pydantic schemas used for request validation and response serialization.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    company_name: Optional[str] = Field(None, max_length=120)
    password: str = Field(..., min_length=8, max_length=72)
    confirm_password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    company_name: Optional[str] = None
    subscription_plan: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    company_name: Optional[str] = Field(None, max_length=120)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)


class MessageResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Dashboard / Analytics schemas
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_users: int
    active_users: int
    churn_risk_users: int
    total_revenue: float
    conversion_rate: float
    trend_dates: List[str]
    trend_active_users: List[int]
    trend_new_signups: List[int]
    trend_revenue: List[float]


class EndUserOut(BaseModel):
    id: int
    external_id: str
    name: Optional[str]
    email: Optional[str]
    signup_date: datetime
    last_active_date: Optional[datetime]
    plan: str
    revenue: float
    sessions_count: int
    features_used: int
    is_churned: bool
    segment: str

    class Config:
        from_attributes = True


class FunnelStage(BaseModel):
    stage: str
    count: int
    conversion_pct: float
    drop_off_pct: float


class FunnelResponse(BaseModel):
    stages: List[FunnelStage]


class ChurnPredictionOut(BaseModel):
    end_user_id: int
    name: Optional[str]
    email: Optional[str]
    churn_probability: float
    risk_level: str


class ChurnSummary(BaseModel):
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    predictions: List[ChurnPredictionOut]


class CohortRow(BaseModel):
    cohort_month: str
    month_0: Optional[float] = None
    month_1: Optional[float] = None
    month_2: Optional[float] = None
    month_3: Optional[float] = None
    month_4: Optional[float] = None
    month_5: Optional[float] = None
    cohort_size: int


class CohortResponse(BaseModel):
    cohorts: List[CohortRow]


class InsightCard(BaseModel):
    category: str
    title: str
    description: str
    severity: str  # info / warning / critical / opportunity
    recommended_action: str


class InsightsResponse(BaseModel):
    insights: List[InsightCard]


class UploadResponse(BaseModel):
    message: str
    rows_imported: int
