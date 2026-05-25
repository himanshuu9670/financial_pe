"""Shared QA fixtures — minimal PDFs, paths, optional API client."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

# Ensure test-friendly defaults before app import
os.environ.setdefault("AUTH_DISABLED", "true")
os.environ.setdefault("REDIS_CACHE_ENABLED", "false")


REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_PDFS_DIR = REPO_ROOT / "test_pdfs"
GENERATED_PDFS = TEST_PDFS_DIR / "generated"


@pytest.fixture(scope="session")
def test_pdfs_dir() -> Path:
    GENERATED_PDFS.mkdir(parents=True, exist_ok=True)
    return TEST_PDFS_DIR


@pytest.fixture
def minimal_pdf_bytes() -> bytes:
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "01/01/2024  SWIGGY PAYMENT", fontsize=10)
    page.insert_text((72, 92), "1,000.00", fontsize=10)
    page.insert_text((400, 92), "9,000.00", fontsize=10)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def minimal_pdf_path(tmp_path, minimal_pdf_bytes) -> Path:
    path = tmp_path / "minimal_statement.pdf"
    path.write_bytes(minimal_pdf_bytes)
    return path


@pytest.fixture
def corrupt_file_bytes() -> bytes:
    return b"NOT_A_VALID_PDF_HEADER"


@pytest.fixture
def empty_pdf_bytes() -> bytes:
    return b""


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture
def statement_id() -> str:
    return str(uuid.uuid4())
