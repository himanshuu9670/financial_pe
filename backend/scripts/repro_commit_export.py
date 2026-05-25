import time
import uuid
import decimal
from datetime import datetime
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Statement
from app.services.edit_session_service import EditSessionService
from app.services.transaction_service import TransactionService
from app.services.pdf_export_service import PdfExportService
from app.financial_engine.models import ChangeType

DB_POLL_SECONDS = 5


def now():
    return datetime.utcnow().isoformat() + "Z"


def dump_meta(db, stmt_id, label):
    stmt = db.get(Statement, stmt_id)
    keys = list((stmt.metadata_json or {}).keys())
    print(f"[{now()}] {label}: stmt_id={stmt_id} keys={keys}")
    try:
        res = db.execute(select(Statement.metadata_json).where(Statement.id == stmt_id)).one()
        print(f"[{now()}] {label} raw_select={res[0]}")
    except Exception as e:
        print(f"[{now()}] {label} raw_select_failed: {e}")


if __name__ == '__main__':
    db = SessionLocal()
    stmt_id = uuid.UUID("d48cec3d-d81c-4d56-b3c0-35c8075befac")

    print(f"[{now()}] START reproduce for statement {stmt_id}")
    dump_meta(db, stmt_id, "initial")

    try:
        parse_result, cached = TransactionService(db).parse_transactions(stmt_id, force_refresh=False)
    except Exception as exc:
        print(f"[{now()}] parse_transactions failed: {exc}")
        db.close()
        raise
    tx_count = len(getattr(parse_result, 'transactions', []) or [])
    print(f"[{now()}] parse_transactions: transactions_count={tx_count} cached={cached}")

    # Pick a transaction to edit
    entry = next((e for e in parse_result.transactions if e.debit is not None), None)
    if not entry:
        print("No suitable transaction found to edit; aborting")
        db.close()
        raise SystemExit(1)

    print(f"[{now()}] picked transaction {entry.transaction_id} debit={entry.debit}")

    # Start session and update
    edit_svc = EditSessionService(db)
    session_id = edit_svc.start_session(stmt_id)
    print(f"[{now()}] started session {session_id}")

    new_value = str(entry.debit + decimal.Decimal('100'))
    state = edit_svc.update_transaction(session_id, entry.transaction_id, ChangeType.DEBIT, new_value)
    print(f"[{now()}] update_transaction modified_count={getattr(state, 'modified_count', None)}")
    dump_meta(db, stmt_id, "after_update")

    # Commit edits
    commit_state = edit_svc.commit(session_id, "repro commit")
    print(f"[{now()}] commit returned modified_count={getattr(commit_state, 'modified_count', None)}")
    dump_meta(db, stmt_id, "after_commit immediate")

    # Poll DB for a short window to catch any delayed writer
    seen_keys = None
    for i in range(DB_POLL_SECONDS):
        stmt_row = db.get(Statement, stmt_id)
        keys = list((stmt_row.metadata_json or {}).keys())
        if seen_keys is None:
            seen_keys = keys
        if keys != seen_keys:
            print(f"[{now()}] metadata changed during poll: keys={keys}")
            seen_keys = keys
        time.sleep(1)

    # Trigger export generation immediately
    pdf_svc = PdfExportService(db)
    print(f"[{now()}] triggering export.apply_edits")
    result, stmt_obj = pdf_svc.apply_edits(stmt_id, session_id=None)
    print(f"[{now()}] export completed replacements_applied={result.replacements_applied}")
    dump_meta(db, stmt_id, "after_export immediate")

    # Final raw select
    dump_meta(db, stmt_id, "final")

    # Extra check: test nested mutation persistence (probe)
    stmt_row = db.get(Statement, stmt_id)
    meta = stmt_row.metadata_json or {}
    meta['__probe_nested_mutation'] = now()
    stmt_row.metadata_json = meta
    db.commit()
    res = db.execute(select(Statement.metadata_json).where(Statement.id == stmt_id)).one()
    print(f"[{now()}] nested_mutation_probe raw_select={res[0]}")

    db.close()
    print(f"[{now()}] DONE")
