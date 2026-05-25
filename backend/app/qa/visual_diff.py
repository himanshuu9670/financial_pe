"""Lightweight PDF/text validation for QA — not pixel-perfect diff."""

from __future__ import annotations

from app.pdf_engine.models import DocumentExtraction


def summarize_extraction(doc: DocumentExtraction) -> dict:
    return {
        "pages": doc.total_pages,
        "spans": doc.span_count,
        "blocks": doc.block_count,
        "is_likely_scanned": doc.is_likely_scanned,
        "warnings": doc.warnings,
    }


def compare_text_coverage(
    before: DocumentExtraction,
    after: DocumentExtraction,
    *,
    min_span_ratio: float = 0.85,
) -> tuple[bool, list[str]]:
    """Heuristic: exported/native re-extract should retain most span count."""
    issues: list[str] = []
    if before.span_count == 0:
        return True, ["no baseline spans"]
    ratio = after.span_count / before.span_count
    if ratio < min_span_ratio:
        issues.append(f"span_count dropped: {before.span_count} -> {after.span_count}")
    if after.total_pages != before.total_pages:
        issues.append(f"page_count changed: {before.total_pages} -> {after.total_pages}")
    return len(issues) == 0, issues
