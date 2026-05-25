"""OCR confidence aggregation and quality gates."""

from __future__ import annotations


def aggregate_word_confidence(confidences: list[int]) -> float:
    if not confidences:
        return 0.0
    valid = [c for c in confidences if c >= 0]
    if not valid:
        return 0.0
    avg = sum(valid) / len(valid)
    return round(min(0.99, avg / 100.0), 2)


def passes_quality_gate(confidence: float, word_count: int, *, min_conf: float = 0.35) -> bool:
    return confidence >= min_conf and word_count >= 10
