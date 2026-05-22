# Financial PDF Editor (StatementForge)

Production-grade foundation for an AI-powered **bank statement PDF editor** with typography-preserving edits, multi-bank support, and automatic balance recalculation.

> **Phase 5** — Invisible typography-preserving PDF export. Prior phases feed coordinate + ledger edits.

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

# 2. Start all services
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
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
| GET | `/api/v1/statements/{id}/transactions` | Parse transactions + validate balances |
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
| 2 | PDF upload, viewer, coordinate extraction |
| 3 | Transaction extraction + bank intelligence (this) |
| 4 | Financial recalculation + invisible PDF edits |
| 4 | Typography-preserving edits |
| 5 | Export pipeline |
| 6 | Multi-bank layouts |
| 7 | Premium UI polish |

## Scalability notes

- **Horizontal API scaling** — stateless FastAPI behind load balancer
- **Worker pool** — scale Celery workers for PDF/OCR throughput
- **Storage** — migrate `storage/` to S3/GCS with signed URLs
- **DB** — read replicas for statement listing; partition by `user_id`
- **Redis** — separate broker DB from cache DB (already split in compose)

## License

Proprietary — internal project.
