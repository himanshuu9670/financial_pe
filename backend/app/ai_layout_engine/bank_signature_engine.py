"""
Multi-bank fingerprinting — keywords, headers, typography patterns.
Extensible registry without per-bank coordinate templates.
"""

from __future__ import annotations

from app.ai_layout_engine.models import BankSignatureMatch
from app.pdf_engine.models import DocumentExtraction

BANK_KEYWORDS: dict[str, list[str]] = {
    "YES_BANK": ["yes bank", "yesbank", "yes bank limited"],
    "AXIS_BANK": ["axis bank", "axis bank ltd", "utib", "axis bank limited"],
    "CANARA_BANK": ["canara bank", "canara bank ltd"],
    "HDFC_BANK": ["hdfc bank", "hdfcbank", "hdfc bank ltd", "housing development"],
    "SBI": ["state bank of india", "sbi", "sbin"],
    "ICICI_BANK": ["icici bank", "icicibank", "icici bank limited"],
    "PNB": ["punjab national bank", "pnb", "punjab national"],
}

HEADER_SIGNATURES: dict[str, list[str]] = {
    "YES_BANK": ["transaction date", "withdrawal", "deposit", "balance", "cheque"],
    "AXIS_BANK": ["tran date", "particulars", "withdrawal", "deposit", "balance", "chq"],
    "CANARA_BANK": ["txn date", "description", "debit", "credit", "balance"],
    "HDFC_BANK": ["date", "narration", "withdrawal", "deposit", "balance"],
    "SBI": ["txn date", "description", "debit", "credit", "balance"],
    "ICICI_BANK": ["value date", "transaction date", "description", "amount", "balance"],
    "PNB": ["date", "particulars", "withdrawal", "deposit", "balance"],
}

LAYOUT_VERSIONS: dict[str, str] = {
    "YES_BANK": "yes_v1",
    "AXIS_BANK": "axis_v2",
    "CANARA_BANK": "canara_v1",
    "HDFC_BANK": "hdfc_v1",
    "SBI": "sbi_v1",
    "ICICI_BANK": "icici_v1",
    "PNB": "pnb_v1",
}


def fingerprint_bank(document: DocumentExtraction) -> BankSignatureMatch:
    full_text = _document_text(document).lower()
    scores: dict[str, float] = {}
    signals: dict[str, list[str]] = {}

    for bank, keywords in BANK_KEYWORDS.items():
        score = 0.0
        bank_signals: list[str] = []
        for kw in keywords:
            if kw in full_text:
                score += 1.0
                bank_signals.append(f"kw:{kw}")

        header_hits = sum(1 for h in HEADER_SIGNATURES.get(bank, []) if h in full_text)
        if header_hits >= 2:
            score += header_hits * 0.6
            bank_signals.append(f"headers:{header_hits}")

        scores[bank] = score
        signals[bank] = bank_signals

    if not scores or max(scores.values()) <= 0:
        return BankSignatureMatch(
            bank="UNKNOWN",
            confidence=0.0,
            layout_version="adaptive_v1",
            signals=["no_signature_match"],
        )

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values()) or 1
    confidence = min(0.99, round(0.35 + (scores[best] / total) * 0.55, 2))

    return BankSignatureMatch(
        bank=best,
        confidence=confidence,
        layout_version=LAYOUT_VERSIONS.get(best, "generic_v1"),
        signals=signals.get(best, []),
    )


def _document_text(document: DocumentExtraction) -> str:
    return " ".join(block.text for page in document.pages for block in page.blocks)
