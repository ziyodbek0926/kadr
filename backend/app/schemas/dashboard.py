from pydantic import BaseModel


class LabelCount(BaseModel):
    label: str
    count: int


class DashboardStats(BaseModel):
    total_employees: int
    by_gender: list[LabelCount]
    by_employment_status: list[LabelCount]
    by_education_level: list[LabelCount]
    by_age_bucket: list[LabelCount]
    by_department: list[LabelCount]
