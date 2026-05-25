"""Canonical cache key builders and engine version tokens for invalidation."""

from __future__ import annotations

import hashlib
from pathlib import Path

# Bump when OCR preprocessing / Tesseract pipeline semantics change.
OCR_ENGINE_VERSION = "ocr-v1"
EXTRACTION_ENGINE_VERSION = "extract-v1"
TRANSACTION_ENGINE_VERSION = "txn-parse-v1"
AI_ENGINE_VERSION = "ai-v9"

PREFIX = "sf:v2"


def file_content_hash(path: Path) -> str:
    """SHA-256 of full file bytes (streaming) — invalidates when PDF bytes change."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def ocr_config_fingerprint(*, dpi_scale: float = 2.0, lang: str = "eng") -> str:
    payload = f"{OCR_ENGINE_VERSION}|dpi={dpi_scale}|lang={lang}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def ocr_result_key(file_hash: str, config_fp: str, pages: str) -> str:
    return f"{PREFIX}:ocr:{file_hash}:{config_fp}:{pages}"


def native_extraction_key(file_hash: str, pages: str) -> str:
    return f"{PREFIX}:native:{EXTRACTION_ENGINE_VERSION}:{file_hash}:{pages}"


def statement_extraction_key(statement_id: str, pages: str) -> str:
    return f"{PREFIX}:stmt:extraction:{statement_id}:{pages}"


def statement_transaction_parse_key(statement_id: str, file_hash: str) -> str:
    return f"{PREFIX}:stmt:txn:{TRANSACTION_ENGINE_VERSION}:{statement_id}:{file_hash}"


def statement_ai_key(statement_id: str) -> str:
    return f"{PREFIX}:stmt:ai:{AI_ENGINE_VERSION}:{statement_id}"


def statement_preview_key(statement_id: str) -> str:
    return f"{PREFIX}:stmt:preview:{statement_id}"


def statement_scan_pattern(statement_id: str) -> str:
    return f"{PREFIX}:stmt:*:{statement_id}*"
