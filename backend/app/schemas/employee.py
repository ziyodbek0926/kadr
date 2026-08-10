from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import EmploymentStatus, Gender, MaritalStatus
from app.schemas.award import AwardRead
from app.schemas.base import ORMBase
from app.schemas.education_history import EducationHistoryRead
from app.schemas.foreign_trip import ForeignTripRead
from app.schemas.position import PositionRead
from app.schemas.relative import RelativeRead
from app.schemas.work_history import WorkHistoryRead
from app.utils.dates import today_tashkent
from app.utils.sanitize import sanitize_rich_text

PINFL_PATTERN = r"^\d{14}$"
PASSPORT_SERIES_PATTERN = r"^[A-Z]{2}$"
PASSPORT_NUMBER_PATTERN = r"^\d{7}$"
PHONE_PATTERN = r"^\+998\d{9}$"


class EmployeeBase(BaseModel):
    last_name: str = Field(min_length=2, max_length=100)
    first_name: str = Field(min_length=2, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    birth_date: date
    birth_place: str | None = Field(default=None, max_length=255)
    gender: Gender
    nationality: str | None = Field(default=None, max_length=100)
    citizenship: str | None = Field(default="O'zbekiston Respublikasi", max_length=100)
    marital_status: MaritalStatus | None = None

    academic_degree: str | None = Field(default=None, max_length=150)
    academic_title: str | None = Field(default=None, max_length=150)
    foreign_languages: str | None = Field(default=None, max_length=255)
    military_rank: str | None = Field(default=None, max_length=150)
    party_affiliation: str | None = Field(default=None, max_length=150)
    public_office_note: str | None = None

    pinfl: str | None = Field(default=None, pattern=PINFL_PATTERN, description="14 xonali JSHSHIR")
    passport_series: str | None = Field(default=None, pattern=PASSPORT_SERIES_PATTERN)
    passport_number: str | None = Field(default=None, pattern=PASSPORT_NUMBER_PATTERN)
    passport_issued_by: str | None = Field(default=None, max_length=255)
    passport_issued_date: date | None = None

    current_address: str | None = Field(default=None, max_length=500)
    permanent_address: str | None = Field(default=None, max_length=500)
    phone_number: str | None = Field(default=None, pattern=PHONE_PATTERN)
    photo_path: str | None = None

    position_id: int | None = None
    position_since: date | None = None
    hire_date: date | None = None
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    termination_date: date | None = None

    specialization_area: str | None = Field(default=None, max_length=100)
    positive_traits: str | None = None
    negative_traits: str | None = None

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, v: date) -> date:
        if v > today_tashkent():
            raise ValueError("Tug'ilgan sana kelajakda bo'lishi mumkin emas")
        return v

    @model_validator(mode="after")
    def check_position_dates(self) -> "EmployeeBase":
        if self.position_since and self.position_since > today_tashkent():
            raise ValueError("Lavozimga tayinlangan sana kelajakda bo'lishi mumkin emas")
        if self.termination_date and self.hire_date and self.termination_date < self.hire_date:
            raise ValueError("Bo'shatilgan sana ishga kirgan sanadan oldin bo'lishi mumkin emas")
        return self

    @field_validator("positive_traits", "negative_traits")
    @classmethod
    def sanitize_traits(cls, v: str | None) -> str | None:
        return sanitize_rich_text(v)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    """Barcha maydonlar ixtiyoriy — faqat yuborilgan maydonlar yangilanadi (PATCH semantikasi)."""

    last_name: str | None = Field(default=None, min_length=2, max_length=100)
    first_name: str | None = Field(default=None, min_length=2, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    birth_date: date | None = None
    birth_place: str | None = Field(default=None, max_length=255)
    gender: Gender | None = None
    nationality: str | None = Field(default=None, max_length=100)
    citizenship: str | None = Field(default=None, max_length=100)
    marital_status: MaritalStatus | None = None
    academic_degree: str | None = Field(default=None, max_length=150)
    academic_title: str | None = Field(default=None, max_length=150)
    foreign_languages: str | None = Field(default=None, max_length=255)
    military_rank: str | None = Field(default=None, max_length=150)
    party_affiliation: str | None = Field(default=None, max_length=150)
    public_office_note: str | None = None
    pinfl: str | None = Field(default=None, pattern=PINFL_PATTERN)
    passport_series: str | None = Field(default=None, pattern=PASSPORT_SERIES_PATTERN)
    passport_number: str | None = Field(default=None, pattern=PASSPORT_NUMBER_PATTERN)
    passport_issued_by: str | None = Field(default=None, max_length=255)
    passport_issued_date: date | None = None
    current_address: str | None = Field(default=None, max_length=500)
    permanent_address: str | None = Field(default=None, max_length=500)
    phone_number: str | None = Field(default=None, pattern=PHONE_PATTERN)
    photo_path: str | None = None
    position_id: int | None = None
    position_since: date | None = None
    hire_date: date | None = None
    employment_status: EmploymentStatus | None = None
    termination_date: date | None = None
    specialization_area: str | None = Field(default=None, max_length=100)
    positive_traits: str | None = None
    negative_traits: str | None = None

    @field_validator("positive_traits", "negative_traits")
    @classmethod
    def sanitize_traits(cls, v: str | None) -> str | None:
        return sanitize_rich_text(v)


class EmployeeRead(ORMBase):
    """Standart javob — PINFL/pasport raqami kabi shifrlangan maydonlarni o'z ichiga OLMAYDI."""

    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    full_name: str
    birth_date: date
    birth_place: str | None
    gender: Gender
    nationality: str | None
    citizenship: str | None
    marital_status: MaritalStatus | None
    academic_degree: str | None
    academic_title: str | None
    foreign_languages: str | None
    military_rank: str | None
    party_affiliation: str | None
    public_office_note: str | None
    passport_series: str | None
    passport_issued_by: str | None
    passport_issued_date: date | None
    current_address: str | None
    permanent_address: str | None
    phone_number: str | None
    photo_path: str | None
    position: PositionRead | None
    position_since: date | None
    hire_date: date | None
    employment_status: EmploymentStatus
    termination_date: date | None
    specialization_area: str | None
    positive_traits: str | None
    negative_traits: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeDetailRead(EmployeeRead):
    """Bitta xodim sahifasi uchun — barcha bog'liq (One-to-Many) yozuvlar bilan birga."""

    relatives: list[RelativeRead] = Field(default_factory=list)
    education_history: list[EducationHistoryRead] = Field(default_factory=list)
    work_history: list[WorkHistoryRead] = Field(default_factory=list)
    awards: list[AwardRead] = Field(default_factory=list)
    foreign_trips: list[ForeignTripRead] = Field(default_factory=list)


class EmployeeSensitiveRead(BaseModel):
    """PINFL/pasport raqamining deshifrlangan qiymati — faqat SuperAdmin/HR_OPERATOR
    rollariga alohida endpoint orqali, audit-log yozuvi bilan birga qaytariladi."""

    pinfl: str | None
    passport_number: str | None


class EmployeeListItem(ORMBase):
    """Ro'yxat/qidiruv natijalarida ishlatiladigan yengillashtirilgan ko'rinish."""

    id: int
    full_name: str
    birth_date: date
    gender: Gender
    position: PositionRead | None
    employment_status: EmploymentStatus
    specialization_area: str | None
