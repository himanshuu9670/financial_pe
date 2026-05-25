"""Semantic understanding of transaction descriptions."""

from __future__ import annotations

import re

from app.ai_intelligence.category_registry import CATEGORY_RULES, DEFAULT_CATEGORY


def normalize_merchant(text: str) -> str:
    t = text.upper().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^A-Z0-9\s/\-]", "", t)
    return t


def parse_semantic(description: str) -> dict:
    """Return semantic tags, inferred intent, and category hint."""
    raw = description or ""
    norm = normalize_merchant(raw)
    lower = norm.lower()

    tags: list[str] = []
    if "upi" in lower or re.search(r"/\d{10,}@", lower):
        tags.append("upi_payment")
    if "neft" in lower or "imps" in lower or "rtgs" in lower:
        tags.append("bank_transfer")
    if "pos" in lower or "card" in lower:
        tags.append("card_payment")
    if "salary" in lower or "payroll" in lower:
        tags.append("income")

    best_cat = DEFAULT_CATEGORY
    best_score = 0.0
    matched: list[str] = []
    for category, keywords in CATEGORY_RULES:
        hits = sum(1 for kw in keywords if kw in lower)
        if hits > best_score:
            best_score = hits
            best_cat = category
            matched = [kw for kw in keywords if kw in lower]

    confidence = min(0.99, 0.45 + best_score * 0.15) if best_score else 0.35

    return {
        "normalized": norm,
        "tags": tags,
        "category_hint": best_cat,
        "category_confidence": confidence,
        "matched_keywords": matched,
        "payment_intent": _infer_intent(lower, tags),
    }


def _infer_intent(lower: str, tags: list[str]) -> str:
    if "salary" in lower or "income" in tags:
        return "income"
    if "emi" in lower or "loan" in lower:
        return "debt_service"
    if "upi" in tags:
        return "peer_or_merchant_payment"
    if "atm" in lower:
        return "cash_withdrawal"
    return "expense"
