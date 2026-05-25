"""
Typography preservation — extract and apply font metrics for invisible edits.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.shared.models import FieldCoordinate

from app.pdf_engine.bbox_detector import infer_alignment_from_bbox
from app.pdf_engine.edit_models import Alignment, TargetSpan, TypographySpec
from app.pdf_engine.font_mapper import is_likely_bold, resolve_pymupdf_font


def typography_from_coordinate(
    coord: FieldCoordinate,
    *,
    page_width: float = 595.0,
) -> TypographySpec:
    alignment = infer_alignment_from_bbox(coord.bbox, page_width)
    font = resolve_pymupdf_font(coord.font)
    if is_likely_bold(coord.font):
        font = "hebo" if font == "helv" else font

    color = (0.0, 0.0, 0.0)
    if coord.color is not None:
        c = coord.color
        if isinstance(c, int):
            r = ((c >> 16) & 255) / 255
            g = ((c >> 8) & 255) / 255
            b = (c & 255) / 255
            color = (r, g, b)

    return TypographySpec(
        font=coord.font or "Unknown",
        font_size=coord.font_size or 10.0,
        color=color,
        alignment=alignment,
        line_height=(coord.font_size or 10) * 1.2,
    )


def build_target_span(
    transaction_id: str,
    row_index: int,
    field: str,
    page: int,
    coord: FieldCoordinate,
    new_value: Decimal | str,
    *,
    page_width: float = 595.0,
) -> TargetSpan:
    original_text = coord.text.strip()
    new_text = format_amount_for_pdf(new_value, original_text)

    typo = typography_from_coordinate(coord, page_width=page_width)
    pymupdf_font = resolve_pymupdf_font(typo.font)
    if is_likely_bold(typo.font):
        pymupdf_font = "hebo" if pymupdf_font == "helv" else pymupdf_font

    return TargetSpan(
        transaction_id=transaction_id,
        row_index=row_index,
        field=field,
        field_id=coord.field_id,
        page=page,
        bbox=list(coord.bbox),
        original_text=original_text,
        new_text=new_text,
        typography=typo,
        pymupdf_font=pymupdf_font,
    )


def format_amount_for_pdf(value: Decimal | str, template_text: str) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    use_grouping = "," in template_text
    abs_val = abs(value)
    sign = "-" if value < 0 else ""

    if use_grouping:
        # Detect grouping style from the template: western (1,234,567) vs indian (12,34,567)
        int_part = int(abs_val)
        # Examine template integer groups
        left = template_text.split(".")[0]
        groups = [g for g in left.split(",") if g != ""]
        grouping_style = "western"
        if len(groups) >= 2:
            # If groups after the first are length 2, it's likely Indian grouping
            tail_lengths = [len(g) for g in groups[1:]]
            if all(l == 2 for l in tail_lengths):
                grouping_style = "indian"

        frac = abs_val - int_part
        if grouping_style == "indian":
            s = f"{sign}{_indian_group(int_part)}.{int(int(round(frac * 100))):02d}"
        else:
            # western grouping
            s = f"{sign}{int_part:,}.{int(int(round(frac * 100))):02d}"
        return s

    decimals = 2
    if "." in template_text:
        parts = template_text.replace(",", "").split(".")
        if len(parts) > 1:
            decimals = len(parts[1])
    return f"{value:.{decimals}f}"


def _indian_group(n: int) -> str:
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return ",".join(groups) + "," + last3
