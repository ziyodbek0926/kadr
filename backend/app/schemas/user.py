from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import UserRole
from app.schemas.base import ORMBase
from app.schemas.role import RoleRead

USERNAME_PATTERN = r"^[a-zA-Z0-9_.]+$"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role_code: UserRole
    employee_id: int | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Parolda kamida bitta katta harf, kichik harf va raqam bo'lishi shart")
        return v


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    role_code: UserRole | None = None
    is_active: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Parolda kamida bitta katta harf, kichik harf va raqam bo'lishi shart")
        return v


class UserRead(ORMBase):
    id: int
    username: str
    full_name: str
    role: RoleRead
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
