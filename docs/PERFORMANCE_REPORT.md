# Performance Report — Phase 11 (QA)

Phase 11 load testing complements Phase 10 performance work.

## Load suites

| Script | VUs | Duration | Endpoints |
|--------|-----|----------|-----------|
| `deployment/load/k6-smoke.js` | 5 | 30s | health, system-status |
| `deployment/load/k6-phase11-load.js` | 20 | 45s | health, system-status, `/metrics` |

## Run

```bash
export API_BASE=http://localhost:8000/api/v1
k6 run deployment/load/k6-phase11-load.js
```

## Related docs

- [CACHE_PERFORMANCE_REPORT.md](./CACHE_PERFORMANCE_REPORT.md) — Redis OCR/extraction cache
- [PERFORMANCE_AUDIT.md](./PERFORMANCE_AUDIT.md) — Phase 10 audit
- [PHASE10.md](./PHASE10.md) — scalability features

## Targets (smoke)

- p95 latency &lt; 3s on health/metrics under 20 VUs
- Error rate &lt; 15% (DB/redis degraded environments may spike)

## Not in automated load (staging only)

- Concurrent PDF uploads
- Concurrent OCR / export jobs
- WebSocket edit-sync fan-out
- AI `/api/v1/ai/*` burst

Use staging + real `test_pdfs` for those scenarios.
