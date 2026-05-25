"""Modular Redis cache layer tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.cache.cache_keys import (
    OCR_ENGINE_VERSION,
    file_content_hash,
    ocr_config_fingerprint,
    ocr_result_key,
)
from app.cache.ocr_cache import OcrCache


def test_ocr_config_fingerprint_stable():
    a = ocr_config_fingerprint(dpi_scale=2.0)
    b = ocr_config_fingerprint(dpi_scale=2.0)
    assert a == b
    assert OCR_ENGINE_VERSION in "ocr-v1"


def test_ocr_result_key_includes_file_and_config(tmp_path):
    pdf = tmp_path / "t.pdf"
    pdf.write_bytes(b"%PDF-1.4 minimal")
    fh = file_content_hash(pdf)
    cfg = ocr_config_fingerprint()
    key = ocr_result_key(fh, cfg, "all")
    assert "sf:v2:ocr:" in key


@patch("app.cache.redis_manager.get_settings")
@patch("app.cache.ocr_cache.redis_manager")
def test_ocr_cache_roundtrip(mock_rm, mock_settings, tmp_path):
    mock_settings.return_value.redis_cache_enabled = True
    store = {}
    mock_rm.enabled.return_value = True

    def set_json(key, val, ttl):
        store[key] = __import__("json").dumps(val)

    def get_json(key):
        raw = store.get(key)
        return __import__("json").loads(raw) if raw else None

    mock_rm.set_json = set_json
    mock_rm.get_json = get_json

    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 test content for hash")

    cache = OcrCache()
    cache.set(pdf, {"document": {"total_pages": 1, "pages": [], "span_count": 0, "block_count": 0}, "ocr_confidence": 0.9})
    hit = cache.get(pdf)
    assert hit is not None
    assert hit["ocr_confidence"] == 0.9
