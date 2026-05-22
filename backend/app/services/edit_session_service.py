"""
Edit session management — in-memory + Redis-backed sessions.
Original PDF untouched until export (Phase 5).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database.redis_client import get_redis
from app.financial_engine.audit_engine import AuditStack, apply_patches, create_inverse_patches
from app.financial_engine.models import (
    AuditRecord,
    ChangeType,
    EditOperation,
    EditSessionState,
    LedgerEntry,
)
from app.financial_engine.recalculator import FinancialRecalculator, parse_decimal_input
from app.models import EditHistory
from app.services.transaction_service import TransactionService
from app.utils.logging import get_logger

logger = get_logger(__name__)

SESSION_TTL_SECONDS = 86400
SESSION_KEY_PREFIX = "edit_session:"

_memory_sessions: dict[str, _SessionBundle] = {}


@dataclass
class _SessionBundle:
    session_id: str
    statement_id: uuid.UUID
    bank: str
    recalculator: FinancialRecalculator
    audit: AuditStack = field(default_factory=AuditStack)
    last_traces: list = field(default_factory=list)


class EditSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.txn_service = TransactionService(db)

    def start_session(self, statement_id: uuid.UUID) -> str:
        parse_result, _ = self.txn_service.parse_transactions(statement_id)
        opening = parse_result.summary.opening_balance

        entries = [LedgerEntry.from_structured(t) for t in parse_result.transactions]
        from app.financial_engine.propagation_engine import propagate_balances

        recalculator = FinancialRecalculator(entries, opening)
        propagate_balances(recalculator.entries, 0, opening, mark_affected=False)

        session_id = str(uuid.uuid4())
        bundle = _SessionBundle(
            session_id=session_id,
            statement_id=statement_id,
            bank=parse_result.bank,
            recalculator=recalculator,
        )
        _memory_sessions[session_id] = bundle
        self._persist_session(bundle)
        logger.info("edit_session_started", session_id=session_id, statement_id=str(statement_id))
        return session_id

    def get_state(self, session_id: str, *, include_debug: bool = False) -> EditSessionState:
        bundle = self._load_bundle(session_id)
        return self._build_state(bundle, include_debug=include_debug)

    def update_transaction(
        self,
        session_id: str,
        transaction_id: str,
        field: ChangeType,
        value: str | None,
    ) -> EditSessionState:
        bundle = self._load_bundle(session_id)

        if field in (ChangeType.DEBIT, ChangeType.CREDIT, ChangeType.BALANCE):
            parse_decimal_input(value)

        patches, traces = bundle.recalculator.update_field(transaction_id, field, value)
        inverse = create_inverse_patches(patches)

        operation = EditOperation(
            patches=patches,
            inverse_patches=inverse,
            description=f"Update {field.value} on {transaction_id}",
        )
        audit = AuditRecord(
            operation_id=operation.operation_id,
            action="update",
            patches=patches,
            propagation_traces=traces,
        )
        bundle.audit.push(operation, audit)
        bundle.last_traces = traces
        self._persist_session(bundle)
        return self._build_state(bundle)

    def undo(self, session_id: str) -> EditSessionState:
        bundle = self._load_bundle(session_id)
        op = bundle.audit.undo()
        if not op:
            raise ValueError("Nothing to undo")
        apply_patches(bundle.recalculator.entries, op.inverse_patches)
        from app.financial_engine.propagation_engine import propagate_balances

        propagate_balances(bundle.recalculator.entries, 0, bundle.recalculator.opening_balance)
        bundle.last_traces = []
        self._persist_session(bundle)
        return self._build_state(bundle)

    def redo(self, session_id: str) -> EditSessionState:
        bundle = self._load_bundle(session_id)
        op = bundle.audit.redo()
        if not op:
            raise ValueError("Nothing to redo")
        apply_patches(bundle.recalculator.entries, op.patches)
        from app.financial_engine.propagation_engine import propagate_balances

        propagate_balances(bundle.recalculator.entries, 0, bundle.recalculator.opening_balance)
        bundle.last_traces = []
        self._persist_session(bundle)
        return self._build_state(bundle)

    def commit(self, session_id: str, notes: str | None = None) -> EditSessionState:
        bundle = self._load_bundle(session_id)
        from app.services.statement_service import StatementService

        statement = StatementService(self.db).get_by_id(bundle.statement_id)
        if not statement:
            raise ValueError("Statement not found")

        summary = bundle.recalculator.get_summary()
        valid, issues = bundle.recalculator.validate()

        meta = statement.metadata_json or {}
        meta["committed_edit_session"] = {
            "session_id": session_id,
            "committed_at": datetime.now(timezone.utc).isoformat(),
            "entries": [e.model_dump(mode="json") for e in bundle.recalculator.entries],
            "summary": summary.model_dump(mode="json"),
            "validation_passed": valid,
        }
        statement.metadata_json = meta
        statement.opening_balance = summary.opening_balance
        statement.closing_balance = summary.closing_balance

        modified = [e for e in bundle.recalculator.entries if e.is_modified or e.propagation_affected]
        for entry in modified:
            self.db.add(
                EditHistory(
                    statement_id=bundle.statement_id,
                    version=statement.version,
                    action="financial_edit",
                    field_changed="ledger",
                    old_value=str(entry.original_balance),
                    new_value=str(entry.balance),
                    change_payload=entry.model_dump(mode="json"),
                    notes=notes,
                )
            )
        statement.version += 1
        self.db.commit()

        logger.info("edit_session_committed", session_id=session_id)
        return self._build_state(bundle)

    def _build_state(self, bundle: _SessionBundle, include_debug: bool = False) -> EditSessionState:
        summary = bundle.recalculator.get_summary()
        valid, issues = bundle.recalculator.validate()
        modified_count = sum(
            1 for e in bundle.recalculator.entries if e.is_modified or e.propagation_affected
        )

        state = EditSessionState(
            session_id=bundle.session_id,
            statement_id=str(bundle.statement_id),
            bank=bundle.bank,
            entries=bundle.recalculator.entries,
            graph=bundle.recalculator.graph,
            summary=summary,
            opening_balance=bundle.recalculator.opening_balance,
            validation_passed=valid,
            validation_issues=issues,
            modified_count=modified_count,
            can_undo=bundle.audit.can_undo,
            can_redo=bundle.audit.can_redo,
            propagation_trace=bundle.last_traces,
        )
        return state

    def _load_bundle(self, session_id: str) -> _SessionBundle:
        if session_id in _memory_sessions:
            return _memory_sessions[session_id]
        try:
            redis = get_redis()
            raw = redis.get(f"{SESSION_KEY_PREFIX}{session_id}")
            if raw:
                data = json.loads(raw)
                entries = [LedgerEntry.model_validate(e) for e in data["entries"]]
                opening = Decimal(data["opening_balance"]) if data.get("opening_balance") else None
                recalculator = FinancialRecalculator(entries, opening)
                bundle = _SessionBundle(
                    session_id=session_id,
                    statement_id=uuid.UUID(data["statement_id"]),
                    bank=data.get("bank", "UNKNOWN"),
                    recalculator=recalculator,
                )
                _memory_sessions[session_id] = bundle
                return bundle
        except Exception as exc:
            logger.warning("redis_session_load_failed", error=str(exc))
        raise ValueError("Edit session not found or expired")

    def _persist_session(self, bundle: _SessionBundle) -> None:
        payload = {
            "statement_id": str(bundle.statement_id),
            "bank": bundle.bank,
            "opening_balance": str(bundle.recalculator.opening_balance)
            if bundle.recalculator.opening_balance
            else None,
            "entries": [e.model_dump(mode="json") for e in bundle.recalculator.entries],
        }
        try:
            redis = get_redis()
            redis.setex(
                f"{SESSION_KEY_PREFIX}{bundle.session_id}",
                SESSION_TTL_SECONDS,
                json.dumps(payload),
            )
        except Exception as exc:
            logger.warning("redis_session_persist_failed", error=str(exc))
