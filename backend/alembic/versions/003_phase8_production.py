"""Phase 8 — auth roles, audit logs, snapshots, export jobs

Revision ID: 003_phase8
Revises: 002_statement_extraction
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_phase8"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=32), server_default="editor", nullable=False),
    )
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), server_default="statement"),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), server_default="success"),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_statement_id", "audit_logs", ["statement_id"])

    op.create_table(
        "pdf_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("snapshot_type", sa.String(32), server_default="edit_commit"),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_pdf_snapshots_statement_id", "pdf_snapshots", ["statement_id"])

    op.create_table(
        "export_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("celery_task_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), server_default="queued"),
        sa.Column("export_name", sa.String(255), nullable=True),
        sa.Column("output_path", sa.String(1024), nullable=True),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pdf_snapshots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("replacements_applied", sa.Integer(), server_default="0"),
        sa.Column("validation_passed", sa.Boolean(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("download_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_export_jobs_statement_id", "export_jobs", ["statement_id"])
    op.create_index("ix_export_jobs_status", "export_jobs", ["status"])
    op.create_index("ix_export_jobs_celery_task_id", "export_jobs", ["celery_task_id"])


def downgrade() -> None:
    op.drop_table("export_jobs")
    op.drop_table("pdf_snapshots")
    op.drop_table("audit_logs")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
