# Production Release Checklist

Use before cutover to production. Check each item on staging first.

## Security

- [ ] `AUTH_DISABLED=false` in production env
- [ ] `JWT_SECRET_KEY` and `SECRET_KEY` rotated (64+ char random)
- [ ] `DEBUG=false`, `APP_ENV=production`
- [ ] `CORS_ORIGINS` set to production domain only
- [ ] TLS terminated (nginx `nginx.tls.conf` or cloud load balancer)
- [ ] HSTS enabled (`ssl-params.conf`)
- [ ] Rate limits appropriate (`RATE_LIMIT_*`)
- [ ] No secrets in git (`.env.production` gitignored)
- [ ] Demo password changed or demo user disabled in prod
- [ ] `/metrics` not public (nginx IP allowlist or internal network)

## Database

- [ ] `alembic upgrade head` on production DB
- [ ] Connection pooling sized for expected load
- [ ] Backup schedule: `scripts/backup.ps1` or managed RDS snapshots
- [ ] Restore tested: `scripts/restore_backup.ps1` on staging copy

## Redis & Celery

- [ ] Redis persistence (AOF) enabled in prod compose
- [ ] Celery workers: `-Q default,ocr,export,ai`
- [ ] Worker count ≥ 2 for OCR/export peak
- [ ] `task_acks_late` + `task_reject_on_worker_lost` confirmed (default)

## Storage

- [ ] `storage/` volumes backed up or S3 `STORAGE_BACKEND=s3`
- [ ] Disk quota / lifecycle policy for exports and snapshots

## Deployment

- [ ] Images built from `Dockerfile.*.prod`
- [ ] Health check passes after deploy
- [ ] Rollback plan documented (previous image tag + DB migration downgrade policy)
- [ ] Smoke: `.\scripts\smoke_phase12.ps1` equivalent on staging URL

## Monitoring

- [ ] Prometheus scraping `/api/v1/metrics`
- [ ] Grafana dashboard imported (`deployment/grafana/dashboards/`)
- [ ] Alerts: 5xx rate, export failures, dead letters, queue backlog, worker count = 0
- [ ] Sentry `SENTRY_DSN` configured (optional)

## DNS & networking

- [ ] Domain points to load balancer / nginx
- [ ] WebSocket path `/api/v1/ws/` works through proxy
- [ ] `client_max_body_size` ≥ max upload (55M nginx / app setting)

## Post-deploy (first 24h)

- [ ] Run UAT smoke on production (read-only test account)
- [ ] Watch `celery_dead_letters_total`, `export_jobs_total{status=failure}`
- [ ] Confirm backups completed
- [ ] On-call has [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md)

## Rollback procedure

1. Scale traffic to previous release (previous Docker tag / compose revision).
2. If migration broke schema: restore DB from last backup (see `restore_backup.ps1`).
3. Clear Redis cache only if corruption suspected (`FLUSHDB` — causes cache miss storm).
4. Communicate via status page; preserve audit logs for RCA.
