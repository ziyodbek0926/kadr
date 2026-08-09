import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.v1.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
async def login(request: Request, response: Response, credentials: LoginRequest, db: DbSession) -> TokenResponse:
    generic_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login yoki parol noto'g'ri")

    user = await user_crud.get_by_username(db, credentials.username)
    if user is None:
        raise generic_error

    if user_crud.is_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Hisob vaqtincha bloklangan — bir necha daqiqadan so'ng qayta urinib ko'ring",
        )

    if not user.is_active or not verify_password(credentials.password, user.hashed_password):
        if user.is_active:
            await user_crud.register_failed_login(db, user=user)
            await db.commit()
        raise generic_error

    await user_crud.register_successful_login(db, user=user)
    await db.commit()

    access_token = create_access_token(subject=user.username, role=user.role.code)
    refresh_token = create_refresh_token(subject=user.username)

    # Refresh token faqat httpOnly cookie orqali — JS tomonidan o'qib bo'lmaydi (XSS orqali o'g'irlanmaydi)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v1/auth",
    )

    return TokenResponse(access_token=access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, db: DbSession) -> TokenResponse:
    refresh_token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token topilmadi")

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token yaroqsiz") from None

    user = await user_crud.get_by_username(db, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    access_token = create_access_token(subject=user.username, role=user.role.code)
    return TokenResponse(access_token=access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/api/v1/auth")


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> User:
    return current_user
