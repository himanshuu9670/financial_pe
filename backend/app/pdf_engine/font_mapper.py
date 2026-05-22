"""
Map extracted PDF font names to PyMuPDF Base14 or document fonts.
"""

from __future__ import annotations

import re

# PyMuPDF Base14 names
FONT_ALIASES: dict[str, str] = {
    "helvetica": "helv",
    "helvetica-bold": "hebo",
    "helvetica-oblique": "heit",
    "helvetica-boldoblique": "hebi",
    "arial": "helv",
    "arial-bold": "hebo",
    "arialmt": "helv",
    "times": "times",
    "times-roman": "tiro",
    "times-bold": "tibo",
    "courier": "cour",
    "courier-new": "cour",
}


def normalize_font_key(name: str) -> str:
    key = name.strip().lower()
    if "+" in key:
        key = key.split("+", 1)[-1]
    key = re.sub(r"[^a-z0-9-]", "", key)
    return key


def resolve_pymupdf_font(extracted_font: str | None) -> str:
    if not extracted_font:
        return "helv"
    key = normalize_font_key(extracted_font)
    if key in FONT_ALIASES:
        return FONT_ALIASES[key]
    for partial, mapped in FONT_ALIASES.items():
        if partial in key:
            return mapped
    return "helv"


def is_likely_bold(font_name: str) -> bool:
    lower = font_name.lower()
    return "bold" in lower or "bd" in lower or "-b" in lower
