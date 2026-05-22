"""
Row grouping via y-axis proximity and font consistency.
Merges multiline / wrapped transaction descriptions.
"""

from __future__ import annotations

from app.ai_engine.models import GroupedRow
from app.ai_engine.span_utils import PageSpan, merge_bbox
from app.pdf_engine.models import TextSpan

FOOTER_KEYWORDS = (
    "end of statement",
    "computer generated",
    "this is a system",
    "page ",
    "total ",
    "registered office",
    "unless the constituent",
)
HEADER_KEYWORDS = (
    "date",
    "description",
    "particulars",
    "narration",
    "debit",
    "credit",
    "withdrawal",
    "deposit",
    "balance",
    "chq",
    "cheque",
    "txn",
    "tran",
    "value date",
)


def _median_line_height(spans: list[PageSpan]) -> float:
    heights = [ps.span.height for ps in spans if ps.span.height > 0]
    if not heights:
        return 12.0
    heights.sort()
    return heights[len(heights) // 2]


def _is_header_row(text: str) -> bool:
    lower = text.lower()
    hits = sum(1 for k in HEADER_KEYWORDS if k in lower)
    return hits >= 3 and len(lower) < 200


def _is_footer_row(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in FOOTER_KEYWORDS)


def group_spans_into_rows(
    page_spans: list[PageSpan],
    *,
    y_tolerance_factor: float = 1.4,
) -> list[GroupedRow]:
    if not page_spans:
        return []

    page = page_spans[0].page
    median_h = _median_line_height(page_spans)
    y_tol = median_h * y_tolerance_factor

    sorted_spans = sorted(page_spans, key=lambda ps: (ps.y_center, ps.span.x))

    raw_rows: list[list[PageSpan]] = []
    current: list[PageSpan] = []
    anchor_y: float | None = None

    for ps in sorted_spans:
        if anchor_y is None or abs(ps.y_center - anchor_y) <= y_tol:
            current.append(ps)
            anchor_y = ps.y_center if anchor_y is None else (anchor_y + ps.y_center) / 2
        else:
            if current:
                raw_rows.append(current)
            current = [ps]
            anchor_y = ps.y_center

    if current:
        raw_rows.append(current)

    grouped: list[GroupedRow] = []
    row_idx = 0

    for cluster in raw_rows:
        cluster.sort(key=lambda ps: ps.span.x)
        text = " ".join(ps.span.text.strip() for ps in cluster).strip()
        bboxes = [ps.span.bbox for ps in cluster]
        bbox = merge_bbox(bboxes)
        y_min = min(ps.span.y for ps in cluster)
        y_max = max(ps.span.y + ps.span.height for ps in cluster)
        y_center = (y_min + y_max) / 2

        grouped.append(
            GroupedRow(
                page=page,
                row_index=row_idx,
                y_center=y_center,
                y_min=y_min,
                y_max=y_max,
                bbox=bbox,
                spans=[ps.span for ps in cluster],
                text=text,
                is_header=_is_header_row(text),
                is_footer=_is_footer_row(text),
            )
        )
        row_idx += 1

    return merge_continuation_rows(grouped, y_tol * 2.5)


def merge_continuation_rows(rows: list[GroupedRow], merge_gap: float) -> list[GroupedRow]:
    """
    Merge rows without a leading date that sit directly below a transaction row
    (multiline descriptions).
    """
    from app.ai_engine.patterns import looks_like_date

    if not rows:
        return []

    merged: list[GroupedRow] = []
    i = 0
    while i < len(rows):
        row = rows[i]
        if row.is_header or row.is_footer:
            merged.append(row)
            i += 1
            continue

        buffer = row
        j = i + 1
        while j < len(rows):
            nxt = rows[j]
            if nxt.is_header or nxt.is_footer:
                break
            gap = nxt.y_min - buffer.y_max
            if gap > merge_gap:
                break
            if looks_like_date(nxt.text.split()[0] if nxt.text else ""):
                break
            buffer = _combine_rows(buffer, nxt)
            j += 1

        merged.append(buffer)
        i = j

    for idx, row in enumerate(merged):
        row.row_index = idx

    return merged


def _combine_rows(a: GroupedRow, b: GroupedRow) -> GroupedRow:
    spans = a.spans + b.spans
    bboxes = [a.bbox, b.bbox]
    return GroupedRow(
        page=a.page,
        row_index=a.row_index,
        y_center=(a.y_center + b.y_center) / 2,
        y_min=min(a.y_min, b.y_min),
        y_max=max(a.y_max, b.y_max),
        bbox=merge_bbox(bboxes),
        spans=spans,
        text=f"{a.text} {b.text}".strip(),
        is_header=False,
        is_footer=False,
    )
