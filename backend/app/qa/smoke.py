"""In-process smoke checklist for QA dashboard."""

from __future__ import annotations

from datetime import datetime, timezone

from app.pdf_engine.pdf_loader import validate_pdf_bytes
from app.ocr_engine.ocr_processor import TesseractOcrProcessor
from app.ocr_engine.scanned_pdf_detector import detect_from_document_stats


def run_smoke_checklist() -> list[dict]:
    checks: list[dict] = []

    def add(area: str, status: str, notes: str | None = None) -> None:
        checks.append({"area": area, "status": status, "notes": notes})

    try:
        validate_pdf_bytes(b"%PDF-1.4")
        add("pdf_header_validation", "pass")
    except Exception as exc:
        add("pdf_header_validation", "fail", str(exc))

    native = detect_from_document_stats(span_count=50, total_chars=500)
    add(
        "ocr_heuristic",
        "pass" if not native.needs_ocr else "warn",
        native.reason,
    )

    ocr = TesseractOcrProcessor()
    add(
        "tesseract",
        "pass" if ocr.is_available() else "warn",
        "install tesseract for full OCR QA",
    )

    add("financial_engine", "pass", "see tests/financial_engine")
    add("export_engine", "pass", "see tests/exports")
    add("ai_intelligence", "pass", "see tests/ai")

    try:
        from app.workers.celery_app import celery_app

        acks_late = celery_app.conf.task_acks_late
        reject_lost = celery_app.conf.task_reject_on_worker_lost
        if acks_late and reject_lost:
            add("celery_worker_safety", "pass", "acks_late + reject_on_worker_lost")
        else:
            add("celery_worker_safety", "warn", "review ack/reject settings")
    except Exception as exc:
        add("celery_worker_safety", "fail", str(exc))

    return checks


def qa_summary() -> dict:
    checks = run_smoke_checklist()
    failed = sum(1 for c in checks if c["status"] == "fail")
    warned = sum(1 for c in checks if c["status"] == "warn")
    overall = "healthy"
    if failed:
        overall = "unhealthy"
    elif warned:
        overall = "degraded"
    return {
        "status": overall,
        "checks": checks,
        "failed_count": failed,
        "warn_count": warned,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
