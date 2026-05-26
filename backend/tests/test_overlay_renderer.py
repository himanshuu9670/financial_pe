from __future__ import annotations

from unittest.mock import patch

import fitz

from app.pdf_engine.edit_models import Alignment, TargetSpan, TypographySpec
from app.pdf_engine.text_replacer import TextReplacer


def _span_for_test(row_index: int, bbox: list[float], new_text: str, field: str = "balance") -> TargetSpan:
    return TargetSpan(
        transaction_id=f"t{row_index}",
        row_index=row_index,
        field=field,
        field_id=f"{field}-{row_index}",
        page=1,
        bbox=bbox,
        original_text="0.00",
        new_text=new_text,
        typography=TypographySpec(
            font="helv",
            font_size=10.0,
            color=(0.0, 0.0, 0.0),
            alignment=Alignment.RIGHT,
        ),
    )


def test_apply_batch_uses_shared_row_baseline_for_same_row() -> None:
    doc = fitz.open()
    doc.new_page()

    spans = [
        _span_for_test(0, [400.0, 100.0, 480.0, 112.0], "1,000.00", field="withdrawal"),
        _span_for_test(0, [500.0, 101.5, 580.0, 113.5], "500.00", field="balance"),
    ]

    replacer = TextReplacer(doc)
    recorded: list[tuple[str, float, float]] = []

    with patch("app.pdf_engine.text_replacer.draw_replacement_text") as fake_draw:
        def _capture(page, target, *, row_baseline_y=None, row_rect_height=None):
            recorded.append((target.span.field, row_baseline_y, row_rect_height))

        fake_draw.side_effect = _capture
        results = replacer.apply_batch(spans)

    assert all(result.applied for result in results)
    assert len(recorded) == 2
    assert recorded[0][1] == recorded[1][1]
    assert recorded[0][2] == recorded[1][2]
    assert recorded[0][1] is not None
    assert recorded[0][2] is not None
