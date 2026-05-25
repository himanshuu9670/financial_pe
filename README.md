# Financial PDF Editor (StatementForge)

Production-grade foundation for an AI-powered **bank statement PDF editor** with typography-preserving edits, multi-bank support, and automatic balance recalculation.

> **Phase 8** — Production hardening: JWT auth, audit logs, versioning, async exports. **Phase 7** added the editing workspace.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, TypeScript, Tailwind CSS, Framer Motion, Zustand, React Query |
| Backend | FastAPI, SQLAlchemy, Alembic, Celery |
| Data | PostgreSQL, Redis |
| Infra | Docker Compose |

## Project structure

```
financial-pdf-editor/
├── frontend/          # React SPA
├── backend/           # FastAPI + workers
├── docker/            # Docker helpers
├── nginx/             # Reverse proxy (production)
├── docs/              # Architecture docs
├── scripts/           # Dev utilities
├── storage/           # PDF file storage
├── docker-compose.yml
└── .env.example
```

## Quick start (Docker)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Copy env (if missing) and start all services
cp .env.example .env   # Windows: copy .env.example .env
docker compose up --build
# Or on Windows PowerShell:
# .\scripts\docker-up.ps1
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 (host; container uses 5432) |
| Redis | localhost:6379 |

## Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL & Redis are running, then:
cp ../.env.example ../.env
# Edit DATABASE_URL for localhost

alembic upgrade head
python scripts/seed_demo_user.py
uvicorn app.main:app --reload --port 8000
```

**OCR (Phase 6):** Install [Tesseract](https://github.com/tesseract-ocr/tesseract) on the host for scanned PDF fallback. Docker images include `tesseract-ocr` automatically.

**Auth (Phase 8):** Demo login after `alembic upgrade head` + seed: `demo@pdfeditor.local` / `demo-password-change-me`. Set `AUTH_DISABLED=false` in production and use strong `JWT_SECRET_KEY`.

```powershell
cd backend
alembic upgrade head
python scripts/seed_demo_user.py
```

### Celery worker (optional)

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Environment variables

See [`.env.example`](.env.example). Key variables:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` / `CELERY_BROKER_URL` — Redis for cache and Celery
- `STORAGE_*` — PDF storage paths
- `VITE_API_BASE_URL` — Frontend → API base URL

## API endpoints (Phase 1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/upload` | Upload PDF |
| GET | `/api/v1/statements` | List statements |
| GET | `/api/v1/statements/{id}` | Get statement |
| GET | `/api/v1/statements/{id}/extract` | Extract text + coordinates + fonts |
| GET | `/api/v1/statements/{id}/transactions` | Hybrid parse (native/OCR) + layout confidence |
| GET | `/api/v1/statements/{id}/intelligence` | Layout analysis debug (columns, tables, OCR) |
| POST | `/api/v1/auth/login` · `/register` · `/refresh` | JWT authentication |
| POST | `/api/v1/exports/queue` | Async export job (Celery) |
| GET | `/api/v1/versions/statement/{id}` | PDF version snapshots |
| GET | `/api/v1/admin/stats` | Admin metrics (admin role) |
| GET | `/api/v1/system-status` | Production health + queues |
| POST | `/api/v1/edit/start-session` | Begin in-memory edit session |
| POST | `/api/v1/edit/update-transaction` | Edit debit/credit/balance with propagation |
| GET | `/api/v1/edit/session-state` | Current ledger + summaries |
| POST | `/api/v1/edit/undo` · `/redo` · `/commit` | Session history + persist metadata |
| POST | `/api/v1/export/apply-edits` | Apply invisible edits + export PDF |
| GET | `/api/v1/preview/{id}/edited` | Download edited PDF |
| GET | `/api/v1/preview/{id}` | Stream PDF |
| POST | `/api/v1/edit/{id}` | Edit scaffold |
| POST | `/api/v1/export/{id}` | Export scaffold |

## Database models

- **User** — accounts (demo user seeded for Phase 1)
- **Statement** — PDF metadata, versions, balances
- **Transaction** — row-level financial data + coordinate JSON
- **EditHistory** — audit trail per edit

## Code quality

```bash
# Frontend
cd frontend && npm run lint

# Backend
cd backend && black app && ruff check app
```

## Phase roadmap

| Phase | Focus |
|-------|--------|
| 1 | Foundation |
| 2 | PDF upload, viewer, coordinate extraction ([docs/PHASE2.md](docs/PHASE2.md)) |
| 3 | Transaction extraction + bank intelligence (this) |
| 4 | Financial recalculation + invisible PDF edits |
| 4 | Typography-preserving edits |
| 5 | Export pipeline |
| 6 | Multi-bank layout intelligence + OCR fallback |
| 7 | Enterprise editing workspace + real-time PDF sync |
| 8 | Auth, audit, versioning, async exports, rate limits, CI |
| 9 | AI financial intelligence ([docs/PHASE9.md](docs/PHASE9.md)) |
| 10 | Performance + cloud deployment ([docs/PHASE10.md](docs/PHASE10.md), [readiness](docs/PRODUCTION_READINESS_REPORT.md)) |
| 11 | QA, stress testing, resilience ([docs/PHASE11.md](docs/PHASE11.md), [QA report](docs/QA_REPORT.md)) |
| 12 | Staging, UAT, production cutover ([docs/PHASE12.md](docs/PHASE12.md), [release checklist](docs/RELEASE_CHECKLIST.md)) |

### Phase 9 AI APIs

- `GET /api/v1/ai/status?statement_id=`
- `GET /api/v1/ai/categories?statement_id=`
- `GET /api/v1/ai/anomalies?statement_id=`
- `GET /api/v1/ai/insights?statement_id=`
- `GET /api/v1/ai/confidence?statement_id=`
- `POST /api/v1/ai/suggestions?statement_id=`
- `GET /api/v1/ai/search?statement_id=&q=`
- `POST /api/v1/ai/analyze/{statement_id}?async_mode=true`

Frontend: **AI Insights** workspace tab, **AI** right-panel confidence, `/insights/:id` dashboard (Recharts).

Smoke: `.\scripts\smoke_phase9.ps1` · Tests: `pytest tests/test_ai_intelligence.py`

### Redis cache layer (operational)

Modular cache: `backend/app/cache/` — [CACHE_PERFORMANCE_REPORT.md](docs/CACHE_PERFORMANCE_REPORT.md)  
Admin: `GET /api/v1/admin/cache-stats` · Monitoring: `GET /api/v1/admin/monitoring` — see [OBSERVABILITY_SETUP.md](docs/OBSERVABILITY_SETUP.md)

## Scalability notes

- **Horizontal API scaling** — stateless FastAPI behind load balancer
- **Worker pool** — scale Celery workers for PDF/OCR throughput
- **Storage** — migrate `storage/` to S3/GCS with signed URLs
- **DB** — read replicas for statement listing; partition by `user_id`
- **Redis** — separate broker DB from cache DB (already split in compose)

## License

Proprietary — internal project.
