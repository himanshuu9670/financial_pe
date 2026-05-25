# Performance Audit — StatementForge (Phase 10)

**Date:** 2026-05-22  
**Scope:** Existing production codebase (Phases 1–9)  
**Method:** Static architecture review + known hot paths (no destructive rewrites)

## Executive summary

The platform is **functionally enterprise-ready** but was optimized for correctness first. Phase 10 adds **Redis hot caches**, **DB indexes**, **batched PDF extraction**, **Celery queue isolation**, and **Prometheus metrics** to address the highest-impact bottlenecks before cloud scale-out.

| Area | Severity | Finding |
|------|----------|---------|
| PDF extraction (500+ pages) | High | Full-document load in memory — **mitigated** with page batching + `pdf_max_pages_in_memory` |
| OCR / parse pipeline | High | CPU-bound, single worker default — **mitigated** with `ocr` queue + concurrency |
| AI insights | Medium | Recomputes on cold cache — **mitigated** with Redis + JSONB dual cache |
| Frontend PDF viewer | Medium | Large bundle (pdfjs + recharts) — **mitigated** with code splitting + lazy routes |
| Overlay rendering | Medium | Many DOM boxes on dense pages — acceptable with overlay toggle; virtualize per page if needed |
| DB listing | Medium | Missing composite indexes — **fixed** migration `004_phase10` |
| Export under load | Medium | Single export queue — **mitigated** with dedicated `export` queue |
| Observability | Low→Fixed | JSON metrics only — **Prometheus** `/api/v1/metrics` added |

## 1. Frontend

### Bottlenecks
- **PDF.js worker + viewer** — largest JS chunk; loads on preview/workspace routes.
- **Recharts** — isolated to insights routes via `manualChunks` + lazy `/insights`.
- **Workspace re-renders** — Zustand + React Query generally fine; overlay toggles reduce paint cost.

### Optimizations applied (Phase 10)
- Route-level `React.lazy` for heavy pages.
- Vite `manualChunks`: `vendor`, `pdf`, `charts`, `query`, `motion`.
- Keep overlay off by default in dense debug scenarios (existing toggle).

### Recommendations
- Profile with React DevTools Profiler on 200+ row statements.
- Consider `requestIdleCallback` for non-critical AI panel fetches.

## 2. Backend API

### Bottlenecks
- Synchronous extraction on `GET /extract` for large PDFs.
- Repeated AI pipeline invocations without cache.

### Optimizations applied
- Redis cache for extraction + AI reports (TTL configurable).
- `X-Response-Time-Ms` header + Prometheus histograms.
- Rate limits on extract, AI search, AI analyze.

### Recommendations
- Prefer Celery for `refresh=true` on large statements (existing async OCR/parse tasks).
- Horizontal scale: 2+ Uvicorn workers behind nginx (production Dockerfile).

## 3. PDF engine

### Bottlenecks
- `get_text("dict")` per page — O(pages × spans).
- Export regenerates full PDF — expected cost.

### Optimizations applied
- Page batch processing with `gc.collect()` between batches.
- Cap in-memory pages (`PDF_MAX_PAGES_IN_MEMORY=500`) with `?pages=` incremental API.

## 4. OCR pipeline

### Bottlenecks
- Tesseract + OpenCV on scanned docs — seconds to minutes per document.

### Optimizations applied
- Dedicated Celery `ocr` queue.
- Task retries + late ack.
- Metrics: `ocr_jobs_total`.

### Recommendations
- Cache OCR output in Redis keyed by statement + file hash (future).
- Parallelize per-page OCR in worker pool (Phase 10+ optional).

## 5. Database

### Optimizations applied
- Indexes: `statements(user_id, created_at)`, `transactions(statement_id, row_index)`, `export_jobs(status)`, `audit_logs(created_at)`.
- Connection pool: `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True` (existing).

## 6. Redis & Celery

### Applied
- Namespaced keys `sf:v1:{namespace}:{statement_id}`.
- Queues: `default`, `ocr`, `export`, `ai`.
- Invalidation on transaction re-parse.

## 7. Target SLIs (production)

| Metric | Target |
|--------|--------|
| API p95 (read) | < 500ms |
| API p95 (extract, small PDF) | < 5s |
| Export job success | > 99% |
| OCR queue lag | < 5 min at P95 load |

Monitor via Prometheus + Grafana (`deployment/docker/docker-compose.prod.yml`).
