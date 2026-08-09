from pydantic import BaseModel, Field

from app.schemas.base import ORMBase


class DepartmentBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    parent_id: int | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    parent_id: int | None = None


class DepartmentRead(DepartmentBase, ORMBase):
    id: int
