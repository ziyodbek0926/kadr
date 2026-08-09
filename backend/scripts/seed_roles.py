import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.enums import UserRole
from app.models.role import Role

_DISPLAY_NAMES = {
    UserRole.SUPER_ADMIN: "Super administrator",
    UserRole.HR_OPERATOR: "Kadrlar bo'limi xodimi",
    UserRole.MANAGEMENT_VIEWER: "Rahbariyat (faqat o'qish)",
    UserRole.IT_ADMIN: "IT administrator",
}


async def seed_roles() -> None:
    async with AsyncSessionLocal() as db:
        existing = {row.code for row in (await db.execute(select(Role))).scalars().all()}
        created = 0
        for role in UserRole:
            if role.value in existing:
                continue
            db.add(Role(code=role.value, display_name=_DISPLAY_NAMES[role]))
            created += 1
        await db.commit()
        print(f"Tayyor: {created} ta yangi rol qo'shildi, {len(existing)} tasi allaqachon mavjud edi.")


if __name__ == "__main__":
    asyncio.run(seed_roles())
