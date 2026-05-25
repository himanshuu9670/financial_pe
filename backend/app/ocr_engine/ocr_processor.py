"""
Tesseract OCR with PyMuPDF page rendering.
"""

from __future__ import annotations

import io
from pathlib import Path

import fitz
from PIL import Image

from app.ocr_engine.base import OcrEngineBase, OcrResult
from app.ocr_engine.confidence_validator import aggregate_word_confidence, passes_quality_gate
from app.ocr_engine.coordinate_rebuilder import build_document, spans_to_page
from app.ocr_engine.image_preprocessor import preprocess_for_ocr
from app.ocr_engine.text_reconstructor import tesseract_dict_to_words
from app.pdf_engine.models import DocumentExtraction, PageExtraction
from app.utils.logging import get_logger

logger = get_logger(__name__)

RENDER_SCALE = 2.0


class TesseractOcrProcessor(OcrEngineBase):
    def __init__(self, *, dpi_scale: float = RENDER_SCALE) -> None:
        self.dpi_scale = dpi_scale
        self._tesseract = None

    def _load_tesseract(self):
        if self._tesseract is None:
            import pytesseract

            self._tesseract = pytesseract
        return self._tesseract

    def is_available(self) -> bool:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_page(self, image_path: Path, page_number: int) -> PageExtraction:
        img = Image.open(image_path)
        return self._ocr_image(img, page_number, img.width / self.dpi_scale, img.height / self.dpi_scale)

    def _ocr_image(
        self,
        image: Image.Image,
        page_number: int,
        page_width: float,
        page_height: float,
    ) -> PageExtraction:
        pytesseract = self._load_tesseract()
        processed = preprocess_for_ocr(image)
        data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
        words = tesseract_dict_to_words(data, scale=self.dpi_scale)
        return spans_to_page(words, page_number, page_width, page_height)

    def extract_document(
        self,
        path: Path,
        *,
        statement_id: str | None = None,
        page_numbers: list[int] | None = None,
    ) -> tuple[DocumentExtraction, float]:
        if not self.is_available():
            raise RuntimeError("Tesseract is not installed or not on PATH.")

        doc = fitz.open(path)
        pages: list[PageExtraction] = []
        all_confs: list[int] = []

        try:
            indices = page_numbers if page_numbers else list(range(1, doc.page_count + 1))
            matrix = fitz.Matrix(self.dpi_scale, self.dpi_scale)

            for num in indices:
                if num < 1 or num > doc.page_count:
                    continue
                page = doc[num - 1]
                rect = page.rect
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                pytesseract = self._load_tesseract()
                processed = preprocess_for_ocr(img)
                data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
                words = tesseract_dict_to_words(data, scale=self.dpi_scale)
                n = len(data.get("text", []))
                for i in range(n):
                    t = (data["text"][i] or "").strip()
                    if not t:
                        continue
                    try:
                        c = int(data["conf"][i])
                        if c >= 0:
                            all_confs.append(c)
                    except (ValueError, TypeError):
                        pass
                page_ext = spans_to_page(words, num, rect.width, rect.height)
                pages.append(page_ext)

            conf = aggregate_word_confidence(all_confs)
            if not passes_quality_gate(conf, sum(len(b.spans) for p in pages for b in p.blocks)):
                logger.warning("ocr_low_quality", confidence=conf, path=str(path))

            document = build_document(
                pages,
                statement_id=statement_id,
                ocr_confidence=conf,
            )
            return document, conf
        finally:
            doc.close()


def ocr_extract_document(
    path: Path,
    *,
    statement_id: str | None = None,
    page_numbers: list[int] | None = None,
) -> tuple[DocumentExtraction, float]:
    processor = TesseractOcrProcessor()
    return processor.extract_document(path, statement_id=statement_id, page_numbers=page_numbers)
