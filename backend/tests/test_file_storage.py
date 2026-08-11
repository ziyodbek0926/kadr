import pytest

from app.core.config import settings
from app.services.file_storage import UploadValidationError, resolve_stored_path, validate_upload


def test_validate_upload_accepts_known_type() -> None:
    ext = validate_upload(filename="diplom.pdf", content_type="application/pdf", size=1024)
    assert ext == ".pdf"


def test_validate_upload_rejects_unknown_extension() -> None:
    with pytest.raises(UploadValidationError):
        validate_upload(filename="virus.exe", content_type="application/octet-stream", size=1024)


def test_validate_upload_rejects_extension_content_type_mismatch() -> None:
    with pytest.raises(UploadValidationError):
        validate_upload(filename="fake.pdf", content_type="image/png", size=1024)


def test_validate_upload_rejects_empty_file() -> None:
    with pytest.raises(UploadValidationError):
        validate_upload(filename="empty.pdf", content_type="application/pdf", size=0)


def test_validate_upload_rejects_oversized_file() -> None:
    too_big = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1
    with pytest.raises(UploadValidationError):
        validate_upload(filename="huge.pdf", content_type="application/pdf", size=too_big)


def test_validate_upload_accepts_file_at_exact_limit() -> None:
    exactly_max = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    validate_upload(filename="max.pdf", content_type="application/pdf", size=exactly_max)


def test_resolve_stored_path_rejects_traversal_outside_upload_root() -> None:
    with pytest.raises(UploadValidationError):
        resolve_stored_path("../../etc/passwd")


def test_resolve_stored_path_accepts_normal_relative_path() -> None:
    path = resolve_stored_path("employees/1/somefile.pdf")
    assert path.name == "somefile.pdf"
