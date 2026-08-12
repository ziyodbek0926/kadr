from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.education_history import EducationHistory
from app.models.employee import Employee
from app.models.enums import EducationLevel, EmploymentStatus, Gender
from app.models.position import Position
from app.schemas.dashboard import DashboardStats, LabelCount
from app.utils.dates import today_tashkent

_GENDER_LABELS = {Gender.MALE: "Erkak", Gender.FEMALE: "Ayol"}

_STATUS_LABELS = {
    EmploymentStatus.ACTIVE: "Faoliyat yuritmoqda",
    EmploymentStatus.ON_LEAVE: "Ta'til/dam olishda",
    EmploymentStatus.DISMISSED: "Bo'shatilgan",
}

_EDUCATION_ORDER = [
    EducationLevel.SECONDARY,
    EducationLevel.SECONDARY_SPECIAL,
    EducationLevel.BACHELOR,
    EducationLevel.MASTER,
    EducationLevel.PHD,
]
_EDUCATION_LABELS = {
    EducationLevel.SECONDARY: "O'rta",
    EducationLevel.SECONDARY_SPECIAL: "O'rta-maxsus",
    EducationLevel.BACHELOR: "Bakalavr",
    EducationLevel.MASTER: "Magistr",
    EducationLevel.PHD: "Fan doktori/nomzodi",
}
_EDUCATION_UNSPECIFIED_LABEL = "Ko'rsatilmagan"

_AGE_BUCKETS: list[tuple[int, int, str]] = [
    (0, 29, "<30"),
    (30, 39, "30-39"),
    (40, 49, "40-49"),
    (50, 59, "50-59"),
    (60, 999, "60+"),
]


def highest_education_level(levels: list[EducationLevel]) -> EducationLevel | None:
    """Bitta xodimning bir nechta ta'lim yozuvidan (masalan bakalavr, keyin magistr)
    eng yuqori darajasini tanlaydi — statistikada har bir xodim faqat bitta marta
    hisoblanishi uchun (aks holda bir necha yozuvli xodim bir necha marta sanaladi)."""
    if not levels:
        return None
    return max(levels, key=_EDUCATION_ORDER.index)


def age_bucket(birth_date: date, today: date) -> str:
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    for low, high, label in _AGE_BUCKETS:
        if low <= age <= high:
            return label
    return _AGE_BUCKETS[-1][2]


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    not_deleted = Employee.is_deleted.is_(False)

    total = (await db.execute(select(func.count(Employee.id)).where(not_deleted))).scalar_one()

    gender_rows = (
        await db.execute(select(Employee.gender, func.count(Employee.id)).where(not_deleted).group_by(Employee.gender))
    ).all()
    gender_counts: dict[Gender, int] = {g: c for g, c in gender_rows}  # noqa: C416
    by_gender = [LabelCount(label=label, count=gender_counts.get(g, 0)) for g, label in _GENDER_LABELS.items()]

    status_rows = (
        await db.execute(
            select(Employee.employment_status, func.count(Employee.id))
            .where(not_deleted)
            .group_by(Employee.employment_status)
        )
    ).all()
    status_counts: dict[EmploymentStatus, int] = {s: c for s, c in status_rows}  # noqa: C416
    by_employment_status = [
        LabelCount(label=label, count=status_counts.get(s, 0)) for s, label in _STATUS_LABELS.items()
    ]

    department_rows = (
        await db.execute(
            select(Department.name, func.count(Employee.id))
            .select_from(Employee)
            .join(Position, Employee.position_id == Position.id)
            .join(Department, Position.department_id == Department.id)
            .where(not_deleted)
            .group_by(Department.name)
            .order_by(func.count(Employee.id).desc())
        )
    ).all()
    by_department = [LabelCount(label=name, count=count) for name, count in department_rows]

    employee_rows = (await db.execute(select(Employee.id, Employee.birth_date).where(not_deleted))).all()

    edu_rows = (
        await db.execute(
            select(EducationHistory.employee_id, EducationHistory.level)
            .select_from(EducationHistory)
            .join(Employee, Employee.id == EducationHistory.employee_id)
            .where(not_deleted)
        )
    ).all()
    levels_by_employee: dict[int, list[EducationLevel]] = {}
    for emp_id, level in edu_rows:
        levels_by_employee.setdefault(emp_id, []).append(level)

    today = today_tashkent()
    age_counts: dict[str, int] = {}
    edu_counts: dict[str, int] = {}
    for emp_id, birth_date in employee_rows:
        bucket = age_bucket(birth_date, today)
        age_counts[bucket] = age_counts.get(bucket, 0) + 1

        highest = highest_education_level(levels_by_employee.get(emp_id, []))
        edu_label = _EDUCATION_LABELS[highest] if highest is not None else _EDUCATION_UNSPECIFIED_LABEL
        edu_counts[edu_label] = edu_counts.get(edu_label, 0) + 1

    by_age_bucket = [LabelCount(label=label, count=age_counts.get(label, 0)) for _, _, label in _AGE_BUCKETS]

    education_label_order = [_EDUCATION_LABELS[lvl] for lvl in _EDUCATION_ORDER] + [_EDUCATION_UNSPECIFIED_LABEL]
    by_education_level = [
        LabelCount(label=label, count=edu_counts[label]) for label in education_label_order if label in edu_counts
    ]

    return DashboardStats(
        total_employees=total,
        by_gender=by_gender,
        by_employment_status=by_employment_status,
        by_education_level=by_education_level,
        by_age_bucket=by_age_bucket,
        by_department=by_department,
    )
