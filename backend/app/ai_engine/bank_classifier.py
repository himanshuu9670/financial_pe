"""
Bank layout classifier — keyword + layout signature analysis.
Extensible registry; not hardcoded per-bank coordinate templates.
"""

from __future__ import annotations

from app.ai_engine.models import BankClassification
from app.pdf_engine.models import DocumentExtraction

BANK_SIGNATURES: dict[str, list[str]] = {
    "YES_BANK": [
        "yes bank",
        "yesbank",
        "yes bank limited",
    ],
    "AXIS_BANK": [
        "axis bank",
        "axis bank ltd",
        "utib",
    ],
    "CANARA_BANK": [
        "canara bank",
        "canara bank ltd",
    ],
}

HEADER_KEYWORDS = {
    "YES_BANK": ["transaction date", "cheque", "withdrawal", "deposit", "balance"],
    "AXIS_BANK": ["tran date", "chq", "withdrawal", "deposit", "balance", "particulars"],
    "CANARA_BANK": ["txn date", "description", "debit", "credit", "balance"],
}


def classify_bank(document: DocumentExtraction) -> BankClassification:
    full_text = " ".join(
        block.text.lower()
        for page in document.pages
        for block in page.blocks
    )

    scores: dict[str, float] = {}
    signals: dict[str, list[str]] = {}

    for bank, keywords in BANK_SIGNATURES.items():
        hit = 0
        bank_signals: list[str] = []
        for kw in keywords:
            if kw in full_text:
                hit += 1
                bank_signals.append(f"keyword:{kw}")
        header_hits = sum(1 for h in HEADER_KEYWORDS.get(bank, []) if h in full_text)
        if header_hits:
            hit += header_hits * 0.5
            bank_signals.append(f"headers:{header_hits}")

        scores[bank] = hit
        signals[bank] = bank_signals

    if not scores or max(scores.values()) == 0:
        return BankClassification(bank="UNKNOWN", confidence=0.0, signals=["no_bank_match"])

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values()) or 1
    confidence = min(0.99, round(scores[best] / total + 0.3, 2))

    return BankClassification(
        bank=best,
        confidence=confidence,
        signals=signals.get(best, []),
    )
