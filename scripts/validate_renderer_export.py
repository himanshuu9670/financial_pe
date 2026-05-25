"""Generate a sample PDF and run the replacement pipeline for visual validation.

Run: python scripts/validate_renderer_export.py
"""
from pathlib import Path
import sys
import uuid
import fitz

# Ensure backend package root is on sys.path for imports when running as a script
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.pdf_engine.edit_models import TypographySpec, TargetSpan, Alignment
from app.pdf_engine.text_replacer import replace_in_pdf


def make_sample_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "01/01/2024  SWIGGY PAYMENT", fontsize=10)
    page.insert_text((72, 92), "1,000.00", fontsize=10)
    page.insert_text((400, 92), "9,000.00", fontsize=10)
    doc.save(str(path))
    doc.close()


def run_validation():
    repo_root = Path(__file__).resolve().parents[1]
    sample_in = repo_root / "storage" / "temp" / "sample_minimal.pdf"
    sample_out = repo_root / "storage" / "exports" / "sample_edited.pdf"

    make_sample_pdf(sample_in)

    # Approximate bbox around (400,92) amount used above.
    amount_bbox = [396.0, 88.0, 460.0, 104.0]

    typo = TypographySpec(
        font="helv",
        font_size=10.0,
        color=(0.0, 0.0, 0.0),
        alignment=Alignment.RIGHT,
    )

    span = TargetSpan(
        transaction_id=str(uuid.uuid4()),
        field="credit",
        page=1,
        bbox=amount_bbox,
        original_text="9,000.00",
        new_text="9,999.99",
        typography=typo,
        pymupdf_font="helv",
    )

    results = replace_in_pdf(sample_in, sample_out, [span])
    print("Replacement results:")
    for r in results:
        print(r)

    print(f"Wrote edited PDF to: {sample_out}")


if __name__ == "__main__":
    run_validation()
