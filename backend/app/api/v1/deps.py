from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=True)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: DbSession,
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kirish tokeni yaroqsiz yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except jwt.PyJWTError:
        raise credentials_error from None

    username = payload.get("sub")
    if username is None:
        raise credentials_error

    user = await user_crud.get_by_username(db, username)
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: UserRole):
    """FastAPI dependency-fabrikasi: faqat ro'yxatdagi rollarga endpoint'ni ochadi.
    Tekshiruv har doim backend'da bajariladi — frontend'dagi rolga qarab UI elementini
    yashirish faqat qulaylik uchun, xavfsizlik chegarasi sifatida ishonib bo'lmaydi."""

    allowed_codes = {role.value for role in allowed_roles}

    async def _check(current_user: CurrentUser) -> User:
        if current_user.role.code not in allowed_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu amal uchun yetarli huquq yo'q",
            )
        return current_user

    return _check


EditorUser = Annotated[User, Depends(require_role(UserRole.SUPER_ADMIN, UserRole.HR_OPERATOR))]
AdminUser = Annotated[User, Depends(require_role(UserRole.SUPER_ADMIN))]


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
