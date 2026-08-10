from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RelativeType

if TYPE_CHECKING:
    from app.models.employee import Employee


class Relative(Base):
    """Yaqin qarindosh (ota, ona, turmush o'rtog'i va h.k.) — Employee'ga One-to-Many."""

    __tablename__ = "relatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )

    relation_type: Mapped[RelativeType] = mapped_column(
        Enum(RelativeType, native_enum=False, length=20), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_year: Mapped[int | None] = mapped_column(Integer)
    # Haqiqiy МАЪЛУМОТНОМА shablonida "Туғилган йили ва жойи" bitta ustun — birth_year bilan birga
    birth_place: Mapped[str | None] = mapped_column(String(255))
    workplace: Mapped[str | None] = mapped_column(String(255))
    position_title: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500))

    employee: Mapped[Employee] = relationship(back_populates="relatives")
