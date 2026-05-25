"""Password hashing and verification."""

import bcrypt as _bcrypt
from passlib.context import CryptContext

if not hasattr(_bcrypt, "about"):
    def about() -> dict[str, str]:
        return {"version": getattr(_bcrypt, "__version__", "unknown")}

    _bcrypt.about = about

_original_hashpw = _bcrypt.hashpw

def _bcrypt_hashpw(secret: bytes, salt: bytes) -> bytes:
    if len(secret) > 72:
        secret = secret[:72]
    return _original_hashpw(secret, salt)

_bcrypt.hashpw = _bcrypt_hashpw

_pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed or hashed == "not-used-phase-1":
        return False
    try:
        return _pwd_context.verify(plain, hashed)
    except Exception:
        return False
