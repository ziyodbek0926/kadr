from datetime import timedelta

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education_history import EducationHistory
from app.models.employee import Employee
from app.models.position import Position
from app.schemas.search import EmployeeSearchFilter
from app.utils.dates import today_tashkent

APPROX_DAYS_PER_YEAR = 365.25


def _build_conditions(filters: EmployeeSearchFilter) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = [Employee.is_deleted.is_(False)]

    if filters.full_name:
        term = f"%{filters.full_name.strip()}%"
        conditions.append(
            or_(
                Employee.last_name.ilike(term),
                Employee.first_name.ilike(term),
                Employee.middle_name.ilike(term),
            )
        )

    if filters.department_id is not None:
        conditions.append(Employee.position.has(Position.department_id == filters.department_id))

    if filters.position_id is not None:
        conditions.append(Employee.position_id == filters.position_id)

    if filters.gender is not None:
        conditions.append(Employee.gender == filters.gender)

    if filters.employment_status is not None:
        conditions.append(Employee.employment_status == filters.employment_status)

    if filters.min_age is not None:
        max_birth_date = today_tashkent() - timedelta(days=filters.min_age * APPROX_DAYS_PER_YEAR)
        conditions.append(Employee.birth_date <= max_birth_date)

    if filters.max_age is not None:
        min_birth_date = today_tashkent() - timedelta(days=(filters.max_age + 1) * APPROX_DAYS_PER_YEAR)
        conditions.append(Employee.birth_date > min_birth_date)

    if filters.education_level is not None:
        conditions.append(Employee.education_history.any(EducationHistory.level == filters.education_level))

    if filters.specialty_keyword:
        term = f"%{filters.specialty_keyword.strip()}%"
        conditions.append(Employee.education_history.any(EducationHistory.specialty.ilike(term)))

    if filters.specialization_area:
        conditions.append(Employee.specialization_area.ilike(f"%{filters.specialization_area.strip()}%"))

    if filters.min_years_in_position is not None:
        cutoff = today_tashkent() - timedelta(days=int(filters.min_years_in_position * APPROX_DAYS_PER_YEAR))
        conditions.append(Employee.position_since.is_not(None))
        conditions.append(Employee.position_since <= cutoff)

    if filters.nationality:
        conditions.append(Employee.nationality.ilike(f"%{filters.nationality.strip()}%"))

    if filters.has_awards is not None:
        conditions.append(Employee.awards.any() if filters.has_awards else ~Employee.awards.any())

    if filters.hired_after is not None:
        conditions.append(Employee.hire_date >= filters.hired_after)

    if filters.hired_before is not None:
        conditions.append(Employee.hire_date <= filters.hired_before)

    return conditions


async def search_employees(db: AsyncSession, filters: EmployeeSearchFilter) -> tuple[int, list[Employee]]:
    conditions = _build_conditions(filters)

    count_stmt = select(func.count(Employee.id)).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    data_stmt = (
        select(Employee)
        .where(*conditions)
        .order_by(Employee.last_name, Employee.first_name)
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    )
    result = await db.execute(data_stmt)
    items = list(result.scalars().unique().all())

    return total, items
