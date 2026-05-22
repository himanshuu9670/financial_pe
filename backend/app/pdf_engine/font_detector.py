"""Font metadata helpers for typography-preserving edits."""

from __future__ import annotations


def normalize_font_name(raw: str | None) -> str:
    if not raw:
        return "Unknown"
    name = raw.strip()
    if "+" in name:
        name = name.split("+", 1)[-1]
    return name


def primary_font_from_spans(spans: list[dict]) -> tuple[str, float]:
    if not spans:
        return "Unknown", 0.0
    dominant = max(spans, key=lambda s: len(s.get("text", "")))
    return (
        normalize_font_name(dominant.get("font")),
        float(dominant.get("size", 0)),
    )
