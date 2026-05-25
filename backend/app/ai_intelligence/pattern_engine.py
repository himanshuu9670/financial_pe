"""Spending patterns and category aggregates."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from app.ai_intelligence.models import CategoryResult, CategorySpend, SpendingInsight


def _dec(val) -> float:
    if val is None:
        return 0.0
    return float(val)


def analyze_spending(
    categories: list[CategoryResult],
    transactions: list,
) -> tuple[list[CategorySpend], SpendingInsight]:
    by_cat: dict[str, dict] = defaultdict(lambda: {"debit": 0.0, "credit": 0.0, "count": 0})
    cat_map = {c.transaction_id: c.category for c in categories}

    total_debit = 0.0
    largest = 0.0
    debits_list: list[float] = []
    merchant_counts: dict[str, int] = defaultdict(int)

    for txn in transactions:
        cat = cat_map.get(txn.transaction_id, "Other")
        d = _dec(txn.debit)
        c = _dec(txn.credit)
        by_cat[cat]["debit"] += d
        by_cat[cat]["credit"] += c
        by_cat[cat]["count"] += 1
        total_debit += d
        if d > largest:
            largest = d
        if d:
            debits_list.append(d)
        merch = (txn.description or "")[:25].upper()
        if merch:
            merchant_counts[merch] += 1

    spends: list[CategorySpend] = []
    for cat, data in sorted(by_cat.items(), key=lambda x: x[1]["debit"], reverse=True):
        pct = (data["debit"] / total_debit * 100) if total_debit else 0
        spends.append(
            CategorySpend(
                category=cat,
                total_debit=round(data["debit"], 2),
                total_credit=round(data["credit"], 2),
                count=data["count"],
                percent_of_debit=round(pct, 1),
            )
        )

    recurring = [m for m, cnt in merchant_counts.items() if cnt >= 3][:8]
    insight = SpendingInsight(
        top_category=spends[0].category if spends else None,
        largest_debit=round(largest, 2) if largest else None,
        avg_debit=round(sum(debits_list) / len(debits_list), 2) if debits_list else None,
        recurring_merchants=recurring,
    )
    return spends, insight
