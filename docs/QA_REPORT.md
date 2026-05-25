# QA Report — Phase 11

**Generated:** Phase 11 implementation  
**Scope:** Testing, validation, hardening (no engine rewrites)

## Test matrix

| Area | Suite | Status |
|------|-------|--------|
| PDF validation | `tests/pdf_engine/test_validation.py` | Automated |
| PDF extraction stress | `tests/pdf_engine/test_extraction_stress.py` | Automated |
| Typography | `tests/typography/test_preservation.py` | Automated |
| Export integrity | `tests/exports/test_export_integrity.py` | Automated |
| OCR resilience | `tests/ocr/test_resilience.py` | Automated (+ Tesseract optional) |
| AI intelligence | `tests/ai/test_qa_pipeline.py` + `test_ai_intelligence.py` | Automated |
| Financial engine | `tests/financial_engine/test_edge_cases.py` + `test_financial_engine.py` | Automated |
| Security | `tests/security/` | Automated |
| Integration smoke | `tests/integration/test_smoke_flows.py` | Automated (needs API) |
| Resilience | `tests/resilience/test_recovery.py` | Automated |
| Celery async | `tests/resilience/test_celery_resilience.py` | Automated |
| Cache / monitoring | `test_cache_layer.py`, `test_monitoring.py` | Automated |
| Frontend coordinates | `frontend/src/utils/__tests__/coordinates.test.ts` | Automated |

## Smoke flows

| Flow | Coverage |
|------|----------|
| Health / metrics | `test_smoke_flows.py` |
| Upload rejection | Non-PDF header test |
| Full upload→extract→edit→export | Manual + staging; use real `test_pdfs/` samples |

## Fixtures

Synthetic PDFs via `scripts/generate_test_pdfs.py`.  
Bank-specific folders (`test_pdfs/hdfc/`, etc.) for manual QA only.

## Gaps (manual / staging)

- Real YES/AXIS/SBI/HDFC/ICICI templates (PII-redacted)
- Pixel-level PDF visual diff (use `app/qa/visual_diff.py` heuristics today)
- WebSocket edit-sync load at scale
- Celery worker crash injection in staging

## How to run

```powershell
cd backend
python -m pytest tests/ -q
```

```powershell
.\scripts\smoke_phase11.ps1
```

## QA dashboard

`GET /api/v1/admin/qa-dashboard` — in-process checklist + live health/export counts.
