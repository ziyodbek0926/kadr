from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.employee import Employee


class Position(TimestampMixin, Base):
    """Shtat jadvalidagi lavozim birligi (bo'sh yoki band)."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), index=True)
    category: Mapped[str | None] = mapped_column(String(100))
    is_vacant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped[Department] = relationship(back_populates="positions", lazy="selectin")
    employees: Mapped[list[Employee]] = relationship(back_populates="position")
