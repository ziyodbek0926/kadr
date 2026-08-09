from datetime import date

from pydantic import BaseModel, Field

from app.schemas.base import ORMBase


class AwardBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    awarded_date: date
    recommending_organization: str | None = Field(default=None, max_length=255)


class AwardCreate(AwardBase):
    pass


class AwardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    awarded_date: date | None = None
    recommending_organization: str | None = Field(default=None, max_length=255)


class AwardRead(AwardBase, ORMBase):
    id: int
    employee_id: int
