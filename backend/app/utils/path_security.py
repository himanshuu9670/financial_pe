"""Path traversal and unsafe filename guards."""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r"[<>:\"|?*\x00-\x1f]")


def safe_filename(name: str, *, default: str = "file.pdf") -> str:
    """Return basename-only safe filename for storage paths."""
    if not name or not name.strip():
        return default
    base = Path(name).name.strip()
    if base in (".", "..") or ".." in base:
        return default
    base = _UNSAFE.sub("_", base)
    if not base.lower().endswith(".pdf"):
        base = f"{base}.pdf" if "." not in base else base
    return base[:255]
