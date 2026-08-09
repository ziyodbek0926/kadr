from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase, ModelType


class CRUDEmployeeChild(CRUDBase[ModelType]):
    """relatives/education_history/work_history/awards/foreign_trips kabi doim
    `employee_id` orqali ota-yozuvga (Employee) bog'langan jadvallar uchun umumiy CRUD.

    `ModelType` (CRUDBase'dan meros) faqat `Base`'ga bog'langan, shuning uchun statik
    tahlilchi `.employee_id` borligini kafolatlay olmaydi — bu barcha bola-modellarda
    haqiqatan mavjud umumiy naqsh (relative.py, education_history.py va h.k.)."""

    async def list_by_employee(self, db: AsyncSession, *, employee_id: int) -> list[ModelType]:
        stmt = select(self.model).where(self.model.employee_id == employee_id)  # type: ignore[attr-defined]
        result = await db.execute(stmt)
        return list(result.scalars().all())
