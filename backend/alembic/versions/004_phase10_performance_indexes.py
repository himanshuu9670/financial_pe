"""Phase 10 — query performance indexes."""

from alembic import op

revision = "004_phase10"
down_revision = "003_phase8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_statements_user_created ON statements (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_statements_status_created ON statements (status, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_transactions_statement_row ON transactions (statement_id, row_index)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_transactions_statement_date ON transactions (statement_id, transaction_date)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_created ON audit_logs (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_statement ON audit_logs (statement_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_export_jobs_status ON export_jobs (status)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_export_jobs_statement ON export_jobs (statement_id)"
    )


def downgrade() -> None:
    op.drop_index("ix_export_jobs_statement", table_name="export_jobs")
    op.drop_index("ix_export_jobs_status", table_name="export_jobs")
    op.drop_index("ix_audit_logs_statement", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created", table_name="audit_logs")
    op.drop_index("ix_transactions_statement_date", table_name="transactions")
    op.drop_index("ix_transactions_statement_row", table_name="transactions")
    op.drop_index("ix_statements_status_created", table_name="statements")
    op.drop_index("ix_statements_user_created", table_name="statements")
