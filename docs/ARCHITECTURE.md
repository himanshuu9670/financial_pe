# Architecture — Phase 1 Foundation

## System overview

```
┌─────────────┐     REST      ┌─────────────┐     SQL      ┌────────────┐
│   React     │ ────────────► │   FastAPI   │ ───────────► │ PostgreSQL │
│  (Vite)     │               │             │              └────────────┘
└─────────────┘               │      │      │
                              │      ▼      │
                              │   Celery    │◄── Redis (broker + cache)
                              └─────────────┘
```

## Backend module boundaries

| Module | Responsibility | Phase |
|--------|----------------|-------|
| `pdf_engine/` | Coordinate extraction, region mapping | 2 |
| `typography_engine/` | Font metadata, invisible text replacement | 4 |
| `ai_engine/` | Transaction parsing, column/row detection | 3+ |
| `ai_layout_engine/` | Multi-bank signatures, table/column layout, hybrid pipeline | 6 |
| `ocr_engine/` | Scanned PDF detection, OpenCV preprocess, Tesseract OCR | 6 |
| `ai_intelligence/` | Categorization, anomalies, fraud, embeddings, insights | 9 |
| `core/cache/` | Redis hot cache (extraction, AI) | 10 |
| `monitoring/` | Prometheus metrics, health, tracing, OCR/export/redis/worker observability | 10+ |
| `core/observability/` | Sentry + metrics re-exports | 10 |
| `services/` | Orchestration, storage, statements | 1+ |
| `workers/` | Async PDF/OCR/AI pipelines (queued) | 2+ |

## Storage layout

```
storage/
├── original_pdfs/   # Uploaded statements
├── edited_pdfs/     # Patched exports
├── previews/        # Thumbnails / previews
├── temp/            # Processing scratch
└── logs/            # Processing logs
```

## API surface (v1)

- `GET /health` — readiness
- `POST /upload` — PDF upload (validated, async I/O, UUID storage)
- `GET /statements` — list
- `GET /statements/{id}` — detail
- `GET /statements/{id}/extract` — coordinate + typography extraction (PyMuPDF dict mode)
- `GET /preview/{id}` — serve PDF
- `POST /edit/{id}` — edit scaffold
- `POST /export/{id}` — export scaffold

## PDF engine (Phase 2)

```
pdf_engine/
├── pdf_loader.py      # open, validate, encrypted/corrupt detection
├── extractor.py       # page.get_text("dict") → spans with bbox + font
├── font_detector.py   # font name normalization
├── coordinate_mapper.py  # PDF ↔ viewport math (Phase 4 editing)
├── parser.py          # orchestration
└── models.py          # Pydantic extraction schema
```

Extraction JSON is cached in `statements.extraction_json`. Use `?refresh=true` or `?pages=1,2` for partial re-runs.

## Transaction intelligence (Phase 3)

```
Coordinate Extraction (Phase 2)
        ↓
Bank Classifier (keyword + header signatures)
        ↓
Row Grouper (y-proximity + multiline merge)
        ↓
Column Detector (x-clustering + header inference)
        ↓
Transaction Detector (span → column assignment)
        ↓
Financial Validator (balance chain)
        ↓
PostgreSQL transactions + metadata_json cache
```

| Module | Path |
|--------|------|
| Bank classifier | `ai_engine/bank_classifier.py` |
| Row grouper | `ai_engine/row_grouper.py` |
| Column detector | `ai_engine/column_detector.py` |
| Transaction detector | `ai_engine/transaction_detector.py` |
| Pipeline | `ai_engine/pipeline.py` |
| Validator | `financial_engine/validator.py` |
| OCR foundation | `ocr_engine/base.py` (stub) |

API: `GET /api/v1/statements/{id}/transactions?refresh=&debug=`

Every transaction field retains `coordinates` + `row_bbox` for Phase 4 editing.

## Financial engine (Phase 4)

```
Edit session (Redis + memory)
    → LedgerEntry chain
    → DependencyGraph (ordered nodes)
    → FinancialRecalculator.update_field
    → propagate_balances (downstream)
    → validate_ledger + compute_summary
    → AuditStack (undo/redo)
```

