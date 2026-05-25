"""Database resilience — session rollback semantics (unit-level)."""

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_transaction_rollback_discards_changes():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    with engine.connect() as conn:
        conn.execute(__import__("sqlalchemy").text("CREATE TABLE t (v INTEGER)"))
        conn.commit()

    session = Session()
    try:
        session.execute(__import__("sqlalchemy").text("INSERT INTO t VALUES (1)"))
        session.rollback()
        count = session.execute(__import__("sqlalchemy").text("SELECT COUNT(*) FROM t")).scalar()
        assert count == 0
    finally:
        session.close()
