from pydantic import BaseModel, Field, field_validator

from app.schemas.user import USERNAME_PATTERN, validate_password_strength


class SetupStatus(BaseModel):
    needs_setup: bool


class SuperAdminCreate(BaseModel):
    """`UserCreate`ning qisqartirilgan varianti — birinchi (va yagona) setup-wizard
    foydalanuvchisi har doim SuperAdmin, xodimga bog'lanmagan holda yaratiladi, shu
    sabab `role_code`/`employee_id` bu yerda yo'q (tanlash imkoniyati emas, natija)."""

    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
