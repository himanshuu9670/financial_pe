# Observability Setup — StatementForge

Lightweight operational monitoring without modifying core PDF, OCR, or financial engines.

## Architecture

```
backend/app/monitoring/
├── metrics.py          # Prometheus registry (canonical)
├── api_metrics.py      # HTTP latency, slow requests, uploads
├── ocr_metrics.py      # OCR duration, cache hits, failures, pages
├── export_metrics.py   # Export duration, queue depth, validation
├── redis_metrics.py    # Redis INFO + cache snapshot
├── worker_metrics.py   # Celery inspect
├── health.py           # Subsystem health checks
└── tracing.py          # X-Request-ID + structlog context
```

`app/core/observability/metrics.py` re-exports from `monitoring` for backward compatibility.

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | Quick health (DB + Redis + status) |
| `GET /api/v1/health?detailed=true` | Full subsystem JSON |
| `GET /api/v1/system-status` | Ops summary + queue depth |
| `GET /api/v1/metrics` | Prometheus scrape (text) |
| `GET /api/v1/metrics?format=json` | JSON ops summary |
| `GET /api/v1/admin/monitoring` | Admin aggregate (auth required) |

## Prometheus metrics (key names)

| Metric | Description |
|--------|-------------|
| `http_requests_total` | API requests by method/endpoint/status |
| `http_request_duration_seconds` | API latency histogram |
| `http_slow_requests_total` | Requests &gt; 2s |
| `ocr_processing_duration_seconds` | OCR run time |
| `ocr_cache_hits_total` / `ocr_cache_misses_total` | OCR Redis cache |
| `ocr_failures_total` | OCR errors by reason |
| `ocr_pages_processed_total` | Pages OCR'd |
| `export_duration_seconds` | Export job duration |
| `export_queue_depth` | Queued + processing exports |
| `export_validation_failures_total` | Failed validation |
| `cache_operations_total` | Cache hit/miss/set by namespace |
| `redis_memory_used_bytes` | Redis memory gauge |
| `celery_active_tasks` | Active + reserved tasks |

## Grafana

1. Start production stack with Prometheus + Grafana:
   ```bash
   docker compose -f deployment/docker/docker-compose.prod.yml up -d prometheus grafana
   ```
2. Prometheus config: `deployment/prometheus/prometheus.yml` scrapes `backend:8000/api/v1/metrics`.
3. Import dashboard: `deployment/grafana/dashboards/statementforge-overview.json`
4. Open Grafana at http://localhost:3001 (default admin password from `.env.production`).

## Admin UI

Navigate to **Admin** in the app (requires admin role). The **Operations** panel shows:

- Subsystem health dots
- Celery workers and queue activity
- Export queue / failures
- Redis cache hit rates
- OCR availability

## Request tracing

Every API request receives:

- `X-Request-ID` response header (pass `X-Request-ID` to correlate)
- `X-Response-Time-Ms` latency header
- `request_id` field in structured logs (structlog)

## Redis monitoring

- Cache hit rates: in-process + `cache_operations_total` Prometheus metric
- Redis server: `used_memory`, `evicted_keys` via periodic `collect_redis_info()` on `/metrics` and `/system-status`

## Celery monitoring

- `inspect_workers()` — non-blocking, 1s timeout
- Metrics: `celery_active_tasks`, `celery_task_retries_total`
- Queue routing: `ocr`, `export`, `ai`, `default`

## Troubleshooting workflow

1. **Degraded health** → `GET /api/v1/health?detailed=true` — see which `checks.*` is false.
2. **Slow API** → Grafana panel "API p95 latency" or filter logs by `request_id`.
3. **OCR backlog** → Check Celery `ocr` queue in admin monitoring; verify `ocr_cache_hits_total` increasing on repeat runs.
4. **Export failures** → `export_jobs_total{status="failure"}` + admin export failed count.
5. **Stale cache** → Invalidate via re-parse (`?refresh=true`); OCR content cache auto-invalidates on file hash change.

## Sentry (optional)

Set `SENTRY_DSN` in environment — initialized in `app/main.py` via `init_sentry()`.

## Performance impact

- Metrics: in-memory Prometheus counters (negligible)
- Health checks: run on demand only (not per-request except lightweight redis gauge on `/metrics`)
- Celery inspect: 1s timeout, only on status/admin endpoints
- No blocking instrumentation in PDF/OCR/financial code paths

## Related docs

- [CACHE_PERFORMANCE_REPORT.md](CACHE_PERFORMANCE_REPORT.md)
- [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md)
- [PHASE10.md](PHASE10.md)
