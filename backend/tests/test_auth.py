"""Phase 8 — authentication tests."""

from app.auth.password_manager import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, verify_access_token
import uuid


def test_password_hash_roundtrip():
    h = hash_password("secure-password-123")
    assert verify_password("secure-password-123", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    uid = uuid.uuid4()
    token = create_access_token(uid, "test@example.com", "editor")
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(uid)
    assert payload["role"] == "editor"
