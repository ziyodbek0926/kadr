from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.models.enums import EducationLevel
from app.schemas.base import ORMBase


class EducationHistoryBase(BaseModel):
    institution_name: str = Field(min_length=2, max_length=255)
    specialty: str | None = Field(default=None, max_length=255)
    level: EducationLevel
    start_date: date | None = None
    end_date: date | None = None
    document_number: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def check_date_order(self) -> "EducationHistoryBase":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas")
        return self


class EducationHistoryCreate(EducationHistoryBase):
    pass


class EducationHistoryUpdate(BaseModel):
    institution_name: str | None = Field(default=None, min_length=2, max_length=255)
    specialty: str | None = Field(default=None, max_length=255)
    level: EducationLevel | None = None
    start_date: date | None = None
    end_date: date | None = None
    document_number: str | None = Field(default=None, max_length=100)


class EducationHistoryRead(EducationHistoryBase, ORMBase):
    id: int
    employee_id: int
