"""Birinchi SuperAdmin foydalanuvchisini yaratish. API orqali foydalanuvchi yaratish
uchun avvaldan SuperAdmin kerak (require_role) — bu skript shu "tuxum-tovuq" muammosini
hal qiladi, to'g'ridan-to'g'ri bazaga yozadi. `alembic upgrade head` va
`scripts/seed_roles.py`dan KEYIN, faqat bir marta ishga tushiriladi:

    python scripts/create_superadmin.py --username admin --password "Kuchli-Parol123"

Login allaqachon mavjud bo'lsa, xavfsiz tarzda hech narsa qilmaydi (idempotent)."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from app.core.database import AsyncSessionLocal
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.schemas.user import UserCreate


async def create_superadmin(username: str, password: str, full_name: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = await user_crud.get_by_username(db, username)
        if existing is not None:
            print(f"'{username}' allaqachon mavjud — hech narsa qilinmadi.")
            return

        payload = UserCreate(username=username, password=password, full_name=full_name, role_code=UserRole.SUPER_ADMIN)
        await user_crud.create(db, obj_in=payload)
        await db.commit()
        print(f"Tayyor: '{username}' SuperAdmin sifatida yaratildi.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Birinchi SuperAdmin foydalanuvchisini yaratish")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--full-name", default="Administrator")
    args = parser.parse_args()

    try:
        UserCreate(username=args.username, password=args.password, full_name=args.full_name, role_code=UserRole.SUPER_ADMIN)
    except ValidationError as exc:
        print("Kiritilgan ma'lumotlar talabga javob bermaydi:")
        print(exc)
        raise SystemExit(1) from exc

    asyncio.run(create_superadmin(args.username, args.password, args.full_name))


if __name__ == "__main__":
    main()
