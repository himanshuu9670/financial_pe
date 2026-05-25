"""Phase 2 — coordinate extraction and PDF engine utilities."""

from app.pdf_engine.coordinate_mapper import (
    normalize_bbox,
    pdf_to_viewport,
    scale_bbox,
    viewport_to_pdf,
)
from app.pdf_engine.models import DocumentExtraction, PageExtraction, TextBlock, TextSpan


def test_text_span_schema_matches_phase2_format():
    span = TextSpan(
        text="5000.00",
        x=412.23,
        y=291.11,
        width=52.3,
        height=11.4,
        font="Helvetica",
        font_size=10.0,
        bbox=[412.23, 291.11, 464.53, 302.51],
    )
    dumped = span.model_dump()
    assert dumped["text"] == "5000.00"
    assert dumped["font_size"] == 10.0
    assert len(dumped["bbox"]) == 4


def test_document_extraction_block_structure():
    block = TextBlock(
        text="5000.00",
        x=412.23,
        y=291.11,
        width=52.3,
        height=11.4,
        font="Helvetica",
        font_size=10.0,
        bbox=[412.23, 291.11, 464.53, 302.51],
        spans=[
            TextSpan(
                text="5000.00",
                x=412.23,
                y=291.11,
                width=52.3,
                height=11.4,
                font="Helvetica",
                font_size=10.0,
                bbox=[412.23, 291.11, 464.53, 302.51],
            )
        ],
    )
    page = PageExtraction(page=1, width=595.0, height=842.0, blocks=[block])
    doc = DocumentExtraction(
        statement_id="test",
        total_pages=1,
        pages=[page],
        span_count=1,
        block_count=1,
    )
    assert doc.pages[0].blocks[0].spans[0].font == "Helvetica"


def test_pdf_to_viewport_scale():
    bbox = [100.0, 200.0, 150.0, 220.0]
    rect = pdf_to_viewport(bbox, page_height=842.0, scale=1.5)
    assert rect["left"] == 150.0
    assert rect["top"] == 300.0
    assert rect["width"] == 75.0
    assert rect["height"] == 30.0


def test_viewport_to_pdf_inverse():
    x, y = viewport_to_pdf(150.0, 300.0, scale=1.5)
    assert round(x, 2) == 100.0
    assert round(y, 2) == 200.0


def test_normalize_bbox_fractions():
    norm = normalize_bbox([100.0, 200.0, 200.0, 400.0], 400.0, 800.0)
    assert norm == [0.25, 0.25, 0.5, 0.5]


def test_scale_bbox():
    assert scale_bbox([10.0, 20.0, 30.0, 40.0], 2.0) == [20.0, 40.0, 60.0, 80.0]
