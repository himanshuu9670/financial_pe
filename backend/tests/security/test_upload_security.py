"""Security QA — uploads, JWT, path traversal."""

import time
import uuid

import pytest

from app.auth.jwt_handler import create_access_token, verify_access_token
from app.pdf_engine.exceptions import PdfValidationError
from app.pdf_engine.pdf_loader import validate_pdf_bytes
from app.services.storage_service import StorageService
from app.utils.path_security import safe_filename


def test_safe_filename_strips_traversal():
    assert safe_filename("../../etc/passwd") == "passwd.pdf"
    assert ".." not in safe_filename("..\\..\\evil.pdf")


def test_storage_edited_path_stays_in_bucket(tmp_path, monkeypatch):
    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "storage_edited", tmp_path)
    svc = StorageService()
    sid = uuid.uuid4()
    path = svc.path_for_edited(sid, "../../../secret.pdf")
    assert path.resolve().parent == tmp_path.resolve()
    assert path.name.startswith(str(sid))


def test_rejects_fake_pdf_upload_header():
    with pytest.raises(PdfValidationError):
        validate_pdf_bytes(b"<html>not pdf</html>")


def test_expired_jwt_rejected(monkeypatch):
    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "jwt_access_expire_minutes", -1)
    token = create_access_token(uuid.uuid4(), "a@b.com", "viewer")
    time.sleep(0.05)
    assert verify_access_token(token) is None
