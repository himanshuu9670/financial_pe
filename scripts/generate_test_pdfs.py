#!/usr/bin/env python3
"""Generate synthetic QA PDF fixtures into test_pdfs/generated/."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from tests.helpers.pdf_fixtures import generate_all_fixtures  # noqa: E402


def main() -> None:
    out = ROOT / "test_pdfs" / "generated"
    paths = generate_all_fixtures(out)
    print(f"Generated {len(paths)} PDFs in {out}")
    for p in paths:
        print(f"  - {p.name} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
