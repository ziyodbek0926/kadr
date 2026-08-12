from __future__ import annotations

import uuid
from pathlib import Path

import anyio
from fastapi import UploadFile

from app.core.config import settings

ALLOWED_CONTENT_TYPES: dict[str, set[str]] = {
    ".pdf": {"application/pdf"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".doc": {"application/msword"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}


class UploadValidationError(ValueError):
    """Fayl kengaytmasi/turi ruxsat etilmagan yoki hajmi chegaradan oshgan — 400 sifatida qaytariladi."""


def _upload_root() -> Path:
    root = Path(settings.UPLOAD_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _employee_dir(employee_id: int) -> Path:
    directory = _upload_root() / "employees" / str(employee_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def resolve_stored_path(relative_path: str) -> Path:
    """`relative_path`ni UPLOAD_DIR ostidagi haqiqiy faylga aylantiradi. Natija UPLOAD_DIR
    tashqarisiga chiqmasligini tekshiradi — stored_path bazada faqat shu modul tomonidan
    generatsiya qilingan bo'lsa-da, path traversal'dan qo'shimcha himoya qatlami sifatida."""
    root = _upload_root()
    candidate = (root / relative_path).resolve()
    if root not in candidate.parents:
        raise UploadValidationError("Yaroqsiz fayl yo'li")
    return candidate


def _extension_of(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload(*, filename: str, content_type: str | None, size: int) -> str:
    """Kengaytma/MIME/hajm qoidalarini tekshiradigan sof funksiya (fayl I/O'siz) —
    save_attachment() undan foydalanadi, testlar esa disk/UploadFile'siz to'g'ridan-to'g'ri
    chaqiradi. Muvaffaqiyatli bo'lsa kengaytmani qaytaradi (chaqiruvchi uni qayta hisoblamasin)."""
    ext = _extension_of(filename)
    allowed_types = ALLOWED_CONTENT_TYPES.get(ext)
    if allowed_types is None:
        raise UploadValidationError(
            f"'{ext or '(kengaytmasiz)'}' fayl turi qo'llab-quvvatlanmaydi. Ruxsat etilgan: "
            + ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        )
    if (content_type or "") not in allowed_types:
        raise UploadValidationError(f"Fayl turi ('{content_type}') kengaytmaga mos kelmadi")

    if size <= 0:
        raise UploadValidationError("Fayl bo'sh")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size > max_bytes:
        raise UploadValidationError(f"Fayl hajmi {settings.MAX_UPLOAD_SIZE_MB} MB dan oshmasligi kerak")

    return ext


async def save_attachment(employee_id: int, upload: UploadFile) -> tuple[str, int, str]:
    """Faylni tekshiradi (kengaytma, MIME turi, hajm) va tasodifiy nom bilan diskka yozadi
    (asl fayl nomi hech qachon disk yo'lida ishlatilmaydi). Qaytaradi:
    (UPLOAD_DIR'ga nisbatan yo'l, hajm baytlarda, content_type)."""
    content = await upload.read()
    content_type = upload.content_type or ""
    ext = validate_upload(filename=upload.filename or "", content_type=content_type, size=len(content))

    stored_name = f"{uuid.uuid4().hex}{ext}"
    destination = _employee_dir(employee_id) / stored_name
    await anyio.to_thread.run_sync(destination.write_bytes, content)

    relative_path = str(destination.relative_to(_upload_root()))
    return relative_path, len(content), content_type


async def delete_attachment_file(relative_path: str) -> None:
    path = resolve_stored_path(relative_path)
    if path.exists():
        await anyio.to_thread.run_sync(path.unlink)
