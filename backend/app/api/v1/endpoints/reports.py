from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.v1.deps import CurrentUser, DbSession
from app.schemas.search import EmployeeSearchFilter
from app.services.excel_export import export_employees_to_excel
from app.services.search_service import search_employees

router = APIRouter()


@router.post("/employees/export")
async def export_employees(filters: EmployeeSearchFilter, db: DbSession, current_user: CurrentUser):
    # Eksport uchun sahifalashsiz — bitta hisobot faylida yetadigan maksimal hajm bilan cheklaymiz
    export_filters = filters.model_copy(update={"page": 1, "page_size": 1000})
    _, employees = await search_employees(db, export_filters)
    buffer = export_employees_to_excel(employees)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="xodimlar_hisobot.xlsx"'},
    )
