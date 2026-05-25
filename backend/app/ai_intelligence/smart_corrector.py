"""OCR and format error detection with suggested fixes."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from app.shared.models import StructuredTransaction
from app.ai_intelligence.models import SmartCorrection

OCR_CHAR_MAP = str.maketrans({
    "O": "0",
    "o": "0",
    "l": "1",
    "I": "1",
    "|": "1",
    "S": "5",
    "B": "8",
})


def _fix_amount_string(raw: str) -> tuple[str | None, float]:
    if not raw:
        return None, 0.0
    cleaned = raw.strip().translate(OCR_CHAR_MAP)
    cleaned = cleaned.replace(",", "").replace(" ", "")
    cleaned = re.sub(r"\.{2,}", ".", cleaned)
    cleaned = re.sub(r"[^0-9.\-]", "", cleaned)
    if not cleaned or cleaned in (".", "-"):
        return None, 0.0
    try:
        val = Decimal(cleaned)
        return str(val), 0.9
    except InvalidOperation:
        return None, 0.0


def suggest_corrections(transactions: list[StructuredTransaction]) -> list[SmartCorrection]:
    corrections: list[SmartCorrection] = []
    ocr_pattern = re.compile(r"[OoIl\|]|\.{2,}")

    for txn in transactions:
        for field_name, value in (
            ("debit", str(txn.debit) if txn.debit is not None else ""),
            ("credit", str(txn.credit) if txn.credit is not None else ""),
            ("balance", str(txn.balance) if txn.balance is not None else ""),
        ):
            if not value or not ocr_pattern.search(value):
                continue
            fixed, conf = _fix_amount_string(value)
            if fixed and fixed != value.replace(",", ""):
                corrections.append(
                    SmartCorrection(
                        transaction_id=txn.transaction_id,
                        field=field_name,
                        original=value,
                        corrected=fixed,
                        confidence=conf,
                        reason="OCR character confusion (O/0, l/1)",
                    )
                )

        if not txn.description or len(txn.description) < 2:
            corrections.append(
                SmartCorrection(
                    transaction_id=txn.transaction_id,
                    field="description",
                    original=txn.description or "",
                    corrected="[review description]",
                    confidence=0.5,
                    reason="Missing or empty description",
                )
            )

    return corrections
