"""Composite fraud risk scoring from anomalies and behavioral patterns."""

from __future__ import annotations

from datetime import datetime

from app.shared.models import StructuredTransaction
from app.ai_intelligence.models import AnomalyFlag, FraudAssessment


def assess_fraud(
    transactions: list[StructuredTransaction],
    anomalies: list[AnomalyFlag],
) -> FraudAssessment:
    flags: list[str] = []
    score = 0.0

    high = sum(1 for a in anomalies if a.severity == "high")
    medium = sum(1 for a in anomalies if a.severity == "medium")
    score += min(0.4, high * 0.12 + medium * 0.05)

    dupes = sum(1 for a in anomalies if a.anomaly_type == "duplicate_transaction")
    if dupes:
        flags.append(f"{dupes} possible duplicate transaction(s)")
        score += 0.1

    large_wd = sum(1 for a in anomalies if a.anomaly_type == "large_withdrawal")
    if large_wd:
        flags.append("Large withdrawal(s) detected")
        score += 0.15

    rapid = _rapid_succession_count(transactions)
    if rapid >= 3:
        flags.append(f"Rapid transaction burst ({rapid} within short window)")
        score += 0.2

    vendors = {}
    for txn in transactions:
        v = (txn.description or "")[:30].upper()
        vendors[v] = vendors.get(v, 0) + 1
    unusual_vendors = [v for v, c in vendors.items() if c == 1 and len(v) > 5]
    if len(unusual_vendors) > len(transactions) * 0.6 and len(transactions) > 10:
        flags.append("Many one-off vendors — review for unusual activity")
        score += 0.08

    score = round(min(0.99, score), 2)
    level = "low"
    if score >= 0.75:
        level = "critical"
    elif score >= 0.55:
        level = "high"
    elif score >= 0.35:
        level = "medium"

    return FraudAssessment(
        risk_score=score,
        risk_level=level,
        flags=flags,
        anomaly_count=len(anomalies),
    )


def _rapid_succession_count(transactions: list[StructuredTransaction]) -> int:
    dated = []
    for t in transactions:
        if not t.date:
            continue
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
            try:
                dated.append((datetime.strptime(t.date.strip(), fmt), t.transaction_id))
                break
            except ValueError:
                continue
    dated.sort()
    if len(dated) < 3:
        return 0
    burst = 0
    max_burst = 0
    for i in range(1, len(dated)):
        delta = (dated[i][0] - dated[i - 1][0]).total_seconds()
        if delta < 3600:
            burst += 1
            max_burst = max(max_burst, burst)
        else:
            burst = 0
    return max_burst + 1 if max_burst else 0
