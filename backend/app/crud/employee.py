from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import encrypt_field, hash_lookup_value
from app.crud.base import CRUDBase
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

_DETAIL_RELATIONSHIPS = (
    "position",
    "relatives",
    "education_history",
    "work_history",
    "awards",
    "foreign_trips",
)


class CRUDEmployee(CRUDBase[Employee]):
    async def get_detail(self, db: AsyncSession, id: int) -> Employee | None:
        stmt = (
            select(Employee)
            .where(Employee.id == id, Employee.is_deleted.is_(False))
            .options(*(selectinload(getattr(Employee, rel)) for rel in _DETAIL_RELATIONSHIPS))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_pinfl(self, db: AsyncSession, pinfl: str) -> Employee | None:
        """Shifrlangan PINFL'ni deshifrlamasdan, deterministik hash orqali topadi
        (yangi xodim qo'shishda dublikat PINFL'ni oldindan ushlash uchun)."""
        stmt = select(Employee).where(Employee.pinfl_hash == hash_lookup_value(pinfl), Employee.is_deleted.is_(False))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: EmployeeCreate) -> Employee:
        data = obj_in.model_dump(exclude={"pinfl", "passport_number"})
        if obj_in.pinfl:
            data["pinfl_encrypted"] = encrypt_field(obj_in.pinfl)
            data["pinfl_hash"] = hash_lookup_value(obj_in.pinfl)
        if obj_in.passport_number:
            data["passport_number_encrypted"] = encrypt_field(obj_in.passport_number)
        db_obj = Employee(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Employee, obj_in: EmployeeUpdate) -> Employee:
        data = obj_in.model_dump(exclude_unset=True, exclude={"pinfl", "passport_number"})
        if obj_in.pinfl is not None:
            data["pinfl_encrypted"] = encrypt_field(obj_in.pinfl)
            data["pinfl_hash"] = hash_lookup_value(obj_in.pinfl)
        if obj_in.passport_number is not None:
            data["passport_number_encrypted"] = encrypt_field(obj_in.passport_number)
        for field, value in data.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, db: AsyncSession, *, db_obj: Employee) -> None:
        db_obj.is_deleted = True
        await db.flush()


employee_crud = CRUDEmployee(Employee)
