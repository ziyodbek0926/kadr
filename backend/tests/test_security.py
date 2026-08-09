import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decrypt_field,
    encrypt_field,
    hash_lookup_value,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("Juda-Kuchli-Parol123")
    assert hashed != "Juda-Kuchli-Parol123"
    assert verify_password("Juda-Kuchli-Parol123", hashed)
    assert not verify_password("Notogri-Parol", hashed)


def test_field_encryption_roundtrip() -> None:
    ciphertext = encrypt_field("30101015550012")
    assert ciphertext != "30101015550012"
    assert decrypt_field(ciphertext) == "30101015550012"


def test_field_encryption_is_non_deterministic() -> None:
    first = encrypt_field("30101015550012")
    second = encrypt_field("30101015550012")
    assert first != second


def test_hash_lookup_value_is_deterministic() -> None:
    assert hash_lookup_value("30101015550012") == hash_lookup_value("30101015550012")
    assert hash_lookup_value("30101015550012") != hash_lookup_value("30101015550013")


def test_access_token_roundtrip() -> None:
    token = create_access_token(subject="hr_operator1", role="hr_operator")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "hr_operator1"
    assert payload["role"] == "hr_operator"


def test_access_token_rejected_as_refresh() -> None:
    token = create_access_token(subject="hr_operator1", role="hr_operator")
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, expected_type="refresh")


def test_refresh_token_roundtrip() -> None:
    token = create_refresh_token(subject="hr_operator1")
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == "hr_operator1"
