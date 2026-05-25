# QA Test PDF Dataset

Place real bank statement samples here for manual and integration QA.

## Directory layout

```
test_pdfs/
├── README.md
├── generated/          # auto-generated synthetic PDFs (gitignored optional)
├── yes_bank/           # optional real samples
├── axis_bank/
├── canara_bank/
├── sbi/
├── hdfc/
├── icici/
├── stress/
│   ├── large/          # 100+ page statements
│   ├── corrupted/
│   └── scans/          # low-quality / rotated scans
```

## Generate synthetic fixtures

```bash
cd backend
python ../scripts/generate_test_pdfs.py
```

Outputs to `test_pdfs/generated/`:

- `minimal_native.pdf` — native text layer
- `multi_page.pdf` — 3 pages
- `low_text_scan_like.pdf` — OCR fallback trigger
- `multiline_rows.pdf` — wrapped descriptions

## Do not commit

- Customer PII or production statements
- Files with real account numbers unless redacted

## CI usage

Unit tests use in-memory minimal PDFs via `tests/conftest.py`.  
Integration tests skip if `test_pdfs/generated/minimal_native.pdf` is missing.
