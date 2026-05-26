"""
Financial validation — balance chain integrity and ledger consistency.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.config import get_settings
from app.shared.models import StructuredTransaction, TransactionSummary
from app.financial_engine.models import LedgerEntry

TOLERANCE = Decimal("0.02")


def validate_transactions(
    transactions: list[StructuredTransaction],
) -> tuple[TransactionSummary, list[str]]:
    entries = [LedgerEntry.from_structured(t) for t in transactions]
    issues = validate_ledger_entries(entries, None)
    from app.financial_engine.summary_engine import compute_summary

    summary = compute_summary(entries)
    summary.validation_passed = len(issues) == 0
    summary.validation_issues = issues
    for t, e in zip(transactions, entries):
        t.validation_warnings = e.validation_warnings
    return summary, issues


def validate_ledger(
    entries: list[LedgerEntry],
    opening_balance: Decimal | None = None,
) -> tuple[bool, list[str]]:
    issues = validate_ledger_entries(entries, opening_balance)
    return len(issues) == 0, issues


def validate_ledger_entries(
    entries: list[LedgerEntry],
    opening_balance: Decimal | None = None,
) -> list[str]:
    issues: list[str] = []
    settings = get_settings()
    max_transaction_amount = settings.max_transaction_amount
    max_negative_balance = settings.max_negative_balance
    max_balance_delta = settings.max_balance_delta

    sorted_entries = sorted(entries, key=lambda e: (e.page, e.row_index))
    prev_balance = opening_balance

    for entry in sorted_entries:
        entry.validation_warnings.clear()

        if entry.debit and entry.debit < 0:
            issues.append(f"Row {entry.row_index}: negative debit")
            entry.validation_warnings.append("Negative debit")

        if entry.credit and entry.credit < 0:
            issues.append(f"Row {entry.row_index}: negative credit")
            entry.validation_warnings.append("Negative credit")

        if entry.balance is not None and entry.balance < 0:
            entry.validation_warnings.append("Negative balance")

        if entry.is_modified:
            if entry.debit is not None and abs(entry.debit) > max_transaction_amount:
                msg = (
                    f"Row {entry.row_index}: edited amount exceeds safe transaction threshold"
                )
                issues.append(msg)
                entry.validation_warnings.append(msg)

            if entry.credit is not None and abs(entry.credit) > max_transaction_amount:
                msg = (
                    f"Row {entry.row_index}: edited amount exceeds safe transaction threshold"
                )
                issues.append(msg)
                entry.validation_warnings.append(msg)

            if entry.balance is not None and entry.balance < max_negative_balance:
                msg = (
                    f"Row {entry.row_index}: edited balance underflow exceeds allowed threshold"
                )
                issues.append(msg)
                entry.validation_warnings.append(msg)

            if entry.debit is not None and entry.original_debit is not None:
                if abs(entry.debit - entry.original_debit) > max_balance_delta:
                    msg = (
                        f"Row {entry.row_index}: transaction change produces abnormal ledger propagation"
                    )
                    issues.append(msg)
                    entry.validation_warnings.append(msg)

            if entry.credit is not None and entry.original_credit is not None:
                if abs(entry.credit - entry.original_credit) > max_balance_delta:
                    msg = (
                        f"Row {entry.row_index}: transaction change produces abnormal ledger propagation"
                    )
                    issues.append(msg)
                    entry.validation_warnings.append(msg)

            if entry.balance is not None and entry.original_balance is not None:
                if abs(entry.balance - entry.original_balance) > max_balance_delta:
                    msg = (
                        f"Row {entry.row_index}: resulting balances appear unrealistic"
                    )
                    issues.append(msg)
                    entry.validation_warnings.append(msg)

        if prev_balance is not None and entry.balance is not None:
            if entry.debit or entry.credit:
                expected = prev_balance
                if entry.debit:
                    expected -= entry.debit
                if entry.credit:
                    expected += entry.credit
                diff = abs(expected - entry.balance)
                if diff > TOLERANCE:
                    if diff > max_balance_delta:
                        msg = (
                            f"Row {entry.row_index}: abnormal ledger propagation "
                            f"(delta {diff} exceeds safe threshold)"
                        )
                    else:
                        msg = (
                            f"Row {entry.row_index}: balance mismatch "
                            f"(expected {expected}, got {entry.balance})"
                        )
                    issues.append(msg)
                    entry.validation_warnings.append(msg)

        if entry.balance is not None:
            prev_balance = entry.balance
        elif entry.debit or entry.credit:
            entry.validation_warnings.append("Missing running balance")

    return issues
