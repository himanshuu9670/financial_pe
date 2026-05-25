"""Create demo user for development (bcrypt password when auth enabled)."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.auth.password_manager import hash_password
from app.core.database import SessionLocal
from app.models import User

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_PASSWORD = "demo-password-change-me"


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.id == DEMO_USER_ID))
        if existing:
            if existing.hashed_password == "not-used-phase-1":
                existing.hashed_password = hash_password(DEMO_PASSWORD)
                existing.role = "admin"
                db.commit()
                print("Demo user password upgraded (admin role)")
            else:
                print("Demo user already exists")
            return
        user = User(
            id=DEMO_USER_ID,
            email="demo@pdfeditor.local",
            full_name="Demo Admin",
            hashed_password=hash_password(DEMO_PASSWORD),
            role="admin",
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        print("Demo user created:", DEMO_USER_ID)
        print("Login: demo@pdfeditor.local /", DEMO_PASSWORD)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
