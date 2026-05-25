import uuid
from datetime import date, datetime, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.ai_layout_engine.hybrid_pipeline import hybrid_extract_document, run_intelligent_pipeline
from app.shared.models import StructuredTransaction
from app.ai_engine.models import TransactionParseResult
from app.models import Transaction
from app.cache import extraction_cache, invalidate_ai_only, invalidate_statement
from app.services.pdf_extraction_service import PdfExtractionService
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    v = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%d-%b-%Y", "%d-%b-%y", "%d %b %Y"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


class TransactionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.pdf_extraction = PdfExtractionService(db)

    def parse_transactions(
        self,
        statement_id: uuid.UUID,
        *,
        force_refresh: bool = False,
        include_debug: bool = False,
    ) -> tuple[TransactionParseResult, bool]:
        from app.services.statement_service import StatementService

        statements = StatementService(self.db)
        statement = statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        if force_refresh:
            invalidate_statement(str(statement_id))

        path = self.pdf_extraction.statements.get_pdf_path(statement)
        if not path:
            raise ValueError("PDF file not found on disk")

        if not force_refresh:
            redis_parse = extraction_cache.get_transaction_parse(str(statement_id), path)
            if redis_parse:
                cached = TransactionParseResult.model_validate(redis_parse)
                db_count = len(statement.transactions) if statement.transactions else 0
                if db_count > 0 or len(cached.transactions) > 0:
                    return cached, True

        meta = statement.metadata_json or {}
        cache_key = "transaction_parse"
        if not force_refresh and cache_key in meta:
            cached = TransactionParseResult.model_validate(meta[cache_key])
            db_count = len(statement.transactions) if statement.transactions else 0
            if db_count > 0 or len(cached.transactions) > 0:
                return cached, True

        document, mode, ocr_conf, _scan = hybrid_extract_document(
            path,
            statement_id=str(statement_id),
        )
        statement.extraction_json = document.model_dump()
        statement.extracted_at = datetime.now(timezone.utc)

        result, _layout, _intel = run_intelligent_pipeline(
            document,
            extraction_mode=mode,
            ocr_confidence=ocr_conf,
            include_debug=include_debug,
        )

        statement.bank_name = result.bank.replace("_", " ").title()
        statement.opening_balance = result.summary.opening_balance
        statement.closing_balance = result.summary.closing_balance
        statement.status = "ready"

        parse_payload = result.model_dump(mode="json")
        meta[cache_key] = parse_payload
        extraction_cache.set_transaction_parse(str(statement_id), path, parse_payload)
        meta["extraction_mode"] = result.extraction_mode
        meta["layout_confidence"] = result.layout_confidence
        meta["ocr_confidence"] = result.ocr_confidence
        meta["transaction_parsed_at"] = datetime.now(timezone.utc).isoformat()
        statement.metadata_json = meta

        self._persist_transactions(statement_id, result.transactions)
        invalidate_ai_only(str(statement_id))
        self.db.commit()
        self.db.refresh(statement)

        return result, False

    def _persist_transactions(
        self,
        statement_id: uuid.UUID,
        transactions: list[StructuredTransaction],
    ) -> None:
        self.db.execute(delete(Transaction).where(Transaction.statement_id == statement_id))

        for txn in transactions:
            coord_meta = txn.model_dump(mode="json")
            self.db.add(
                Transaction(
                    id=uuid.UUID(txn.transaction_id)
                    if _is_uuid(txn.transaction_id)
                    else uuid.uuid4(),
                    statement_id=statement_id,
                    row_index=txn.row_index,
                    transaction_date=_parse_date(txn.date),
                    description=txn.description,
                    debit_amount=txn.debit,
                    credit_amount=txn.credit,
                    balance=txn.balance,
                    coordinate_metadata=coord_meta,
                )
            )

        logger.info("transactions_persisted", statement_id=str(statement_id), count=len(transactions))


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
