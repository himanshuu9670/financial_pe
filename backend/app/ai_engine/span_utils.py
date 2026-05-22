"""Shared span flattening and geometry helpers."""

from __future__ import annotations

from dataclasses import dataclass

from app.pdf_engine.models import DocumentExtraction, TextSpan


@dataclass
class PageSpan:
    span: TextSpan
    page: int
    page_width: float
    page_height: float

    @property
    def x_center(self) -> float:
        return self.span.x + self.span.width / 2

    @property
    def y_center(self) -> float:
        return self.span.y + self.span.height / 2


def flatten_spans(document: DocumentExtraction) -> list[PageSpan]:
    out: list[PageSpan] = []
    for page in document.pages:
        for block in page.blocks:
            for span in block.spans:
                if span.text.strip():
                    out.append(
                        PageSpan(
                            span=span,
                            page=page.page,
                            page_width=page.width,
                            page_height=page.height,
                        )
                    )
    return out


def merge_bbox(boxes: list[list[float]]) -> list[float]:
    if not boxes:
        return [0, 0, 0, 0]
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    return [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]


def span_to_field_coordinate(span: TextSpan) -> dict:
    return {
        "text": span.text,
        "x": span.x,
        "y": span.y,
        "width": span.width,
        "height": span.height,
        "bbox": span.bbox,
        "font": span.font,
        "font_size": span.font_size,
    }
