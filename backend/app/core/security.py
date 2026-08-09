import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_password_hasher = PasswordHasher()
_fernet = Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


def hash_password(plain_password: str) -> str:
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": subject, "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {"sub": subject, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> dict[str, Any]:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Kutilgan token turi '{expected_type}', kelgani '{payload.get('type')}'")
    return payload


def encrypt_field(value: str) -> str:
    """PINFL/pasport kabi nozik maydonlarni bazaga yozishdan oldin shifrlaydi."""
    return _fernet.encrypt(value.encode()).decode()


def decrypt_field(token: str) -> str:
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Shifrlangan maydonni ochib bo'lmadi — kalit noto'g'ri yoki ma'lumot buzilgan") from exc


def hash_lookup_value(value: str) -> str:
    """PINFL kabi shifrlangan maydonni har safar deshifrlamasdan tenglik bo'yicha
    qidirish/unikallikni tekshirish uchun deterministik HMAC. Fernet shifrlash har
    safar boshqa IV ishlatgani sababli ciphertext ustida to'g'ridan-to'g'ri qidirib
    bo'lmaydi — shu hash alohida, indekslangan ustunda saqlanadi."""
    return hmac.new(settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()
