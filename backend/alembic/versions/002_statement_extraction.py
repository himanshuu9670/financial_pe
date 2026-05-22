"""Add extraction cache fields to statements

Revision ID: 002
Revises: 001
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("statements", sa.Column("processing_error", sa.Text(), nullable=True))
    op.add_column(
        "statements",
        sa.Column("extraction_json", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "statements",
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("statements", "extracted_at")
    op.drop_column("statements", "extraction_json")
    op.drop_column("statements", "processing_error")
