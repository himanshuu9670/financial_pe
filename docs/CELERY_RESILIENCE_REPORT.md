# Celery Resilience Report — Phase 11

## Architecture audit

| Component | Configuration | Notes |
|-----------|---------------|-------|
| Broker | Redis (`CELERY_BROKER_URL`) | JSON serialization |
| Result backend | Redis | Results expire after 24h |
| Queues | `default`, `ocr`, `export`, `ai` | Routed per task |
| `task_acks_late` | `true` | Re-queue on worker crash |
| `task_reject_on_worker_lost` | `true` | No silent loss on SIGKILL |
| `worker_prefetch_multiplier` | `1` | Fair dispatch under load |
| `task_time_limit` | 900s | Hard kill for stuck OCR/export |
| `task_soft_time_limit` | 840s | Grace window |

### Tasks & retries

| Task | Queue | max_retries | Retry delay | Dead-letter |
|------|-------|-------------|-------------|-------------|
| `process_statement_pdf` | ocr | 2 | 30s | Statement `status=error` + audit |
| `run_ocr_pipeline` | ocr | 2 | 30s | Same handler as above |
| `run_pdf_export` | export | 2 | 45s | ExportJob `failed` + metadata |
| `run_ai_intelligence` | ai | 2 | 20s | Safe failure payload (non-blocking) |

### Fixes applied (Phase 11b)

1. **Export retries** — `run_pdf_export` now calls `self.retry()` before `mark_failed` (previously never retried).
2. **`run_ocr_pipeline`** — Uses shared `_run_statement_pdf_task` (no broken nested `.apply().get()`).
3. **Idempotency** — Completed/dead-letter exports skipped; duplicate `queued|processing` jobs prevented per statement.
4. **Structured logging** — `async.retry`, `async.dead_letter`, `async.recovery` audit actions + Prometheus counters.
5. **Safe user messages** — Stored in job/statement metadata for API responses.

## Recovery scenarios

| Scenario | Expected behavior | Validated by |
|----------|-------------------|--------------|
| OCR transient failure | Up to 2 retries, then statement error + dead-letter | `test_celery_resilience.py` |
| Export transient failure | Retry with metadata bump, then failed job + user_message | integration tests |
| Worker crash mid-task | `acks_late` + `reject_on_worker_lost` re-queue | config audit + staging drill |
| Redis cache down | `RedisManager` returns None; API continues | `test_recovery.py` |
| Redis broker outage | Celery `broker_connection_retry_on_startup` | staging |
| Duplicate export request | Returns existing active job | `test_duplicate_export_queue_prevented` |
| Retry after success | Idempotent skip, no second snapshot | `test_run_pdf_export_idempotent_completed` |

## Observability

### Prometheus

- `celery_task_retries_total{task}`
- `celery_retry_events_total{task,outcome}`
- `celery_dead_letters_total{task}`
- `celery_active_tasks`

### Admin QA dashboard

`GET /api/v1/admin/qa-dashboard` includes `celery`:

- `recovery_status`, `retries_24h`, `dead_letters_24h`, `recoveries_24h`
- `queue_backlog`, `exports`, `workers`, `statements_error`

## Remaining risks

| Risk | Mitigation | Priority |
|------|------------|----------|
| Partial export writes snapshot before failure | Retry may create extra snapshots (rare) | Medium — add snapshot dedup by job_id |
| Broker partition | Monitor Redis; multi-AZ in prod | High |
| OCR timeout > soft limit | Tune limits per page count | Medium |
| No automatic DLQ re-drive UI | Manual re-queue from admin | Low |

## Run tests

```bash
cd backend
pytest tests/resilience/test_celery_resilience.py -q
pytest tests/resilience/ -q
```

## Staging drills

1. `docker compose stop worker` during export → job should return to queue or retry.
2. `docker compose stop redis` briefly → workers reconnect; no corrupted ExportJob rows.
3. Force OCR failure (bad PDF path) → statement `error` + audit `async.dead_letter`.
