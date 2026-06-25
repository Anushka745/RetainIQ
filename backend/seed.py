"""
seed.py
Seeds the database with:
- A sample admin account (admin@retainiq.com / Admin@123 - password is bcrypt-hashed before storage)
- Synthetic EndUser, UserSession, and Event records for demoing analytics,
  churn prediction, funnel analysis, cohorts, and insights.

Run with:
    python seed.py

NOTE: The admin account password below is for local development/demo only.
Change or remove this account before deploying to production.
"""

import logging
import random
from datetime import datetime, timedelta

from database import Base, SessionLocal, engine
from auth_utils import hash_password
import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("retainiq.seed")

random.seed(42)

PLANS = ["free", "starter", "pro", "enterprise"]
FIRST_NAMES = ["Alex", "Priya", "Liam", "Sara", "Noah", "Maya", "Ethan", "Zoe", "Omar", "Ivy",
               "Lucas", "Aria", "Mason", "Nora", "Leo", "Ella", "Kai", "Ruby", "Felix", "Tara"]
LAST_NAMES = ["Patel", "Kim", "Garcia", "Smith", "Chen", "Brown", "Singh", "Davis", "Lee", "Khan"]


def random_date(days_ago_min: int, days_ago_max: int) -> datetime:
    days_ago = random.randint(days_ago_min, days_ago_max)
    return datetime.utcnow() - timedelta(days=days_ago)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin = db.query(models.User).filter(models.User.email == "admin@retainiq.com").first()
        if not admin:
            admin = models.User(
                full_name="RetainIQ Admin",
                email="admin@retainiq.com",
                company_name="RetainIQ",
                password_hash=hash_password("Admin@123"),
                created_at=datetime.utcnow(),
                subscription_plan="enterprise",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("Created admin account: admin@retainiq.com (id=%s)", admin.id)
        else:
            logger.info("Admin account already exists (id=%s)", admin.id)

        existing_end_users = db.query(models.EndUser).filter(models.EndUser.owner_id == admin.id).count()
        if existing_end_users > 0:
            logger.info("Sample end-users already seeded (%d records). Skipping.", existing_end_users)
            return

        n_users = 250
        end_users = []
        for i in range(1, n_users + 1):
            signup_date = random_date(20, 220)
            is_churned = random.random() < 0.22
            if is_churned:
                last_active_date = signup_date + timedelta(days=random.randint(1, 40))
            else:
                last_active_date = random_date(0, 13)

            sessions_count = max(0, int(random.gauss(18, 14)))
            features_used = min(12, max(0, int(random.gauss(5, 3))))
            plan = random.choices(PLANS, weights=[0.4, 0.3, 0.22, 0.08])[0]
            revenue = {"free": 0.0, "starter": 19.0, "pro": 49.0, "enterprise": 199.0}[plan]
            revenue = revenue * random.uniform(0.9, 1.1) if revenue else 0.0

            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            end_user = models.EndUser(
                owner_id=admin.id,
                external_id=f"usr_{i:04d}",
                name=name,
                email=f"{name.lower().replace(' ', '.')}{i}@example.com",
                signup_date=signup_date,
                last_active_date=last_active_date,
                plan=plan,
                revenue=round(revenue, 2),
                sessions_count=sessions_count,
                features_used=features_used,
                is_churned=is_churned,
                segment="New Users",
            )
            end_users.append(end_user)

        db.add_all(end_users)
        db.commit()
        for u in end_users:
            db.refresh(u)
        logger.info("Seeded %d sample end-users.", len(end_users))

        # Sessions
        sessions = []
        for u in end_users:
            for _ in range(min(u.sessions_count, 40)):
                started_at = u.signup_date + timedelta(
                    days=random.randint(0, max((u.last_active_date - u.signup_date).days, 1))
                )
                sessions.append(
                    models.UserSession(
                        end_user_id=u.id,
                        started_at=started_at,
                        duration_minutes=round(random.uniform(1, 45), 1),
                        pages_viewed=random.randint(1, 20),
                    )
                )
        db.add_all(sessions)
        db.commit()
        logger.info("Seeded %d sample sessions.", len(sessions))

        # Funnel events: Visit -> Signup -> Activation -> Purchase
        events = []
        for u in end_users:
            events.append(models.Event(end_user_id=u.id, event_name="visit", event_timestamp=u.signup_date - timedelta(days=1)))
            if random.random() < 0.85:
                events.append(models.Event(end_user_id=u.id, event_name="signup", event_timestamp=u.signup_date))
                if random.random() < 0.65:
                    events.append(
                        models.Event(
                            end_user_id=u.id,
                            event_name="activation",
                            event_timestamp=u.signup_date + timedelta(days=random.randint(0, 5)),
                        )
                    )
                    if u.revenue > 0 and random.random() < 0.7:
                        events.append(
                            models.Event(
                                end_user_id=u.id,
                                event_name="purchase",
                                event_timestamp=u.signup_date + timedelta(days=random.randint(1, 10)),
                            )
                        )
        db.add_all(events)
        db.commit()
        logger.info("Seeded %d funnel events.", len(events))

        logger.info("Seeding complete.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
