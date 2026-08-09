from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.schemas.base import ORMBase


class WorkHistoryBase(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    position_title: str = Field(min_length=2, max_length=255)
    start_date: date
    end_date: date | None = None
    order_reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @model_validator(mode="after")
    def check_date_order(self) -> "WorkHistoryBase":
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas")
        return self


class WorkHistoryCreate(WorkHistoryBase):
    pass


class WorkHistoryUpdate(BaseModel):
    organization_name: str | None = Field(default=None, min_length=2, max_length=255)
    position_title: str | None = Field(default=None, min_length=2, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    order_reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class WorkHistoryRead(WorkHistoryBase, ORMBase):
    id: int
    employee_id: int
