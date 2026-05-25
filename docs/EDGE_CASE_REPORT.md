# Edge Case Report — Phase 11

## PDF inputs

| Case | Handling | Test |
|------|----------|------|
| Non-PDF header | Rejected at upload | `test_validation.py`, security |
| Empty file | `PdfValidationError` | `test_validation.py` |
| Corrupt xref | `PdfCorruptedError` | `test_validation.py` |
| Zero pages | `PdfValidationError` on open | loader |
| Multi-page (50+) | Batched extraction (`pdf_page_batch_size`) | `test_extraction_stress.py` |
| Low native text | `detect_scanned_pdf` → OCR | `test_resilience.py` |
| Multiline descriptions | Extraction spans | `test_extraction_stress.py` |
| Encrypted PDF | `PdfEncryptedError` | manual |
| Huge file | `max_upload_size_bytes` | storage service |

## Financial

| Case | Handling | Test |
|------|----------|------|
| 50-row propagation | `validate_ledger` after edit | `test_edge_cases.py` |
| Sequential edits | Deterministic recalc | `test_edge_cases.py` |
| Balance mismatch | Validator flags | `test_financial_engine.py` |
| Undo patches | Inverse patches | `test_edge_cases.py` |

## OCR

| Case | Handling | Test |
|------|----------|------|
| No Tesseract | Skip OCR integration test | `test_resilience.py` |
| Blurry / skewed scans | Preprocessor + confidence gate | manual samples in `test_pdfs/stress/scans/` |
| OCR typo amounts | `smart_corrector` | `test_ai_intelligence.py` |

## Export / typography

| Case | Handling | Test |
|------|----------|------|
| Amount grouping | `format_amount_for_pdf` | typography tests |
| Bbox drift | Targets reuse original bbox | `test_preservation.py` |
| Re-extract coverage | `compare_text_coverage` | `test_export_integrity.py` |

## Security

| Case | Handling | Test |
|------|----------|------|
| Path traversal filename | `safe_filename` | `test_upload_security.py` |
| Expired JWT | `verify_access_token` → None | security |
| Malicious upload | Header validation | security + integration |

## Frontend

| Case | Mitigation |
|------|------------|
| Large transaction tables | Virtualization recommended in workspace |
| Overlay desync | Coordinate layer + zoom state in pdf-editor components |
| Route transitions | Lazy-loaded routes (Phase 10) |

Add redacted real PDFs under `test_pdfs/` to extend this matrix.
