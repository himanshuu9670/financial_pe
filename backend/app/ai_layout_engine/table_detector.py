"""
Transaction table region detection via span density and whitespace analysis.
"""

from __future__ import annotations

from app.ai_engine.span_utils import PageSpan, flatten_spans, merge_bbox
from app.ai_layout_engine.models import TableRegion
from app.pdf_engine.models import DocumentExtraction


def detect_table_regions(
    document: DocumentExtraction,
    *,
    header_y: float | None = None,
) -> list[TableRegion]:
    regions: list[TableRegion] = []
    by_page: dict[int, list[PageSpan]] = {}

    for ps in flatten_spans(document):
        by_page.setdefault(ps.page, []).append(ps)

    for page_num, spans in by_page.items():
        if not spans:
            continue

        table_spans = spans
        if header_y is not None:
            table_spans = [ps for ps in spans if ps.y_center >= header_y - 5]

        if len(table_spans) < 5:
            continue

        bboxes = [ps.span.bbox for ps in table_spans]
        bbox = merge_bbox(bboxes)
        page_h = table_spans[0].page_height

        row_estimate = _estimate_rows(table_spans)
        confidence = min(0.99, 0.5 + min(len(table_spans), 200) / 400)

        regions.append(
            TableRegion(
                page=page_num,
                bbox=bbox,
                row_count_estimate=row_estimate,
                confidence=round(confidence, 2),
            )
        )

    return regions


def _estimate_rows(spans: list[PageSpan]) -> int:
    if not spans:
        return 0
    heights = [ps.span.height for ps in spans if ps.span.height > 0]
    median_h = sorted(heights)[len(heights) // 2] if heights else 12
    y_vals = sorted(ps.y_center for ps in spans)
    if len(y_vals) < 2:
        return 1
    clusters = 1
    for i in range(1, len(y_vals)):
        if y_vals[i] - y_vals[i - 1] > median_h * 1.3:
            clusters += 1
    return clusters
