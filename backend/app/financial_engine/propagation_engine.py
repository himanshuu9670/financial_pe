"""
Deterministic downstream balance propagation.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.financial_engine.models import LedgerEntry, PropagationTrace


def _compute_balance(previous: Decimal | None, entry: LedgerEntry) -> Decimal | None:
    if previous is None:
        return entry.balance
    result = previous
    if entry.debit:
        result -= entry.debit
    if entry.credit:
        result += entry.credit
    return result


def propagate_balances(
    entries: list[LedgerEntry],
    start_index: int,
    opening_balance: Decimal | None,
    *,
    mark_affected: bool = True,
) -> list[PropagationTrace]:
    """
    Recalculate running balances from start_index through end of ledger.
    Formula: balance[i] = balance[i-1] - debit[i] + credit[i]
    """
    traces: list[PropagationTrace] = []
    sorted_entries = sorted(entries, key=lambda e: (e.page, e.row_index))

    if start_index < 0 or start_index >= len(sorted_entries):
        return traces

    prev: Decimal | None
    if start_index == 0:
        prev = opening_balance
        if prev is None and sorted_entries[0].balance is not None:
            first = sorted_entries[0]
            if first.debit or first.credit:
                prev = (first.balance or Decimal(0)) + (first.debit or Decimal(0)) - (first.credit or Decimal(0))
            else:
                prev = first.balance
    else:
        prev = sorted_entries[start_index - 1].balance

    for i in range(start_index, len(sorted_entries)):
        entry = sorted_entries[i]
        if entry.debit is None and entry.credit is None and entry.balance is None:
            prev = entry.balance
            continue

        new_balance = _compute_balance(prev, entry)
        if new_balance is not None and entry.balance != new_balance:
            old_str = str(entry.balance) if entry.balance is not None else None
            entry.balance = new_balance
            if mark_affected and i > start_index:
                entry.propagation_affected = True
            traces.append(
                PropagationTrace(
                    transaction_id=entry.transaction_id,
                    field="balance",
                    old_value=old_str,
                    new_value=str(new_balance),
                    reason="downstream_propagation",
                )
            )

        entry.previous_balance = prev
        prev = entry.balance

    return traces
