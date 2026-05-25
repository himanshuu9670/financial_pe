# Phase 11 — Quality Assurance & Resilience

Phase 11 adds **tests, fixtures, load scripts, QA dashboard, and reports** without rewriting core engines.

## Test layout

```
backend/tests/
├── conftest.py          # fixtures, API client
├── helpers/pdf_fixtures.py
├── pdf_engine/
├── typography/
├── exports/
├── ocr/
├── ai/
├── financial_engine/
├── security/
├── integration/
├── resilience/
├── load/README.md
└── frontend/            # placeholder; UI tests in frontend/src
```

## Test PDFs

```bash
python scripts/generate_test_pdfs.py
```

Output: `test_pdfs/generated/`. Add real bank samples under `test_pdfs/{bank}/` (not committed).

## Run QA

```powershell
.\scripts\smoke_phase11.ps1
```

Or in Docker:

```bash
docker compose exec backend pytest tests/ -q
```

## Load testing

```bash
k6 run deployment/load/k6-smoke.js
k6 run deployment/load/k6-phase11-load.js
```

## Admin QA dashboard

`GET /api/v1/admin/qa-dashboard` (admin role) — surfaced on **Admin** page.

## Reports

| Document | Purpose |
|----------|---------|
| [QA_REPORT.md](./QA_REPORT.md) | Test matrix & coverage |
| [STABILITY_REPORT.md](./STABILITY_REPORT.md) | Failure modes & recovery |
| [EDGE_CASE_REPORT.md](./EDGE_CASE_REPORT.md) | PDF/OCR/financial edge cases |
| [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md) | Load & cache (links Phase 10) |
| [CELERY_RESILIENCE_REPORT.md](./CELERY_RESILIENCE_REPORT.md) | Async retries, dead letters, queue recovery |

## Hardening (incremental)

- `safe_filename()` — path traversal on edited exports
- Production error handler — no raw exception text unless `DEBUG=true`
