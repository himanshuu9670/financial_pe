# Phase 12 — Staging Release + UAT + Production Cutover

Release engineering phase: operational readiness without rewriting core engines.

## Quick start

### 1. Local green run (dev compose)

```powershell
.\scripts\smoke_phase12.ps1
```

Validates: Docker up, migrations, pytest, health, frontend, Celery ping.

### 2. Staging stack

```powershell
cp .env.staging.example .env.staging
# Edit secrets + CORS_ORIGINS
.\scripts\staging_up.ps1
```

- **Auth:** `AUTH_DISABLED=false` in `.env.staging`
- **UAT user:** `demo@pdfeditor.local` / `demo-password-change-me` (admin)
- **App:** http://localhost (nginx → API + SPA)

### 3. TLS (production / public staging)

1. Place `fullchain.pem` + `privkey.pem` in `deployment/docker/certs/`
2. Mount TLS nginx config:

```yaml
# In docker-compose.staging.yml nginx volumes:
- ../nginx/nginx.tls.conf:/etc/nginx/nginx.conf:ro
```

3. Set `CORS_ORIGINS=https://staging.your-domain.com`

## End-to-end UAT flow

See [UAT_CHECKLIST.md](./UAT_CHECKLIST.md).

```
Upload → Extract/OCR → Workspace edit → Recalc → Export → Download
```

Test PDFs: add redacted samples under `test_pdfs/{bank}/`.

## Load testing (staging)

```bash
k6 run deployment/load/k6-staging-uat.js
# With auth:
UAT_TOKEN=<jwt> API_BASE=https://staging.example.com/api/v1 k6 run deployment/load/k6-staging-uat.js
```

## Observability

| Service | URL (staging compose) |
|---------|------------------------|
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |
| API metrics | Internal `/api/v1/metrics` via nginx (restricted) |
| Admin QA | `/admin` → QA dashboard |

## Production cutover

1. [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)
2. [FINAL_PRODUCTION_AUDIT.md](./FINAL_PRODUCTION_AUDIT.md)
3. Copy `.env.production.example` → `.env.production`
4. `docker compose -f deployment/docker/docker-compose.prod.yml --env-file .env.production up -d`

## Related docs

| Doc | Purpose |
|-----|---------|
| [UAT_CHECKLIST.md](./UAT_CHECKLIST.md) | Manual acceptance tests |
| [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) | Go-live checklist |
| [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md) | On-call playbooks |
| [CELERY_RESILIENCE_REPORT.md](./CELERY_RESILIENCE_REPORT.md) | Async recovery |
| [PRODUCTION_READINESS_REPORT.md](./PRODUCTION_READINESS_REPORT.md) | Phase 10 baseline |
