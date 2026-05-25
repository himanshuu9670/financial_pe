"""Financial engine edge cases — long chains, undo, invalid edits."""

from decimal import Decimal

from app.financial_engine.audit_engine import apply_patches, create_inverse_patches
from app.financial_engine.models import ChangeType, LedgerEntry, TransactionPatch
from app.financial_engine.propagation_engine import propagate_balances
from app.financial_engine.recalculator import FinancialRecalculator
from app.financial_engine.validator import validate_ledger


def _entry(tid: str, idx: int, debit: str | None, credit: str | None, balance: str) -> LedgerEntry:
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


def test_long_propagation_chain_50_rows():
    opening = Decimal("1000000")
    entries = []
    balance = opening
    for i in range(50):
        debit = Decimal("10")
        balance -= debit
        entries.append(
            _entry(f"t{i}", i, str(debit), None, str(balance)),
        )
    propagate_balances(entries, 0, opening, mark_affected=False)
    valid, issues = validate_ledger(entries, opening)
    assert valid, issues

    recalc = FinancialRecalculator(entries, opening)
    recalc.update_field("t25", ChangeType.DEBIT, "20")
    valid2, issues2 = validate_ledger(recalc.entries, opening)
    assert valid2, issues2


def test_multiple_sequential_edits_deterministic():
    opening = Decimal("10000")
    entries = [
        _entry("t1", 0, "1000", None, "9000"),
        _entry("t2", 1, "500", None, "8500"),
        _entry("t3", 2, None, "200", "8700"),
    ]
    propagate_balances(entries, 0, opening, mark_affected=False)
    r1 = FinancialRecalculator(entries, opening)
    r1.update_field("t1", ChangeType.DEBIT, "1100")
    r2 = FinancialRecalculator(r1.entries, opening)
    r2.update_field("t2", ChangeType.DEBIT, "600")
    valid, _ = validate_ledger(r2.entries, opening)
    assert valid


def test_undo_restores_prior_debit():
    entry = _entry("t1", 0, "7000", None, "3000")
    patch = TransactionPatch(
        transaction_id="t1",
        field=ChangeType.DEBIT,
        old_value="5000",
        new_value="7000",
    )
    inverse = create_inverse_patches([patch])
    apply_patches([entry], inverse)
    assert entry.debit == Decimal("5000")
