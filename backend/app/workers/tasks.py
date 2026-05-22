import uuid

from app.utils.logging import get_logger
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.workers.tasks.process_statement_pdf")
def process_statement_pdf(statement_id: str) -> dict:
    """Async coordinate extraction — offloads heavy PDFs from request thread."""
    from app.core.database import SessionLocal
    from app.services.pdf_extraction_service import PdfExtractionService

    logger.info("process_statement_pdf_started", statement_id=statement_id)
    db = SessionLocal()
    try:
        from app.services.transaction_service import TransactionService

        pdf_service = PdfExtractionService(db)
        pdf_service.extract(uuid.UUID(statement_id), force_refresh=True)
        txn_service = TransactionService(db)
        result, _ = txn_service.parse_transactions(uuid.UUID(statement_id), force_refresh=True)
        return {
            "statement_id": statement_id,
            "status": "ready",
            "transaction_count": len(result.transactions),
            "bank": result.bank,
        }
    except Exception as exc:
        logger.error("process_statement_pdf_failed", statement_id=statement_id, error=str(exc))
        return {"statement_id": statement_id, "status": "error", "error": str(exc)}
    finally:
        db.close()
