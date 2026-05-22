"""OCR engine abstract interface — not implemented until scanned PDF phase."""

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field

from app.pdf_engine.models import PageExtraction


class OcrResult(BaseModel):
    pages: list[PageExtraction] = Field(default_factory=list)
    confidence: float = 0.0
    engine: str = "tesseract"


class OcrEngineBase(ABC):
    @abstractmethod
    def extract_page(self, image_path: Path, page_number: int) -> PageExtraction:
        """Convert a page image to coordinate-aware spans."""

    @abstractmethod
    def is_available(self) -> bool:
        """Whether OCR dependencies are installed on this host."""
