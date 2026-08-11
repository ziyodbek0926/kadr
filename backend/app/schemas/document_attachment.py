from datetime import datetime

from app.schemas.base import ORMBase


class DocumentAttachmentRead(ORMBase):
    """`stored_path` ataylab bu yerda yo'q — bu server ichki fayl yo'li, klientga
    hech qachon oshkor qilinmaydi (yuklab olish faqat /download endpoint orqali)."""

    id: int
    employee_id: int
    file_type: str
    original_filename: str
    content_type: str
    size_bytes: int
    uploaded_by_id: int | None
    uploaded_at: datetime
