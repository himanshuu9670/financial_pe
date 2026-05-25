"""Typography — amount formatting and bbox target collection."""

from decimal import Decimal

from app.shared.models import FieldCoordinate, TransactionCoordinates
from app.financial_engine.models import LedgerEntry
from app.pdf_engine.editor import collect_targets_from_ledger
from app.pdf_engine.typography_engine import format_amount_for_pdf


def _coord(text: str, bbox: list[float]) -> FieldCoordinate:
    return FieldCoordinate(
        text=text,
        x=bbox[0],
        y=bbox[1],
        width=bbox[2] - bbox[0],
        height=bbox[3] - bbox[1],
        bbox=bbox,
        font="Helvetica",
        font_size=10,
    )


def test_amount_grouping_preserved():
    assert format_amount_for_pdf(Decimal("1234567.89"), "1,234,567.89") == "1,234,567.89"


def test_debit_target_bbox_unchanged():
    entry = LedgerEntry(
        transaction_id="t1",
        row_index=0,
        page=1,
        debit=Decimal("7000"),
        original_debit=Decimal("5000"),
        balance=Decimal("3000"),
        is_modified=True,
        coordinates=TransactionCoordinates(
            debit=_coord("5,000.00", [400, 100, 480, 112]),
        ),
    )
    targets = collect_targets_from_ledger([entry])
    assert targets[0].bbox == [400, 100, 480, 112]
    assert targets[0].font == "Helvetica"
