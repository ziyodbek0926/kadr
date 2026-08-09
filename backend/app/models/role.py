from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    """Rollar ro'yxati (SuperAdmin/HR/Rahbariyat/IT) — sobit to'plam, boshlang'ich
    qatorlari bootstrap migratsiyasi orqali kiritiladi. `code` app.models.enums.UserRole
    qiymatlariga mos keladi va require_role() dependency'sida solishtirish uchun ishlatiladi."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

    users: Mapped[list[User]] = relationship(back_populates="role")
