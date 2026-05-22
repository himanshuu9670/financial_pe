import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.config import get_settings
from app.pdf_engine.pdf_loader import validate_pdf_bytes


class StorageService:
    """Manages PDF and preview file paths on disk."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def path_for_statement(self, statement_id: uuid.UUID) -> Path:
        return self.settings.storage_original / f"{statement_id}.pdf"

    async def save_original_pdf_async(
        self,
        upload: UploadFile,
        statement_id: uuid.UUID,
    ) -> tuple[str, Path, int]:
        dest = self.path_for_statement(statement_id)
        size = 0
        header = b""

        async with aiofiles.open(dest, "wb") as out:
            while chunk := await upload.read(1024 * 1024):
                if size == 0:
                    header = chunk[:8]
                    validate_pdf_bytes(header)
                size += len(chunk)
                if size > self.settings.max_upload_size_bytes:
                    dest.unlink(missing_ok=True)
                    raise ValueError(
                        f"File exceeds maximum size of {self.settings.max_upload_size_mb}MB"
                    )
                await out.write(chunk)

        await upload.seek(0)
        return str(dest), dest, size

    def save_original_pdf_sync(
        self,
        content: bytes,
        statement_id: uuid.UUID,
    ) -> tuple[str, Path, int]:
        validate_pdf_bytes(content[:8])
        if len(content) > self.settings.max_upload_size_bytes:
            raise ValueError(
                f"File exceeds maximum size of {self.settings.max_upload_size_mb}MB"
            )
        dest = self.path_for_statement(statement_id)
        dest.write_bytes(content)
        return str(dest), dest, len(content)

    def path_for_edited(self, statement_id: uuid.UUID, filename: str) -> Path:
        return self.settings.storage_edited / f"{statement_id}_{filename}"

    def path_for_preview(self, statement_id: uuid.UUID) -> Path:
        return self.settings.storage_previews / f"{statement_id}.png"
