import enum
from datetime import date, datetime
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, enum.Enum):
        return value.value
    return value


def model_snapshot(obj: object) -> dict[str, Any]:
    """ORM obyektining o'z ustunlarini (relationship'larsiz) audit-log uchun
    JSON-mos lug'atga aylantiradi. old_values/new_values sifatida ishlatiladi."""
    state = inspect(obj)
    if state is None:
        raise ValueError("model_snapshot faqat SQLAlchemy ORM obyektlari uchun ishlatiladi")
    return {col.key: _jsonable(getattr(obj, col.key)) for col in state.mapper.column_attrs}


async def record_audit(
    db: AsyncSession,
    *,
    user_id: int | None,
    action: str,
    table_name: str,
    record_id: int,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    """Audit yozuvini joriy tranzaksiyaga qo'shadi (flush qiladi, lekin commit qilmaydi —
    chaqiruvchi asosiy CRUD amali bilan bitta tranzaksiyada birga commit/rollback qiladi,
    shunda audit yozuvi haqiqiy o'zgarishdan "ajralib qolmaydi")."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
