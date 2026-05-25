# Incident Response Playbook

**Platform:** StatementForge  
**On-call:** _______________

## Severity guide

| Level | Example | Response |
|-------|---------|----------|
| S1 | Data corruption, auth bypass, total outage | Immediate |
| S2 | Export/OCR down for all users | < 1 hour |
| S3 | Degraded performance, single-tenant issue | < 4 hours |
| S4 | Cosmetic / non-critical | Next business day |

---

## OCR failures

**Symptoms:** Statements stuck in `extracting` or `error`; `ocr_failures_total` rising; Tesseract unavailable in health.

**Steps:**

1. Check health: `GET /api/v1/health?detailed=true` → `ocr.available`
2. Worker logs: `docker compose logs celery_worker --tail 100`
3. Verify PDF is valid; retry upload for single user
4. If worker OOM: increase memory or reduce `--concurrency`
5. Dead letter: audit `async.dead_letter` for statement ID; user sees safe message in UI
6. **Do not** delete statement row without backup; re-queue: re-upload or manual re-extract API if exposed

**Escalation:** Scanned PDF only → document known `scanned_fallback` limitation; offer native PDF workaround.

---

## Export corruption / failure

**Symptoms:** `ExportJob.status=failed`; user reports misaligned PDF; `export_validation_failures_total` up.

**Steps:**

1. Find job: Admin → stats or DB `export_jobs` by `statement_id`
2. Check `error_message` and `metadata_json.dead_letter`
3. User message in metadata — communicate retry export
4. If typography drift: compare original vs export in workspace; file bug with sample PDF (redacted)
5. Retry: new export queues only if no active `queued|processing` job (idempotent guard)
6. Rollback: use previous `pdf_snapshots` version if snapshot exists

---

## Worker crashes

**Symptoms:** Queue backlog; `workers_online=0` in QA dashboard; tasks not completing.

**Steps:**

1. `docker compose restart celery_worker`
2. `celery -A app.workers.celery_app inspect ping`
3. Redis up: `redis-cli ping`
4. Stuck tasks: with `task_acks_late`, tasks should re-queue after worker loss
5. Scale workers horizontally (additional containers, same queues)

---

## Redis outage

**Symptoms:** Cache miss storm; Celery broker errors; health `redis: false`.

**Steps:**

1. Restart Redis container / failover to replica
2. API may run with `REDIS_CACHE_ENABLED=false` temporarily (performance hit)
3. Celery **requires** Redis broker — workers cannot process until broker returns
4. After recovery: monitor queue depth; no automatic duplicate exports if idempotency guards active

---

## Database outage

**Symptoms:** 500 on all API calls; health `database: false`.

**Steps:**

1. Check Postgres container / RDS status
2. Connection string / credentials in env
3. Disk full on volume → expand or prune logs
4. Restore from latest backup (`scripts/restore_backup.ps1`) to **new** DB if corruption
5. Run `alembic upgrade head` after restore if restoring older snapshot

---

## Security incident

**Symptoms:** Suspicious uploads, auth anomalies, rate limit spikes.

**Steps:**

1. Rotate `JWT_SECRET_KEY` (invalidates all sessions)
2. Review `audit_logs` last 24h
3. Block IP at nginx / WAF if applicable
4. Preserve logs for investigation; do not wipe storage without legal/compliance sign-off

---

## Communication template

> We are investigating issues with [upload/export/OCR]. Your data is stored securely. Please avoid [action] until resolved. ETA: [time].

---

## Post-incident

- [ ] RCA document within 48h
- [ ] Update [FINAL_PRODUCTION_AUDIT.md](./FINAL_PRODUCTION_AUDIT.md) known risks if new
- [ ] Add automated test or alert if gap found
