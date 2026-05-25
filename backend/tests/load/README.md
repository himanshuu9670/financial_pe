# Load testing (Phase 11)

## k6

```bash
# Smoke (health + system-status)
k6 run ../deployment/load/k6-smoke.js

# Phase 11 — concurrent health, metrics, AI status
k6 run ../deployment/load/k6-phase11-load.js
```

Set `API_BASE=http://localhost:8000/api/v1` for remote targets.

## Locust (optional)

Install `locust` and run `locust -f locustfile.py` when added for upload/export stress against staging only.

## Thresholds

- p95 API latency &lt; 2s for smoke endpoints
- Error rate &lt; 10% on health probes (degraded DB may fail strict checks)
