from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Oddiy (maxsus mantiqsiz) modellar uchun umumiy CRUD. Employee/User kabi
    shifrlash yoki qo'shimcha biznes-qoida talab qiladigan modellar buni meros
    qilib olib, create/update metodlarini o'zgartiradi (bunday qilishning
    o'zi ham employees.py'dagi kabi vazifalarni yagona joyda ushlab turadi).

    `obj_in: Any` ataylab qat'iy `dict` emas — CRUDEmployee/CRUDUser kabi vorislar
    Pydantic sxemasini to'g'ridan-to'g'ri qabul qiladi (encrypt_field/hash_password
    kabi qo'shimcha ishlov berish shart bo'lgani uchun), bazaviy klass esa oddiy
    lug'atni kutadi — shu farq shu yerda ochiq e'lon qilinadi."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        return await db.get(self.model, id)

    async def list(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: Any) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: Any) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: ModelType) -> None:
        await db.delete(db_obj)
        await db.flush()
