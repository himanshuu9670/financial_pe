"""Safe cache invalidation — statement scope vs content-scoped OCR."""

from __future__ import annotations

from app.cache.cache_keys import PREFIX, statement_ai_key, statement_extraction_key
from app.cache.redis_manager import redis_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Statement-bound namespaces (never delete content-hash OCR keys here).
_STATEMENT_PREFIXES = ("stmt:extraction", "stmt:txn", "stmt:ai", "stmt:preview")


def invalidate_statement(statement_id: str) -> int:
    """
    Clear per-statement caches when PDF is replaced, re-parsed, or edited.
    OCR results keyed by file hash are preserved for reuse across statements.
    """
    deleted = 0
    patterns = [
        f"{PREFIX}:stmt:extraction:{statement_id}:*",
        f"{PREFIX}:stmt:txn:*:{statement_id}:*",
        statement_ai_key(statement_id),
        f"{PREFIX}:stmt:preview:{statement_id}",
        # Legacy v1 keys
        f"sf:v1:extraction:{statement_id}",
        f"sf:v1:extraction:{statement_id}:*",
        f"sf:v1:ai:{statement_id}",
        f"sf:v1:transactions:{statement_id}",
    ]
    for pattern in patterns:
        if "*" in pattern:
            deleted += redis_manager.scan_delete(pattern)
        else:
            deleted += redis_manager.delete(pattern)
    logger.info("cache_invalidated_statement", statement_id=statement_id, deleted=deleted)
    return deleted


def invalidate_ai_only(statement_id: str) -> int:
    return redis_manager.delete(statement_ai_key(statement_id))


def invalidate_extraction_pages(statement_id: str, pages: str) -> int:
    return redis_manager.delete(statement_extraction_key(statement_id, pages))
