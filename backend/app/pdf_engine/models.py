from pydantic import BaseModel, Field


class TextSpan(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float
    font: str
    font_size: float
    bbox: list[float] = Field(..., min_length=4, max_length=4)
    flags: int | None = None
    color: int | None = None


class TextLine(BaseModel):
    bbox: list[float]
    spans: list[TextSpan]


class TextBlock(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float
    font: str
    font_size: float
    bbox: list[float]
    spans: list[TextSpan] = Field(default_factory=list)


class PageExtraction(BaseModel):
    page: int
    width: float
    height: float
    blocks: list[TextBlock]


class DocumentExtraction(BaseModel):
    statement_id: str | None = None
    total_pages: int
    pages: list[PageExtraction]
    span_count: int
    block_count: int
    warnings: list[str] = Field(default_factory=list)
    is_likely_scanned: bool = False
