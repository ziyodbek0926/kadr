from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.base import CRUDBase
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class CRUDUser(CRUDBase[User]):
    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        role_stmt = select(Role).where(Role.code == obj_in.role_code.value)
        role = (await db.execute(role_stmt)).scalar_one_or_none()
        if role is None:
            raise ValueError(
                f"Rol topilmadi: {obj_in.role_code.value} — avval bootstrap migratsiyasini bajaring"
            )
        db_obj = User(
            username=obj_in.username,
            hashed_password=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            role_id=role.id,
            employee_id=obj_in.employee_id,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    def is_locked(self, user: User) -> bool:
        return user.locked_until is not None and user.locked_until > datetime.now(UTC)

    async def register_failed_login(self, db: AsyncSession, *, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now(UTC) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        await db.flush()

    async def register_successful_login(self, db: AsyncSession, *, user: User) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)
        await db.flush()


user_crud = CRUDUser(User)
