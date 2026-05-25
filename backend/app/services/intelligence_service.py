"""AI document intelligence — layout analysis without full transaction persist."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.ai_layout_engine.hybrid_pipeline import hybrid_extract_document, run_intelligent_pipeline
from app.ai_layout_engine.models import IntelligenceDebugPayload, LayoutAnalysis
from app.ai_engine.models import TransactionParseResult
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class IntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.statements = StatementService(db)

    def analyze(
        self,
        statement_id: uuid.UUID,
        *,
        force_refresh: bool = False,
        force_ocr: bool = False,
        include_debug: bool = True,
    ) -> tuple[LayoutAnalysis, TransactionParseResult, IntelligenceDebugPayload | None, bool]:
        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        meta = statement.metadata_json or {}
        cache_key = "intelligence_analysis"
        if not force_refresh and cache_key in meta and not force_ocr:
            cached = meta[cache_key]
            layout = LayoutAnalysis.model_validate(cached["layout"])
            parse = TransactionParseResult.model_validate(cached["parse"])
            debug = (
                IntelligenceDebugPayload.model_validate(cached["debug"])
                if cached.get("debug")
                else None
            )
            return layout, parse, debug, True

        path = self.statements.get_pdf_path(statement)
        if not path:
            raise ValueError("PDF file not found on disk")

        document, mode, ocr_conf, scan = hybrid_extract_document(
            path,
            statement_id=str(statement_id),
            force_ocr=force_ocr,
        )

        result, layout, intel_debug = run_intelligent_pipeline(
            document,
            extraction_mode=mode,
            ocr_confidence=ocr_conf,
            include_debug=include_debug,
        )

        layout.warnings.append(f"scan_detection:{scan.reason}")

        meta[cache_key] = {
            "layout": layout.model_dump(mode="json"),
            "parse": result.model_dump(mode="json"),
            "debug": intel_debug.model_dump(mode="json") if intel_debug else None,
            "scan": scan.model_dump(mode="json"),
        }
        statement.metadata_json = meta
        self.db.commit()

        logger.info(
            "intelligence_analysis_complete",
            statement_id=str(statement_id),
            bank=layout.bank.bank,
            mode=mode.value,
        )
        return layout, result, intel_debug, False
