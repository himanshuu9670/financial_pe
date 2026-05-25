"""Statement-scoped extraction, transaction parse, and AI insight caches."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.cache.cache_keys import (
    EXTRACTION_ENGINE_VERSION,
    file_content_hash,
    native_extraction_key,
    statement_ai_key,
    statement_extraction_key,
    statement_transaction_parse_key,
)
from app.cache.metrics import record_op
from app.cache.redis_manager import redis_manager
from app.core.config import get_settings
from app.pdf_engine.models import DocumentExtraction
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _pages_label(page_numbers: list[int] | None) -> str:
    if not page_numbers:
        return "all"
    return ",".join(str(p) for p in sorted(page_numbers))


class ExtractionCache:
    # --- Coordinate extraction (per statement) ---
    def get_statement_extraction(
        self, statement_id: str, pages: str = "all"
    ) -> dict | None:
        key = statement_extraction_key(statement_id, pages)
        data = redis_manager.get_json(key)
        record_op("extraction", "hit" if data else "miss")
        return data

    def set_statement_extraction(
        self, statement_id: str, data: dict, pages: str = "all"
    ) -> None:
        key = statement_extraction_key(statement_id, pages)
        redis_manager.set_json(key, data, get_settings().cache_ttl_extraction)
        record_op("extraction", "set")

    # --- Native layer by file hash (shared across statements) ---
    def get_native(self, path: Path, page_numbers: list[int] | None) -> dict | None:
        fh = file_content_hash(path)
        key = native_extraction_key(fh, _pages_label(page_numbers))
        data = redis_manager.get_json(key)
        record_op("native", "hit" if data else "miss")
        return data

    def set_native(self, path: Path, document: DocumentExtraction, page_numbers: list[int] | None) -> None:
        fh = file_content_hash(path)
        key = native_extraction_key(fh, _pages_label(page_numbers))
        redis_manager.set_json(
            key,
            {
                "document": document.model_dump(mode="json"),
                "engine_version": EXTRACTION_ENGINE_VERSION,
            },
            get_settings().cache_ttl_extraction,
        )
        record_op("native", "set")

    # --- Parsed transactions ---
    def get_transaction_parse(self, statement_id: str, path: Path) -> dict | None:
        fh = file_content_hash(path)
        key = statement_transaction_parse_key(statement_id, fh)
        data = redis_manager.get_json(key)
        record_op("transactions", "hit" if data else "miss")
        return data

    def set_transaction_parse(self, statement_id: str, path: Path, data: dict) -> None:
        fh = file_content_hash(path)
        key = statement_transaction_parse_key(statement_id, fh)
        redis_manager.set_json(key, data, get_settings().cache_ttl_transactions)
        record_op("transactions", "set")

    # --- AI insights ---
    def get_ai(self, statement_id: str) -> dict | None:
        key = statement_ai_key(statement_id)
        data = redis_manager.get_json(key)
        record_op("ai", "hit" if data else "miss")
        return data

    def set_ai(self, statement_id: str, data: dict) -> None:
        key = statement_ai_key(statement_id)
        redis_manager.set_json(key, data, get_settings().cache_ttl_ai)
        record_op("ai", "set")


extraction_cache = ExtractionCache()
