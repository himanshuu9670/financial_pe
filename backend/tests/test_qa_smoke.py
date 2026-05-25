"""QA smoke module unit tests."""

from app.qa.smoke import qa_summary, run_smoke_checklist


def test_smoke_checklist_has_core_areas():
    checks = run_smoke_checklist()
    areas = {c["area"] for c in checks}
    assert "pdf_header_validation" in areas
    assert "ocr_heuristic" in areas


def test_qa_summary_status():
    summary = qa_summary()
    assert summary["status"] in ("healthy", "degraded", "unhealthy")
    assert "checks" in summary
