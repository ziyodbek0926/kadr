from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import func, select

from app.api.v1.deps import DbSession
from app.core.config import settings
from app.core.rate_limit import limiter
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.setup import SetupStatus, SuperAdminCreate
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


async def _no_users_exist(db: DbSession) -> bool:
    count = (await db.execute(select(func.count(User.id)))).scalar_one()
    return count == 0


@router.get("/status", response_model=SetupStatus)
async def get_setup_status(db: DbSession) -> SetupStatus:
    return SetupStatus(needs_setup=await _no_users_exist(db))


@router.post("/create-superadmin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
async def create_superadmin(request: Request, payload: SuperAdminCreate, db: DbSession) -> User:
    """Faqat `users` jadvali BO'SH bo'lganda ishlaydi — standalone o'rnatuvchining birinchi
    ishga tushirilishidagi bir martalik "sozlash sehrgari" uchun. Autentifikatsiya talab
    qilmaydi (hali hech kim yo'q) — shu sabab haqiqiy xavfsizlik chegarasi aynan shu
    "bo'shmi" tekshiruvi: `GET /status`dagi frontend ko'rsatkichiga ishonib bo'lmaydi,
    shuning uchun bu yerda SERVER tomonida qayta tekshiriladi."""
    if not await _no_users_exist(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tizim allaqachon sozlangan — bu amal faqat birinchi ishga tushirishda mavjud",
        )

    if await user_crud.get_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu login band")

    user_in = UserCreate(
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
        role_code=UserRole.SUPER_ADMIN,
    )
    try:
        user = await user_crud.create(db, obj_in=user_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    await db.commit()
    return user
