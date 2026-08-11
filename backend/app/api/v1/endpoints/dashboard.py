from fastapi import APIRouter

from app.api.v1.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import get_dashboard_stats

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
async def read_dashboard_stats(db: DbSession, current_user: CurrentUser) -> DashboardStats:
    # CurrentUser (barcha rollar) — Rahbariyat ham shu sahifani ko'ra olishi kerak,
    # chunki uning tizimdagi asosiy vazifasi aynan ko'rish/hisobot olish (TZ 8-bo'lim).
    return await get_dashboard_stats(db)
