"""Financial text pattern helpers (used with coordinate logic, not regex-only parsing)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

DATE_PATTERNS = [
    re.compile(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$"),
    re.compile(r"^\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4}$", re.I),
    re.compile(r"^\d{1,2}-[A-Za-z]{3}-\d{2,4}$", re.I),
    re.compile(r"^\d{2}-\d{2}-\d{4}$"),
]

AMOUNT_CLEAN = re.compile(r"[^\d.,-]")


def looks_like_date(text: str) -> bool:
    t = text.strip()
    if not t or len(t) > 20:
        return False
    return any(p.match(t) for p in DATE_PATTERNS)


def parse_amount(text: str) -> Decimal | None:
    cleaned = AMOUNT_CLEAN.sub("", text.strip())
    if not cleaned or cleaned in (".", "-", ","):
        return None
    cleaned = cleaned.replace(",", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None
