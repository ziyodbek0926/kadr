from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.v1.deps import CurrentUser, DbSession, EditorUser
from app.crud.department import department_crud
from app.crud.position import position_crud
from app.models.department import Department
from app.models.position import Position
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.schemas.position import PositionCreate, PositionRead, PositionReadWithDepartment, PositionUpdate

router = APIRouter()


async def _get_department_or_404(db: DbSession, department_id: int) -> Department:
    department = await department_crud.get(db, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bo'lim topilmadi")
    return department


async def _get_position_or_404(db: DbSession, position_id: int) -> Position:
    position = await position_crud.get(db, position_id)
    if position is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lavozim topilmadi")
    return position


# ---- Bo'limlar ----


@router.get("/departments", response_model=list[DepartmentRead])
async def list_departments(db: DbSession, current_user: CurrentUser) -> list[Department]:
    return await department_crud.list(db, limit=500)


@router.post("/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(payload: DepartmentCreate, db: DbSession, current_user: EditorUser) -> Department:
    department = await department_crud.create(db, obj_in=payload.model_dump())
    await db.commit()
    return department


@router.patch("/departments/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: int, payload: DepartmentUpdate, db: DbSession, current_user: EditorUser
) -> Department:
    department = await _get_department_or_404(db, department_id)
    department = await department_crud.update(db, db_obj=department, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return department


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: int, db: DbSession, current_user: EditorUser) -> None:
    department = await _get_department_or_404(db, department_id)
    try:
        await department_crud.remove(db, db_obj=department)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu bo'limda lavozimlar mavjud — avval ularni o'chiring yoki boshqa bo'limga ko'chiring",
        ) from None


# ---- Lavozimlar ----


@router.get("/positions", response_model=list[PositionReadWithDepartment])
async def list_positions(
    db: DbSession, current_user: CurrentUser, department_id: int | None = None
) -> list[Position]:
    positions = await position_crud.list(db, limit=1000)
    if department_id is not None:
        positions = [p for p in positions if p.department_id == department_id]
    return positions


@router.post("/positions", response_model=PositionRead, status_code=status.HTTP_201_CREATED)
async def create_position(payload: PositionCreate, db: DbSession, current_user: EditorUser) -> Position:
    await _get_department_or_404(db, payload.department_id)
    position = await position_crud.create(db, obj_in=payload.model_dump())
    await db.commit()
    return position


@router.patch("/positions/{position_id}", response_model=PositionRead)
async def update_position(
    position_id: int, payload: PositionUpdate, db: DbSession, current_user: EditorUser
) -> Position:
    position = await _get_position_or_404(db, position_id)
    if payload.department_id is not None:
        await _get_department_or_404(db, payload.department_id)
    position = await position_crud.update(db, db_obj=position, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return position


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(position_id: int, db: DbSession, current_user: EditorUser) -> None:
    position = await _get_position_or_404(db, position_id)
    await position_crud.remove(db, db_obj=position)
    await db.commit()
