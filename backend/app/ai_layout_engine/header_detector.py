"""Header row detection via keyword density and y-position clustering."""

from __future__ import annotations

from app.ai_engine.span_utils import PageSpan, flatten_spans
from app.pdf_engine.models import DocumentExtraction

HEADER_TOKENS = (
    "date",
    "description",
    "particulars",
    "narration",
    "debit",
    "credit",
    "withdrawal",
    "deposit",
    "balance",
    "chq",
    "cheque",
    "txn",
    "tran",
    "amount",
    "dr",
    "cr",
)


def detect_header_y(document: DocumentExtraction) -> float | None:
    spans = flatten_spans(document)
    if not spans:
        return None

    by_y: dict[int, list[PageSpan]] = {}
    for ps in spans:
        bucket = int(ps.y_center / 8)
        by_y.setdefault(bucket, []).append(ps)

    best_y: float | None = None
    best_score = 0

    for bucket, group in by_y.items():
        line = " ".join(ps.span.text.lower() for ps in group)
        score = sum(1 for t in HEADER_TOKENS if t in line)
        if score > best_score and score >= 3:
            best_score = score
            best_y = sum(ps.y_center for ps in group) / len(group)

    return best_y
