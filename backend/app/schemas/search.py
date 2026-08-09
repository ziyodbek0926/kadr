from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import EducationLevel, EmploymentStatus, Gender
from app.schemas.employee import EmployeeListItem


class EmployeeSearchFilter(BaseModel):
    """Advanced Search uchun kiruvchi filtrlar. `extra="forbid"` — klient whitelist'dan
    tashqari noma'lum kalit yuborsa 422 bilan rad etiladi (jim ravishda e'tiborsiz qoldirilmaydi,
    xatoni yashirmaslik uchun). Har bir maydon app.services.search_service'dagi whitelist orqali
    SQLAlchemy ustun ifodasiga aylantiriladi — xom SQL yoki ustun nomi hech qachon qabul qilinmaydi."""

    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, max_length=255, description="FIO bo'yicha qisman/imlo xatosiga chidamli qidiruv")
    department_id: int | None = None
    position_id: int | None = None
    gender: Gender | None = None
    employment_status: EmploymentStatus | None = EmploymentStatus.ACTIVE
    min_age: int | None = Field(default=None, ge=0, le=100)
    max_age: int | None = Field(default=None, ge=0, le=100)
    education_level: EducationLevel | None = None
    specialty_keyword: str | None = Field(default=None, max_length=255)
    specialization_area: str | None = Field(default=None, max_length=100)
    min_years_in_position: float | None = Field(default=None, ge=0, le=60)
    nationality: str | None = Field(default=None, max_length=100)
    has_awards: bool | None = None
    hired_after: date | None = None
    hired_before: date | None = None

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=200)

    @model_validator(mode="after")
    def check_ranges(self) -> "EmployeeSearchFilter":
        if self.min_age is not None and self.max_age is not None and self.min_age > self.max_age:
            raise ValueError("min_age qiymati max_age'dan katta bo'lishi mumkin emas")
        if self.hired_after and self.hired_before and self.hired_after > self.hired_before:
            raise ValueError("hired_after qiymati hired_before'dan keyin bo'lishi mumkin emas")
        return self


class EmployeeSearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EmployeeListItem]
