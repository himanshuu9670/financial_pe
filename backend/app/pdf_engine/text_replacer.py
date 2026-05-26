"""
Targeted text replacement workflow: redact → insert with preserved typography.
"""

from __future__ import annotations

from pathlib import Path

import fitz

from app.pdf_engine.bbox_detector import detect_replacement_region
from app.pdf_engine.edit_models import ReplacementResult, TargetSpan, TextReplacementTarget
from app.pdf_engine.overlay_renderer import batch_redact_page, draw_replacement_text
from app.pdf_engine.pdf_loader import open_pdf
from app.utils.logging import get_logger

logger = get_logger(__name__)


class TextReplacer:
    def __init__(self, doc: fitz.Document) -> None:
        self.doc = doc
        self._redacted_pages: set[int] = set()

    def replace_span(self, span: TargetSpan) -> ReplacementResult:
        page_index = span.page - 1
        if page_index < 0 or page_index >= self.doc.page_count:
            return ReplacementResult(
                target=TextReplacementTarget(
                    span=span, rect=span.bbox, insert_point=(0, 0), success=False, error="Bad page"
                ),
                applied=False,
                message="Invalid page number",
            )

        page = self.doc[page_index]
        target = detect_replacement_region(span, page)
        if not target.success:
            return ReplacementResult(target=target, applied=False, message=target.error or "detect failed")

        try:
            batch_redact_page(page, [target.rect])
            draw_replacement_text(page, target)
            return ReplacementResult(target=target, applied=True, message="ok")
        except Exception as exc:
            logger.error("replace_span_failed", txn=span.transaction_id, field=span.field, error=str(exc))
            return ReplacementResult(target=target, applied=False, message=str(exc))

    def apply_batch(self, spans: list[TargetSpan]) -> list[ReplacementResult]:
        by_page: dict[int, list[TargetSpan]] = {}
        for s in spans:
            by_page.setdefault(s.page, []).append(s)

        results: list[ReplacementResult] = []
        for page_num in sorted(by_page.keys()):
            page_index = page_num - 1
            page = self.doc[page_index]
            redact_rects: list[list[float]] = []
            targets: list[TextReplacementTarget] = []

            for span in by_page[page_num]:
                t = detect_replacement_region(span, page)
                targets.append(t)
                if t.success:
                    redact_rects.append(t.rect)

            batch_redact_page(page, redact_rects)

            row_targets_by_key: dict[tuple[int, int], list[TextReplacementTarget]] = {}
            for span, target in zip(by_page[page_num], targets):
                if not target.success:
                    continue

                key = (span.page, span.row_index)
                row_targets_by_key.setdefault(key, []).append(target)

            row_baseline_values: dict[tuple[int, int], tuple[float, float]] = {}
            for key, targets_for_row in row_targets_by_key.items():
                y_positions = [t.insert_point[1] for t in targets_for_row]
                height_values = [t.rect[3] - t.rect[1] for t in targets_for_row]
                row_baseline_values[key] = (
                    sum(y_positions) / len(y_positions),
                    sum(height_values) / len(height_values),
                )

            for span, target in zip(by_page[page_num], targets):
                if not target.success:
                    results.append(ReplacementResult(target=target, applied=False))
                    continue

                row_key = (span.page, span.row_index)
                baseline_y, row_height = row_baseline_values.get(row_key, (target.insert_point[1], target.rect[3] - target.rect[1]))
                try:
                    draw_replacement_text(
                        page,
                        target,
                        row_baseline_y=baseline_y,
                        row_rect_height=row_height,
                    )
                    results.append(ReplacementResult(target=target, applied=True))
                except Exception as exc:
                    results.append(
                        ReplacementResult(target=target, applied=False, message=str(exc))
                    )

        return results


def replace_in_pdf(source: Path, output: Path, spans: list[TargetSpan]) -> list[ReplacementResult]:
    doc = open_pdf(source)
    try:
        replacer = TextReplacer(doc)
        results = replacer.apply_batch(spans)
        doc.save(output, garbage=4, deflate=True, incremental=False)
        return results
    finally:
        doc.close()
