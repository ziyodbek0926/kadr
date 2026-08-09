from pydantic import BaseModel, Field, field_validator

from app.models.enums import RelativeType
from app.schemas.base import ORMBase
from app.utils.dates import today_tashkent


class RelativeBase(BaseModel):
    relation_type: RelativeType
    full_name: str = Field(min_length=2, max_length=255)
    birth_year: int | None = Field(default=None, ge=1900)
    workplace: str | None = Field(default=None, max_length=255)
    position_title: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)

    @field_validator("birth_year")
    @classmethod
    def birth_year_not_in_future(cls, v: int | None) -> int | None:
        if v is not None and v > today_tashkent().year:
            raise ValueError("Tug'ilgan yil kelajakda bo'lishi mumkin emas")
        return v


class RelativeCreate(RelativeBase):
    pass


class RelativeUpdate(BaseModel):
    relation_type: RelativeType | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    birth_year: int | None = Field(default=None, ge=1900)
    workplace: str | None = Field(default=None, max_length=255)
    position_title: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)


class RelativeRead(RelativeBase, ORMBase):
    id: int
    employee_id: int
