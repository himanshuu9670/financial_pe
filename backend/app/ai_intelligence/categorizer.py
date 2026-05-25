"""Transaction categorization — semantic + keyword scoring."""

from __future__ import annotations

from decimal import Decimal

from app.shared.models import StructuredTransaction
from app.ai_intelligence.models import CategoryResult
from app.ai_intelligence.semantic_parser import parse_semantic


def categorize_transactions(transactions: list[StructuredTransaction]) -> list[CategoryResult]:
    results: list[CategoryResult] = []
    for txn in transactions:
        sem = parse_semantic(txn.description)
        cat = sem["category_hint"]
        conf = sem["category_confidence"]

        if txn.credit and (txn.debit is None or txn.debit == 0):
            if cat == "Other" and sem["payment_intent"] == "income":
                cat = "Salary"
                conf = max(conf, 0.75)

        results.append(
            CategoryResult(
                transaction_id=txn.transaction_id,
                description=txn.description,
                category=cat,
                confidence=round(conf, 2),
                signals=sem.get("matched_keywords", [])[:5],
            )
        )
    return results
