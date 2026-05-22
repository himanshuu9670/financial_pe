"""
Dynamic column detection via x-position clustering and header inference.
"""

from __future__ import annotations

from app.ai_engine.models import ColumnDefinition, GroupedRow

COLUMN_ALIASES: dict[str, list[str]] = {
    "date": ["date", "txn date", "tran date", "transaction date", "value date"],
    "description": [
        "description",
        "particulars",
        "narration",
        "details",
        "remarks",
        "transaction particulars",
    ],
    "debit": ["debit", "withdrawal", "withdrawals", "dr", "paid out"],
    "credit": ["credit", "deposit", "deposits", "cr", "paid in"],
    "balance": ["balance", "closing balance", "running balance", "avl bal"],
}


def _cluster_x_positions(centers: list[float], gap_threshold: float) -> list[tuple[float, float]]:
    if not centers:
        return []
    sorted_x = sorted(centers)
    clusters: list[list[float]] = [[sorted_x[0]]]
    for x in sorted_x[1:]:
        if x - clusters[-1][-1] <= gap_threshold:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    return [(min(c), max(c)) for c in clusters]


def detect_columns(
    rows: list[GroupedRow],
    page_width: float,
) -> list[ColumnDefinition]:
    header = next((r for r in rows if r.is_header), None)
    if header:
        return _columns_from_header_row(header)

    numeric_centers: list[float] = []
    text_centers: list[float] = []

    for row in rows:
        if row.is_header or row.is_footer:
            continue
        for span in row.spans:
            xc = span.x + span.width / 2
            from app.ai_engine.patterns import parse_amount

            if parse_amount(span.text) is not None:
                numeric_centers.append(xc)
            else:
                text_centers.append(xc)

    gap = page_width * 0.06
    num_clusters = _cluster_x_positions(numeric_centers, gap)
    text_clusters = _cluster_x_positions(text_centers, gap * 1.5)

    columns: list[ColumnDefinition] = []

    if text_clusters:
        left = text_clusters[0]
        columns.append(
            ColumnDefinition(
                name="description",
                x_min=left[0] - 10,
                x_max=left[1] + page_width * 0.35,
                x_center=(left[0] + left[1]) / 2,
            )
        )
        if len(text_clusters) > 0:
            date_cluster = text_clusters[0]
            columns.insert(
                0,
                ColumnDefinition(
                    name="date",
                    x_min=0,
                    x_max=date_cluster[1] + 20,
                    x_center=date_cluster[0],
                ),
            )

    if num_clusters:
        num_clusters.sort(key=lambda c: c[0])
        names_from_right = ["balance", "credit", "debit"]
        for i, cluster in enumerate(reversed(num_clusters[-3:])):
            name = names_from_right[i] if i < len(names_from_right) else f"amount_{i}"
            columns.append(
                ColumnDefinition(
                    name=name,
                    x_min=cluster[0] - 15,
                    x_max=cluster[1] + 15,
                    x_center=(cluster[0] + cluster[1]) / 2,
                )
            )

    columns.sort(key=lambda c: c.x_min)
    return _dedupe_columns(columns)


def _columns_from_header_row(header: GroupedRow) -> list[ColumnDefinition]:
    columns: list[ColumnDefinition] = []
    for span in sorted(header.spans, key=lambda s: s.x):
        label = span.text.strip().lower()
        matched = None
        for col_name, aliases in COLUMN_ALIASES.items():
            if any(a in label for a in aliases):
                matched = col_name
                break
        if matched:
            columns.append(
                ColumnDefinition(
                    name=matched,
                    x_min=span.x - 8,
                    x_max=span.x + span.width + 80,
                    x_center=span.x + span.width / 2,
                )
            )

    columns.sort(key=lambda c: c.x_min)
    return _expand_column_boundaries(columns, header)


def _expand_column_boundaries(
    columns: list[ColumnDefinition], header: GroupedRow
) -> list[ColumnDefinition]:
    if not columns:
        return columns
    page_right = max(s.x + s.width for s in header.spans) + 200
    expanded: list[ColumnDefinition] = []
    for i, col in enumerate(columns):
        x_max = columns[i + 1].x_min if i + 1 < len(columns) else page_right
        expanded.append(
            ColumnDefinition(
                name=col.name,
                x_min=col.x_min,
                x_max=x_max,
                x_center=col.x_center,
            )
        )
    return expanded


def _dedupe_columns(columns: list[ColumnDefinition]) -> list[ColumnDefinition]:
    seen: set[str] = set()
    out: list[ColumnDefinition] = []
    for col in columns:
        if col.name in seen:
            continue
        seen.add(col.name)
        out.append(col)
    return out


