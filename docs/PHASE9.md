# Phase 9 — AI Financial Intelligence (Production)

## Architecture

```
PDF → Extraction → Layout Intelligence → Transaction Parse
    → Semantic Parser → Categorizer → Anomaly Detector
    → Fraud Engine → Smart Corrector → Confidence Booster
    → Insights (cached in statement.metadata_json)
```

### Backend modules (`backend/app/ai_intelligence/`)

| Module | Role |
|--------|------|
| `semantic_parser.py` | Merchant/intent tags, category hints |
| `categorizer.py` | Transaction categories |
| `anomaly_detector.py` | Z-score, duplicates, balance jumps |
| `fraud_engine.py` | Composite risk score |
| `smart_corrector.py` | OCR amount fixes |
| `confidence_booster.py` | OCR + layout + financial + semantic |
| `embeddings_engine.py` | Hash-trick vectors (no GPU required) |
| `embeddings_cache.py` | Fingerprinted cache in `metadata_json` |
| `pattern_engine.py` | Category spend aggregates |
| `suggestion_engine.py` | UX suggestions |
| `pipeline.py` | Orchestration |
| `model_providers.py` | Pluggable backends (optional sentence-transformers) |

### Caching keys (`statements.metadata_json`)

- `ai_intelligence` — full report
- `ai_embeddings_cache` — vectors + fingerprint
- `ai_processing_status` — running | completed | failed
- `ai_dashboard` — summary for status API

### APIs

| Method | Path |
|--------|------|
| GET | `/api/v1/ai/status?statement_id=` |
| GET | `/api/v1/ai/categories?statement_id=` |
| GET | `/api/v1/ai/anomalies?statement_id=` |
| GET | `/api/v1/ai/insights?statement_id=` |
| GET | `/api/v1/ai/confidence?statement_id=` |
| POST | `/api/v1/ai/suggestions?statement_id=` |
| GET | `/api/v1/ai/search?statement_id=&q=` |
| POST | `/api/v1/ai/analyze/{id}?async_mode=true` |

### Async

- Celery task: `app.workers.tasks.run_ai_intelligence`
- Auto-queue after `process_statement_pdf` when `AI_AUTO_ANALYZE_AFTER_PARSE=true`

## Frontend

- Workspace left tab: **AI Insights** (`AiInsightsPanel`)
- Right tab: **AI** confidence meter
- Full dashboard: `/insights/:id` (Recharts)
- Client: `frontend/src/services/aiApi.ts`, `hooks/useAiIntelligence.ts`

## Configuration

```env
AI_EMBEDDINGS_DIM=64
AI_CACHE_EMBEDDINGS=true
AI_AUTO_ANALYZE_AFTER_PARSE=true
```

## Verify

```powershell
docker compose up -d
docker compose exec backend pytest tests/test_ai_intelligence.py -q
.\scripts\smoke_phase9.ps1
```

## Tests

- `backend/tests/test_ai_intelligence.py` — pipeline, cache, semantic search, OCR

## Next: Phase 10

See [PHASE10.md](PHASE10.md) — performance, cloud deployment, horizontal scaling.
