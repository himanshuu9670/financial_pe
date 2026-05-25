"""
Template matching — scores known layout families without fixed coordinates.
"""

from __future__ import annotations

from app.ai_layout_engine.bank_signature_engine import HEADER_SIGNATURES, LAYOUT_VERSIONS
from app.ai_layout_engine.models import BankSignatureMatch


def match_template(bank_match: BankSignatureMatch, full_text_lower: str) -> BankSignatureMatch:
    headers = HEADER_SIGNATURES.get(bank_match.bank, [])
    if not headers:
        return bank_match

    hits = sum(1 for h in headers if h in full_text_lower)
    if hits >= 3:
        bank_match.confidence = min(0.99, bank_match.confidence + 0.05)
        bank_match.signals.append(f"template:{bank_match.layout_version}")
        bank_match.layout_version = LAYOUT_VERSIONS.get(bank_match.bank, bank_match.layout_version)

    return bank_match
