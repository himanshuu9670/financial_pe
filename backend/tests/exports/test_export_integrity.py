"""Export QA — visual diff heuristics on re-extracted documents."""

from app.pdf_engine.extractor import extract_document
from app.qa.visual_diff import compare_text_coverage
from tests.helpers.pdf_fixtures import write_minimal_native_pdf


def test_reextract_span_coverage_stable(tmp_path):
    path = write_minimal_native_pdf(tmp_path / "stmt.pdf")
    before = extract_document(path)
    after = extract_document(path)
    ok, issues = compare_text_coverage(before, after, min_span_ratio=0.99)
    assert ok, issues
