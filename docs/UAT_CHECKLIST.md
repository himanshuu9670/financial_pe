# UAT Checklist — StatementForge

**Environment:** Staging (`AUTH_DISABLED=false`)  
**Tester:** _______________  **Date:** _______________

## Prerequisites

- [ ] Staging deployed (`.\scripts\staging_up.ps1`)
- [ ] Login works (`demo@pdfeditor.local` or production UAT accounts)
- [ ] Celery worker running (`celery inspect ping`)
- [ ] Test PDFs in `test_pdfs/` (native + scan samples)

---

## 1. Upload workflow

| # | Step | Pass | Notes |
|---|------|------|-------|
| 1.1 | Upload native PDF (HDFC/SBI/etc.) | ☐ | |
| 1.2 | Upload completes; statement appears in list | ☐ | |
| 1.3 | Reject non-PDF file (`.txt`) | ☐ | Expect 4xx |
| 1.4 | Reject oversize file (if testable) | ☐ | |

## 2. Extraction & OCR

| # | Step | Pass | Notes |
|---|------|------|-------|
| 2.1 | Native PDF: transactions extracted | ☐ | |
| 2.2 | Low-text / scan PDF: OCR path or degraded message | ☐ | |
| 2.3 | Multiline descriptions parsed reasonably | ☐ | |
| 2.4 | Large PDF (10+ pages): completes without timeout | ☐ | |
| 2.5 | Failed processing shows safe error (not stack trace) | ☐ | |

## 3. Workspace editing

| # | Step | Pass | Notes |
|---|------|------|-------|
| 3.1 | Edit debit/credit; balance propagates | ☐ | |
| 3.2 | Summary cards update | ☐ | |
| 3.3 | PDF overlay aligns at 100% zoom | ☐ | |
| 3.4 | Rapid edits: UI remains responsive | ☐ | |
| 3.5 | Route navigation (dashboard → workspace → admin) | ☐ | |

## 4. Financial recalculation

| # | Step | Pass | Notes |
|---|------|------|-------|
| 4.1 | Chain of 10+ edits: balances consistent | ☐ | |
| 4.2 | Invalid balance flagged by validator | ☐ | |
| 4.3 | Undo/redo restores prior values | ☐ | |

## 5. Export workflow

| # | Step | Pass | Notes |
|---|------|------|-------|
| 5.1 | Queue export; job status progresses | ☐ | |
| 5.2 | Download exported PDF | ☐ | |
| 5.3 | Typography: amounts keep grouping (e.g. commas) | ☐ | |
| 5.4 | Visual: no obvious misalignment vs original | ☐ | |
| 5.5 | Duplicate export click does not create parallel jobs | ☐ | |
| 5.6 | Failed export shows user-safe message | ☐ | |

## 6. AI insights (if enabled)

| # | Step | Pass | Notes |
|---|------|------|-------|
| 6.1 | Categories appear for food/travel-like txns | ☐ | |
| 6.2 | Anomalies flagged for outlier amounts | ☐ | |
| 6.3 | Insights tab loads without blocking workspace | ☐ | |

## 7. Security (staging auth on)

| # | Step | Pass | Notes |
|---|------|------|-------|
| 7.1 | Unauthenticated API calls rejected (401) | ☐ | |
| 7.2 | Non-admin cannot access `/admin` | ☐ | |
| 7.3 | Expired JWT rejected | ☐ | |

## 8. Observability

| # | Step | Pass | Notes |
|---|------|------|-------|
| 8.1 | `/api/v1/health` returns healthy/degraded | ☐ | |
| 8.2 | Admin monitoring panel loads | ☐ | |
| 8.3 | QA dashboard shows Celery stats | ☐ | |

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA | | | |
| Product | | | |
| Engineering | | | |

**UAT result:** ☐ Pass  ☐ Pass with exceptions  ☐ Fail  

**Blockers:**
