# Phase 2 — PDF Upload, Viewer & Coordinate Extraction

Status: **complete** in this repository.

## Backend

| Deliverable | Location |
|-------------|----------|
| Upload API `POST /api/v1/upload` | `backend/app/api/routes/upload.py` |
| Extraction API `GET /api/v1/statements/{id}/extract` | `backend/app/api/routes/extract.py` |
| PDF engine (dict-mode PyMuPDF) | `backend/app/pdf_engine/` |
| Storage `storage/original_pdfs/{uuid}.pdf` | `StorageService`, `settings.storage_original` |
| PostgreSQL metadata | `backend/app/models/statement.py` |
| Service layer | `StatementService`, `PdfExtractionService` |

### Extraction format

Each span includes: `text`, `x`, `y`, `width`, `height`, `font`, `font_size`, `bbox` — from `page.get_text("dict")`.

## Frontend

| Deliverable | Location |
|-------------|----------|
| Drag-and-drop upload | `frontend/src/components/pdf/UploadZone.tsx` |
| PDF viewer + zoom/pages | `frontend/src/components/pdf/StatementPdfViewer.tsx` |
| Coordinate overlay | `frontend/src/components/pdf/ExtractionOverlay.tsx` |
| Zustand PDF state | `frontend/src/store/usePdfStore.ts` |
| Preview page | `frontend/src/pages/PreviewPage.tsx` |
| Coordinate utils | `frontend/src/utils/coordinates.ts` |

## Verify locally

```bash
docker compose up --build
# Upload at http://localhost:5173/preview
# Or: POST /api/v1/upload with a PDF
# Then: GET /api/v1/statements/{id}/extract
```

## Tests

- `backend/tests/test_pdf_extraction.py`
- `frontend/src/utils/__tests__/coordinates.test.ts`

## Next phases (out of scope for Phase 2)

- Transaction parsing (Phase 3+)
- Invisible PDF editing (Phase 4+)
- AI intelligence (Phase 9)
