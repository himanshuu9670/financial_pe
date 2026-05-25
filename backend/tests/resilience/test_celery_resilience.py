"""Celery resilience — retries, dead letters, idempotency, Redis degradation."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.workers.resilience import (
    ACTION_DEAD_LETTER,
    ACTION_RETRY,
    bump_export_retry_metadata,
    export_job_idempotent_skip,
    mark_export_dead_letter,
    mark_statement_processing_error,
)


class _FakeJob:
    def __init__(self, status: str = "processing", metadata: dict | None = None):
        self.id = uuid.uuid4()
        self.status = status
        self.metadata_json = metadata
        self.error_message = None
        self.output_path = "/tmp/out.pdf"


class _FakeStatement:
    def __init__(self):
        self.status = "extracting"
        self.processing_error = None
        self.metadata_json = None
        self.user_id = uuid.uuid4()


def test_export_idempotent_skip_completed():
    job = _FakeJob(status="completed")
    result = export_job_idempotent_skip(job)
    assert result["idempotent"] is True
    assert result["status"] == "completed"


def test_export_idempotent_skip_dead_letter():
    job = _FakeJob(status="failed", metadata={"dead_letter": True, "user_message": "safe"})
    result = export_job_idempotent_skip(job)
    assert result["dead_letter"] is True
    assert result["user_message"] == "safe"


def test_bump_export_retry_metadata_increments():
    job = _FakeJob(metadata={"retry_count": 1})
    count = bump_export_retry_metadata(job, "timeout")
    assert count == 2
    assert job.metadata_json["retry_count"] == 2
    assert "last_retry_reason" in job.metadata_json


def test_mark_export_dead_letter_sets_user_message():
    job = _FakeJob()
    mark_export_dead_letter(job, "disk full")
    assert job.metadata_json["dead_letter"] is True
    assert "user_message" in job.metadata_json


def test_mark_statement_processing_error():
    stmt = _FakeStatement()
    mark_statement_processing_error(stmt, "OCR timeout")
    assert stmt.status == "error"
    assert stmt.metadata_json["async_dead_letter"] is True


@pytest.fixture
def celery_eager():
    from app.workers.celery_app import celery_app

    prev = {
        "task_always_eager": celery_app.conf.task_always_eager,
        "task_eager_propagates": celery_app.conf.task_eager_propagates,
    }
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = False
    yield celery_app
    celery_app.conf.task_always_eager = prev["task_always_eager"]
    celery_app.conf.task_eager_propagates = prev["task_eager_propagates"]


def test_statement_task_dead_letter_on_exhausted_retries():
    from app.workers import tasks as task_module

    mock_self = MagicMock()
    mock_self.request.retries = 2
    mock_self.max_retries = 2

    stmt = _FakeStatement()
    db = MagicMock()
    db.get.return_value = stmt

    with patch.object(task_module, "execute_statement_pdf_processing", side_effect=RuntimeError("ocr timeout")):
        with patch("app.workers.tasks.SessionLocal", return_value=db):
            with patch("app.workers.tasks.record_dead_letter") as mock_dl:
                with pytest.raises(RuntimeError):
                    task_module._run_statement_pdf_task(
                        mock_self, str(uuid.uuid4()), task_label="process_statement_pdf"
                    )
                mock_dl.assert_called_once()
    assert stmt.status == "error"


def test_run_pdf_export_idempotent_completed():
    from app.workers.tasks import run_pdf_export

    job_id = str(uuid.uuid4())
    fake_job = _FakeJob(status="completed")

    with patch("app.workers.tasks.SessionLocal") as mock_session:
        db = MagicMock()
        mock_session.return_value = db
        db.get.return_value = fake_job

        result = run_pdf_export.run(job_id)
        assert result.get("idempotent") is True


def test_redis_manager_disabled_on_outage(monkeypatch):
    from app.cache.redis_manager import RedisManager
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "redis_cache_enabled", False)
    mgr = RedisManager()
    assert mgr.get_json("any-key") is None
    assert mgr.enabled() is False


def test_record_dead_letter_writes_audit():
    db = MagicMock()
    with patch("app.audit.audit_service.AuditService") as mock_audit:
        from app.workers.resilience import record_dead_letter

        record_dead_letter(
            db,
            task_name="run_pdf_export",
            resource_id="job-1",
            error="final failure",
            statement_id=uuid.uuid4(),
        )
        mock_audit.return_value.log.assert_called_once()
        assert mock_audit.return_value.log.call_args[0][0] == ACTION_DEAD_LETTER


def test_duplicate_export_queue_prevented():
    from app.services.export_job_service import ExportJobService

    db = MagicMock()
    existing = _FakeJob(status="processing")
    db.scalars.return_value.first.return_value = existing
    svc = ExportJobService(db)
    with patch("app.services.export_job_service.run_pdf_export") as mock_export:
        result = svc.queue_export(uuid.uuid4(), uuid.uuid4())
        assert result is existing
        mock_export.delay.assert_not_called()
        db.add.assert_not_called()
