"""PDF export engine tests — typography formatting and target collection."""

from decimal import Decimal

from app.shared.models import FieldCoordinate, TransactionCoordinates
from app.financial_engine.models import LedgerEntry
from app.pdf_engine.editor import collect_targets_from_ledger
from app.pdf_engine.export_engine import PdfExportEngine
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


def test_format_amount_preserves_grouping():
    assert format_amount_for_pdf(Decimal("7000"), "5,000.00") == "7,000.00"


def test_collect_targets_on_debit_change():
    entry = LedgerEntry(
        transaction_id="t1",
        row_index=0,
        page=1,
        debit=Decimal("7000"),
        original_debit=Decimal("5000"),
        balance=Decimal("3000"),
        original_balance=Decimal("5000"),
        is_modified=True,
        coordinates=TransactionCoordinates(
            debit=_coord("5,000.00", [400, 100, 480, 112]),
        ),
    )
    targets = collect_targets_from_ledger([entry])
    assert len(targets) == 1
    assert targets[0].new_text == "7,000.00"
    assert targets[0].field == "debit"
    assert targets[0].field_id == entry.coordinates.debit.field_id
    assert targets[0].row_index == entry.row_index


def test_validate_targets_rejects_duplicate_overlay_targets():
    entry = LedgerEntry(
        transaction_id="t1",
        row_index=0,
        page=1,
        debit=Decimal("7000"),
        original_debit=Decimal("5000"),
        balance=Decimal("3000"),
        original_balance=Decimal("5000"),
        is_modified=True,
        coordinates=TransactionCoordinates(
            debit=_coord("5,000.00", [400, 100, 480, 112]),
        ),
    )
    targets = collect_targets_from_ledger([entry])
    targets.append(targets[0])
    engine = PdfExportEngine()

    issues = engine._validate_targets([entry], targets)

    assert any("duplicate_overlay_target" in issue for issue in issues)


def test_validate_targets_rejects_missing_coordinate_targets():
    entry = LedgerEntry(
        transaction_id="t1",
        row_index=0,
        page=1,
        debit=Decimal("7000"),
        original_debit=Decimal("5000"),
        balance=Decimal("3000"),
        original_balance=Decimal("5000"),
        is_modified=True,
    )
    engine = PdfExportEngine()

    issues = engine._validate_targets([entry], [])

    assert any("transaction_overlay_mismatch" in issue for issue in issues)
