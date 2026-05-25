"""OCR result cache — keyed by file content hash + OCR config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.cache.cache_keys import file_content_hash, ocr_config_fingerprint, ocr_result_key
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


class OcrCache:
    def resolve_keys(
        self,
        path: Path,
        page_numbers: list[int] | None,
        *,
        dpi_scale: float = 2.0,
    ) -> tuple[str, str, str]:
        fh = file_content_hash(path)
        cfg = ocr_config_fingerprint(dpi_scale=dpi_scale)
        pages = _pages_label(page_numbers)
        return fh, cfg, ocr_result_key(fh, cfg, pages)

    def get(
        self,
        path: Path,
        page_numbers: list[int] | None = None,
        *,
        dpi_scale: float = 2.0,
    ) -> dict[str, Any] | None:
        _, _, key = self.resolve_keys(path, page_numbers, dpi_scale=dpi_scale)
        data = redis_manager.get_json(key)
        if data:
            record_op("ocr", "hit")
            try:
                from app.monitoring.ocr_metrics import record_cache_hit

                record_cache_hit()
            except Exception:
                pass
            logger.info("ocr_cache_hit", key=key[:48])
            return data
        record_op("ocr", "miss")
        try:
            from app.monitoring.ocr_metrics import record_cache_miss

            record_cache_miss()
        except Exception:
            pass
        return None

    def set(
        self,
        path: Path,
        payload: dict[str, Any],
        page_numbers: list[int] | None = None,
        *,
        dpi_scale: float = 2.0,
    ) -> None:
        _, _, key = self.resolve_keys(path, page_numbers, dpi_scale=dpi_scale)
        ttl = get_settings().cache_ttl_ocr
        redis_manager.set_json(key, payload, ttl)
        record_op("ocr", "set")
        logger.info("ocr_cache_set", key=key[:48], ttl=ttl)

    def get_document(
        self,
        path: Path,
        page_numbers: list[int] | None = None,
    ) -> tuple[DocumentExtraction, float | None] | None:
        cached = self.get(path, page_numbers)
        if not cached:
            return None
        doc = DocumentExtraction.model_validate(cached["document"])
        return doc, cached.get("ocr_confidence")

    def set_document(
        self,
        path: Path,
        document: DocumentExtraction,
        ocr_confidence: float | None,
        *,
        page_numbers: list[int] | None = None,
        scan: dict | None = None,
    ) -> None:
        self.set(
            path,
            {
                "document": document.model_dump(mode="json"),
                "ocr_confidence": ocr_confidence,
                "engine_version": ocr_config_fingerprint(),
                "scan": scan,
            },
            page_numbers=page_numbers,
        )


ocr_cache = OcrCache()
