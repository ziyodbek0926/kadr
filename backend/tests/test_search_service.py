import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.employee import Employee
from app.schemas.search import EmployeeSearchFilter
from app.services.search_service import _build_conditions


def test_filter_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        EmployeeSearchFilter(raw_sql="DROP TABLE employees;")


def test_filter_rejects_min_age_greater_than_max_age() -> None:
    with pytest.raises(ValidationError):
        EmployeeSearchFilter(min_age=50, max_age=20)


def test_build_conditions_compiles_to_parameterized_sql() -> None:
    filters = EmployeeSearchFilter(full_name="Aliyev O'", specialization_area="IT", min_years_in_position=2)
    conditions = _build_conditions(filters)
    stmt = select(Employee).where(*conditions)

    compiled = stmt.compile(dialect=postgresql.dialect())

    assert "Aliyev" not in str(compiled)
    assert "Aliyev O'" in list(compiled.params.values()) or any(
        "Aliyev" in str(v) for v in compiled.params.values()
    )


def test_build_conditions_always_excludes_soft_deleted() -> None:
    filters = EmployeeSearchFilter()
    conditions = _build_conditions(filters)
    stmt = select(Employee).where(*conditions)
    compiled_sql = str(stmt.compile(dialect=postgresql.dialect()))
    assert "is_deleted" in compiled_sql
