import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Statement(Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    statement_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    statement_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_pdf_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    edited_pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    preview_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(50), default="uploaded", index=True
    )  # uploaded, extracting, ready, error

    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    opening_balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    closing_balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="statements")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="statement", cascade="all, delete-orphan"
    )
    edit_history: Mapped[list["EditHistory"]] = relationship(  # noqa: F821
        back_populates="statement", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["PdfSnapshot"]] = relationship(  # noqa: F821
        back_populates="statement", cascade="all, delete-orphan"
    )
    export_jobs: Mapped[list["ExportJob"]] = relationship(  # noqa: F821
        back_populates="statement", cascade="all, delete-orphan"
    )
