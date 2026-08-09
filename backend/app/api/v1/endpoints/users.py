from fastapi import APIRouter, HTTPException, status

from app.api.v1.deps import AdminUser, CurrentUser, DbSession
from app.core.security import hash_password, verify_password
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import PasswordChange, UserCreate, UserRead

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def list_users(db: DbSession, current_user: AdminUser) -> list[User]:
    return await user_crud.list(db)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DbSession, current_user: AdminUser) -> User:
    if await user_crud.get_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu login band")
    try:
        user = await user_crud.create(db, obj_in=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    await db.commit()
    return user


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(payload: PasswordChange, db: DbSession, current_user: CurrentUser) -> None:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Joriy parol noto'g'ri")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()


@router.patch("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(user_id: int, db: DbSession, current_user: AdminUser) -> None:
    user = await user_crud.get(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
    user.is_active = False
    await db.commit()
