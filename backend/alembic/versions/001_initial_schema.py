"""Initial schema: users, statements, transactions, edit_history

Revision ID: 001
Revises:
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "statements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("bank_name", sa.String(100), nullable=True),
        sa.Column("account_number", sa.String(64), nullable=True),
        sa.Column("statement_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("statement_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("original_pdf_path", sa.String(1024), nullable=False),
        sa.Column("edited_pdf_path", sa.String(1024), nullable=True),
        sa.Column("preview_path", sa.String(1024), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column("status", sa.String(50), server_default="uploaded"),
        sa.Column("opening_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("closing_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_statements_user_id", "statements", ["user_id"])
    op.create_index("ix_statements_bank_name", "statements", ["bank_name"])
    op.create_index("ix_statements_status", "statements", ["status"])

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statements.id", ondelete="CASCADE")),
        sa.Column("row_index", sa.Integer(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("debit_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("credit_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("coordinate_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_statement_id", "transactions", ["statement_id"])

    op.create_table(
        "edit_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statements.id", ondelete="CASCADE")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("field_changed", sa.String(255), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("change_payload", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_edit_history_statement_id", "edit_history", ["statement_id"])


def downgrade() -> None:
    op.drop_table("edit_history")
    op.drop_table("transactions")
    op.drop_table("statements")
    op.drop_table("users")
