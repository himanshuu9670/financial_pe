class PdfEngineError(Exception):
    """Base error for PDF engine operations."""


class PdfValidationError(PdfEngineError):
    """Invalid or unsupported PDF file."""


class PdfEncryptedError(PdfValidationError):
    """PDF requires a password."""


class PdfCorruptedError(PdfValidationError):
    """PDF cannot be opened or parsed."""


class PdfExtractionError(PdfEngineError):
    """Text/coordinate extraction failed."""