| Module | Role |
|--------|------|
| `dependency_graph.py` | Ordered transaction chain |
| `propagation_engine.py` | `balance[i] = balance[i-1] - debit + credit` |
| `recalculator.py` | Edit orchestration |
| `audit_engine.py` | Undo/redo patches |
| `summary_engine.py` | Totals and closing balance |
| `validator.py` | Chain integrity checks |

Commit writes to `metadata_json` + `edit_history` — **does not patch PDF** until export.

## Invisible PDF editing (Phase 5)

```
Ledger changes (Phase 4)
    → collect_targets_from_ledger (coordinate + typography)
    → batch_redact_page (white-out minimal region)
    → insert_text (PyMuPDF, matched font/size/alignment)
    → visual_validator (region text check)
    → storage/edited_pdfs/{statement_id}.pdf
```

| Module | Role |
|--------|------|
| `typography_engine.py` | Font metrics + amount formatting |
| `bbox_detector.py` | Expand/isolate replacement rects |
| `text_replacer.py` | Redact + draw pipeline |
| `overlay_renderer.py` | Vector-safe PyMuPDF calls |
| `export_engine.py` | Full export orchestration |
| `visual_validator.py` | Post-export QA |
| `scanned_fallback.py` | Legacy stub — superseded by `ocr_engine/` |

API: `POST /api/v1/export/apply-edits` · `GET /preview/{id}/edited`

## AI document intelligence (Phase 6)

```
PDF upload
    → scanned_pdf_detector (text density / image ratio)
    ├── native: pdf_engine.extract_document
    └── OCR: ocr_processor (render → preprocess → Tesseract → coordinate_rebuilder)
    → layout_detector (bank_signature, table_detector, column_mapper, row_segmenter)
    → run_transaction_pipeline + confidence_engine
    → financial validator
```

| Module | Role |
|--------|------|
| `bank_signature_engine.py` | Keyword/header fingerprints (YES, AXIS, HDFC, SBI, ICICI, PNB, …) |
| `table_detector.py` | Transaction region bboxes |
| `column_mapper.py` | Spatial column clustering (no fixed coordinates) |
| `hybrid_pipeline.py` | Native/OCR routing + in-memory OCR cache |
| `confidence_engine.py` | Per-transaction + layout scores |

API: `GET /api/v1/statements/{id}/intelligence` · transactions endpoint uses hybrid pipeline by default

Frontend: `/intelligence/:id` — layout overlays (tables, columns, row segments) + debug panel

## Enterprise editing workspace (Phase 7)

```
Edit session (REST) + optional WebSocket /ws/edit/{session_id}
    → Zustand: workspace, pdf, transactions, edit session
    → PDFCanvas: SelectionLayer + OverlayEditor (click-to-edit amounts)
    → LivePreviewLayer: instant value overlay on PDF
    → VirtualizedLedgerTable ↔ bidirectional highlight sync
    → Financial recalc → propagation flash + validation panel
```

| Route | Purpose |
|-------|---------|
| `/workspace/:id` | Multi-panel editing workspace |
| `/compare/:id` | Original vs edited PDF |
| `/history/:id` | Edit timeline + propagation |
| `/validation/:id` | Live ledger validation |

WebSocket foundation: subscribe/ping only; collaboration not enabled yet.

## Production infrastructure (Phase 8)

| Module | Role |
|--------|------|
| `auth/` | JWT access + refresh, RBAC (admin/editor/viewer) |
| `audit/` | Immutable audit log for uploads, edits, exports, auth |
| `services/version_service.py` | PDF snapshots under `storage/snapshots/` |
| `services/export_job_service.py` | Celery-backed export queue + secure download tokens |
| `services/storage_optimizer.py` | Temp cleanup, disk usage metrics |
| `api/middleware/security_headers.py` | HSTS, nosniff, frame deny |
| `api/middleware/rate_limit.py` | slowapi limits on upload/auth/export |

Production checklist: `AUTH_DISABLED=false`, rotate `JWT_SECRET_KEY`, run Celery worker, `alembic upgrade head`.

## Design principles

1. **Never regenerate PDFs** — patch coordinates only (Phase 4+).
2. **Isolate engines** — PDF, typography, and financial logic stay separate.
3. **Bank plugins** — layout profiles per institution (Phase 6).
4. **Async by default** — heavy work via Celery.
