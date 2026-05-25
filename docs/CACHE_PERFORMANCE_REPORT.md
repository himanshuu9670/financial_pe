# Cache Performance Report — OCR & Extraction Redis Layer

**Implementation:** `backend/app/cache/`  
**Date:** 2026-05-22

## Architecture

| Layer | Key strategy | TTL (default) | Invalidation |
|-------|----------------|---------------|--------------|
| OCR results | `sha256(file_bytes) + ocr_config + pages` | 24h (`CACHE_TTL_OCR`) | File bytes change → new hash |
| Native extraction | `file_hash + engine version + pages` | 1h | File or `EXTRACTION_ENGINE_VERSION` bump |
| Statement extraction | `statement_id + pages` | 1h | `invalidate_statement()` |
| Transaction parse | `statement_id + file_hash + engine version` | 1h | Re-parse / `force_refresh` |
| AI insights | `statement_id + AI_ENGINE_VERSION` | 30m | `invalidate_ai_only()` after txn re-parse |

**Important:** OCR caches are **content-scoped**, not statement-scoped — re-uploading the same PDF to a new statement reuses OCR work.

## Integration points (no pipeline rewrites)

1. **`hybrid_pipeline.py`** — Redis OCR + native caches before Tesseract / `get_text("dict")`
2. **`transaction_service.py`** — Redis transaction parse cache; Celery checks cache before `force_refresh`
3. **`pdf_extraction_service.py`** — statement extraction via `extraction_cache`
4. **`ai_intelligence_service.py`** — AI report via `extraction_cache`

## Expected performance impact

| Scenario | Before | After (warm cache) |
|----------|--------|---------------------|
| Repeat OCR on same scanned PDF | Full Tesseract run (~10–120s) | Redis hit (~5–20ms) |
| Re-open statement (parsed) | DB JSONB read | Redis → DB fallback |
| Celery re-queue same statement | Full parse | Cache hit skips OCR + parse |
| Second statement, identical file | Full OCR again | OCR cache hit (same file hash) |

*Estimates depend on page count and hardware; measure in staging with `/admin/cache-stats`.*

## Observability

- **Prometheus:** `cache_operations_total{namespace,result}`
- **Admin API:** `GET /api/v1/admin/cache-stats`
- **In-process snapshot:** hit rates per namespace (`ocr`, `native`, `extraction`, `transactions`, `ai`)

## Benchmark procedure

```powershell
# 1) First parse (cold)
Measure-Command { Invoke-RestMethod "$api/statements/$id/transactions?refresh=true" }

# 2) Second parse (warm — should be faster)
Measure-Command { Invoke-RestMethod "$api/statements/$id/transactions" }

# 3) Check cache stats
Invoke-RestMethod "$api/admin/cache-stats" -Headers @{ Authorization = "Bearer $token" }
```

Compare `namespaces.ocr.hit` and `namespaces.transactions.hit` between runs.

## Safety rules enforced

1. **Financial data** — transaction/AI caches invalidated on re-parse; not serving OCR cache as final ledger without parse validation.
2. **Engine versions** — bump `TRANSACTION_ENGINE_VERSION` / `AI_ENGINE_VERSION` in `cache_keys.py` when semantics change.
3. **Stale PDF** — content hash invalidates OCR when file bytes change.
4. **Redis down** — all cache modules no-op; PostgreSQL JSONB caches remain.

## Frontend

- React Query `staleTime` / `gcTime` increased for extraction and AI hooks.
- `placeholderData: (prev) => prev` for smoother re-navigation (stale-while-revalidate).

## Recommendations

1. Monitor OCR hit rate in Grafana from `cache_operations_total`.
2. Alert if OCR hit rate → 0 while Redis healthy (possible key churn).
3. For 500+ page OCR, combine with existing page batching + `?pages=` incremental API.
