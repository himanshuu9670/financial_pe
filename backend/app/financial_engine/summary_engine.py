"""Ledger summary computation with memoization-friendly pure functions."""

from __future__ import annotations

from decimal import Decimal

from app.ai_engine.models import TransactionSummary
from app.financial_engine.models import LedgerEntry


def compute_summary(entries: list[LedgerEntry]) -> TransactionSummary:
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    opening: Decimal | None = None
    closing: Decimal | None = None

    sorted_entries = sorted(entries, key=lambda e: (e.page, e.row_index))

    for i, entry in enumerate(sorted_entries):
        if entry.debit:
            total_debit += entry.debit
        if entry.credit:
            total_credit += entry.credit
        if entry.balance is not None:
            if opening is None:
                if entry.previous_balance is not None:
                    opening = entry.previous_balance
                elif i == 0:
                    opening = _infer_opening(entry)
            closing = entry.balance

    return TransactionSummary(
        total_debit=total_debit,
        total_credit=total_credit,
        opening_balance=opening,
        closing_balance=closing,
        transaction_count=len(sorted_entries),
    )


def _infer_opening(entry: LedgerEntry) -> Decimal | None:
    if entry.balance is None:
        return None
    bal = entry.balance
    if entry.debit:
        bal += entry.debit
    if entry.credit:
        bal -= entry.credit
    return bal
