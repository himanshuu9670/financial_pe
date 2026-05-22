from pydantic import BaseModel, Field

from app.pdf_engine.models import DocumentExtraction


class ExtractionResponse(DocumentExtraction):
    cached: bool = False
    processing_status: str = "ready"


class ExtractionPageQuery(BaseModel):
    pages: str | None = Field(
        default=None,
        description="Comma-separated page numbers, e.g. '1,2,3'. Omit for all pages.",
    )
