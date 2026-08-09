from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.schemas.base import ORMBase


class ForeignTripBase(BaseModel):
    country: str = Field(min_length=2, max_length=100)
    purpose: str | None = None
    start_date: date
    end_date: date | None = None
    order_basis: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def check_date_order(self) -> "ForeignTripBase":
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas")
        return self


class ForeignTripCreate(ForeignTripBase):
    pass


class ForeignTripUpdate(BaseModel):
    country: str | None = Field(default=None, min_length=2, max_length=100)
    purpose: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    order_basis: str | None = Field(default=None, max_length=255)


class ForeignTripRead(ForeignTripBase, ORMBase):
    id: int
    employee_id: int
