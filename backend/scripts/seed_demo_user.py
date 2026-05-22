"""Create demo user for development uploads (no auth in Phase 1)."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import User

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.id == DEMO_USER_ID))
        if existing:
            print("Demo user already exists")
            return
        user = User(
            id=DEMO_USER_ID,
            email="demo@pdfeditor.local",
            full_name="Demo User",
            hashed_password="not-used-phase-1",
        )
        db.add(user)
        db.commit()
        print("Demo user created:", DEMO_USER_ID)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
