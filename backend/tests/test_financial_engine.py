"""Financial engine unit tests — propagation, validation, undo semantics."""

from decimal import Decimal

import pytest

from app.financial_engine.audit_engine import apply_patches, create_inverse_patches
from app.financial_engine.models import ChangeType, LedgerEntry, TransactionPatch
from app.financial_engine.propagation_engine import propagate_balances
from app.financial_engine.recalculator import FinancialRecalculator
from app.financial_engine.validator import validate_ledger


def _entry(
    tid: str,
    idx: int,
    debit: str | None,
    credit: str | None,
    balance: str,
) -> LedgerEntry:
    return LedgerEntry(
        transaction_id=tid,
        row_index=idx,
        page=1,
        debit=Decimal(debit) if debit else None,
        credit=Decimal(credit) if credit else None,
        balance=Decimal(balance),
        original_debit=Decimal(debit) if debit else None,
        original_balance=Decimal(balance),
    )


def test_debit_edit_propagates_downstream():
    entries = [
        _entry("t1", 0, "5000", None, "5000"),
        _entry("t2", 1, "1000", None, "4000"),
        _entry("t3", 2, None, "500", "4500"),
    ]
    opening = Decimal("10000")
    recalc = FinancialRecalculator(entries, opening)
    propagate_balances(recalc.entries, 0, opening, mark_affected=False)

    patches, traces = recalc.update_field("t1", ChangeType.DEBIT, "7000")

    assert recalc.entries[0].debit == Decimal("7000")
    assert recalc.entries[0].balance == Decimal("3000")
    assert recalc.entries[1].balance == Decimal("2000")
    assert recalc.entries[2].balance == Decimal("2500")
    assert len(traces) >= 2


def test_rejects_huge_transaction_edit():
    entries = [
        _entry("t1", 0, "5000", None, "5000"),
        _entry("t2", 1, "1000", None, "4000"),
    ]
    opening = Decimal("10000")
    recalc = FinancialRecalculator(entries, opening)
    propagate_balances(recalc.entries, 0, opening, mark_affected=False)

    with pytest.raises(ValueError, match="Edited amount exceeds safe transaction threshold"):
        recalc.update_field("t1", ChangeType.DEBIT, "1000000000")


def test_balance_chain_validation():
    entries = [
        _entry("t1", 0, "5000", None, "5000"),
        _entry("t2", 1, "1000", None, "4000"),
    ]
    opening = Decimal("10000")
    propagate_balances(entries, 0, opening, mark_affected=False)
    valid, issues = validate_ledger(entries, opening)
    assert valid
    assert not issues


def test_balance_mismatch_detected():
    entries = [
        _entry("t1", 0, "5000", None, "9999"),
    ]
    opening = Decimal("10000")
    valid, issues = validate_ledger(entries, opening)
    assert not valid
    assert len(issues) > 0


def test_strict_row_by_row_balance_recalculation_with_skipped_rows():
    entries = [
        _entry("t1", 0, "1000", None, "9000"),
        LedgerEntry(transaction_id="blank", row_index=1, page=1),
        _entry("t2", 2, "500", None, "8500"),
    ]
    opening = Decimal("10000")
    propagate_balances(entries, 0, opening, mark_affected=False)

    recalc = FinancialRecalculator(entries, opening)
    recalc.update_field("t1", ChangeType.DEBIT, "1100")

    assert recalc.entries[0].balance == Decimal("8900")
    assert recalc.entries[2].balance == Decimal("8400")


def test_balance_edit_recalculates_from_opening_balance():
    entries = [
        _entry("t1", 0, "1000", None, "9000"),
        _entry("t2", 1, None, "500", "9500"),
    ]
    opening = Decimal("10000")
    recalc = FinancialRecalculator(entries, opening)

    _, traces = recalc.update_field("t1", ChangeType.BALANCE, "9500")

    assert recalc.entries[0].balance == Decimal("9000")
    assert recalc.entries[1].balance == Decimal("9500")
    assert len(traces) == 1


def test_undo_inverse_patches():
    entry = _entry("t1", 0, "5000", None, "5000")
    patch = TransactionPatch(
        transaction_id="t1",
        field=ChangeType.DEBIT,
        old_value="5000",
        new_value="7000",
    )
    apply_patches([entry], [patch])
    assert entry.debit == Decimal("7000")

    inverse = create_inverse_patches([patch])
    apply_patches([entry], inverse)
    assert entry.debit == Decimal("5000")
