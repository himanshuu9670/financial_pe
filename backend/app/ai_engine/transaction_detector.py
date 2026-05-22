"""
Coordinate-aware transaction detection — assigns spans to columns and builds rows.
"""

from __future__ import annotations

from decimal import Decimal

from app.ai_engine.column_detector import detect_columns
from app.ai_engine.patterns import looks_like_date, parse_amount
from app.ai_engine.models import (
    ColumnDefinition,
    FieldCoordinate,
    FontMetadata,
    GroupedRow,
    StructuredTransaction,
    TransactionCoordinates,
)
from app.ai_engine.row_grouper import group_spans_into_rows
from app.ai_engine.span_utils import PageSpan, span_to_field_coordinate
from app.pdf_engine.models import TextSpan

def assign_span_to_column(span: TextSpan, columns: list[ColumnDefinition]) -> str | None:
    xc = span.x + span.width / 2
    for col in columns:
        if col.x_min <= xc <= col.x_max:
            return col.name
    nearest = min(columns, key=lambda c: abs(c.x_center - xc), default=None)
    return nearest.name if nearest else None


def _field_from_span(span: TextSpan | None) -> FieldCoordinate | None:
    if not span or not span.text.strip():
        return None
    return FieldCoordinate(**span_to_field_coordinate(span))


def parse_row_to_transaction(
    row: GroupedRow,
    columns: list[ColumnDefinition],
    *,
    global_row_index: int,
) -> StructuredTransaction | None:
    if row.is_header or row.is_footer or not row.spans:
        return None

    by_column: dict[str, list[TextSpan]] = {c.name: [] for c in columns}
    unassigned: list[TextSpan] = []

    for span in row.spans:
        col = assign_span_to_column(span, columns) if columns else None
        if col and col in by_column:
            by_column[col].append(span)
        else:
            unassigned.append(span)

    date_span = _pick_date_span(by_column.get("date", []) + unassigned)
    date_str = date_span.text.strip() if date_span else None

    if not date_str:
        first_tokens = row.text.split()
        if first_tokens and looks_like_date(first_tokens[0]):
            date_str = first_tokens[0]

    desc_spans = by_column.get("description", [])
    if not desc_spans:
        desc_spans = [
            s
            for s in unassigned
            if not looks_like_date(s.text) and not parse_amount(s.text)
        ]
    description = " ".join(s.text.strip() for s in sorted(desc_spans, key=lambda s: s.x)).strip()

    if not description and not date_str:
        numeric_only = all(parse_amount(s.text) for s in row.spans if s.text.strip())
        if numeric_only:
            return None

    debit_span = _pick_amount_span(by_column.get("debit", []))
    credit_span = _pick_amount_span(by_column.get("credit", []))
    balance_span = _pick_amount_span(by_column.get("balance", []))

    if not balance_span:
        right_spans = sorted(
            [s for s in row.spans if parse_amount(s.text)],
            key=lambda s: s.x,
            reverse=True,
        )
        if right_spans:
            balance_span = right_spans[0]
        if len(right_spans) >= 2:
            credit_span = credit_span or right_spans[1]
        if len(right_spans) >= 3:
            debit_span = debit_span or right_spans[2]

    debit = parse_amount(debit_span.text) if debit_span else None
    credit = parse_amount(credit_span.text) if credit_span else None
    balance = parse_amount(balance_span.text) if balance_span else None

    has_financial = debit is not None or credit is not None or balance is not None
    if not has_financial and not date_str:
        return None

    fonts = [s.font for s in row.spans if s.font]
    sizes = [s.font_size for s in row.spans if s.font_size]

    return StructuredTransaction(
        page=row.page,
        row_index=global_row_index,
        date=date_str,
        description=description or row.text[:500],
        debit=debit,
        credit=credit,
        balance=balance,
        coordinates=TransactionCoordinates(
            date=_field_from_span(date_span),
            description=_field_from_span(desc_spans[0]) if desc_spans else None,
            debit=_field_from_span(debit_span),
            credit=_field_from_span(credit_span),
            balance=_field_from_span(balance_span),
        ),
        font_metadata=FontMetadata(
            primary_font=fonts[0] if fonts else "Unknown",
            primary_size=sizes[0] if sizes else 0,
        ),
        row_bbox=row.bbox,
        confidence=0.85 if date_str and has_financial else 0.6,
    )


def _pick_date_span(spans: list[TextSpan]) -> TextSpan | None:
    for s in sorted(spans, key=lambda x: x.x):
        if looks_like_date(s.text.strip()):
            return s
    return spans[0] if spans else None


def _pick_amount_span(spans: list[TextSpan]) -> TextSpan | None:
    candidates = [s for s in spans if parse_amount(s.text)]
    if not candidates:
        return None
    return max(candidates, key=lambda s: len(s.text))


def detect_transactions_on_page(
    page_spans: list[PageSpan],
    page_width: float,
    start_index: int,
) -> tuple[list[StructuredTransaction], list[ColumnDefinition], list[GroupedRow]]:
    rows = group_spans_into_rows(page_spans)
    columns = detect_columns(rows, page_width)
    transactions: list[StructuredTransaction] = []
    idx = start_index

    for row in rows:
        txn = parse_row_to_transaction(row, columns, global_row_index=idx)
        if txn:
            transactions.append(txn)
            idx += 1

    return transactions, columns, rows
