"""
Apply ledger edits to PDF and persist edited file.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.financial_engine.models import LedgerEntry
from app.financial_engine.validator import validate_ledger
from app.pdf_engine.export_engine import PdfExportEngine
from app.pdf_engine.scanned_fallback import needs_ocr_fallback
from app.services.edit_session_service import EditSessionService, _memory_sessions
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PdfExportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.statements = StatementService(db)
        self.export_engine = PdfExportEngine()

    def apply_edits(
        self,
        statement_id: uuid.UUID,
        session_id: str | None = None,
    ):
        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        source = self.statements.get_pdf_path(statement, edited=False)
        if not source:
            raise ValueError("Original PDF not found")

        # Log current metadata keys to trace whether a committed session is present
        try:
            meta_keys = list((statement.metadata_json or {}).keys())
        except Exception:
            meta_keys = []
        logger.info("export_resolve_start", statement_id=str(statement_id), metadata_keys=meta_keys, session_id=session_id)

        entries, bank = self._resolve_entries(statement_id, session_id, statement.metadata_json)
        valid, issues = validate_ledger(entries, statement.opening_balance)
        if not valid:
            logger.warning(
                "export_transaction_validation_failed",
                statement_id=str(statement_id),
                issues=issues,
            )
            raise ValueError(
                "Cannot export: transaction validation failed. "
                + " ".join(issues)
            )

        output = self.settings.storage_edited / f"{statement_id}.pdf"
        extraction = statement.extraction_json or {}
        scanned = needs_ocr_fallback(extraction, extraction.get("span_count", 999))

        result = self.export_engine.export(
            statement_id,
            source,
            output,
            entries,
            extraction_json=extraction,
            is_likely_scanned=scanned,
        )

        statement.edited_pdf_path = str(output)
        statement.status = "exported"
        meta = statement.metadata_json or {}
        meta["last_export"] = {
            "path": str(output),
            "replacements_applied": result.replacements_applied,
            "validation_passed": result.validation.passed,
        }
        statement.metadata_json = meta
        try:
            self.db.flush()
            self.db.refresh(statement)
        except Exception:
            logger.warning("export_flush_refresh_failed", statement_id=str(statement.id))
        self.db.commit()
        self.db.refresh(statement)

        return result, statement

    def _resolve_entries(
        self,
        statement_id: uuid.UUID,
        session_id: str | None,
        metadata: dict | None,
    ) -> tuple[list[LedgerEntry], str]:
        if session_id:
            if session_id in _memory_sessions:
                bundle = _memory_sessions[session_id]
                if bundle.statement_id != statement_id:
                    raise ValueError("Session does not match statement")
                return bundle.recalculator.entries, bundle.bank
            edit_svc = EditSessionService(self.db)
            try:
                state = edit_svc.get_state(session_id)
                if str(statement_id) != state.statement_id:
                    raise ValueError("Session does not match statement")
                return state.entries, state.bank
            except ValueError as exc:
                if str(exc) == "Edit session not found or expired":
                    logger.warning(
                        "edit_session_not_found_falling_back_to_committed",
                        session_id=session_id,
                        statement_id=str(statement_id),
                    )
                else:
                    raise

        meta = metadata or {}
        if "committed_edit_session" in meta:
            committed_meta = meta["committed_edit_session"] or {}
            raw = committed_meta.get("entries", [])
            bank = committed_meta.get("bank") or meta.get("bank", "UNKNOWN")
            return [LedgerEntry.model_validate(e) for e in raw], bank

        if session_id:
            raise ValueError("Edit session not found — start session or commit first")

        from app.services.transaction_service import TransactionService

        parse_result, _ = TransactionService(self.db).parse_transactions(statement_id)
        return [LedgerEntry.from_structured(t) for t in parse_result.transactions], parse_result.bank
