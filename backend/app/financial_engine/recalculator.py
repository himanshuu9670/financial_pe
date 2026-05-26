"""
Financial recalculation orchestrator — edits, propagation, validation, summaries.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.core.config import get_settings
from app.financial_engine.audit_engine import apply_patches, create_inverse_patches
from app.financial_engine.dependency_graph import build_dependency_graph, index_of
from app.financial_engine.models import (
    ChangeType,
    EditOperation,
    LedgerEntry,
    PropagationTrace,
    TransactionPatch,
)
from app.financial_engine.propagation_engine import propagate_balances
from app.financial_engine.summary_engine import compute_summary
from app.financial_engine.validator import validate_ledger


class FinancialRecalculator:
    def __init__(self, entries: list[LedgerEntry], opening_balance: Decimal | None = None) -> None:
        self.entries = sorted(entries, key=lambda e: (e.page, e.row_index))
        self.opening_balance = opening_balance
        self.graph = build_dependency_graph(self.entries, opening_balance)

    def update_field(
        self,
        transaction_id: str,
        field: ChangeType,
        new_value: str | None,
    ) -> tuple[list[TransactionPatch], list[PropagationTrace]]:
        entry = self._get_entry(transaction_id)
        idx = index_of(self.graph, transaction_id)

        patch = TransactionPatch(
            transaction_id=transaction_id,
            field=field,
            old_value=self._field_value(entry, field),
            new_value=new_value,
        )

        if field in (ChangeType.DEBIT, ChangeType.CREDIT, ChangeType.BALANCE):
            new_value_decimal = parse_decimal_input(new_value)
            if new_value_decimal is not None:
                self._validate_transaction_change(entry, field, new_value_decimal)

        apply_patches(self.entries, [patch])
        entry.is_modified = True
        entry.propagation_affected = False

        traces: list[PropagationTrace] = []
        if field in (ChangeType.DEBIT, ChangeType.CREDIT, ChangeType.BALANCE):
            traces = propagate_balances(self.entries, 0, self.opening_balance)

        return [patch], traces

    def delete_transaction(self, transaction_id: str) -> list[TransactionPatch]:
        idx = index_of(self.graph, transaction_id)
        entry = self.entries[idx]
        patch = TransactionPatch(
            transaction_id=transaction_id,
            field=ChangeType.DELETE,
            old_value=entry.model_dump_json(),
            new_value=None,
        )
        self.entries.pop(idx)
        self.graph = build_dependency_graph(self.entries, self.opening_balance)
        propagate_balances(self.entries, 0, self.opening_balance)
        return [patch]

    def get_summary(self):
        return compute_summary(self.entries)

    def validate(self) -> tuple[bool, list[str]]:
        return validate_ledger(self.entries, self.opening_balance)

    def _get_entry(self, transaction_id: str) -> LedgerEntry:
        for e in self.entries:
            if e.transaction_id == transaction_id:
                return e
        raise KeyError(transaction_id)

    @staticmethod
    def _field_value(entry: LedgerEntry, field: ChangeType) -> str | None:
        if field == ChangeType.DEBIT:
            return str(entry.debit) if entry.debit is not None else None
        if field == ChangeType.CREDIT:
            return str(entry.credit) if entry.credit is not None else None
        if field == ChangeType.BALANCE:
            return str(entry.balance) if entry.balance is not None else None
        if field == ChangeType.DESCRIPTION:
            return entry.description
        if field == ChangeType.DATE:
            return entry.date
        return None

    @staticmethod
    def _validate_transaction_change(
        entry: LedgerEntry,
        field: ChangeType,
        new_value: Decimal,
    ) -> None:
        settings = get_settings()
        max_transaction_amount = settings.max_transaction_amount
        max_negative_balance = settings.max_negative_balance
        max_balance_delta = settings.max_balance_delta

        if field in (ChangeType.DEBIT, ChangeType.CREDIT):
            if abs(new_value) > max_transaction_amount:
                raise ValueError(
                    "Edited amount exceeds safe transaction threshold"
                )
            original_value = entry.original_debit if field == ChangeType.DEBIT else entry.original_credit
            if original_value is not None and abs(new_value - original_value) > max_balance_delta:
                raise ValueError(
                    "Transaction change produces abnormal ledger propagation"
                )

        if field == ChangeType.BALANCE:
            if new_value < max_negative_balance:
                raise ValueError(
                    "Edited balance underflow exceeds allowed threshold"
                )
            if entry.original_balance is not None and abs(new_value - entry.original_balance) > max_balance_delta:
                raise ValueError(
                    "Resulting balances appear unrealistic"
                )


def parse_decimal_input(value: str | None) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {value}") from exc
