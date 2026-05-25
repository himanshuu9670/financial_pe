"""Storage lifecycle — temp cleanup, dedup hints."""

from __future__ import annotations

import time
from pathlib import Path

from app.core.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class StorageOptimizer:
    def __init__(self) -> None:
        self.settings = get_settings()

    def cleanup_temp(self) -> dict:
        temp = self.settings.storage_temp
        if not temp.exists():
            return {"removed": 0, "bytes_freed": 0}

        cutoff = time.time() - self.settings.temp_retention_hours * 3600
        removed = 0
        bytes_freed = 0
        for path in temp.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                try:
                    bytes_freed += path.stat().st_size
                    path.unlink()
                    removed += 1
                except OSError as exc:
                    logger.warning("temp_cleanup_skip", path=str(path), error=str(exc))

        logger.info("temp_cleanup_done", removed=removed, bytes_freed=bytes_freed)
        return {"removed": removed, "bytes_freed": bytes_freed}

    def disk_usage_summary(self) -> dict:
        def _dir_size(p: Path) -> int:
            if not p.exists():
                return 0
            return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

        return {
            "original_bytes": _dir_size(self.settings.storage_original),
            "edited_bytes": _dir_size(self.settings.storage_edited),
            "snapshots_bytes": _dir_size(self.settings.storage_snapshots),
            "exports_bytes": _dir_size(self.settings.storage_exports),
            "temp_bytes": _dir_size(self.settings.storage_temp),
        }
