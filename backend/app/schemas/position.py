from pydantic import BaseModel, Field

from app.schemas.base import ORMBase
from app.schemas.department import DepartmentRead


class PositionBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    department_id: int
    category: str | None = Field(default=None, max_length=100)
    is_vacant: bool = True


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    department_id: int | None = None
    category: str | None = Field(default=None, max_length=100)
    is_vacant: bool | None = None


class PositionRead(PositionBase, ORMBase):
    id: int


class PositionReadWithDepartment(PositionRead):
    department: DepartmentRead
