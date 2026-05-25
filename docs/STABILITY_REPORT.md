# Stability Report — Phase 11

## Resilience mechanisms

| Failure | Behavior |
|---------|----------|
| Redis unavailable | Cache reads return `None`; app continues without cache (`REDIS_CACHE_ENABLED=false` in tests) |
| OCR unavailable | `TesseractOcrProcessor.is_available()` false; scanned PDFs flagged; hybrid pipeline degrades |
| Invalid PDF upload | `validate_pdf_bytes` rejects before persist |
| Corrupt PDF open | `PdfCorruptedError` / `PdfValidationError` |
| DB error | SQLAlchemy handler returns 500 without leaking queries |
| Unhandled exception | Generic 500; detail only if `DEBUG=true` |
| Export path traversal | `safe_filename()` on edited export paths |
| Rate limit | slowapi `RateLimitExceeded` handler |

## Worker / queue

- Celery queues: `default`, `ocr`, `export`, `ai`
- Failed exports tracked on `ExportJob.status == failed`
- Admin monitoring: queue depth, worker inspect
- **Phase 11b:** Structured retries (`async.retry`), dead letters (`async.dead_letter`), recoveries (`async.recovery`) — see [CELERY_RESILIENCE_REPORT.md](./CELERY_RESILIENCE_REPORT.md)
- Export tasks retry up to 2× before dead-letter; duplicate active exports blocked per statement

## Recovery tests

`tests/resilience/test_recovery.py` — cache disabled mode, health structure.

## Recommended staging drills

1. Stop Redis → verify API health `degraded`, uploads still work
2. Kill Celery worker mid-export → job should mark `failed` or retry per task config
3. Upload `test_pdfs/generated/low_text_scan_like.pdf` → OCR path

## Known limitations

- `scanned_fallback.export_via_ocr_overlay` may be unimplemented for some banks
- Full DB integration tests require PostgreSQL (docker-compose)
