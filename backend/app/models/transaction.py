import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    statement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("statements.id", ondelete="CASCADE"),
        index=True,
    )

    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    debit_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    credit_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    # PDF coordinate metadata for typography-preserving edits (Phase 2+)
    coordinate_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    statement: Mapped["Statement"] = relationship(back_populates="transactions")  # noqa: F821
