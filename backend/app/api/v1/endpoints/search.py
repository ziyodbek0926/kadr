from fastapi import APIRouter

from app.api.v1.deps import CurrentUser, DbSession
from app.schemas.employee import EmployeeListItem
from app.schemas.search import EmployeeSearchFilter, EmployeeSearchResult
from app.services.search_service import search_employees

router = APIRouter()


@router.post("/employees/search", response_model=EmployeeSearchResult)
async def advanced_employee_search(
    filters: EmployeeSearchFilter,
    db: DbSession,
    current_user: CurrentUser,
) -> EmployeeSearchResult:
    """10+ parametrli dinamik qidiruv (masalan: 'joriy lavozimida 2 yildan ortiq
    ishlayotgan IT sohasidagi mutaxassislar'). Filtrlar POST body orqali yuboriladi
    (GET query-string emas) — 14 ta ixtiyoriy maydonni URL'da tashish o'rniga."""

    total, items = await search_employees(db, filters)
    return EmployeeSearchResult(
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        items=[EmployeeListItem.model_validate(item) for item in items],
    )
