"""Statistical and pattern-based anomaly detection."""

from __future__ import annotations

import statistics
from decimal import Decimal

from app.shared.models import StructuredTransaction
from app.ai_intelligence.embeddings_engine import EmbeddingsIndex
from app.ai_intelligence.models import AnomalyFlag


def _to_float(val: Decimal | None) -> float | None:
    if val is None:
        return None
    return float(val)


def detect_anomalies(
    transactions: list[StructuredTransaction],
    *,
    embeddings_index: EmbeddingsIndex | None = None,
) -> list[AnomalyFlag]:
    flags: list[AnomalyFlag] = []
    if not transactions:
        return flags

    debits = [_to_float(t.debit) for t in transactions if _to_float(t.debit)]
    credits = [_to_float(t.credit) for t in transactions if _to_float(t.credit)]

    if len(debits) >= 4:
        mean_d = statistics.mean(debits)
        stdev_d = statistics.stdev(debits) or 1.0
        for txn in transactions:
            d = _to_float(txn.debit)
            if d is None:
                continue
            z = (d - mean_d) / stdev_d
            if abs(z) > 2.5:
                flags.append(
                    AnomalyFlag(
                        transaction_id=txn.transaction_id,
                        anomaly_type="amount_spike",
                        severity="high" if abs(z) > 3.5 else "medium",
                        message=f"Unusual debit amount (z={z:.1f})",
                        score=min(0.99, abs(z) / 5),
                        details={"z_score": round(z, 2), "amount": d},
                    )
                )

    for txn in transactions:
        d = _to_float(txn.debit)
        c = _to_float(txn.credit)
        if d and d > 500_000:
            flags.append(
                AnomalyFlag(
                    transaction_id=txn.transaction_id,
                    anomaly_type="large_withdrawal",
                    severity="high",
                    message="Very large withdrawal detected",
                    score=0.85,
                    details={"debit": d},
                )
            )

    balances = []
    for txn in transactions:
        b = _to_float(txn.balance)
        if b is not None:
            balances.append((txn.transaction_id, b, txn.row_index))

    for i in range(1, len(balances)):
        _, prev_b, _ = balances[i - 1]
        cur_id, cur_b, _ = balances[i]
        delta = abs(cur_b - prev_b)
        if delta > 500_000:
            flags.append(
                AnomalyFlag(
                    transaction_id=cur_id,
                    anomaly_type="balance_jump",
                    severity="high" if delta > 1_000_000 else "medium",
                    message=f"Large balance step ({delta:,.0f}) vs previous row",
                    score=0.7,
                    details={"delta": delta, "previous": prev_b, "current": cur_b},
                )
            )

    index = embeddings_index if embeddings_index is not None else EmbeddingsIndex(transactions)
    for id_a, id_b, sim in index.find_duplicates(0.95):
        flags.append(
            AnomalyFlag(
                transaction_id=id_a,
                anomaly_type="duplicate_transaction",
                severity="medium",
                message=f"Possible duplicate of another row (similarity {sim})",
                score=sim,
                details={"duplicate_of": id_b},
            )
        )

    desc_counts: dict[str, int] = {}
    for txn in transactions:
        key = (txn.description or "").strip().upper()[:40]
        if key:
            desc_counts[key] = desc_counts.get(key, 0) + 1
    flagged_patterns: set[str] = set()
    for txn in transactions:
        key = (txn.description or "").strip().upper()[:40]
        if not key or desc_counts.get(key, 0) < 5 or key in flagged_patterns:
            continue
        flagged_patterns.add(key)
        flags.append(
            AnomalyFlag(
                transaction_id=txn.transaction_id,
                anomaly_type="repeated_pattern",
                severity="low",
                message=f"Repeated description pattern ({desc_counts[key]}x)",
                score=0.5,
                details={"pattern": key, "count": desc_counts[key]},
            )
        )

    return flags
