from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EducationLevel

if TYPE_CHECKING:
    from app.models.employee import Employee


class EducationHistory(Base):
    __tablename__ = "education_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )

    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(255), index=True)
    level: Mapped[EducationLevel] = mapped_column(Enum(EducationLevel, native_enum=False, length=30), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    document_number: Mapped[str | None] = mapped_column(String(100))

    employee: Mapped[Employee] = relationship(back_populates="education_history")
