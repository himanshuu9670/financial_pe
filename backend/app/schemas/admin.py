from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogSchema(BaseModel):
    id: UUID
    user_id: UUID | None
    statement_id: UUID | None
    action: str
    status: str
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExportJobSchema(BaseModel):
    id: UUID
    statement_id: UUID
    status: str
    export_name: str | None
    replacements_applied: int
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None

    model_config = {"from_attributes": True}


class SystemStatusResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    celery_workers: int = 0
    storage: dict = Field(default_factory=dict)
    queue_depth: int = 0
    timestamp: datetime


class AdminStatsResponse(BaseModel):
    users: int
    statements: int
    exports_queued: int
    exports_failed: int
    audit_events_24h: int


class CacheStatsResponse(BaseModel):
    redis_connected: bool
    cache_enabled: bool
    stats: dict = Field(default_factory=dict)


class MonitoringOverviewResponse(BaseModel):
    """Aggregated operational view for admin monitoring panel."""
    status: str
    health: dict = Field(default_factory=dict)
    workers: dict = Field(default_factory=dict)
    cache: dict = Field(default_factory=dict)
    exports: dict = Field(default_factory=dict)
    timestamp: datetime


class QaCheckItem(BaseModel):
    area: str
    status: str
    notes: str | None = None


class CeleryResilienceOverview(BaseModel):
    recovery_status: str = "unknown"
    retries_24h: int = 0
    dead_letters_24h: int = 0
    recoveries_24h: int = 0
    queue_backlog: int = 0
    statements_error: int = 0
    exports: dict = Field(default_factory=dict)
    workers: dict = Field(default_factory=dict)


class QaDashboardResponse(BaseModel):
    """Phase 11 internal QA dashboard payload."""
    status: str
    checks: list[QaCheckItem] = Field(default_factory=list)
    failed_count: int = 0
    warn_count: int = 0
    health: dict = Field(default_factory=dict)
    cache: dict = Field(default_factory=dict)
    exports: dict = Field(default_factory=dict)
    celery: CeleryResilienceOverview | dict = Field(default_factory=dict)
    generated_at: datetime
    docs: dict[str, str] = Field(
        default_factory=lambda: {
            "qa_report": "docs/QA_REPORT.md",
            "stability": "docs/STABILITY_REPORT.md",
            "edge_cases": "docs/EDGE_CASE_REPORT.md",
            "performance": "docs/PERFORMANCE_REPORT.md",
            "celery": "docs/CELERY_RESILIENCE_REPORT.md",
        }
    )
