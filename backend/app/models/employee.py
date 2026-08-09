from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EmploymentStatus, Gender, MaritalStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.award import Award
    from app.models.document_attachment import DocumentAttachment
    from app.models.education_history import EducationHistory
    from app.models.foreign_trip import ForeignTrip
    from app.models.position import Position
    from app.models.relative import Relative
    from app.models.work_history import WorkHistory


class Employee(TimestampMixin, SoftDeleteMixin, Base):
    """Asosiy kadrlar jadvali. Qarindoshlar/ta'lim/mehnat faoliyati/mukofotlar/xorijga
    chiqishlar shu jadvalga One-to-Many bog'langan (employee_id FK, cascade delete-orphan)."""

    __tablename__ = "employees"
    __table_args__ = (
        Index(
            "ix_employees_fullname_trgm",
            "last_name",
            "first_name",
            "middle_name",
            postgresql_using="gin",
            postgresql_ops={
                "last_name": "gin_trgm_ops",
                "first_name": "gin_trgm_ops",
                "middle_name": "gin_trgm_ops",
            },
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    middle_name: Mapped[str | None] = mapped_column(String(100))

    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_place: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[Gender] = mapped_column(Enum(Gender, native_enum=False, length=10), nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(100))
    citizenship: Mapped[str | None] = mapped_column(String(100), default="O'zbekiston Respublikasi")
    marital_status: Mapped[MaritalStatus | None] = mapped_column(
        Enum(MaritalStatus, native_enum=False, length=20)
    )

    pinfl_encrypted: Mapped[str | None] = mapped_column(String(512))
    pinfl_hash: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    passport_series: Mapped[str | None] = mapped_column(String(4))
    passport_number_encrypted: Mapped[str | None] = mapped_column(String(512))
    passport_issued_by: Mapped[str | None] = mapped_column(String(255))
    passport_issued_date: Mapped[date | None] = mapped_column(Date)

    current_address: Mapped[str | None] = mapped_column(String(500))
    permanent_address: Mapped[str | None] = mapped_column(String(500))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    photo_path: Mapped[str | None] = mapped_column(String(500))

    position_id: Mapped[int | None] = mapped_column(ForeignKey("positions.id", ondelete="SET NULL"), index=True)
    # Joriy lavozimda ishlay boshlagan sana — "2 yildan ortiq joriy lavozimda" kabi Advanced Search so'rovlari shunga tayanadi
    position_since: Mapped[date | None] = mapped_column(Date, index=True)
    hire_date: Mapped[date | None] = mapped_column(Date)
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus, native_enum=False, length=20),
        default=EmploymentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    termination_date: Mapped[date | None] = mapped_column(Date)

    specialization_area: Mapped[str | None] = mapped_column(String(100), index=True)

    positive_traits: Mapped[str | None] = mapped_column(Text)
    negative_traits: Mapped[str | None] = mapped_column(Text)

    position: Mapped[Position | None] = relationship(back_populates="employees", lazy="selectin")
    relatives: Mapped[list[Relative]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="Relative.id"
    )
    education_history: Mapped[list[EducationHistory]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="EducationHistory.start_date"
    )
    work_history: Mapped[list[WorkHistory]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="WorkHistory.start_date"
    )
    awards: Mapped[list[Award]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="Award.awarded_date"
    )
    foreign_trips: Mapped[list[ForeignTrip]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="ForeignTrip.start_date"
    )
    attachments: Mapped[list[DocumentAttachment]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)
