from app.ocr_engine.ocr_processor import TesseractOcrProcessor, ocr_extract_document
from app.ocr_engine.scanned_pdf_detector import ScanDetectionResult, detect_scanned_pdf

__all__ = [
    "TesseractOcrProcessor",
    "ocr_extract_document",
    "ScanDetectionResult",
    "detect_scanned_pdf",
]
