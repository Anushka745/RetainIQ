"""
services/churn_model.py
Trains and serves a scikit-learn churn prediction model.

The model is trained on-the-fly from each account's EndUser data using a
RandomForestClassifier. Because real labelled churn data is generated
synthetically for the demo dataset (is_churned flag), the model learns the
relationship between behavioural features and churn so it can score
currently-active users by churn probability.
"""

import logging
from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import models

logger = logging.getLogger("retainiq.churn_model")

FEATURE_COLUMNS = [
    "days_since_signup",
    "days_since_last_active",
    "sessions_count",
    "features_used",
    "revenue",
]


def _build_feature_frame(end_users: List[models.EndUser]) -> pd.DataFrame:
    now = datetime.utcnow()
    rows = []
    for u in end_users:
        days_since_signup = (now - u.signup_date).days if u.signup_date else 0
        days_since_last_active = (now - u.last_active_date).days if u.last_active_date else days_since_signup
        rows.append(
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "days_since_signup": days_since_signup,
                "days_since_last_active": days_since_last_active,
                "sessions_count": u.sessions_count or 0,
                "features_used": u.features_used or 0,
                "revenue": u.revenue or 0.0,
                "is_churned": int(u.is_churned),
            }
        )
    return pd.DataFrame(rows)


def train_and_predict(end_users: List[models.EndUser]) -> Tuple[pd.DataFrame, float]:
    """
    Trains a RandomForestClassifier on the provided end-user population and
    returns a DataFrame with churn_probability and risk_level for every user,
    plus the model's holdout accuracy (for logging/diagnostics).
    """
    if len(end_users) < 10:
        # Not enough data to train meaningfully; fall back to heuristic scoring.
        return _heuristic_predict(end_users), 0.0

    df = _build_feature_frame(end_users)
    X = df[FEATURE_COLUMNS]
    y = df["is_churned"]

    accuracy = 0.0
    if y.nunique() < 2:
        # All users share the same label; can't train a classifier meaningfully.
        df["churn_probability"] = y.astype(float)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y if y.value_counts().min() >= 2 else None
        )
        clf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, class_weight="balanced")
        clf.fit(X_train, y_train)
        accuracy = float(clf.score(X_test, y_test))
        probabilities = clf.predict_proba(X)[:, list(clf.classes_).index(1)] if 1 in clf.classes_ else np.zeros(len(X))
        df["churn_probability"] = probabilities

    df["risk_level"] = df["churn_probability"].apply(_risk_bucket)
    logger.info("Churn model trained. Holdout accuracy=%.3f, n_users=%d", accuracy, len(df))
    return df, accuracy


def _heuristic_predict(end_users: List[models.EndUser]) -> pd.DataFrame:
    """Simple rule-based fallback when there isn't enough data to train an ML model."""
    df = _build_feature_frame(end_users)
    if df.empty:
        df["churn_probability"] = []
        df["risk_level"] = []
        return df

    inactivity_score = (df["days_since_last_active"] / 30).clip(0, 1)
    engagement_score = 1 - (df["sessions_count"] / (df["sessions_count"].max() or 1)).clip(0, 1)
    df["churn_probability"] = (0.6 * inactivity_score + 0.4 * engagement_score).clip(0, 1)
    df["risk_level"] = df["churn_probability"].apply(_risk_bucket)
    return df


def _risk_bucket(prob: float) -> str:
    if prob >= 0.66:
        return "High"
    if prob >= 0.33:
        return "Medium"
    return "Low"
