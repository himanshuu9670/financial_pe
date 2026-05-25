"""Orchestrates AI intelligence pipeline with metadata caching."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.ai_intelligence.embeddings_cache import CACHE_KEY as EMB_CACHE_KEY, load_index_from_meta
from app.ai_intelligence.exceptions import AiNoTransactionsError
from app.ai_intelligence.insights_engine import build_dashboard_summary
from app.ai_intelligence.models import AiIntelligenceReport, ConfidenceBreakdown, SmartSuggestion
from app.ai_intelligence.pipeline import run_ai_pipeline
from app.core.config import get_settings
from app.cache import extraction_cache, invalidate_ai_only
from app.services.statement_service import StatementService
from app.services.transaction_service import TransactionService
from app.utils.logging import get_logger

logger = get_logger(__name__)

CACHE_KEY = "ai_intelligence"
STATUS_KEY = "ai_processing_status"


class AiIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.statements = StatementService(db)
        self.transactions = TransactionService(db)
        self.settings = get_settings()

    def _set_status(self, meta: dict, status: str, **extra: Any) -> dict:
        meta[STATUS_KEY] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        return meta

    def get_status(self, statement_id: uuid.UUID) -> dict:
        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")
        meta = statement.metadata_json or {}
        status = meta.get(STATUS_KEY, {"status": "unknown"})
        dashboard = meta.get("ai_dashboard")
        return {
            "statement_id": str(statement_id),
            "processing": status,
            "has_report": CACHE_KEY in meta,
            "embeddings_cached": EMB_CACHE_KEY in meta,
            "dashboard": dashboard,
            "analyzed_at": meta.get("ai_intelligence_at"),
        }

    def analyze(
        self,
        statement_id: uuid.UUID,
        *,
        force_refresh: bool = False,
    ) -> tuple[AiIntelligenceReport, bool]:
        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        meta = statement.metadata_json or {}

        if force_refresh:
            invalidate_ai_only(str(statement_id))

        if not force_refresh:
            redis_cached = extraction_cache.get_ai(str(statement_id))
            if redis_cached:
                report = AiIntelligenceReport.model_validate(redis_cached)
                report.cached = True
                return report, True
            if CACHE_KEY in meta:
                report = AiIntelligenceReport.model_validate(meta[CACHE_KEY])
                report.cached = True
                extraction_cache.set_ai(str(statement_id), meta[CACHE_KEY])
                return report, True

        meta = self._set_status(meta, "running", statement_id=str(statement_id))
        statement.metadata_json = meta
        self.db.commit()

        try:
            parse_result, _ = self.transactions.parse_transactions(statement_id)
            if not parse_result.transactions:
                raise AiNoTransactionsError(
                    "No transactions parsed — run extraction and transaction parse first"
                )

            meta = statement.metadata_json or {}
            ocr_conf = meta.get("ocr_confidence")
            layout_conf = meta.get("layout_confidence")

            dim = getattr(self.settings, "ai_embeddings_dim", 64)
            emb_index, emb_fragment, emb_hit = load_index_from_meta(
                meta,
                parse_result.transactions,
                dim=dim,
                force_rebuild=force_refresh,
            )

            report = run_ai_pipeline(
                str(statement_id),
                parse_result.transactions,
                parse_result,
                ocr_confidence=float(ocr_conf) if ocr_conf is not None else parse_result.ocr_confidence,
                layout_confidence=float(layout_conf)
                if layout_conf is not None
                else parse_result.layout_confidence,
                embeddings_index=emb_index,
            )

            report_payload = report.model_dump(mode="json")
            meta[CACHE_KEY] = report_payload
            extraction_cache.set_ai(str(statement_id), report_payload)
            meta.update(emb_fragment)
            meta["ai_intelligence_at"] = datetime.now(timezone.utc).isoformat()
            meta["ai_dashboard"] = build_dashboard_summary(report)
            meta["ai_embeddings_cache_hit"] = emb_hit
            meta = self._set_status(
                meta,
                "completed",
                confidence=report.confidence.overall,
                anomaly_count=len(report.anomalies),
                embeddings_cache_hit=emb_hit,
            )
            statement.metadata_json = meta
            self.db.commit()

            logger.info(
                "ai_intelligence_complete",
                statement_id=str(statement_id),
                anomalies=len(report.anomalies),
                confidence=report.confidence.overall,
                embeddings_cache_hit=emb_hit,
            )
            return report, False

        except Exception as exc:
            meta = statement.metadata_json or {}
            meta = self._set_status(meta, "failed", error=str(exc)[:500])
            statement.metadata_json = meta
            self.db.commit()
            raise

    def semantic_search(
        self,
        statement_id: uuid.UUID,
        query: str,
        limit: int = 20,
    ) -> list[dict]:
        if not query or len(query.strip()) < 2:
            return []

        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        report, _ = self.analyze(statement_id)
        parse_result, _ = self.transactions.parse_transactions(statement_id)
        meta = statement.metadata_json or {}
        dim = getattr(self.settings, "ai_embeddings_dim", 64)
        index, _, _ = load_index_from_meta(meta, parse_result.transactions, dim=dim)

        hits = index.semantic_search(query.strip(), limit=limit)
        by_id = {t.transaction_id: t for t in parse_result.transactions}
        cat_map = {c.transaction_id: c.category for c in report.categories}

        return [
            {
                "transaction_id": tid,
                "score": score,
                "description": by_id[tid].description if tid in by_id else "",
                "category": cat_map.get(tid, "Other"),
            }
            for tid, score in hits
        ]

    @staticmethod
    def empty_report(statement_id: str, message: str) -> AiIntelligenceReport:
        return AiIntelligenceReport(
            statement_id=statement_id,
            confidence=ConfidenceBreakdown(overall=0.0, factors=["no_transactions"]),
            suggestions=[
                SmartSuggestion(
                    id="no-txn",
                    severity="high",
                    title="No transactions",
                    message=message,
                    action="parse_transactions",
                )
            ],
        )
