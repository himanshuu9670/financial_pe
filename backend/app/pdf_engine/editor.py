"""
Invisible PDF editor — orchestrates target detection and targeted replacements.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.ai_engine.models import FieldCoordinate
from app.financial_engine.models import LedgerEntry
from app.pdf_engine.edit_models import TargetSpan
from app.pdf_engine.typography_engine import build_target_span
from app.utils.logging import get_logger

logger = get_logger(__name__)

FINANCIAL_FIELDS = ("debit", "credit", "balance")


def collect_targets_from_ledger(
    entries: list[LedgerEntry],
    *,
    page_width: float = 595.0,
) -> list[TargetSpan]:
    """Build replacement targets for any changed financial field with coordinates."""
    targets: list[TargetSpan] = []

    for entry in entries:
        for field in FINANCIAL_FIELDS:
            coord: FieldCoordinate | None = getattr(entry.coordinates, field, None)
            if not coord or not coord.bbox or len(coord.bbox) < 4:
                continue

            current = getattr(entry, field)
            original = getattr(entry, f"original_{field}")

            if current is None:
                continue
            if original is not None and current == original:
                continue

            targets.append(
                build_target_span(
                    entry.transaction_id,
                    field,
                    entry.page,
                    coord,
                    current,
                    page_width=page_width,
                )
            )

    logger.info("edit_targets_collected", count=len(targets))
    return targets


def resolve_page_width(extraction_json: dict | None, page: int) -> float:
    if not extraction_json:
        return 595.0
    for p in extraction_json.get("pages", []):
        if p.get("page") == page:
            return float(p.get("width", 595))
    return 595.0
