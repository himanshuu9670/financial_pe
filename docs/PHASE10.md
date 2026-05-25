# Phase 10 — Performance, Cloud Deployment & Scalability

**Status:** Implemented (incremental hardening on existing architecture)

## Deliverables map

| # | Deliverable | Location |
|---|-------------|----------|
| 1 | Performance audit | [PERFORMANCE_AUDIT.md](PERFORMANCE_AUDIT.md) |
| 2 | Frontend optimization | `frontend/vite.config.ts`, `src/routes/index.tsx` |
| 3 | PDF engine optimization | `pdf_engine/extractor.py` (batching) |
| 4 | OCR / worker optimization | `workers/celery_app.py`, `docker-compose.yml` |
| 5 | DB optimization | `alembic/versions/004_phase10_performance_indexes.py` |
| 6 | Redis caching | `app/cache/` (OCR, extraction, AI) + `app/core/cache` facade |
| 7 | Celery hardening | Queues, retries, metrics |
| 8 | Large PDF support | Settings + batched extraction |
| 9 | Observability | Prometheus + optional Sentry |
| 10 | Error monitoring | `sentry_setup.py`, `SENTRY_DSN` |
| 11 | Production Docker | `deployment/docker/Dockerfile.*.prod` |
| 12 | NGINX | `deployment/nginx/nginx.conf` |
| 13 | Cloud architecture | `deployment/terraform`, `kubernetes` |
| 14 | S3 storage | `services/storage_backend.py` |
| 15 | Backup | `scripts/backup.ps1` |
| 16 | API rate control | extract + AI limits |
| 17 | Security | Non-root prod image, existing Phase 8 headers |
| 18 | Frontend prod build | Code splitting |
| 19 | Staging/prod env | `.env.production.example` |
| 20 | CI/CD | `.github/workflows/cd.yml` |
| 21 | Load testing | `deployment/load/k6-smoke.js` |
| 22 | Readiness report | [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md) |

## Quick start (production compose)

```bash
cp .env.production.example .env.production
# edit secrets
docker compose -f deployment/docker/docker-compose.prod.yml --env-file .env.production up -d --build
```

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- Metrics scrape: `GET /api/v1/metrics`
- JSON summary: `GET /api/v1/metrics?format=json`

## Smoke

```powershell
.\scripts\smoke_phase10.ps1
.\scripts\smoke_phase9.ps1
```
