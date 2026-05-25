"""Row segmentation with confidence scores."""

from __future__ import annotations

from app.ai_engine.row_grouper import group_spans_into_rows
from app.ai_engine.span_utils import PageSpan, flatten_spans
from app.ai_layout_engine.models import RowSegment
from app.pdf_engine.models import DocumentExtraction


def segment_rows(document: DocumentExtraction) -> list[RowSegment]:
    segments: list[RowSegment] = []
    by_page: dict[int, list[PageSpan]] = {}

    for ps in flatten_spans(document):
        by_page.setdefault(ps.page, []).append(ps)

    for page_num, page_spans in by_page.items():
        rows = group_spans_into_rows(page_spans)
        for row in rows:
            if row.is_header or row.is_footer:
                continue
            conf = 0.9 if row.spans else 0.4
            if len(row.text) < 3:
                conf *= 0.5
            segments.append(
                RowSegment(
                    page=page_num,
                    row_index=row.row_index,
                    bbox=row.bbox,
                    text=row.text[:500],
                    span_count=len(row.spans),
                    confidence=round(conf, 2),
                )
            )
    return segments
