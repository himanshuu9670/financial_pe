"""
Dynamic column mapping — spatial clustering + header inference (no hardcoded x positions).
"""

from __future__ import annotations

from app.ai_engine.column_detector import detect_columns
from app.ai_engine.models import ColumnDefinition
from app.ai_engine.row_grouper import group_spans_into_rows
from app.ai_engine.span_utils import PageSpan, flatten_spans
from app.pdf_engine.models import DocumentExtraction


def map_columns(
    document: DocumentExtraction,
    *,
    page: int | None = None,
) -> list[ColumnDefinition]:
    """Detect columns per page and merge; unknown banks use generic clustering."""
    all_columns: list[ColumnDefinition] = []
    by_page: dict[int, list[PageSpan]] = {}

    for ps in flatten_spans(document):
        if page is not None and ps.page != page:
            continue
        by_page.setdefault(ps.page, []).append(ps)

    for page_num, page_spans in by_page.items():
        if not page_spans:
            continue
        page_width = page_spans[0].page_width
        rows = group_spans_into_rows(page_spans)
        cols = detect_columns(rows, page_width)
        for c in cols:
            if not any(existing.name == c.name for existing in all_columns):
                all_columns.append(c)

    return sorted(all_columns, key=lambda c: c.x_min)
