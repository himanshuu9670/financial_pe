"""Undo/redo stacks and audit trail for edit sessions."""

from __future__ import annotations

from copy import deepcopy

from app.financial_engine.models import AuditRecord, EditOperation, LedgerEntry, TransactionPatch


class AuditStack:
    def __init__(self) -> None:
        self.undo_stack: list[EditOperation] = []
        self.redo_stack: list[EditOperation] = []
        self.audit_log: list[AuditRecord] = []

    def push(self, operation: EditOperation, audit: AuditRecord) -> None:
        self.undo_stack.append(operation)
        self.redo_stack.clear()
        self.audit_log.append(audit)

    def undo(self) -> EditOperation | None:
        if not self.undo_stack:
            return None
        op = self.undo_stack.pop()
        self.redo_stack.append(op)
        return op

    def redo(self) -> EditOperation | None:
        if not self.redo_stack:
            return None
        op = self.redo_stack.pop()
        self.undo_stack.append(op)
        return op

    @property
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0


def snapshot_entries(entries: list[LedgerEntry]) -> list[LedgerEntry]:
    return [e.model_copy(deep=True) for e in entries]


def apply_patches(entries: list[LedgerEntry], patches: list[TransactionPatch]) -> None:
    by_id = {e.transaction_id: e for e in entries}
    for patch in patches:
        entry = by_id.get(patch.transaction_id)
        if not entry:
            continue
        _apply_patch_to_entry(entry, patch)


def _apply_patch_to_entry(entry: LedgerEntry, patch: TransactionPatch) -> None:
    from app.financial_engine.models import ChangeType
    from decimal import Decimal, InvalidOperation

    field = patch.field
    val = patch.new_value

    if field == ChangeType.DEBIT:
        entry.debit = _to_decimal(val)
    elif field == ChangeType.CREDIT:
        entry.credit = _to_decimal(val)
    elif field == ChangeType.BALANCE:
        entry.balance = _to_decimal(val)
    elif field == ChangeType.DESCRIPTION:
        entry.description = val or ""
    elif field == ChangeType.DATE:
        entry.date = val


def _to_decimal(val: str | None) -> Decimal | None:
    if val is None or val == "":
        return None
    from decimal import Decimal, InvalidOperation

    try:
        return Decimal(str(val).replace(",", ""))
    except InvalidOperation:
        return None


def create_inverse_patches(patches: list[TransactionPatch]) -> list[TransactionPatch]:
    return [
        TransactionPatch(
            transaction_id=p.transaction_id,
            field=p.field,
            old_value=p.new_value,
            new_value=p.old_value,
        )
        for p in patches
    ]
