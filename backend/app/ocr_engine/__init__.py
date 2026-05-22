"""
OCR Engine — Phase 4+ foundation for scanned bank statements.

Pipeline (future):
  PDF page image → OpenCV preprocess → Tesseract → span injection → transaction pipeline

Implementations:
  - ocr_engine.preprocessor: deskew, denoise, binarize
  - ocr_engine.tesseract_runner: OCR with bounding boxes
  - ocr_engine.span_adapter: convert OCR boxes to TextSpan format
"""

from app.ocr_engine.base import OcrEngineBase, OcrResult

__all__ = ["OcrEngineBase", "OcrResult"]
